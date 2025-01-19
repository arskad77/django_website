import os
from decimal import Decimal
from collections import defaultdict
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

        city_salary_data_all = defaultdict(list)
        city_salary_data_backend = defaultdict(list)

        vacancies = Vacancy.objects.filter(area_name__isnull=False)
        backend_query = Q()
        for keyword in backend_keywords:
            backend_query |= Q(name__icontains=keyword)
        vacancies_backend = Vacancy.objects.filter(backend_query, area_name__isnull=False)

        for vacancy in vacancies:
            city = vacancy.area_name
            salary_values = []
            if vacancy.salary_from and vacancy.salary_from <= Decimal(10_000_000):
                salary_values.append(vacancy.salary_from)
            if vacancy.salary_to and vacancy.salary_to <= Decimal(10_000_000):
                salary_values.append(vacancy.salary_to)
            if salary_values:
                average_salary = sum(salary_values) / len(salary_values)
                average_salary = round(average_salary)
                city_salary_data_all[city].append(average_salary)

        for vacancy in vacancies_backend:
            city = vacancy.area_name
            salary_values = []
            if vacancy.salary_from and vacancy.salary_from <= Decimal(10_000_000):
                salary_values.append(vacancy.salary_from)
            if vacancy.salary_to and vacancy.salary_to <= Decimal(10_000_000):
                salary_values.append(vacancy.salary_to)
            if salary_values:
                average_salary = sum(salary_values) / len(salary_values)
                average_salary = round(average_salary)
                city_salary_data_backend[city].append(average_salary)

        city_salary_stats_all = {
            city: float(sum(salaries) / len(salaries))
            for city, salaries in city_salary_data_all.items()
        }

        city_salary_stats_backend = {
            city: float(sum(salaries) / len(salaries))
            for city, salaries in city_salary_data_backend.items()
        }

        sorted_city_salary_stats_all = sorted(city_salary_stats_all.items(), key=lambda x: x[1], reverse=True)[:20]
        sorted_city_salary_stats_backend = sorted(city_salary_stats_backend.items(), key=lambda x: x[1], reverse=True)[:20]

        self.stdout.write("Уровень зарплат по городам (в порядке убывания) для всех профессий:")
        self.stdout.write(f"{'Город':<30}{'Средняя зарплата (RUB)':<20}")
        for city, avg_salary in sorted_city_salary_stats_all:
            self.stdout.write(f"{city:<30}{avg_salary:<20.0f}")

        self.stdout.write("Уровень зарплат по городам (в порядке убывания) для Backend-программистов:")
        self.stdout.write(f"{'Город':<30}{'Средняя зарплата (RUB)':<20}")
        for city, avg_salary in sorted_city_salary_stats_backend:
            self.stdout.write(f"{city:<30}{avg_salary:<20.0f}")

        cities_all = [item[0] for item in sorted_city_salary_stats_all]
        avg_salaries_all = [item[1] for item in sorted_city_salary_stats_all]

        cities_backend = [item[0] for item in sorted_city_salary_stats_backend]
        avg_salaries_backend = [item[1] for item in sorted_city_salary_stats_backend]

        plt.figure(figsize=(12, max(6, len(cities_all) // 4)))
        plt.barh(cities_all[::-1], avg_salaries_all[::-1], color="green")
        plt.title("Уровень зарплат по городам для всех профессий")
        plt.xlabel("Средняя зарплата (RUB)")
        plt.ylabel("Город")
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        plt.tight_layout()

        filename_all = "city_salary_all_trends.png"
        graph_path_all = os.path.join(output_path, filename_all)
        plt.savefig(graph_path_all)
        plt.close()

        plt.figure(figsize=(12, max(6, len(cities_backend) // 4)))
        plt.barh(cities_backend[::-1], avg_salaries_backend[::-1], color="orange")
        plt.title("Уровень зарплат по городам для Backend-программистов")
        plt.xlabel("Средняя зарплата (RUB)")
        plt.ylabel("Город")
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        plt.tight_layout()

        filename_backend = "city_salary_backend_trends.png"
        graph_path_backend = os.path.join(output_path, filename_backend)
        plt.savefig(graph_path_backend)
        plt.close()

        html_content = """
            <h1>Уровень зарплат по городам для всех профессий</h1>
            <table border="1">
                <tr>
                    <th>Город</th>
                    <th>Средняя зарплата (RUB)</th>
                </tr>
        """
        for city, avg_salary in sorted_city_salary_stats_all:
            html_content += f"""
                <tr>
                    <td>{city}</td>
                    <td>{avg_salary:.0f}</td>
                </tr>
            """
        html_content += f"""
            </table>
            <h2>График</h2>
            <img src="{os.path.join('/static/images/', filename_all)}" alt="Уровень зарплат по городам для всех профессий">
            <br><br>
            <h1>Уровень зарплат по городам для Backend-программистов</h1>
            <table border="1">
                <tr>
                    <th>Город</th>
                    <th>Средняя зарплата (RUB)</th>
                </tr>
        """
        for city, avg_salary in sorted_city_salary_stats_backend:
            html_content += f"""
                <tr>
                    <td>{city}</td>
                    <td>{avg_salary:.0f}</td>
                </tr>
            """
        html_content += f"""
            </table>
            <h2>График</h2>
            <img src="{os.path.join('/static/images/', filename_backend)}" alt="Уровень зарплат по городам для Backend-программистов">
        """

        with open(os.path.join(template_path, "city_salary_statistics_with_backend.html"), "w", encoding="utf-8") as file:
            file.write(html_content)

        self.stdout.write("HTML-контент для статистики по зарплатам и Backend-программистам успешно сохранён.")

