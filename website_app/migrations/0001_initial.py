# Generated by Django 4.2.17 on 2025-01-09 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Vacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название вакансии')),
                ('key_skills', models.TextField(blank=True, null=True, verbose_name='Ключевые навыки')),
                ('salary_from', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Зарплата от')),
                ('salary_to', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Зарплата до')),
                ('salary_currency', models.CharField(blank=True, max_length=10, null=True, verbose_name='Валюта зарплаты')),
                ('area_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Город/регион')),
                ('published_at', models.DateTimeField(verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name': 'Вакансия',
                'verbose_name_plural': 'Вакансии',
                'ordering': ['-published_at'],
            },
        ),
    ]
