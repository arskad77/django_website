from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Vacancy, PageContent


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("name", "salary_from", "salary_to", "area_name", "published_at")
    search_fields = ("name", "area_name")
    list_filter = ("salary_currency", "area_name", "published_at")


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ('page_name',)
