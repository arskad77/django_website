import os
from collections import Counter
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from website_app.models import Vacancy


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        output_path = os.path.join("website_app", "static", "images")
        os.makedirs(output_path, exist_ok=True)

        vacancies = Vacancy.objects.filter(published_at__isnull=False)

        vacancy_count_by_year = Counter()
        for vacancy in vacancies:
            year = vacancy.published_at.year
            vacancy_count_by_year[year] += 1

        self.stdout.write("Динамика количества вакансий по годам:")
        self.stdout.write(f"{'Год':<10}{'Количество вакансий':<20}")
        for year, count in sorted(vacancy_count_by_year.items()):
            self.stdout.write(f"{year:<10}{count:<20}")

        years = sorted(vacancy_count_by_year.keys())
        vacancy_counts = [vacancy_count_by_year[year] for year in years]

        plt.figure(figsize=(10, 6))
        plt.bar(years, vacancy_counts, color="skyblue", label="Количество вакансий")
        plt.title("Динамика количества вакансий по годам")
        plt.xlabel("Год")
        plt.ylabel("Количество вакансий")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.xticks(years, rotation=45)
        plt.legend()
        plt.tight_layout()

        graph_path = os.path.join(output_path, "vacancy_count_trends.png")
        plt.savefig(graph_path)
        plt.close()

        self.stdout.write(f"График сохранён по пути: {graph_path}")
