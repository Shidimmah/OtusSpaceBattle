from fastapi import FastAPI
from auth import router as auth_router

app = FastAPI(title="Auth Service")

app.include_router(auth_router, prefix="/auth")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
