from django.urls import path
from . import views


urlpatterns = [
     path("", views.index, name="index"),
    path("author/<slug:slug>", views.author_details, name="author-details" ),
    path('authors/', views.author_list, name='author_list'),
    path('authors/<slug:slug>/', views.author_detail, name='author_detail'),
]
