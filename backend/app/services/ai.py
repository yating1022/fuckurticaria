from datetime import date, timedelta

import httpx
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.outbreak import Outbreak
from app.models.uas7 import UAS7Score
from app.models.lifestyle import LifestyleLog
from app.models.weather import WeatherSnapshot
from app.models.medication import MedicationRecord
from app.models.setting import SystemSetting


def _get_setting(db: Session, key: str) -> str | None:
    s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    return s.value if s else None


def _env_stats(rows: list) -> str:
    """Generate environment statistics summary from WeatherSnapshot rows."""
    if not rows:
        return "（无环境数据）"

    temps = [r.temperature for r in rows if r.temperature is not None]
    humids = [r.humidity for r in rows if r.humidity is not None]
    aqis = [r.aqi for r in rows if r.aqi is not None]
    pollens = [r.pollen_index for r in rows if r.pollen_index is not None]

    parts = [f"数据点数: {len(rows)}"]
    if temps:
        parts.append(f"温度: avg={sum(temps)/len(temps):.1f}°C min={min(temps):.1f}°C max={max(temps):.1f}°C")
    if humids:
        parts.append(f"湿度: avg={sum(humids)/len(humids):.0f}% min={min(humids)}% max={max(humids)}%")
    if aqis:
        parts.append(f"AQI: avg={sum(aqis)/len(aqis):.0f} max={max(aqis)} 天数超标(>100)={sum(1 for a in aqis if a > 100)}")
    if pollens:
        high_days = sum(1 for p in pollens if p is not None and p >= 3)
        parts.append(f"花粉: max={max(pollens)} 高花粉天数(>=3)={high_days}")
    return "\n  ".join(parts)


def _build_prompt(db: Session, user_id: int, days: int = 30) -> str:
    today = date.today()
    start = today - timedelta(days=days)

    # UAS7 daily scores
    uas7_rows = (
        db.query(UAS7Score)
        .filter(UAS7Score.user_id == user_id, UAS7Score.score_date >= start)
        .order_by(UAS7Score.score_date)
        .all()
    )
    uas7_text = "\n".join(
        f"  {r.score_date}: wheal={r.wheal_score} itch={r.itch_score} daily={r.wheal_score + r.itch_score}"
        for r in uas7_rows
    ) or "  （无记录，默认全部为 0 分）"

    # Outbreaks
    ob_rows = (
        db.query(Outbreak)
        .filter(Outbreak.user_id == user_id, Outbreak.started_at >= start)
        .order_by(Outbreak.started_at)
        .all()
    )
    ob_text = "\n".join(
        f"  {r.started_at}: severity={r.severity} body_parts={[d.body_part for d in r.details]} trigger={r.trigger_guess}"
        for r in ob_rows
    ) or "  （无记录）"

    # Lifestyle
    life_rows = (
        db.query(LifestyleLog)
        .filter(LifestyleLog.user_id == user_id, LifestyleLog.log_date >= start)
        .order_by(LifestyleLog.log_date)
        .all()
    )
    life_text = "\n".join(
        f"  {r.log_date}: sleep={r.sleep_hours}h stress={r.stress_level}/5 exercise={'Y' if r.exercise else 'N'} diet_tags={r.diet_tags}"
        for r in life_rows
    ) or "  （无记录）"

    # Medication records
    med_rows = (
        db.query(MedicationRecord)
        .filter(MedicationRecord.user_id == user_id, MedicationRecord.taken_at >= start)
        .order_by(MedicationRecord.taken_at)
        .all()
    )
    med_text = "\n".join(
        f"  {r.taken_at}: med_id={r.medication_id} dose={r.dose} notes={r.notes} effectiveness={r.effectiveness}/5 side_effects={r.side_effects} feedback={r.feedback_note}"
        for r in med_rows
    ) or "  （无记录）"

    # Weather (full analysis period)
    wx_rows = (
        db.query(WeatherSnapshot)
        .filter(WeatherSnapshot.user_id == user_id, WeatherSnapshot.snapshot_at >= start)
        .order_by(WeatherSnapshot.snapshot_at)
        .all()
    )
    wx_text = "\n".join(
        f"  {r.snapshot_at}: temp={r.temperature}°C humidity={r.humidity}% aqi={r.aqi} pollen={r.pollen_index}"
        for r in wx_rows
    ) or "  （无数据）"

    wx_stats = _env_stats(wx_rows)

    return f"""你是一名专业的皮肤科/过敏科医学顾问。请根据以下荨麻疹患者的近 {days} 天数据，给出分析报告。

## UAS7 每日评分（未记录日默认为 0 分）
{uas7_text}

## 发病记录
{ob_text}

## 生活习惯
{life_text}

## 用药记录
{med_text}

## 近 {days} 天环境数据
{wx_text}

### 环境统计摘要
  {wx_stats}

请用 JSON 格式输出，结构如下（不要输出任何额外文字，只输出合法 JSON）：
{{
  "summary": "整体病情概述（2-3 句话）",
  "trend": "好转 | 稳定 | 恶化",
  "uas7_avg": 0.0,
  "uas7_level": "控制良好 | 轻度 | 中度 | 重度",
  "risk_factors": ["可能的风险因素1", "风险因素2"],
  "environment_correlation": "环境因素与症状的关联分析",
  "lifestyle_correlation": "生活习惯与症状的关联分析",
  "medication_effectiveness": "用药效果分析",
  "suggestions": ["建议1", "建议2", "建议3"],
  "high_risk_days": ["2025-01-15", "2025-01-20"]
}}"""


