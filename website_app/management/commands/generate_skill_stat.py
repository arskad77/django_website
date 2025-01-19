import os
from collections import defaultdict, Counter
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

        skills_by_year_all = defaultdict(Counter)
        vacancies_all = Vacancy.objects.filter(published_at__isnull=False, key_skills__isnull=False)

        for vacancy in vacancies_all:
            year = vacancy.published_at.year
            skills = vacancy.key_skills.split("\n") if vacancy.key_skills else []
            skills_by_year_all[year].update(skill.strip() for skill in skills if skill.strip())

        top_skills_all = {}
        for year, skills_counter in skills_by_year_all.items():
            top_skills_all[year] = skills_counter.most_common(20)

        all_skills_counter = Counter()
        for vacancy in vacancies_all:
            skills = vacancy.key_skills.split("\n") if vacancy.key_skills else []
            all_skills_counter.update(skill.strip() for skill in skills if skill.strip())

        top_skills_all_time = all_skills_counter.most_common(20)

        skills_all_time = [skill for skill, _ in top_skills_all_time]
        counts_all_time = [count for _, count in top_skills_all_time]

        plt.figure(figsize=(12, 8))
        plt.barh(skills_all_time[::-1], counts_all_time[::-1], color="lightgreen")
        plt.title("ТОП-20 навыков по всем вакансиям")
        plt.xlabel("Частота")
        plt.ylabel("Навык")
        plt.tight_layout()

        filename_all_time = "top_skills_all_time.png"
        graph_path_all_time = os.path.join(output_path, filename_all_time)
        plt.savefig(graph_path_all_time)
        plt.close()

        html_content_all_time = """
            <h1>ТОП-20 навыков по всем вакансиям</h1>
            <table border="1">
                <tr>
                    <th>Навык</th>
                    <th>Частота</th>
                </tr>
        """
        for skill, count in top_skills_all_time:
            html_content_all_time += f"""
                <tr>
                    <td>{skill}</td>
                    <td>{count}</td>
                </tr>
            """
        html_content_all_time += f"""
            </table>
            <h2>График</h2>
            <img src="/static/images/{filename_all_time}" alt="ТОП-20 навыков по всем вакансиям">
        """

        with open(os.path.join(template_path, "all_time_skills_statistics.html"), "w", encoding="utf-8") as file:
            file.write(html_content_all_time)

        skills_by_year_backend = defaultdict(Counter)
        vacancies_backend = vacancies_all.filter(Q(name__icontains="backend") | Q(name__icontains="бэкенд"))

        for vacancy in vacancies_backend:
            year = vacancy.published_at.year
            skills = vacancy.key_skills.split("\n") if vacancy.key_skills else []
            skills_by_year_backend[year].update(skill.strip() for skill in skills if skill.strip())

        top_skills_backend = {}
        for year, skills_counter in skills_by_year_backend.items():
            top_skills_backend[year] = skills_counter.most_common(20)

        html_content_backend = """
            <h1>ТОП-20 навыков по годам для Backend-программистов</h1>
            <table border="1">
                <tr>
                    <th>Год</th>
                    <th>Навык</th>
                    <th>Частота</th>
                </tr>
        """
        for year, top_skills in top_skills_backend.items():
            for skill, count in top_skills:
                html_content_backend += f"""
                    <tr>
                        <td>{year}</td>
                        <td>{skill}</td>
                        <td>{count}</td>
                    </tr>
                """
            skills = [skill for skill, _ in top_skills]
            counts = [count for _, count in top_skills]

            plt.figure(figsize=(12, 8))
            plt.barh(skills[::-1], counts[::-1], color="orange")
            plt.title(f"ТОП-20 навыков для Backend-программистов в {year}")
            plt.xlabel("Частота")
            plt.ylabel("Навык")
            plt.tight_layout()

            filename_backend = f"top_skills_backend_{year}.png"
            graph_path_backend = os.path.join(output_path, filename_backend)
            plt.savefig(graph_path_backend)
            plt.close()

            html_content_backend += f'<h3>{year}</h3>'
            html_content_backend += f'<img src="/static/images/{filename_backend}" alt="ТОП-20 навыков для Backend-программистов в {year}"><br>'

        html_content_backend += """
            </table>
        """

        with open(os.path.join(template_path, "backend_skills_statistics.html"), "w", encoding="utf-8") as file:
            file.write(html_content_backend)

        self.stdout.write("HTML-контент для статистики по навыкам сохранён.")
