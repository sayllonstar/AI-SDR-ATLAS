from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.core.database import get_db
from app.models.db_models import Lead
from app.schemas.lead_schemas import (
    LeadResponse,
    LeadUpdateStatus,
    LeadMetricsResponse,
)

router = APIRouter(prefix="/leads", tags=["Leads Admin"])


@router.get("/", response_model=List[LeadResponse])
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):

    """
    Lista os leads cadastrados com suporte a paginação e filtros por status do funil.
    """
    query = select(Lead).order_by(Lead.Created_at.desc())

    if status_filter:
        query = query.where(Lead.status == status_filter)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    leads = result.scalars().all()
    return leads


@router.get("/metrics", response_model=LeadMetricsResponse)
async def get_lead_metrics(db: AsyncSession = Depends(get_db)):
    """
    Retorna métricas consolidadas do funil de qualificação do SDR.
    """
    total_query = select(func.count(Lead.id))
    total_res = await db.execute(total_query)
    total_leads = total_res.scalar_one_or_none() or 0

    status_query = select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
    status_res = await db.execute(status_query)
    status_counts = dict(status_res.all())

    return {
        "total_leads": total_leads,
        "uncontacted": status_counts.get("uncontacted", 0),
        "qualifying": status_counts.get("qualifying", 0),
        "qualified": status_counts.get("qualified", 0),
        "disqualified": status_counts.get("desqualified", 0),
        "meeting_booked": status_counts.get("meeting_booked", 0),
    }
    

    @router.get("/{lead_id}", response_model=LeadResponse)
    async def get_lead_by_id(
        lead_id: UUID,
        db: AsyncSession = Depends(get_db),
    ):
        """
        Retorna os detalhes de um lead específico pelo seu UUID.
        """
        query = select(Lead).where(Lead.id == lead_id)
        result = await db.execute(query)
        lead = result.scalar_one_or_none()

        if not lead:
            raise HTTPException(
                status_code=status.HTTP_400_NOT_FOUND,
                detail="Lead não encontrado.",
            )
        return lead

    
@router.patch("/{lead_id}/status", response_model=LeadResponse)
async def update_lead_status(
    lead_id: UUID,
    payload: LeadUpdateStatus,
    db: AsyncSession = Depends(get_db),
):

    """
    Atualiza manualmente o status ou pontuação de qualificação de um lead.
    """
    query = select(Lead).where(Lead.id == lead_id)
    result = await db.execute(query)
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead não encontrado.",
        )

    if payload.status:
        lead.status = payload.status
    if payload.qualification_score is not None:
        lead.qualification_score = payload.qualification_score

    await db.commit()
    await db.refresh(lead)
    return lead

