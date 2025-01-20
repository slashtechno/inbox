from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from inbox.db.models.message import MessageCreate, Message, MessagePublic
from typing import Annotated
from inbox.db import get_session

router = APIRouter(prefix="/messages", tags=["messages"])

# Create message
# @router.post("/", response_model=MessagePublic)
@router.post("/")
def create_message(message: MessageCreate, session: Annotated[Session, Depends(get_session)]) -> MessagePublic:
    db_message = Message.model_validate(message)
    session.add(db_message)
    session.commit()
    session.refresh(db_message)
    return db_message

# TODO: Pagination...?
@router.get("/")
def return_message(session: Annotated[Session, Depends(get_session)]) -> list[MessagePublic]:
    return session.exec(
        select(Message)
    ).all()