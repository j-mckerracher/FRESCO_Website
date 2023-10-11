from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='FRESCO-Data-Repo-Home'),
    path('about/', views.about, name='FRESCO-Data-Repo-About'),
    path('team/', views.team, name='FRESCO-Data-Repo-Team'),
    path('news/', views.news, name='FRESCO-Data-Repo-News')
]
