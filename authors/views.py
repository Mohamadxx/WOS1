from django.shortcuts import render, get_object_or_404
from .models import Author
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
# Create your views here.



def author_list(request):
    authors = Author.objects.all()
    paginator = Paginator(authors, 20) # Display 10 authors per page
    page_number = request.GET.get('page', 1)  # Default to page 1
    page_obj = paginator.get_page(page_number)

    return render(request, 'authors/author_list.html', {'page_obj': page_obj})

def author_detail(request, slug):
    author = get_object_or_404(Author, slug=slug)
    print('authors', author.name)
    for publication in author.publications.all():
        print(publication.title)
        print(publication.volume)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('authors/author_detail.html', {'author': author})
        return JsonResponse({'html': html})
    return render(request, 'authors/author_detail.html', {'author': author})


def index(request):
    print("view is triggered")
    all_authors = Author.objects.all()
    return render(request, "base.html", {
      "all_authors": all_authors
    })


def author_details(request, slug):
     identified_author = get_object_or_404(Author, slug=slug)
     all_authors = Author.objects.all()
     return render(request, "authors/author.html", {
      "details": identified_author,
       "all_authors": all_authors
    })


