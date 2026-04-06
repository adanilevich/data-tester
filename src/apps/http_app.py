from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.apps.http_di import HttpDependencyInjector
from src.apps.http_routers import (
    domain_config,
    reports,
    specifications,
    testsets,
    testruns,
)
from src.config import Config


def create_app(config: Config, di: HttpDependencyInjector | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        app.state.di = di if di is not None else HttpDependencyInjector(config)
        yield

    app = FastAPI(title="Data Tester API", lifespan=lifespan)
    app.include_router(domain_config.router)
    app.include_router(testsets.router)
    app.include_router(specifications.router)
    app.include_router(testruns.router)
    app.include_router(reports.router)
    return app
