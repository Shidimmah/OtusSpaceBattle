FROM python:3.11-slim

WORKDIR /app

COPY matchmaking_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY matchmaking_service/src/ .
COPY common /app/common

CMD ["python", "app.py"]
