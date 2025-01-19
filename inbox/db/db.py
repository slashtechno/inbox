from sqlmodel import Field, SQLModel, create_engine, Session
from inbox import settings


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str


# Echo SQL statements
engine = create_engine(settings.db_url, echo=True)


def create_db_and_tables():
    # Create the table (https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#create-the-database-and-table)
    SQLModel.metadata.create_all(engine)


def create_test_message():
    # Create a Message object
    test_message = Message(text="Hello, SQL!")
    with Session(engine) as session:
        # Add the object to the session
        session.add(test_message)
        session.commit()
        # access a single field that'll be refreshed (https://sqlmodel.tiangolo.com/tutorial/automatic-id-none-refresh/#print-a-single-field)
        print(f"DEBUG: test_message text: {test_message.text}")
        # Explicitly refresh the entire object
        session.refresh(test_message)
        print(f"DEBUG: test_message: {test_message}")




def main():
    create_db_and_tables()
    create_test_message()


if __name__ == "__main__":
    main()
