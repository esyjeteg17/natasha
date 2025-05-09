FROM python:3.12-slim

# Отключить буферизацию вывода Python
ENV PYTHONUNBUFFERED=1

# Установить зависимости apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Создать рабочую директорию и перейти в неё
WORKDIR /app

# Скопировать файл зависимостей и установить их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt uvicorn gunicorn django-environ && \
    rm -rf /root/.cache/pip

# Скопировать код приложения
COPY . /app

# Запустить приложение через Gunicorn
CMD ["gunicorn", "--workers=4", "--threads=2", "--timeout=90", "--bind=0.0.0.0:8000", "studentportal.asgi:application", "-k", "uvicorn.workers.UvicornWorker"]
