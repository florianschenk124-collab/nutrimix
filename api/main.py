"""
NutrientMixer API – FastAPI Applikation.

Lokal:       uvicorn api.main:app --reload
Produktion:  uvicorn api.main:app --host 0.0.0.0 --port $PORT
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.routers.recipes import router as recipes_router
from api.routers.water_profiles import router as water_router
from api.routers.salts import router as salts_router, ions_router
from api.routers.calculator import router as calculator_router
from api.routers.tools import router as tools_router
from api.routers.data import (
    plants_router, growth_router,
    settings_router, locales_router,
)

VERSION = "0.5.0-alpha"
STATIC_DIR = Path(__file__).parent.parent / "static"


class LanguageMiddleware(BaseHTTPMiddleware):
    """Setzt die Backend-Sprache pro Request basierend auf X-Lang Header."""

    async def dispatch(self, request: Request, call_next):
        lang = request.headers.get("x-lang", "en")
        if lang in ("de", "en"):
            from ui.locales import set_language
            set_language(lang)
        response = await call_next(request)
        return response


def create_app() -> FastAPI:
    app = FastAPI(
        title="NutrientMixer API",
        description="REST API für Pflanzenernährungs-Berechnungen",
        version=VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Sprach-Middleware ──
    app.add_middleware(LanguageMiddleware)

    # ── API Router ──
    app.include_router(recipes_router)
    app.include_router(water_router)
    app.include_router(salts_router)
    app.include_router(ions_router)
    app.include_router(calculator_router)
    app.include_router(tools_router)
    app.include_router(plants_router)
    app.include_router(growth_router)
    app.include_router(settings_router)
    app.include_router(locales_router)

    # ── Startup ──
    @app.on_event("startup")
    def startup():
        from ui.locales import init_language
        from database.data_manager import register_custom_salts, apply_costs_to_salts
        init_language()
        register_custom_salts()
        apply_costs_to_salts()

    # ── Health ──
    @app.get("/api/health", tags=["System"])
    def health():
        return {
            "status": "ok",
            "version": VERSION,
            "alpha": True,
        }

    # ── Static Files (Produktion) ──
    if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
        app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        async def spa_fallback(request: Request, path: str):
            file_path = STATIC_DIR / path
            if file_path.is_file():
                return FileResponse(file_path)
            return FileResponse(STATIC_DIR / "index.html")

    return app


app = create_app()
