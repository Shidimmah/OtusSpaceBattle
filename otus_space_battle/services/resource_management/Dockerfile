FROM python:3.11-slim

WORKDIR /app

COPY resource_management/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY resource_management/src/ .
COPY common /app/common

CMD ["python", "app.py"] 