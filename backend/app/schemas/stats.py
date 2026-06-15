from pydantic import BaseModel


class FrequencyPoint(BaseModel):
    date: str
    count: int
    avg_severity: float | None = None


class FrequencyResponse(BaseModel):
    granularity: str
    data: list[FrequencyPoint]


class HeatmapCell(BaseModel):
    day: int       # 0=Monday ... 6=Sunday
    hour: int      # 0-23
    value: int


class HeatmapResponse(BaseModel):
    data: list[HeatmapCell]


class SeveritySlice(BaseModel):
    severity: int
    label: str
    count: int


class SeverityDistributionResponse(BaseModel):
    total: int
    data: list[SeveritySlice]
