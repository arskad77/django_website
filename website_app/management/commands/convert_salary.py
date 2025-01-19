from lxml import etree
from io import BytesIO
from decimal import Decimal
import requests
from django.core.management.base import BaseCommand
from website_app.models import Vacancy
from collections import defaultdict

API_URL = "http://www.cbr.ru/scripts/XML_daily.asp"


class Command(BaseCommand):
    help = "Convert salary ranges in vacancies to RUB using Central Bank API"

    def handle(self, *args, **options):
        currency_rate_cache = {}
        byr_vacancies = Vacancy.objects.filter(salary_currency__iexact="BYR")
        if byr_vacancies.exists():
            self.stdout.write(f"Found {byr_vacancies.count()} vacancies with BYR currency.")
            updated_byr_count = 0
            skipped_byr_count = 0

            for vacancy in byr_vacancies:
                date_for_rate = vacancy.published_at.replace(day=1).strftime("%d/%m/%Y")

                if ("BYR", date_for_rate) not in currency_rate_cache:
                    try:
                        currency_rate_cache[("BYR", date_for_rate)] = self.fetch_currency_rate("BYR", date_for_rate)
                    except Exception as e:
                        self.stderr.write(f"Error fetching BYR rate for {date_for_rate}: {str(e)}")
                        skipped_byr_count += 1
                        continue

                rate = currency_rate_cache[("BYR", date_for_rate)]
                if rate is None:
                    self.stdout.write(f"Currency rate for BYR on {date_for_rate} not found. Skipping vacancy.")
                    vacancy.salary_currency = "BYN"  # Замена BYR на BYN
                    vacancy.save()
                    skipped_byr_count += 1
                    continue

                try:
                    salary_from_rub = round(vacancy.salary_from * rate) if vacancy.salary_from else None
                    salary_to_rub = round(vacancy.salary_to * rate) if vacancy.salary_to else None

                    vacancy.salary_from = salary_from_rub
                    vacancy.salary_to = salary_to_rub
                    vacancy.salary_currency = "RUR"
                    vacancy.save()

                    updated_byr_count += 1
                    self.stdout.write(
                        f"Updated BYR vacancy: {vacancy.name} ({vacancy.published_at}, "
                        f"from: {salary_from_rub}, to: {salary_to_rub})"
                    )
                except Exception as e:
                    self.stderr.write(f"Error updating BYR vacancy {vacancy.name} {vacancy.published_at}: {str(e)}")
                    skipped_byr_count += 1

            self.stdout.write(f"Successfully updated {updated_byr_count} BYR vacancies.")
            self.stdout.write(f"Skipped {skipped_byr_count} BYR vacancies.")

        self.update_other_currencies(currency_rate_cache)

    def update_other_currencies(self, currency_rate_cache):
        vacancies = Vacancy.objects.exclude(salary_currency__iexact='RUR').exclude(salary_currency__iexact='BYR').filter(
            salary_currency__isnull=False,
            published_at__isnull=False
        )

        if not vacancies.exists():
            self.stdout.write("No vacancies with non-RUR salaries found.")
            return

        grouped_vacancies = defaultdict(list)
        for vacancy in vacancies:
            currency = vacancy.salary_currency.upper()
            date_for_rate = vacancy.published_at.replace(day=1).strftime("%d/%m/%Y")
            grouped_vacancies[(currency, date_for_rate)].append(vacancy)

        updated_count = 0
        skipped_count = 0
        for (currency, date_for_rate), vacancy_group in grouped_vacancies.items():
            if (currency, date_for_rate) not in currency_rate_cache:
                try:
                    currency_rate_cache[(currency, date_for_rate)] = self.fetch_currency_rate(currency, date_for_rate)
                except Exception as e:
                    self.stderr.write(f"Error fetching currency rate for {currency} on {date_for_rate}: {str(e)}")
                    skipped_count += len(vacancy_group)
                    continue

            rate = currency_rate_cache[(currency, date_for_rate)]
            if rate is None:
                self.stdout.write(
                    f"Currency rate for {currency} on {date_for_rate} not found. Skipping {len(vacancy_group)} vacancies."
                )
                skipped_count += len(vacancy_group)
                continue

            for vacancy in vacancy_group:
                try:
                    salary_from_rub = round(vacancy.salary_from * rate) if vacancy.salary_from else None
                    salary_to_rub = round(vacancy.salary_to * rate) if vacancy.salary_to else None

                    vacancy.salary_from = salary_from_rub
                    vacancy.salary_to = salary_to_rub
                    vacancy.salary_currency = "RUR"
                    vacancy.save()

                    updated_count += 1
                    self.stdout.write(
                        f"Updated: {vacancy.name} {vacancy.published_at} ({currency} -> RUR, "
                        f"from: {salary_from_rub}, to: {salary_to_rub})"
                    )
                except Exception as e:
                    self.stderr.write(f"Error updating vacancy {vacancy.name} {vacancy.published_at}: {str(e)}")
                    skipped_count += 1

        self.stdout.write(f"Successfully updated {updated_count} vacancies.")
        self.stdout.write(f"Skipped {skipped_count} vacancies.")

    def fetch_currency_rate(self, currency: str, date: str) -> Decimal:
        response = requests.get(API_URL, params={"date_req": date})
        response.encoding = 'windows-1251'
        data = response.content
        root = etree.parse(BytesIO(data))

        for valute in root.xpath("//Valute"):
            char_code = valute.findtext("CharCode")
            if char_code == currency:
                nominal = int(valute.findtext("Nominal"))
                value = float(valute.findtext("Value").replace(",", "."))
                return Decimal(value) / Decimal(nominal)
        return None


