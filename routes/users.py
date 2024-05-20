import os
import json
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi import Depends, APIRouter, HTTPException, Response, status


from schemas.users import RegisterRequest
from repo.users import UserRepo
from services.jwt import decode_google_jwt as decode, \
create_jwt_session as new_session, JWTBearer
from utils.database import get_db
from utils.logging import logger

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
    response.set_cookie(
        key="jwt_token", 
        value=token, 
        httponly=True, 
        samesite='None', 
        secure=True,  #NOTE: secure=False for local testing
        # domain="api-goatsdao.onrender.com",
        path='/'
    )

    logger.info(f"Set-Cookie header: {response.headers.get('set-cookie')}")
    logger.info(f"JWT token set: {token}")

     # Serialize the user object to JSON
    user_data = jsonable_encoder(user)

    response.headers["Access-Control-Expose-Headers"] = "Set-Cookie"

    return Response(
        content=json.dumps(user_data),
        media_type="application/json",
        status_code=status.HTTP_200_OK,
        headers=response.headers
    )
    #return user

@router.post("/register", dependencies=[Depends(JWTBearer())])
async def register_user(user : dict, db: Session = Depends(get_db)):
    print("user: ", user)
    return UserRepo.reigster_user(user, db)

@router.get("/session", dependencies=[Depends(JWTBearer())])
async def session_check():
    return Response(status_code=200)