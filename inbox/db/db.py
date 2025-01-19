from sqlmodel import Field, SQLModel, col, create_engine, Session, select
from inbox import settings


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # https://sqlmodel.tiangolo.com/tutorial/indexes
    text: str = Field(index=True)


# Echo SQL statements
engine = create_engine(settings.db_url, echo=True)


def create_db_and_tables():
    # Create the table (https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#create-the-database-and-table)
    SQLModel.metadata.create_all(engine)


def create_test_message():
    # Create a Message object
    test_messages = [Message(text="Hello, SQL!"), Message(text="Hi, SQL!")]
    with Session(engine) as session:
        # Add the object to the session
        [session.add(m) for m in test_messages]
        session.commit()
        # access a single field that'll be refreshed (https://sqlmodel.tiangolo.com/tutorial/automatic-id-none-refresh/#print-a-single-field)
        print(f"test_message text: {test_messages[0].text}")
        # Explicitly refresh the entire object
        session.refresh(test_messages[0])
        print(f"test_message: {test_messages[0]}")


def read_data():
    # https://sqlmodel.tiangolo.com/tutorial/select
    with Session(engine) as session:
        statement = select(Message)
        results = session.exec(statement)
        # results = results.all() # return an array
        print("Printing all messages")
        for m in results:
            print(f"message: {m}")
        # Filter rows where the text begins with "Hi" and ends with "!"
        # https://sqlmodel.tiangolo.com/tutorial/where/
        statement = (
            select(Message)
            .where(col(Message.text).startswith("Hi"))  # noqa: F821
            .where(col(Message.text).endswith("!"))
        )
        print(session.exec(statement).all())


def main():
    create_db_and_tables()
    create_test_message()
    read_data()


if __name__ == "__main__":
    main()
