import logging
from datetime import datetime

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.weather import WeatherSnapshot

logger = logging.getLogger(__name__)


def _api_base() -> str:
    return f"https://{settings.QWEATHER_API_DOMAIN}"


def fetch_and_store(user_id: int = 1) -> WeatherSnapshot | None:
    key = settings.QWEATHER_API_KEY
    loc = settings.QWEATHER_LOCATION_ID
    if not key or not loc:
        logger.warning("QWeather API key or location not configured")
        return None

    # Current weather
    weather = _get("/v7/weather/now", key, loc)
    # Air quality (paid API returns pm25/pm10/no2/so2/co/o3)
    air = _get("/v7/air/now", key, loc)
    # Life indices (pollen)
    indices = _get("/v7/indices/1d", key, loc, type="5,13")

    if not weather or weather.get("code") != "200":
        logger.error("QWeather weather error: %s", weather)
        return None

    now = weather.get("now", {})
    air_now = air.get("now", {}) if air and air.get("code") == "200" else {}
    pollen = _extract_index(indices, "13") if indices and indices.get("code") == "200" else None

    db = SessionLocal()
    try:
        snapshot = WeatherSnapshot(
            user_id=user_id,
            snapshot_at=datetime.now(),
            temperature=float(now.get("temp", 0)) if now.get("temp") else None,
            humidity=int(now.get("humidity", 0)) if now.get("humidity") else None,
            pressure=int(now.get("pressure", 0)) if now.get("pressure") else None,
            pollen_index=int(pollen.get("level", 0)) if pollen and pollen.get("level") else None,
            aqi=int(air_now.get("aqi", 0)) if air_now.get("aqi") else None,
            aqi_category=air_now.get("category"),
            aqi_primary=air_now.get("primary"),
            pm25=float(air_now["pm2p5"]) if air_now.get("pm2p5") else None,
            pm10=float(air_now["pm10"]) if air_now.get("pm10") else None,
            no2=float(air_now["no2"]) if air_now.get("no2") else None,
            so2=float(air_now["so2"]) if air_now.get("so2") else None,
            co=float(air_now["co"]) if air_now.get("co") else None,
            o3=float(air_now["o3"]) if air_now.get("o3") else None,
            weather_desc=now.get("text"),
            city=settings.QWEATHER_CITY,
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        logger.info("Weather snapshot saved: %s %s°C %s AQI=%s(%s) PM2.5=%s",
                     snapshot.city, snapshot.temperature, snapshot.weather_desc,
                     snapshot.aqi, snapshot.aqi_category, snapshot.pm25)
        return snapshot
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get(path: str, key: str, location: str, **extra) -> dict | None:
    params = {"location": location, "key": key, **extra}
    try:
        r = requests.get(f"{_api_base()}{path}", params=params, timeout=10)
        return r.json()
    except Exception as e:
        logger.error("QWeather request failed: %s", e)
        return None


def _extract_index(data: dict, index_type: str) -> dict | None:
    for item in data.get("daily", []):
        if item.get("type") == index_type:
            return item
    return None
