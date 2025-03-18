FROM python:3.11-slim

WORKDIR /app

COPY fleet_management_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fleet_management_service/src/ .
COPY common /app/common

CMD ["python", "app.py"] 