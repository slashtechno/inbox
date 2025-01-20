from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from inbox.db.models.inbox import Inbox, InboxCreate
from typing import Annotated
from inbox.db import get_session
from passlib.context import CryptContext
from inbox import settings
from inbox.routers import auth

SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_expire_minutes
MAGIC_LINK_EXPIRE_MINUTES = 15

router = APIRouter(prefix="/inboxes", tags=["inboxes"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




# Create an inbox
@router.post("/", tags=["auth"])
def create_inbox(
    inbox: InboxCreate, session: Annotated[Session, Depends(get_session)]
) -> None:
    hashed = auth.get_password_hash(inbox.password)
    # Update needs to be used since InboxCreate has a `password` field but Inbox only has a `hashed_password` field
    db_inbox = Inbox.model_validate(inbox, update={"hashed_password": hashed})
    session.add(db_inbox)
    session.commit()
    session.refresh(db_inbox)
    return db_inbox


@router.get("/")
def return_inbox(
    inbox: Annotated[Inbox, Depends(auth.get_current_inbox)],
    # session: Annotated[Session, Depends(get_session)],
) -> Inbox:
# ) -> list[MessagePublic]:
    # return session.exec(select(Message)).all()
    return inbox
