import os
from fastapi import Depends, APIRouter, HTTPException, Response
from sqlalchemy.orm import Session

from schemas.users import RegisterRequest
from repo.users import UserRepo
from services.jwt import decode_google_jwt as decode, \
create_jwt_session as new_session, JWTBearer
from utils.database import get_db


router = APIRouter()
# TODO: add request and response models

@router.post("/auth")
async def auth( response: Response, data: dict, db: Session = Depends(get_db)):
    credential = data.get('data', {}).get('credential')

    if not credential or data.get('type') != 'google':
        raise HTTPException(status_code=400, detail="Invalid request data")

    credentials = await decode(credential)
    user = UserRepo.access_google_auth(credentials, db)

    if not user:
        raise HTTPException(status_code=404, detail="Authentication failed")

    # create users jwt session
    token = new_session({
        'sub': data.get('sub')
    }, os.getenv('JWT_SECRET_KEY'))

    # set create jwt token in an http only cookie
    #NOTE: set secure to true in prod
    response.set_cookie(key="jwt_token", value=token, httponly=True, path="/", samesite="Lax", secure=True)  #NOTE: secure=False for local testing

    return user

@router.post("/register", dependencies=[Depends(JWTBearer())])
async def register_user(user : dict, db: Session = Depends(get_db)):
    print("user: ", user)
    return UserRepo.reigster_user(user, db)

@router.get("/session", dependencies=[Depends(JWTBearer())])
async def session_check():
    return Response(status_code=200)