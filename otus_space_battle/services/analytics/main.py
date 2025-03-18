from fastapi import FastAPI
import uvicorn
import os
from prometheus_client import start_http_server

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Analytics Service"}

if __name__ == "__main__":
    # Start metrics server
    metrics_port = int(os.getenv("METRICS_PORT", "9004"))
    start_http_server(metrics_port)
    
    # Start main API server
    api_port = 8000
    uvicorn.run(app, host="0.0.0.0", port=api_port) 