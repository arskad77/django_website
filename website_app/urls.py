from django.urls import path
from . import views

urlpatterns = [
    path('backend-vacancies/', views.backend_vacancies, name='backend_vacancies'),
    path('', views.home, name='home'),
    path('statistics/', views.general_stats, name='statistics'),
    path('popularity/', views.popularity_stats, name='popularity'),
    path('geography/', views.geography_stats, name='geography'),
    path('skills/', views.skills_stats, name='skills'),
]