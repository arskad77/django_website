import pandas as pd
import os
import logging
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from website_app.models import Vacancy

class Command(BaseCommand):
    help = 'Load vacancies from a CSV file'

    def handle(self, *args, **kwargs):
        logging.basicConfig(filename='errors.log', level=logging.ERROR)
        csv_file_path = 'vacancies_2024.csv'
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_file_path}'))
            return

        self.stdout.write(self.style.WARNING('Deleting all existing vacancies...'))
        Vacancy.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All vacancies deleted.'))

        vac_to_save = []
        bath_size = 10000
        count = 0

        try:
            df = pd.read_csv(csv_file_path, low_memory=False)
            self.stdout.write(self.style.SUCCESS('CSV file loaded successfully!'))
            added_count = 0
            for _, row in df.iterrows():
                try:
                    vacancy = Vacancy(
                        name=row['name'],
                        key_skills=row['key_skills'] if pd.notna(row['key_skills']) else None,
                        salary_from=self.parse_decimal(row['salary_from']),
                        salary_to=self.parse_decimal(row['salary_to']),
                        salary_currency=row['salary_currency'] if pd.notna(row['salary_currency']) else None,
                        area_name=row['area_name'] if pd.notna(row['area_name']) else None,
                        published_at=row['published_at'],
                    )
                    vac_to_save.append(vacancy)
                    added_count += 1
                except Exception as e:
                    error_message = f"Error saving row: {row.to_dict()} - {e}"
                    self.stdout.write(self.style.ERROR(error_message))
                    logging.error(error_message)
                if len(vac_to_save) >= bath_size:
                    Vacancy.objects.bulk_create(vac_to_save)
                    vac_to_save = []
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'{bath_size*count} vacancies added successfully.'))
            if vac_to_save:
                Vacancy.objects.bulk_create(vac_to_save)
                self.stdout.write(self.style.SUCCESS(f'{bath_size * count + len(vac_to_save)} vacancies added successfully.'))

            self.stdout.write(self.style.SUCCESS(f'{added_count} vacancies added successfully.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing CSV file: {e}'))

    @staticmethod
    def parse_decimal(value):
        if pd.isna(value) or value == '':
            return None
        try:
            normalized_value = str(value).strip().replace(' ', '').replace(',', '.')
            decimal_value = Decimal(normalized_value)

            if decimal_value.adjusted() > 7:
                logging.error(f"Value exceeds max_digits: {value}")
                return None

            return decimal_value
        except (InvalidOperation, ValueError) as e:
            logging.error(f"Invalid decimal value: '{value}' - {e}")
            return None

