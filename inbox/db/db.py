from sqlmodel import Field, SQLModel, col, create_engine, Session, select, Relationship
from inbox import settings


class MessageInboxLink(SQLModel, table=True):
    inbox_id: int | None = Field(
        default = None,
        foreign_key="inbox.id",
        primary_key=True
    )
    hero_id: int | None = Field(
        default=None,
        foreign_key="message.id",
        primary_key=True
    )



class Inbox(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Seems putting Message in quotes is a form of a forward reference
    # Setting cascade_delete to true means that if the inbox is deleted, all the messages will be too. By default, without this, their inbox value would just be set to null
    # cascade_delete only works with deletions from within the program but should coexist with ondelete (https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/cascade-delete-relationships/#using-cascade_delete-or-ondelete)
    # It seems that cascade_delete doesn't work with a many-to-many-relationship though
    messages: list["Message"] = Relationship(back_populates="inboxes", link_model=MessageInboxLink)


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # https://sqlmodel.tiangolo.com/tutorial/indexes
    text: str = Field(index=True)

    # https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/back-populates/#a-mental-trick-to-remember-back_populates
    # ondelete options, as described in the docs (https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/cascade-delete-relationships/#set-ondelete-to-cascade):
    # CASCADE: Automatically delete this record (hero) when the related one (team) is deleted.
    # SET NULL: Set this foreign key (hero.team_id) field to NULL when the related record is deleted.
    # RESTRICT: Prevent the deletion of this record (hero) if there is a foreign key value by raising an error.

    inboxes: list[Inbox] | None = Relationship(back_populates="messages", link_model=MessageInboxLink)


# Print SQL statements in echo is True
engine = create_engine(settings.db_url, echo=False)


def create_db_and_tables():
    # Create the table (https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#create-the-database-and-table)
    SQLModel.metadata.create_all(engine)


def create_test_message():
    with Session(engine) as session:
        # Create a primary inbox
        inbox_primary = Inbox(name="Primary Inbox")

        # Create a Message object
        test_messages = [
            Message(text="Hello, SQL!", inboxes=[inbox_primary]),
            Message(text="Hi, SQL!", )
        ]

        # Add the second message to the secondary inbox and primary inbox
        inbox_secondary = Inbox(name="Secondary Inbox", messages=[test_messages[1]])
        print(inbox_secondary.messages)
        inbox_primary.messages.append(test_messages[1])
        # Add the objects to the session
        [session.add(m) for m in test_messages]
        session.commit()
        # access a single field that'll be refreshed (https://sqlmodel.tiangolo.com/tutorial/automatic-id-none-refresh/#print-a-single-field)
        print(f"second test message inboxes: {test_messages[1].inboxes}")
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
        # https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/read-relationships/#get-relationship-team-new-way
        print(f"Message/row 2's inbox: {message.inbox}")

        # Get messages and their inbox relations
        statement = select(Message, Inbox).where(col(Inbox.id) == col(Message.inbox_id))
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

        # Print the primary inbox's messages
        statement = select(Inbox).where(col(Inbox.name) == "Primary Inbox")
        primary_inbox = session.exec(statement).one()
        print(f"Primary inbox messages: {primary_inbox.messages}")

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

        # Select the message
        message = session.exec(select(Message).where(Message.text == text)).one()
        print(f"Message prior to update: {message} | message is in {message.inboxes}")
        # Select an inbox
        inbox = session.exec(select(Inbox).where(Inbox.name == "Primary Inbox")).one()


        # Update text
        message.text = "Updated!"
        # Update relation
        message.inboxes.append(inbox)
        # Add and commit
        session.add(message)
        session.commit()
        # Explicitly refresh and print
        session.refresh(message)
        print(f"Updated message: {message} | message is in {message.inboxes}")

        # Remove relation
        inbox.messages.remove(message)
        session.add(message)
        session.commit()
        session.refresh(message)
        print(f"Unlinked from inbox: {message} | inboxes: {message.inboxes}")


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
    # read_data()
    # batch_read()
    update()
    # delete()


if __name__ == "__main__":
    main()

# Getting single rows (https://sqlmodel.tiangolo.com/tutorial/one)
