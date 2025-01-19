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

        def calculate_average_salary(vacancies):
            salary_data = defaultdict(list)
            for vacancy in vacancies:
                year = vacancy.published_at.year
                salary_values = []

                if vacancy.salary_from and vacancy.salary_from <= Decimal(10_000_000):
                    salary_values.append(vacancy.salary_from)
                if vacancy.salary_to and vacancy.salary_to <= Decimal(10_000_000):
                    salary_values.append(vacancy.salary_to)

                if salary_values:
                    average_salary = sum(salary_values) / len(salary_values)
                    average_salary = round(average_salary)
                    salary_data[year].append(average_salary)

            return {
                year: float(sum(salaries) / len(salaries))
                for year, salaries in salary_data.items()
            }

        def calculate_vacancy_count(vacancies):
            vacancy_count = defaultdict(int)
            for vacancy in vacancies:
                year = vacancy.published_at.year
                vacancy_count[year] += 1
            return dict(vacancy_count)

        def generate_html_content(title, salary_stats, vacancy_count, graph_path_salary, graph_path_count):
            html_content = f"""
                <h1>{title}</h1>
                <h2>Динамика уровня зарплат по годам</h2>
                <table border="1">
                    <tr>
                        <th>Год</th>
                        <th>Средняя зарплата (RUB)</th>
                    </tr>
            """
            for year, avg_salary in sorted(salary_stats.items()):
                html_content += f"""
                    <tr>
                        <td>{year}</td>
                        <td>{avg_salary:.0f}</td>
                    </tr>
                """
            html_content += "</table>"

            html_content += """
                <h2>Динамика количества вакансий по годам</h2>
                <table border="1">
                    <tr>
                        <th>Год</th>
                        <th>Количество вакансий</th>
                    </tr>
            """
            for year, count in sorted(vacancy_count.items()):
                html_content += f"""
                    <tr>
                        <td>{year}</td>
                        <td>{count}</td>
                    </tr>
                """
            html_content += "</table>"

            html_content += f"""
                <h2>Графики</h2>
                <h3>Средняя зарплата</h3>
                <img src="{os.path.join('/static/images/', graph_path_salary)}" alt="Динамика зарплат">
                <h3>Количество вакансий</h3>
                <img src="{os.path.join('/static/images/', graph_path_count)}" alt="Динамика количества вакансий">
            """
            return html_content

        def generate_graph(x, y, filename, title, xlabel, ylabel, color='blue'):
            plt.figure(figsize=(10, 6))
            plt.plot(x, y, marker="o", color=color)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.grid(True)
            plt.tight_layout()

            graph_path = os.path.join(output_path, filename)
            plt.savefig(graph_path)
            plt.close()
            return filename

        vacancies_all = Vacancy.objects.filter(published_at__isnull=False)

        backend_query = Q()
        for keyword in backend_keywords:
            backend_query |= Q(name__icontains=keyword)

        vacancies_backend = Vacancy.objects.filter(published_at__isnull=False).filter(backend_query)

        all_year_salary_stats = calculate_average_salary(vacancies_all)
        backend_year_salary_stats = calculate_average_salary(vacancies_backend)

        all_year_vacancy_count = calculate_vacancy_count(vacancies_all)
        backend_year_vacancy_count = calculate_vacancy_count(vacancies_backend)

        years_all = sorted(all_year_salary_stats.keys())
        avg_salaries_all = [all_year_salary_stats[year] for year in years_all]
        graph_path_salary_all = generate_graph(
            years_all, avg_salaries_all, "salary_trends_all.png",
            "Динамика уровня зарплат (все вакансии)", "Год", "Средняя зарплата (RUB)"
        )

        vacancy_counts_all = [all_year_vacancy_count[year] for year in years_all]
        graph_path_count_all = generate_graph(
            years_all, vacancy_counts_all, "vacancy_counts_all.png",
            "Динамика количества вакансий (все вакансии)", "Год", "Количество вакансий"
        )

        years_backend = sorted(backend_year_salary_stats.keys())
        avg_salaries_backend = [backend_year_salary_stats[year] for year in years_backend]
        graph_path_salary_backend = generate_graph(
            years_backend, avg_salaries_backend, "salary_trends_backend.png",
            "Динамика уровня зарплат (Backend-программисты)", "Год", "Средняя зарплата (RUB)", color='orange'
        )

        vacancy_counts_backend = [backend_year_vacancy_count[year] for year in years_backend]
        graph_path_count_backend = generate_graph(
            years_backend, vacancy_counts_backend, "vacancy_counts_backend.png",
            "Динамика количества вакансий (Backend-программисты)", "Год", "Количество вакансий", color='orange'
        )

        general_html = generate_html_content(
            "Общая статистика", all_year_salary_stats, all_year_vacancy_count,
            graph_path_salary_all, graph_path_count_all
        )
        backend_html = generate_html_content(
            "Статистика для Backend-программистов", backend_year_salary_stats, backend_year_vacancy_count,
            graph_path_salary_backend, graph_path_count_backend
        )

        with open(os.path.join(template_path, "general_statistics.html"), "w", encoding="utf-8") as file:
            file.write(general_html)

        with open(os.path.join(template_path, "backend_statistics.html"), "w", encoding="utf-8") as file:
            file.write(backend_html)

        self.stdout.write("HTML-контент успешно сохранён.")