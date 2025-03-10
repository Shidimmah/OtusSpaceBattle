from fastapi import FastAPI, HTTPException
import logging
import datetime

app = FastAPI(title="Logging Service")

# Настраиваем логирование
log_filename = "/app/logs/service.log"
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename=log_filename, filemode="a")

@app.post("/log")
async def log_event(service: str, level: str, message: str):
    """Принимает логи от сервисов"""
    timestamp = datetime.datetime.utcnow().isoformat()
    log_entry = f"{timestamp} [{service}] {level.upper()}: {message}"

    if level.lower() == "info":
        logging.info(log_entry)
    elif level.lower() == "warning":
        logging.warning(log_entry)
    elif level.lower() == "error":
        logging.error(log_entry)
    else:
        logging.debug(log_entry)

    return {"status": "logged", "message": log_entry}

@app.get("/logs")
async def get_logs():
    """Возвращает последние 100 строк логов"""
    try:
        with open(log_filename, "r") as file:
            logs = file.readlines()[-100:]
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения логов: {str(e)}")
