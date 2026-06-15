import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.ai import router as ai_router
from app.api.auth import get_current_user, router as auth_router
from app.api.lifestyle import router as lifestyle_router
from app.api.medications import router as medications_router
from app.api.outbreaks import router as outbreaks_router
from app.api.stats import router as stats_router
from app.api.uas7 import router as uas7_router
from app.api.weather import router as weather_router
from app.core.database import SessionLocal
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WEATHER_FETCH_INTERVAL = 1 * 3600  # 1 hour

_auth_dep = [Depends(get_current_user)]


async def _weather_loop():
    from app.services.weather import fetch_and_store
    while True:
        try:
            fetch_and_store(1)
        except Exception as e:
            logger.error("Weather fetch failed: %s", e)
        await asyncio.sleep(WEATHER_FETCH_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.id == 1).first():
            db.add(User(id=1, username="default", password_hash="placeholder", nickname="默认用户"))
            db.commit()
    finally:
        db.close()

    task = asyncio.create_task(_weather_loop())
    yield
    task.cancel()


app = FastAPI(title="FuckUrticaria API", lifespan=lifespan)

cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:2563").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth (no auth required for login)
app.include_router(auth_router)

# Protected routes
app.include_router(outbreaks_router, dependencies=_auth_dep)
app.include_router(stats_router, dependencies=_auth_dep)
app.include_router(medications_router, dependencies=_auth_dep)
app.include_router(uas7_router, dependencies=_auth_dep)
app.include_router(lifestyle_router, dependencies=_auth_dep)
app.include_router(weather_router, dependencies=_auth_dep)
app.include_router(admin_router, dependencies=_auth_dep)
app.include_router(ai_router, dependencies=_auth_dep)


@app.get("/api/health")
async def health():
    return {"message": "后端运行正常 ✓", "status": "ok"}