def _build_trigger_prompt(db: Session, user_id: int, days: int = 60) -> str:
    today = date.today()
    start = today - timedelta(days=days)

    # Outbreaks — 时间精确到小时，是找周期的关键
    ob_rows = (
        db.query(Outbreak)
        .filter(Outbreak.user_id == user_id, Outbreak.started_at >= start)
        .order_by(Outbreak.started_at)
        .all()
    )
    ob_text = "\n".join(
        f"  {r.started_at.isoformat()}: severity={r.severity} duration_hours={((r.ended_at or r.started_at) - r.started_at).total_seconds() / 3600:.1f} body_parts={[d.body_part for d in r.details]} trigger_guess={r.trigger_guess}"
        for r in ob_rows
    ) or "  （无记录）"

    # UAS7 — 提供症状强度的时间线
    uas7_rows = (
        db.query(UAS7Score)
        .filter(UAS7Score.user_id == user_id, UAS7Score.score_date >= start)
        .order_by(UAS7Score.score_date)
        .all()
    )
    uas7_text = "\n".join(
        f"  {r.score_date}: daily={r.wheal_score + r.itch_score}"
        for r in uas7_rows
    ) or "  （无记录）"

    # Medication records — 用药模式与发病的关系
    med_rows = (
        db.query(MedicationRecord)
        .filter(MedicationRecord.user_id == user_id, MedicationRecord.taken_at >= start)
        .order_by(MedicationRecord.taken_at)
        .all()
    )
    med_text = "\n".join(
        f"  {r.taken_at.isoformat()}: med_id={r.medication_id} dose={r.dose} is_prn={r.is_prn} effectiveness={r.effectiveness}/5 side_effects={r.side_effects} feedback={r.feedback_note}"
        for r in med_rows
    ) or "  （无记录）"

    # Lifestyle — 压力/睡眠与发病的时间相关性
    life_rows = (
        db.query(LifestyleLog)
        .filter(LifestyleLog.user_id == user_id, LifestyleLog.log_date >= start)
        .order_by(LifestyleLog.log_date)
        .all()
    )
    life_text = "\n".join(
        f"  {r.log_date}: sleep={r.sleep_hours}h quality={r.sleep_quality}/5 stress={r.stress_level}/5 exercise={'Y' if r.exercise else 'N'} diet_tags={r.diet_tags}"
        for r in life_rows
    ) or "  （无记录）"

    # Weather — 环境变化周期
    wx_rows = (
        db.query(WeatherSnapshot)
        .filter(WeatherSnapshot.user_id == user_id, WeatherSnapshot.snapshot_at >= start)
        .order_by(WeatherSnapshot.snapshot_at)
        .all()
    )
    wx_text = "\n".join(
        f"  {r.snapshot_at.isoformat()}: temp={r.temperature}°C humidity={r.humidity}% aqi={r.aqi} pollen={r.pollen_index} weather={r.weather_desc}"
        for r in wx_rows
    ) or "  （无数据）"

    wx_stats = _env_stats(wx_rows)

    return f"""你是一名擅长数据分析的皮肤科/过敏科医学顾问。请根据以下荨麻疹患者近 {days} 天的数据，进行**触发周期与高危窗口分析**。

重点任务：
1. 从发病时间序列中寻找**周期性规律**（如每周几、每月几号、间隔多少天复发）
2. 结合用药记录，判断是否存在**药物减量后反弹**的模式
3. 从生活习惯中发现**压力/睡眠/饮食**与发病的时间因果关系
4. 从天气数据中发现**环境触发因素**（温度骤变、花粉高峰等）
5. 基于以上分析，**预测未来 2 周的高危窗口期**

## 发病时间序列（ISO 时间，精确到小时）
{ob_text}

## UAS7 每日评分
{uas7_text}

## 用药记录
{med_text}

## 生活习惯记录
{life_text}

## 环境天气数据
{wx_text}

### 环境统计摘要
  {wx_stats}

请用 JSON 格式输出（不要输出任何额外文字，只输出合法 JSON）：
{{
  "summary": "触发周期分析总结（2-3句话）",
  "patterns": [
    {{
      "cycle_type": "周期性 | 季节性 | 随机 | 饮食相关 | 压力相关 | 用药相关",
      "cycle_description": "描述发现的周期模式",
      "avg_interval_days": 7.0,
      "confidence": "高 | 中 | 低"
    }}
  ],
  "trigger_factors": ["最重要的触发因素1", "触发因素2", "触发因素3"],
  "high_risk_windows": [
    {{
      "start_date": "2025-02-01",
      "end_date": "2025-02-03",
      "risk_level": "高 | 中 | 低",
      "reason": "预测依据"
    }}
  ],
  "medication_correlation": "用药与发病的时间关联分析",
  "environment_correlation": "环境因素与发病的关联分析",
  "suggestions": ["基于周期分析的具体建议1", "建议2", "建议3"]
}}"""


