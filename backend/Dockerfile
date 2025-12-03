FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir
COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# проверяем, что все изменения в моделях отражены в миграциях
RUN python manage.py makemigrations --check

ENTRYPOINT ["/entrypoint.sh"]