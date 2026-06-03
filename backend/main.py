import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.core.config import settings
from app.routers import webhook, api, test

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("TONATIVE SME BOT starting up")
    logger.info("=" * 60)
    logger.info(f"Groq LLM:      {'READY' if settings.groq_enabled else 'NOT CONFIGURED'}")
    logger.info(f"AethexAI:      {'READY' if settings.aethex_enabled else 'NOT CONFIGURED'}")
    logger.info(f"PostgreSQL:    {'READY' if settings.DATABASE_URL else 'USING IN-MEMORY'}")
    logger.info(f"Twilio:        {'READY' if settings.TWILIO_ACCOUNT_SID else 'NOT CONFIGURED'}")
    logger.info(f"Public URL:    {settings.PUBLIC_URL}")
    logger.info("=" * 60)
    yield
    from app.services.database import close_pool
    await close_pool()
    logger.info("TONATIVE SME BOT shut down cleanly")


app = FastAPI(
    title="BizPadi",
    description="WhatsApp AI Companion for African SMEs.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    if "/webhook/" in request.url.path:
        from app.services.whatsapp import build_twiml_text
        return Response(
            content=build_twiml_text("I am having a technical issue. Please try again in a moment."),
            media_type="application/xml",
        )
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


app.include_router(webhook.router)
app.include_router(api.router)
app.include_router(test.router)


@app.get("/")
async def root():
    return {
        "service": "BizPadi",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
        "status_dashboard": "/api/status",
        "webhook": "/webhook/whatsapp",
        "test_chat": "/test/chat",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
