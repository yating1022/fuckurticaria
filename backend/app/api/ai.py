from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ai_insight import AIInsight
from app.schemas.ai import AIAnalysisResult, AIInsightOut
from app.services.ai import call_deepseek, call_deepseek_trigger

router = APIRouter(prefix="/api/ai", tags=["ai"])

DEFAULT_USER_ID = 1


@router.post("/analyze", response_model=AIInsightOut)
def run_analysis(days: int = Query(30, ge=7, le=90), db: Session = Depends(get_db)):
    today = date.today()
    start = today - timedelta(days=days)

    try:
        result = call_deepseek(db, DEFAULT_USER_ID, days)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(502, f"AI 分析请求失败：{e}")

    insight = AIInsight(
        user_id=DEFAULT_USER_ID,
        insight_type="period_report",
        content=result,
        analysis_range_start=start,
        analysis_range_end=today,
        model_version="deepseek-chat",
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


@router.post("/trigger-analysis", response_model=AIInsightOut)
def run_trigger_analysis(days: int = Query(60, ge=30, le=180), db: Session = Depends(get_db)):
    today = date.today()
    start = today - timedelta(days=days)

    try:
        result = call_deepseek_trigger(db, DEFAULT_USER_ID, days)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(502, f"AI 分析请求失败：{e}")

    insight = AIInsight(
        user_id=DEFAULT_USER_ID,
        insight_type="trigger_analysis",
        content=result,
        analysis_range_start=start,
        analysis_range_end=today,
        model_version="deepseek-chat",
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


@router.get("/insights", response_model=list[AIInsightOut])
def list_insights(
    insight_type: str | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    q = db.query(AIInsight).filter(AIInsight.user_id == DEFAULT_USER_ID)
    if insight_type:
        q = q.filter(AIInsight.insight_type == insight_type)
    return q.order_by(AIInsight.created_at.desc()).limit(limit).all()


@router.get("/insights/{insight_id}", response_model=AIInsightOut)
def get_insight(insight_id: int, db: Session = Depends(get_db)):
    s = db.query(AIInsight).filter(AIInsight.id == insight_id, AIInsight.user_id == DEFAULT_USER_ID).first()
    if not s:
        raise HTTPException(404, "分析记录不存在")
    return s
