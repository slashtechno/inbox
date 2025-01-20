from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    # Put circular imports here (https://sqlmodel.tiangolo.com/tutorial/code-structure/#make-circular-imports-work)
    # from .foo import bar
    ...

class MessageBase(SQLModel):
    name: str = Field(index=True)
    text: str   
class MessageCreate(MessageBase):
    ...
class Message(MessageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
class MessagePublic(MessageBase):
    id: int
