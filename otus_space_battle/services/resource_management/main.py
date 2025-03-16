from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Resource Management Service"}

if __name__ == "__main__":
    port = int(os.getenv("METRICS_PORT", "9002"))
    uvicorn.run(app, host="0.0.0.0", port=port) 