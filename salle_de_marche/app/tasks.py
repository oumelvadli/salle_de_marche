from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.db import transaction
import ftplib
import tempfile
import os
import pandas as pd
from .models import *
from datetime import datetime, timedelta

def last_business_day():
    today = datetime.today()
    offset = max(1, (today.weekday() + 6) % 7 - 3)
    last_working_day = today - timedelta(days=offset)
    return last_working_day

@shared_task
def download_and_inject():
    ftp_server = '10.158.120.210'
    username = 'Moustapha'
    password = 'Admin@CDI123'
    print("Starting download_and_inject task")

    last_day = last_business_day()
    remote_filename = f'operations/OSDM_{last_day.strftime("%d_%m_%Y")}.xlsx'

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_filename = temp_file.name
        try:
            with ftplib.FTP(ftp_server) as ftp:
                ftp.login(username, password)
                print("Connected to FTP server.")
                ftp.retrbinary(f'RETR {remote_filename}', temp_file.write)
                print("File downloaded")
        except ftplib.all_errors as e:
            print(f"FTP error: {e}")
            return
        finally:
            temp_file.close()

        def convert_date(date_str):
            try:
                return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                return None

        try:
            with pd.ExcelFile(temp_filename, engine='openpyxl') as xls:
                data = pd.read_excel(xls)
            print("File read into DataFrame")

            with transaction.atomic():
                for index, row in data.iterrows():
                    datoper = convert_date(row['DATOPER'])
                    if not OperationCorp.objects.filter(nooper=row['NOOPER'], datoper=datoper).exists():
                        OperationCorp.objects.create(
                            modev=row['MODEV'],
                            nooper=row['NOOPER'],
                            datoper=datoper,
                            devisec=row['DEVISEC'],
                            devised=row['DEVISED'],
                            mntdevd=row['MNTDEVD'],
                            mntdevc=row['MNTDEVC'],
                            cours12=row['COURS12'],
                            nomd=row['NOMD'],
                            libelle=row['LIBELLE'],
                            client=row['CLIENT'],
                            comptec=row['COMPTEC'],
                            agence=row['AGENCE'],
                        )
                print("Data inserted into database")
        except Exception as e:
            print(f"Error processing file: {e}")
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                print("Temporary file deleted and task completed")
