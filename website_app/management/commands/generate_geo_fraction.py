import os
from collections import Counter
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from website_app.models import Vacancy
from django.db.models import Q


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        output_path = os.path.join("website_app", "static", "images")
        template_path = os.path.join("website_app", "templates", "website_app")
        os.makedirs(output_path, exist_ok=True)
        os.makedirs(template_path, exist_ok=True)

        backend_keywords = [
            'backend', 'бэкэнд', 'бэкенд', 'бекенд', 'бэкэнд',
            'back end', 'бэк энд', 'бэк енд', 'django', 'flask',
            'laravel', 'yii', 'symfony'
        ]

        city_vacancy_counts = Counter()
        city_vacancy_counts_backend = Counter()

        vacancies = Vacancy.objects.all()

        backend_query = Q()
        for keyword in backend_keywords:
            backend_query |= Q(name__icontains=keyword)

        vacancies_backend = Vacancy.objects.filter(backend_query)

        for vacancy in vacancies:
            city = vacancy.area_name if vacancy.area_name else "Не указано"
            city_vacancy_counts[city] += 1

        for vacancy in vacancies_backend:
            city = vacancy.area_name if vacancy.area_name else "Не указано"
            city_vacancy_counts_backend[city] += 1

        total_vacancies = sum(city_vacancy_counts.values())
        total_vacancies_backend = sum(city_vacancy_counts_backend.values())

        city_vacancy_shares = {
            city: (count / total_vacancies) * 100
            for city, count in city_vacancy_counts.items()
        }

        city_vacancy_shares_backend = {
            city: (count / total_vacancies_backend) * 100
            for city, count in city_vacancy_counts_backend.items()
        }

        sorted_city_vacancy_shares = sorted(city_vacancy_shares.items(), key=lambda x: x[1], reverse=True)[:20]
        sorted_city_vacancy_shares_backend = sorted(city_vacancy_shares_backend.items(), key=lambda x: x[1], reverse=True)[:20]

        self.stdout.write("Доля вакансий по городам (топ-20) для всех профессий:")
        self.stdout.write(f"{'Город':<30}{'Доля вакансий (%)':<20}")
        for city, share in sorted_city_vacancy_shares:
            self.stdout.write(f"{city:<30}{share:<20.4f}")

        self.stdout.write("Доля вакансий по городам (топ-20) для Backend-программистов:")
        self.stdout.write(f"{'Город':<30}{'Доля вакансий (%)':<20}")
        for city, share in sorted_city_vacancy_shares_backend:
            self.stdout.write(f"{city:<30}{share:<20.4f}")

        cities_all = [item[0] for item in sorted_city_vacancy_shares]
        shares_all = [item[1] for item in sorted_city_vacancy_shares]

        cities_backend = [item[0] for item in sorted_city_vacancy_shares_backend]
        shares_backend = [item[1] for item in sorted_city_vacancy_shares_backend]

        plt.figure(figsize=(12, 8))
        plt.barh(cities_all[::-1], shares_all[::-1], color="skyblue")
        plt.title("Доля вакансий по городам (топ-20) для всех профессий")
        plt.xlabel("Доля вакансий (%)")
        plt.ylabel("Город")
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        plt.tight_layout()

        filename_all = "city_vacancis.png"
        graph_path_all = os.path.join(output_path, filename_all)
        plt.savefig(graph_path_all)
        plt.close()

        plt.figure(figsize=(12, 8))
        plt.barh(cities_backend[::-1], shares_backend[::-1], color="orange")
        plt.title("Доля вакансий по городам (топ-20) для Backend-программистов")
        plt.xlabel("Доля вакансий (%)")
        plt.ylabel("Город")
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        plt.tight_layout()

        filename_backend = "city_vacancy_shares_backend_top20.png"
        graph_path_backend = os.path.join(output_path, filename_backend)
        plt.savefig(graph_path_backend)
        plt.close()

        html_content = """
            <h1>Доля вакансий по городам (топ-20) для всех профессий</h1>
            <table border="1">
                <tr>
                    <th>Город</th>
                    <th>Доля вакансий (%)</th>
                </tr>
        """
        for city, share in sorted_city_vacancy_shares:
            html_content += f"""
                <tr>
                    <td>{city}</td>
                    <td>{share:.2f}</td>
                </tr>
            """
        html_content += f"""
            </table>
            <h2>График</h2>
            <img src="{os.path.join('/static/images/', filename_all)}" alt="Доля вакансий по городам (топ-20) для всех профессий">
            <br><br>
            <h1>Доля вакансий по городам (топ-20) для Backend-программистов</h1>
            <table border="1">
                <tr>
                    <th>Город</th>
                    <th>Доля вакансий (%)</th>
                </tr>
        """
        for city, share in sorted_city_vacancy_shares_backend:
            html_content += f"""
                <tr>
                    <td>{city}</td>
                    <td>{share:.2f}</td>
                </tr>
            """
        html_content += f"""
            </table>
            <h2>График</h2>
            <img src="{os.path.join('/static/images/', filename_backend)}" alt="Доля вакансий по городам (топ-20) для Backend-программистов">
        """

        with open(os.path.join(template_path, "city_vacancy_statistics_with_backend.html"), "w", encoding="utf-8") as file:
            file.write(html_content)

        self.stdout.write("HTML-контент для статистики по городам и Backend-программистам успешно сохранён.")

