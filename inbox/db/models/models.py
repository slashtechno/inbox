from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    # Put circular imports here (https://sqlmodel.tiangolo.com/tutorial/code-structure/#make-circular-imports-work)
    # from inbox.db.models.message import Message
    ...
class InboxBase(SQLModel):
    username: str = Field(index=True)
class InboxCreate(InboxBase):
    password: str
class Inbox(InboxBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    messages: list["Message"] = Relationship(back_populates="inbox", cascade_delete=True)
    hashed_password: str = Field()
class InboxPublic(InboxBase):
    messages: list["Message"] = []


class MessageBase(SQLModel):
    name: str = Field(index=True)
    text: str   
    to: str
class MessageCreate(MessageBase):
    ...
class Message(MessageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    inbox: Inbox | None = Relationship(back_populates="messages")
    inbox_id: int | None = Field(foreign_key="inbox.id", default="1", ondelete="CASCADE")
class MessagePublic(MessageBase):
    id: int
