import importlib
from pathlib import Path
from fastapi.concurrency import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from inbox.db import create_db_and_tables

# https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#sqlmodel-metadata-order-matters

# https://fastapi.tiangolo.com/advanced/events/#lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup:
    create_db_and_tables()
    # ---
    yield
    # ---
    # On shutdown:

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=PlainTextResponse)
async def help():
    return "This is Inbox, a rudimentary system to create \"inboxes\", which you can send and receive messages to. Uses SQLModel and FastAPI. See the source code at https://github.com/slashtecho/inbox"

# Dynamically import all routers
routers_dir = Path(__file__).parent / "routers"
for path in routers_dir.glob("*.py"):
    if path.name != "__init__.py":
        module_name = f"{__package__}.routers.{path.stem}"
        module = importlib.import_module(module_name)
        # If the module has a router attribute, include it in the app
        if hasattr(module, "router"):
            app.include_router(getattr(module, "router"))


if __name__ == "__main__":
    # Go to http://localhost:8000/docs to see the Swagger UI
    # or http://localhost:8000/redoc to see the specification
    uvicorn.run(app, host="0.0.0.0", port=8000)