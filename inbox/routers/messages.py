from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from inbox.db.models.models import Inbox, MessageCreate, Message, MessagePublic
from typing import Annotated
from inbox.db import get_session
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from inbox.routers import auth

router = APIRouter(prefix="/messages", tags=["messages"])

# Create message
# @router.post("/", response_model=MessagePublic)
# @router.post("/")
@router.post("/send", summary="Send a message to an inbox")
def create_message(message: MessageCreate, session: Annotated[Session, Depends(get_session)]) -> MessagePublic:
    """
    Send a message to the inbox with the given username
    """
    try:
        inbox = session.exec(select(Inbox).where(Inbox.username == message.to)).one()
    except (MultipleResultsFound, NoResultFound):
        raise HTTPException(404, detail="Inbox not found")
    db_message = Message.model_validate(message, update={"inbox": inbox})
    session.add(db_message)
    session.commit()
    session.refresh(db_message)
    return db_message



# TODO: Pagination...?
@router.get("/", summary="Read my messages")
def return_message(session: Annotated[Session, Depends(get_session)], inbox: Annotated[Inbox, Depends(auth.get_current_inbox)],) -> list[MessagePublic]:
    """Return all messages for the logged-in inbox"""
    return inbox.messages