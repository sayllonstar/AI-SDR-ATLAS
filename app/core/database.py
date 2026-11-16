from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Criação do Engine Assincrono utilizando a URI dinamicamente construida pelo Pydantic Settings
engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    echo=(settings.ENVIRONMENT == "development"), # Exibe queries SQL no terminal em modo desenvolvimento
    future=True,
    pool_pre_ping=True, # Verifica se a conexão com o banco de dados está ativa antes de cada requisição
)

# Fabrica de sessões anssíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    classh_=AsyncSession,
    autorflush=False,
    autocommit=False,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    """
    classe base para todos os modelos ORM SQLAlchemy da aplicação.
    """
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Injeta uma sessão assíncrona do banco de dados por requisição HTTP nos endpoints FastAPI (Dependency Injection).
    Garante o fechamento automático da sessão após a conclusão do processamento.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

