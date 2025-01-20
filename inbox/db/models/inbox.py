from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    # Put circular imports here (https://sqlmodel.tiangolo.com/tutorial/code-structure/#make-circular-imports-work)
    # from .foo import bar
    ...

class InboxBase(SQLModel):
    username: str = Field(index=True)
class InboxCreate(InboxBase):
    password: str
class Inbox(InboxBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field()
class InboxPublic(InboxBase):
    id: int
