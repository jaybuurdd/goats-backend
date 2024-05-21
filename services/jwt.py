import os
import jwt
import requests
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from jose import jwt, jwk, JWTError, ExpiredSignatureError
from jose.utils import base64url_decode
from typing import Optional

from utils.logging import logger

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

async def get_google_keys():
    discovery = requests.get(GOOGLE_DISCOVERY_URL).json()
    jwks_uri = discovery['jwks_uri']
    jwks = requests.get(jwks_uri).json()
    return {jwk["kid"]: jwk for jwk in jwks["keys"]}

async def decode_google_jwt(token: str):
    logger.info("Retrieving Google public keys")
    keys = await get_google_keys()
    try:
        header = jwt.get_unverified_header(token)
        key = jwk.construct(keys[header["kid"]])
        message, encoded_sig = token.rsplit('.', 1)
        decoded_sig = base64url_decode(encoded_sig.encode())
        if not key.verify(message.encode(), decoded_sig):
            logger.error("Issue verifying users signature")
            raise JWTError("Signature verification failed")
        claims = jwt.get_unverified_claims(token)
        logger.info(f"JWT Decode Complete")
        return claims
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid JWT")
    except JWTError as e:
        raise HTTPException(status_code=400, detail=f"JWT Error: {e}")

def create_jwt_session(user_data, secret_key):
    expiration = datetime.now(timezone.utc) + timedelta(hours=int(os.getenv('JWT_EXPIRES')))
    logger.info(f"Token creation time (UTC): {datetime.now(timezone.utc)}")
    logger.info(f"Token expiration time (UTC): {expiration}")

    payload = {
        "sub": str(user_data['sub']),
        "exp": expiration
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    logger.info(f"token created: {token}")

    return token

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.token_cookie = 'jwt_token'

    async def __call__(self, request: Request):
        logger.info("JWTBearer __call__ method invoked")
        logger.info(f"Request headers: {request.headers}")
        logger.info(f"Request cookies: {request.cookies}")

        credentials: Optional[str] = request.cookies.get(self.token_cookie)
        logger.info(f"jwt credentials check: {credentials}")
        if credentials:
            if not self.verify_jwt(credentials):
                logger.error("The provided token was invalid or expired")
                raise HTTPException(status_code=401, detail="Invalid token or expired token.")
            return True
        else:
            logger.error("The provided authorization code is invalid: ")
            raise HTTPException(status_code=401, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        logger.info("verify_jwt method invoked")
        try:
            decoded_token = jwt.decode(jwtoken, os.getenv('JWT_SECRET_KEY'), algorithms=["HS256"])
            logger.info(f"Decoded token: {decoded_token}")
            return True
        except ExpiredSignatureError:
            logger.error("Token has expired")
            return False
        except JWTError as e:
            logger.error(f"JWT token verification failed: {e}")
            return False