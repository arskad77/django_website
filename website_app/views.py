from django.shortcuts import render

from website_app.models import PageContent
from website_app.utils.hhAPI import get_backend_vacancies


# Create your views here.
def home(request):
    try:
        page_content = PageContent.objects.get(page_name="Главная")
        html_content = page_content.html_content
    except PageContent.DoesNotExist:
        html_content = "<p>Содержимое страницы пока не добавлено.</p>"

    return render(request, 'website_app/home.html', {'html_content': html_content})


def backend_vacancies(request):
    vacancies = get_backend_vacancies()
    return render(request, "website_app/backend_vacancies.html", {"vacancies": vacancies})


def general_stats(request):
    try:
        page_content = PageContent.objects.get(page_name="Общая статистика")
        html_content = page_content.html_content
    except PageContent.DoesNotExist:
        html_content = "<p>Содержимое страницы пока не добавлено.</p>"

    return render(request, 'website_app/general_stats.html', {'html_content': html_content})


def popularity_stats(request):
    try:
        page_content = PageContent.objects.get(page_name="Востребованность")
        html_content = page_content.html_content
    except PageContent.DoesNotExist:
        html_content = "<p>Содержимое страницы пока не добавлено.</p>"

    return render(request, 'website_app/popularity_stats.html', {'html_content': html_content})


def geography_stats(request):
    try:
        page_content = PageContent.objects.get(page_name="География")
        html_content = page_content.html_content
    except PageContent.DoesNotExist:
        html_content = "<p>Содержимое страницы пока не добавлено.</p>"

    return render(request, 'website_app/geography_stats.html', {'html_content': html_content})


def skills_stats(request):
    try:
        page_content = PageContent.objects.get(page_name="Навыки")
        html_content = page_content.html_content
    except PageContent.DoesNotExist:
        html_content = "<p>Содержимое страницы пока не добавлено.</p>"

    return render(request, 'website_app/skills_stats.html', {'html_content': html_content})