FROM python:3.11-slim

WORKDIR /app

COPY auth_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY auth_service/src/ .
COPY common /app/common

CMD ["python", "app.py"]
