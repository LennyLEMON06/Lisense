@echo off
cd /d "C:\Users\Ksenia\OneDrive\Рабочий стол\test\web"
call ..\venv\Scripts\activate
python manage.py check_license_expirations
python manage.py test_license_email