# Generated by Django 4.2.17 on 2025-01-16 18:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website_app', '0002_backendvacancy_alter_vacancy_options'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BackendVacancy',
        ),
        migrations.AlterModelOptions(
            name='vacancy',
            options={'ordering': ['-published_at'], 'verbose_name': 'Вакансия', 'verbose_name_plural': 'Вакансии'},
        ),
    ]
