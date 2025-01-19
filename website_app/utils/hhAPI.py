import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

BASE_URL = "https://api.hh.ru/vacancies"
HEADERS = {
    "User-Agent": "BackProgrammerWebsite/1.0 (arskad77@gmail.com)"
}


def get_backend_vacancies(days=1):
    date_from = (datetime.utcnow() - timedelta(days=days)).isoformat()
    params = {
        "text": "backend OR бэкенд OR django OR flask OR laravel OR yii OR symfony OR бэкенд OR бекенд OR бекэнд"
                "OR back end OR бэк энд OR бэк енд",
        "search_field": "name",
        "date_from": date_from,
        "per_page": 10,
        "order_by": "publication_time"
    }

    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()

    vacancies = []
    for item in data.get('items', []):
        vacancy = {
            "name": item["name"],
            "company": item["employer"]["name"],
            "region": item["area"]["name"],
            "salary": format_salary(item["salary"]),
            "published_at": item["published_at"],
            "url": item["alternate_url"]
        }

        vacancy_details = get_vacancy_details(item["id"])
        raw_description = vacancy_details.get("description", "Не указано")
        soup = BeautifulSoup(raw_description, "html.parser")
        vacancy["description"] = soup.get_text(strip=True)
        vacancy["skills"] = ", ".join(skill["name"] for skill in vacancy_details.get("key_skills", []))
        vacancies.append(vacancy)
    return vacancies


def get_vacancy_details(vacancy_id):
    """
    Получает детали вакансии.
    """
    url = f"{BASE_URL}/{vacancy_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def format_salary(salary):
    """
    Форматирует зарплату.
    """
    if not salary:
        return "Не указано"
    salary_from = salary.get("from")
    salary_to = salary.get("to")
    currency = salary.get("currency")
    if salary_from and salary_to:
        return f"{salary_from} - {salary_to} {currency}"
    if salary_from:
        return f"от {salary_from} {currency}"
    if salary_to:
        return f"до {salary_to} {currency}"
    return "Не указано"
