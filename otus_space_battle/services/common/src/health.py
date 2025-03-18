from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import httpx
from datetime import datetime

router = APIRouter()

class HealthCheck:
    def __init__(self, db: Session = None):
        self.db = db
        self.start_time = datetime.utcnow()
        self.dependencies: Dict[str, Any] = {}

    async def check_database(self) -> Dict[str, Any]:
        if not self.db:
            return {"status": "not_configured"}
        try:
            self.db.execute("SELECT 1")
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_elasticsearch(self) -> Dict[str, Any]:
        if "elasticsearch_url" not in self.dependencies:
            return {"status": "not_configured"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.dependencies['elasticsearch_url']}/_cluster/health")
                return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_dependencies(self) -> Dict[str, Any]:
        results = {}
        if self.db:
            results["database"] = await self.check_database()
        if "elasticsearch_url" in self.dependencies:
            results["elasticsearch"] = await self.check_elasticsearch()
        return results

    @router.get("/health")
    async def health_check(self) -> Dict[str, Any]:
        dependencies_status = await self.check_dependencies()
        return {
            "status": "healthy",
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "dependencies": dependencies_status
        }

    @router.get("/readiness")
    async def readiness_check(self) -> Dict[str, Any]:
        dependencies_status = await self.check_dependencies()
        is_ready = all(
            dep.get("status") == "healthy" 
            for dep in dependencies_status.values()
        )
        return {
            "status": "ready" if is_ready else "not_ready",
            "dependencies": dependencies_status
        }

    @router.get("/liveness")
    async def liveness_check(self) -> Dict[str, Any]:
        return {
            "status": "alive",
            "uptime": (datetime.utcnow() - self.start_time).total_seconds()
        } 