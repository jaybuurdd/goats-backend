from fastapi import APIRouter, Response

router = APIRouter()

@router.get("/health-check")
async def ping(response: Response):
    response.status_code = 200
    response.body = {"status": "OK"}
    return response