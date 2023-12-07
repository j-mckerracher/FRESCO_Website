from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='FRESCO-Data-Repo-Home'),
    path('about/', views.about, name='FRESCO-Data-Repo-About'),
    path('team/', views.team, name='FRESCO-Data-Repo-Team'),
    path('news/', views.news, name='FRESCO-Data-Repo-News'),
    path('simple-repository-search/', views.repository_simple_search, name='FRESCO-Data-Repo-Simple-Search'),
    path('download-csv/', views.download_search_results_as_csv, name='FRESCO-Data-Repo-Download-Host-CSV')
]
