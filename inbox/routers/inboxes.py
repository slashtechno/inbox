from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from inbox.db.models.models import Inbox, InboxCreate, InboxPublic
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
@router.post("/", tags=["auth"], response_model=InboxPublic, summary="Create an inbox / signup")
def create_inbox(
    inbox: InboxCreate, session: Annotated[Session, Depends(get_session)],
) -> None:
    """Create an inbox with the given username and password"""
    hashed = auth.get_password_hash(inbox.password)
    # Update needs to be used since InboxCreate has a `password` field but Inbox only has a `hashed_password` field
    db_inbox = Inbox.model_validate(inbox, update={"hashed_password": hashed})
    session.add(db_inbox)
    session.commit()
    session.refresh(db_inbox)
    return db_inbox


@router.get("/", summary="Get inbox info")
def return_inbox(
    inbox: Annotated[Inbox, Depends(auth.get_current_inbox)],
    # session: Annotated[Session, Depends(get_session)],
) -> InboxPublic:  
    """Return all data for the logged-in inbox"""
# ) -> list[MessagePublic]:
    # return session.exec(select(Message)).all()
    return InboxPublic.model_validate(inbox, update={
        "messages": inbox.messages,
    })