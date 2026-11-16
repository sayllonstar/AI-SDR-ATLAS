import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)

from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Lead(Base):
    """
    Modelo ORM para a tabela 'leads'.
    Armazena dados do contato, estado no funil de vendas e pontuação de qualificação.
    """
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    whatsapp_id: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
      : [Optional[str]] = mapped_column(String(100), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
