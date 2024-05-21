import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.logging import logger
from routes.users import router as user_router
from routes.wallets import router as wallet_router
from routes.server import router as server_router


def register_endpoints():
    logger.info("Starting API endpoints registration")
    api = FastAPI()

    origins = [
        'https://goatsdao.com',
        # 'http://localhost:3000'
    ]

    api.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Set-Cookie"]
    )

    api.include_router(user_router, prefix="/api/v1/user", tags=["users"])
    api.include_router(wallet_router, prefix="/api/v1/wallet", tags=["wallets"])
    api.include_router(server_router, prefix="/api/v1/server", tags=["servers"])
    logger.info("Ending API endpoints registration")
    return api