def call_deepseek(db: Session, user_id: int, days: int = 30) -> dict:
    api_key = _get_setting(db, "deepseek_api_key")
    base_url = _get_setting(db, "deepseek_base_url") or "https://api.deepseek.com"
    model = _get_setting(db, "deepseek_model") or "deepseek-chat"

    if not api_key:
        raise ValueError("DeepSeek API Key 未配置，请在管理后台设置")

    prompt = _build_prompt(db, user_id, days)

    resp = httpx.post(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "你是荨麻疹治疗管理 AI 顾问，输出必须为合法 JSON。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        },
        timeout=60,
    )
    resp.raise_for_status()
    body = resp.json()
    import json
    content = body["choices"][0]["message"]["content"]
    return json.loads(content)


def call_deepseek_trigger(db: Session, user_id: int, days: int = 60) -> dict:
    api_key = _get_setting(db, "deepseek_api_key")
    base_url = _get_setting(db, "deepseek_base_url") or "https://api.deepseek.com"
    model = _get_setting(db, "deepseek_model") or "deepseek-chat"

    if not api_key:
        raise ValueError("DeepSeek API Key 未配置，请在管理后台设置")

    prompt = _build_trigger_prompt(db, user_id, days)

    resp = httpx.post(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "你是荨麻疹触发周期分析专家，擅长从时间序列数据中发现隐藏模式，输出必须为合法 JSON。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        },
        timeout=90,
    )
    resp.raise_for_status()
    body = resp.json()
    import json
    content = body["choices"][0]["message"]["content"]
    return json.loads(content)
