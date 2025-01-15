import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from authors.models import Author, Publication
from django.utils.text import slugify
import random


def parse_bibliographic_file(file_path):
    
    publications = []
    record = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            # Parse fields based on prefixes
            if line.startswith("TI"):
                record["title"] = line[3:].strip()
            elif line.startswith("DI"):
                record["doi"] = line[3:].strip()
            elif line.startswith("AU"):
                authors = record.get("authors", [])
                authors.append(line[3:].strip())
                record["authors"] = authors
            elif line.startswith("SO"):
                record["source"] = line[3:].strip()
            elif line.startswith("PY"):
                record["publication_date"] = line[3:].strip()
            elif line.startswith("VL"):
                record["volume"] = line[3:].strip()
            elif line.startswith("IS"):
                # Safely process the issue field
                record["issue"] = line[3:].strip() if len(line) > 3 else ""
            elif line.startswith("BP"):
                record["pages"] = line[3:].strip()
            elif line.startswith("EP"):
                record["pages"] = record.get("pages", "") + f"-{line[3:].strip()}"
            elif line.startswith("ER"):
                # End of record: save and reset
                publications.append(record)
                record = {}

    return publications




def parse_date(date_str):
    
    try:
        
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        pass

    try:
       
        datetime.strptime(date_str, '%Y')
        return f"{date_str}-01-01"
    except ValueError:
        pass

    
    return None


class Command(BaseCommand):
    help = "Import data from CSV and text files into the database"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the text file containing publication data')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        if not os.path.exists(file_path):
            self.stderr.write(f"Error: File not found: {file_path}")
            return

        #self.import_authors()
        self.import_publications(file_path)


    def import_authors(self):
        authors_file = '/root/WOS/data/1981/author_h_index.csv'

        if not os.path.exists(authors_file):
            self.stderr.write(f"Error: File not found: {authors_file}")
            return

        with open(authors_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not row.get('name') or not row.get('h_index') or len(row['name'].strip()) == 0:
                    self.stdout.write(self.style.WARNING(f"Skipping row with missing data: {row}"))
                    continue

                base_slug = slugify(row['name'])
                unique_slug = self.generate_unique_slug(base_slug, Author)

                author, created = Author.objects.get_or_create(
                    name=row['name'].strip(),
                    defaults={
                        'slug': unique_slug,
                        'h_index': int(row['h_index']) if row['h_index'].isdigit() else 0,
                    },
                )

                if not created:
                    if row.get('h_index') and row['h_index'].isdigit():
                        author.h_index = int(row['h_index'])
                    author.save()

                if created:
                    self.stdout.write(f"Created new author: {author.name}")
                else:
                    self.stdout.write(f"Author already exists: {author.name}")

        self.stdout.write(self.style.SUCCESS('Successfully imported authors'))

    def import_publications(self, file_path):
        """
        Import parsed publication data into the database.

        """

        def generate_unique_slug(name):
            base_slug = slugify(name)
            unique_slug = base_slug
            counter = 1
            while Author.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{random.randint(1, 9999)}"
                counter += 1
            return unique_slug
        records = parse_bibliographic_file(file_path)
        existing_publications = {p.doi: p for p in Publication.objects.all()}

        for idx, record in enumerate(records, 1):
            self.stdout.write(f"Processing record {idx}/{len(records)}")

            doi = record.get("doi")
            if not record.get("title"):
                self.stdout.write(self.style.ERROR("Skipping publication without a title."))
                continue

            # Parse the publication date
            raw_date = record.get("publication_date", "")
            parsed_date = parse_date(raw_date)
            if parsed_date is None:
                self.stdout.write(self.style.ERROR(f"Skipping publication with invalid date: {raw_date}"))
                continue

            fields = {
                "title": record.get("title"),
                "source": record.get("source"),
                "publication_date": parsed_date,
                "volume": record.get("volume"),
                "issue": record.get("issue"),
                "pages": record.get("pages"),
                "doi": doi,
            }

            if doi in existing_publications:
                publication = existing_publications[doi]
                for key, value in fields.items():
                    setattr(publication, key, value)
                publication.save()
            else:
                publication = Publication.objects.create(**fields)
                existing_publications[doi] = publication

            # Associate authors
            if "authors" in record:
                author_objects = []
                for author_name in record["authors"]:
                    #author_slug = slugify(author_name)
                    author_slug = generate_unique_slug(author_name)
                    author, _ = Author.objects.get_or_create(name=author_name, defaults={"slug": author_slug})

                    #author, _ = Author.objects.get_or_create(name=author_name, defaults={"slug": author_slug})
                    author_objects.append(author)
                publication.authors.set(author_objects)

        self.stdout.write(self.style.SUCCESS("Successfully imported publications"))
