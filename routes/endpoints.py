import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from utils.logging import logger, LoggingMiddleware
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
    
    
    @api.options("/{path:path}")
    async def option_handler():
        return JSONResponse(content={"message": "OK"}, headers={
            "Access-Control-Allow-Origin": "https://goatsdao.com",
            "Access-Control-Allow-Methods": "OPTIONS, GET, POST, PUT, DELETE",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Cookie, Set-Cookie",
            "Access-Control-Allow-Credentials": "true"
        })
    
    logger.info("Ending API endpoints registration")
    return api