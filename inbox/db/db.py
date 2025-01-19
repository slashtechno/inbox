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
        print(f"First result: {results.first()}")
        # print("Printing all messages")
        # for m in results:
        # print(f"message: {m}")

        # Filter rows where the text begins with "Hi" and ends with "!"
        # https://sqlmodel.tiangolo.com/tutorial/where/
        statement = (
            select(Message)
            .where(col(Message.text).startswith("Hi"))
            .where(col(Message.text).endswith("!"))
        )
        print(session.exec(statement).all())
        # Get the message matching a query, and if there is more than one (or no) message matching the query, error
        results = session.exec(select(Message).where(col(Message.id) == 1))
        print(f"Row 1: {results.one()}")

        # Unlike .one, .get will return None instead of an error if there is no match
        message = session.get(Message, 2)
        print(f"Row 2: {message}")


def batch_read():
    with Session(engine) as session:
        # Create some messages
        for i in range(10):
            session.add(Message(text=str(i)))
        session.commit()

        # Get the first three messages
        statement = select(Message).limit(3)
        results = session.exec(statement)
        print(f"First three rows: {results.all()}")

        # Get the three after the first three
        statement = select(Message).offset(3).limit(3)
        results = session.exec(statement)
        print(f"Next three rows: {results.all()}")

def update():
    with Session(engine) as session:
        # Create a new message
        text = "Update me!"
        session.add(Message(text=text))
        session.commit()
        
        # Select it
        message = session.exec(
            select(Message).where(Message.text == text)
        ).one()
        print(f"Message prior to update: {message}")

        # Set a field value
        message.text = "Updated!"
        # Add and commit
        session.add(message)
        session.commit()
        # Explicitly refresh and print
        session.refresh(message)
        print(f"Updated message: {message}")

def delete():
    with Session(engine) as session:
        # Create a new message
        text = "Delete me!"
        session.add(Message(text=text))
        session.commit()
        
        # Select it
        message = session.exec(
            select(Message).where(Message.text == text)
        ).one()
        print(f"Message prior to deletion: {message}")

        # Delete it... but not before commiting the change.
        session.delete(message)
        session.commit()

        # The object still exists as unexpired
        print("Deleted message:", message)
        message = session.exec(
            select(Message).where(Message.text == text)
        ).first()
        print(f"Result for messages matching \"{text}\": {message}")

def main():
    create_db_and_tables()

    # create_test_message()
    # read_data()
    # batch_read()
    # update()
    delete()

if __name__ == "__main__":
    main()

# Getting single rows (https://sqlmodel.tiangolo.com/tutorial/one)
