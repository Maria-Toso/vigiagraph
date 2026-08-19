from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse

from app import __version__
from app.api.routes import router
from app.config import settings
from app.dependencies import get_repository


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_repository().initialize()
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="API explicavel para analise de risco em transacoes financeiras.",
    lifespan=lifespan,
)
app.include_router(router)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard")


@app.get("/dashboard", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(Path(__file__).parent / "web" / "index.html")

