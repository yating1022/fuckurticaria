from datetime import datetime

from pydantic import BaseModel


class WeatherSnapshotOut(BaseModel):
    id: int
    user_id: int
    snapshot_at: datetime
    temperature: float | None
    humidity: int | None
    pressure: int | None
    pollen_index: int | None
    aqi: int | None
    aqi_category: str | None = None
    aqi_primary: str | None = None
    pm25: float | None = None
    pm10: float | None = None
    no2: float | None = None
    so2: float | None = None
    co: float | None = None
    o3: float | None = None
    weather_desc: str | None
    city: str | None

    model_config = {"from_attributes": True}


class CityUpdate(BaseModel):
    city: str
    location_id: str


class CityOut(BaseModel):
    city: str
    location_id: str
