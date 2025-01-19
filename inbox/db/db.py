from sqlmodel import Field, SQLModel, col, create_engine, Session, select
from inbox import settings


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # https://sqlmodel.tiangolo.com/tutorial/indexes
    text: str = Field(index=True)
    inbox_id: int | None = Field(foreign_key="inbox.id", default="1")


class Inbox(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


# Print SQL statements in echo is True
engine = create_engine(settings.db_url, echo=False)


def create_db_and_tables():
    # Create the table (https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#create-the-database-and-table)
    SQLModel.metadata.create_all(engine)


def create_test_message():
    with Session(engine) as session:
        # Create inboxes
        inbox = Inbox(name="Primary Inbox")
        inbox = Inbox(name="Secondary Inbox")
        session.add(inbox)

        # Create a Message object
        test_messages = [Message(text="Hello, SQL!", inbox_id=inbox.id), Message(text="Hi, SQL!", inbox_id=inbox.id)]
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

        # Get messages and their inbox relations
        statement = select(
            Message, Inbox
        ).where(col(Inbox.id) == col(Message.inbox_id))
        results = session.exec(statement)
        for m, i in results:
            print(f"Inbox: {i} | Message: {m}")

        # Use JOIN (https://sqlmodel.tiangolo.com/tutorial/connect/read-connected-data/#join-tables-in-sqlmodel)
        # "This LEFT OUTER part tells the database that we want to keep everything on the first table, the one on the LEFT in the imaginary space, even if those rows would be left out, so we want it to include the OUTER rows too." - from the docs
        statement = select(Message, Inbox).join(Inbox, isouter=True)
        results = session.exec(statement)
        print("Using Join:")
        for m, i in results:
            print(f"Inbox: {i} | Message: {m}")
        

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
        session.add(Message(text=text, inbox_id=1))
        session.commit()

        # Select it
        message = session.exec(select(Message).where(Message.text == text)).one()
        print(f"Message prior to update: {message}")

        # Update text
        message.text = "Updated!"
        # Update relation
        message.inbox_id = 2
        # Add and commit
        session.add(message)
        session.commit()
        # Explicitly refresh and print
        session.refresh(message)
        print(f"Updated message: {message}")
        
        # Remove relation
        message.inbox_id = None
        session.add(message)
        session.commit()
        session.refresh(message)
        print(f"Unliked from inbox: {message}")


def delete():
    with Session(engine) as session:
        # Create a new message
        text = "Delete me!"
        session.add(Message(text=text))
        session.commit()

        # Select it
        message = session.exec(select(Message).where(Message.text == text)).one()
        print(f"Message prior to deletion: {message}")

        # Delete it... but not before commiting the change.
        session.delete(message)
        session.commit()

        # The object still exists as unexpired
        print("Deleted message:", message)
        message = session.exec(select(Message).where(Message.text == text)).first()
        print(f'Result for messages matching "{text}": {message}')


def main():
    create_db_and_tables()

    create_test_message()
    read_data()
    # batch_read()
    update()
    # delete()


if __name__ == "__main__":
    main()

# Getting single rows (https://sqlmodel.tiangolo.com/tutorial/one)
