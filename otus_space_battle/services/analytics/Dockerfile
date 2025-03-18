FROM python:3.11-slim

WORKDIR /app

COPY analytics/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY analytics/src/ .
COPY common /app/common

CMD ["python", "app.py"] 