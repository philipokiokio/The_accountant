from fastapi import APIRouter
from accountant.routers.auth_router import api_router as auth_router
from accountant.routers.ums_router import api_router as ums_router
from accountant.routers.earning_router import api_router as earning_router
from accountant.routers.tracker_router import api_router as tracker_router


api_router = APIRouter()


api_router.include_router(router=auth_router)
api_router.include_router(router=ums_router)
api_router.include_router(router=earning_router)
api_router.include_router(router=tracker_router)
