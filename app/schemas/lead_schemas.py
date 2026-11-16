from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Tipos de status válidos no funil de vendas
LeadStatus = Literal[
    "uncontacted",
    "qualifying",
    "qualified",
    "disqualified",
    "meeting_booked"
]

class LeadBase(BaseModel):
    whatsapp_id: str = Field(
        ...,
        description="Número de Whatsapp/JID do lead no formato internacional (EX: 5511999999999)",
        example="5511999999999"
    )
    nmae: Optional[str] = Field(None, description="Nome do lead ou contato", example="Felipe Santos")
    email: Optional[EmailStr] = Field(None, description="E-mail corporativo do lead", example="felipe@empresa.com")
    company: Optional[str] = Field(None, description="Nome da empresa do lead", example="Atlas Technology")
    status: LeadStatus = Field(
        default="uncontacted",
        description="Status atual do lead no funil de atendimento"
    )
    qualification_score: int = Field(
        default=0,
        ge=0,
        le=100,
        descrpition="Pontuação de qualificação calculada pelo agente de IA (0 a )100)"
    )

# pyrefly: ignore[parse-error]
class Leadcreate(LeadBase):
    """Schema para criação de um novo lead."""
    pass

class LeadUpdateStatus(BaseModel):
    """Schema para atualização parcial do status e score do lead."""
    status: Optional[LeadStatus] = Field(None, description="Novo status do lead")
    qualification_score: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Nova pontuação de qualificação"
    )

    class LeadResponse(LeadBase):
        """Schema de resposta retornado pela API para consultas de leads."""
        model_config = ConfigDict(from_attributes=True)

        id: UUID
        created_at: datetime
        updated_at: datetime

    class LeadMetricsResponse(BaseModel):
        """Schema para consolidação das métricas do funil de qualificação."""
        total_leads: int = Field(..., description="Total geral de leads cadastrados")
        uncontacted: int = Field(0, description="Leads capturados ainda não contatados")
        qualifying: int = Field(0, description="Leads em processo de qualificação com a IA")
        qualified: int = Field(0, description="Leads qualificados aguardando agendamento")
        desqualified: int = Field(0, description="Leads desqualificados fora do ICP")
        meeting_booked: int = Field(0, description="Leads com reunião agendada na agenda")