FROM python:3.11-slim

WORKDIR /app

COPY game_session_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY game_session_service/src/ .
COPY common /app/common

CMD ["python", "app.py"] 