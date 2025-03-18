FROM python:3.11-slim

WORKDIR /app

COPY ranking/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ranking/main.py .
COPY common /app/common

CMD ["python", "main.py"] 