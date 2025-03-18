FROM python:3.11-slim

WORKDIR /app

COPY resource_management/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY resource_management/src/ .
COPY resource_management/main.py .
COPY resource_management/alembic.ini .
COPY common /app/common

CMD ["python", "main.py"] 