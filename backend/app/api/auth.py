from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    if not settings.ACCESS_PASSWORD:
        raise HTTPException(status_code=500, detail="服务端未配置 ACCESS_PASSWORD")
    if body.password != settings.ACCESS_PASSWORD:
        raise HTTPException(status_code=401, detail="密码错误")
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": "user", "exp": expire}, settings.SECRET_KEY, algorithm="HS256")
    return TokenResponse(access_token=token)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"]
        )
        if payload.get("sub") != "user":
            raise HTTPException(status_code=401, detail="无效的凭证")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="凭证已过期或无效")
