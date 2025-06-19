# web/Dockerfile

FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libmariadb-dev \
        pkg-config \
        && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Устанавливаем PYTHONPATH, чтобы найти `web/`
ENV PYTHONPATH=/app

CMD ["gunicorn", "web.wsgi:application", "--bind", "0.0.0.0:8000"]