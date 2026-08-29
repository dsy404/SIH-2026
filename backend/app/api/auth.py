from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    role: str # ADMIN, DISTRICT_OFFICER, FIELD_VERIFIER

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Auth stub
    if token == "admin_token":
        return User(username="admin", role="ADMIN")
    elif token == "officer_token":
        return User(username="officer", role="DISTRICT_OFFICER")
    elif token == "verifier_token":
        return User(username="verifier", role="FIELD_VERIFIER")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

