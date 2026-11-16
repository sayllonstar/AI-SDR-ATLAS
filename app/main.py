from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.leads import router as leads_router
from app.api.v1.webhooks import router as webhooks_router
from app.core.config import settings
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclos de vida da aplicação FastAPI.
    Executa a inicialização de esquemas no PostgreSQL na subida e fecha o pool de conexões ao encerrar.
    """
    # 1. CRia as tabelas no PostegreSQL caso não existam (Desenvolvimento/Protipação)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        print(f"{settings.PROJECT_NAME} iniciado com sucesso no ambiente")

        yield 

        await engine.dispose()
        print("Conexão com o PostgreSQL encerrada com sucesso")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="""
        ## AI SDR Engine - Atlas Scoiety API

        API assíncrona para qualificação autônoma de leads corporativos e agendamento de reuniões via WhatsApp.

        ### Principais Funcionalidades:
        * **Webhooks:** Recebimento assíncrono de eventos e mensagens da Evolution API.
        * **Leads Admin:** Gerenciamento do funil de vendas, pontuação de qualificação e métricas.
        * **Agente IA:** Orquestração de raciocínio via Amazon Bedrock (Claude 3.5 sonnet) com Tool Calling.
        """,
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["Health Check"])
    async def health_check():
        """
        Endpoint de verificação de saúde (Health Check) para monitoramento do container.
        """
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "project": settings.PROJECT_NAME,
        }


        app.include_router(webwooks_router, prefix=settings.API_V1_STR)
        app.include_router(leads_router, prefix=settings.API_V1_STR)

        