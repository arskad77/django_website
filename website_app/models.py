# Create your models here.
from django.db import models


class Vacancy(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название вакансии")

    key_skills = models.TextField(null=True, blank=True, verbose_name="Ключевые навыки")

    salary_from = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Зарплата от"
    )

    salary_to = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Зарплата до"
    )

    salary_currency = models.CharField(
        max_length=10, null=True, blank=True, verbose_name="Валюта зарплаты"
    )

    area_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Город/регион"
    )

    published_at = models.DateTimeField(verbose_name="Дата публикации")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["-published_at"]


class PageContent(models.Model):
    page_name = models.CharField(max_length=255, unique=True)
    html_content = models.TextField()

    def __str__(self):
        return self.page_name
