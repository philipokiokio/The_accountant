from fastapi import APIRouter
from accountant.routers.auth_router import api_router as auth_router
from accountant.routers.ums_router import api_router as ums_router


api_router = APIRouter()


api_router.include_router(router=auth_router)
api_router.include_router(router=ums_router)
