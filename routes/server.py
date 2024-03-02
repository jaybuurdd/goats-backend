from fastapi import Depends, APIRouter, Response

router = APIRouter()

@router.get("/health-check")
async def ping():
    return Response(status_code=200)