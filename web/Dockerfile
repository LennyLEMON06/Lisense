# web/Dockerfile

FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        default-libmysqlclient-dev \
        pkg-config \
        && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Собираем статику (если используешь)
RUN python manage.py collectstatic --noinput

# Устанавливаем PYTHONPATH, чтобы найти `web/`
ENV PYTHONPATH=/app

CMD ["gunicorn", "web.wsgi:application", "--bind", "0.0.0.0:8000"]