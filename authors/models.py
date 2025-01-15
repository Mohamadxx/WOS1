from django.db import models
from django.utils.text import slugify

class Author(models.Model):
    name = models.CharField(max_length=500, unique=True)
    slug = models.SlugField(max_length=500, unique=True, db_index=True)
    h_index = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    
class Publication(models.Model):
    title = models.TextField()  
    authors = models.ManyToManyField(Author, related_name="publications")  
    source = models.TextField(null=True, blank=True, default="Unknown")  
    language = models.TextField()  
    document_type = models.TextField()  
    publication_date = models.DateField(null=True, blank=True)
    volume = models.TextField(null=True, blank=True)  
    issue = models.TextField(null=True, blank=True)  
    pages = models.TextField(null=True, blank=True)  
    doi = models.TextField(null=True, blank=True, unique=True) 
    wos_id = models.TextField(unique=True,null=True, blank=True)  
    category = models.TextField(null=True, blank=True)  
    citations = models.IntegerField(default=0)
    



    def __str__(self):
        return self.title