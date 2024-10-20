from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Request, Header, BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
import uvicorn
import jwt

from pydantic_models import Token, User, TokenInput
from database_actions import DataBaseActions
from services import AuthActions
from config import settings


app = FastAPI(title="TimeTable", version="1.0.0")  # приложение FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # схема для работы с токенами
db_act = DataBaseActions()
auth_act = AuthActions()


# --- DEPENDS функции для FastAPI ---
# Декодирование и проверка токена
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[auth_act.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = await db_act.get_user(username)
    if user is None:
        raise credentials_exception
    return user
# --- DEPENDS функции для FastAPI ---


# --- FASTAPI ENDPOINTS ---
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db_act.authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_act.create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/me/")
async def read_users_me(token: TokenInput):
    current_user = await get_current_user(token.access_token)
    return current_user
# --- FASTAPI ENDPOINTS ---


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
