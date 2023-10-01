from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='FRESCO-Data-Repo-Home'),
    path('about/', views.about, name='FRESCO-Data-Repo-About'),
]
