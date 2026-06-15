from datetime import date, datetime

from pydantic import BaseModel


class AIAnalysisResult(BaseModel):
    summary: str
    trend: str  # 好转 / 稳定 / 恶化
    uas7_avg: float
    uas7_level: str  # 控制良好 / 轻度 / 中度 / 重度
    risk_factors: list[str]
    environment_correlation: str
    lifestyle_correlation: str
    medication_effectiveness: str
    suggestions: list[str]
    high_risk_days: list[str]


class TriggerPattern(BaseModel):
    cycle_type: str  # 周期性 / 季节性 / 随机 / 饮食相关 / 压力相关
    cycle_description: str
    avg_interval_days: float | None = None
    confidence: str  # 高 / 中 / 低


class HighRiskWindow(BaseModel):
    start_date: str
    end_date: str
    risk_level: str  # 高 / 中 / 低
    reason: str


class TriggerAnalysisResult(BaseModel):
    summary: str
    patterns: list[TriggerPattern]
    trigger_factors: list[str]  # 排名的触发因素
    high_risk_windows: list[HighRiskWindow]
    medication_correlation: str
    environment_correlation: str
    suggestions: list[str]


class AIInsightOut(BaseModel):
    id: int
    user_id: int
    insight_type: str
    content: AIAnalysisResult | TriggerAnalysisResult | dict
    analysis_range_start: date | None
    analysis_range_end: date | None
    model_version: str | None
    created_at: datetime
    model_config = {"from_attributes": True}
