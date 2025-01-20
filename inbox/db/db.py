import importlib
from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine
from inbox import settings


# Print SQL statements in echo is True
# print(f"DEBUG: {settings.db_url}")
engine = create_engine(settings.db_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Import models
routers_dir = Path(__file__).parent / "models"
for path in routers_dir.glob("*.py"):
    if path.name != "__init__.py":
        module_name = f"{__package__}.models.{path.stem}"
        # print(f"DEBUG: {module_name}")
        module = importlib.import_module(module_name)
        
# https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/
def get_session():
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    create_db_and_tables()
