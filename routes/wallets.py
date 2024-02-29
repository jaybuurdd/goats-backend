from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from repo.wallets import GoatsRepo
from utils.database import get_db
from services.jwt import JWTBearer

router = APIRouter()

@router.get("/member/{goat_id}", dependencies=[Depends(JWTBearer())])
async def get_member_wallet_and_goat(goat_id: int, db: Session = Depends(get_db)):
    return GoatsRepo.search_goat_owner_wallet(goat_id, db)