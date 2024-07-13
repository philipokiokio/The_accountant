from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from accountant.root.app_router import api_router as api
import time
from accountant.root.settings import Settings


settings = Settings()


def intialize() -> FastAPI:
    app = FastAPI()

    ORIGINS = [
        "http://localhost:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origin_regex="http://localhost:*",
    )
    app.include_router(router=api)

    return app


app = intialize()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/", status_code=307)
def root():
    if settings.db_migration_env is False:
        return RedirectResponse(url="/docs")

    raise HTTPException(detail="not found", status_code=404)
