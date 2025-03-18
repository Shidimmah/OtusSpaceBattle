FROM python:3.11-slim

WORKDIR /app

COPY battle_mechanics/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY battle_mechanics/src/ .
COPY common /app/common

CMD ["python", "app.py"] 