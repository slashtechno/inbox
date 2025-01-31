from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel
from sqlmodel import Session, col, select
from inbox.db.models.models import Inbox
from typing import Annotated
from inbox.db import get_session
from passlib.context import CryptContext
from inbox import settings
import bcrypt

SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_expire_minutes
MAGIC_LINK_EXPIRE_MINUTES = 15

router = APIRouter(prefix="", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password, hashed_password) -> True:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def get_inbox(session: Session, username: str) -> Inbox | None:
    return session.exec(
        select(Inbox).where(col(Inbox.username) == username)
    ).one_or_none()


def authenticate_inbox(session: Session, username: str, password: str):
    inbox = get_inbox(session, username)
    if not inbox:
        return False
    if not verify_password(password, inbox.hashed_password):
        return False
    return inbox


async def get_current_inbox(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> Inbox:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    inbox = get_inbox(session, username)
    if inbox is None:
        raise credentials_exception
    return inbox


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = timedelta(ACCESS_TOKEN_EXPIRE_MINUTES),
    token_type: str = "access",
):
    to_encode = data.copy()
    to_encode.update({"token_type": token_type})
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login", summary="Login")
async def login_for_access_token(
    form_data: Annotated[
        # https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#oauth2passwordrequestform
        OAuth2PasswordRequestForm, Depends()
    ],  # https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/#shortcut
    session: Annotated[Session, Depends(get_session)],
) -> Token:
    user = authenticate_inbox(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


# https://github.com/pyca/bcrypt/issues/684
if not hasattr(bcrypt, '__about__'):
    bcrypt.__about__ = type('about', (object,), {'__version__': bcrypt.__version__})