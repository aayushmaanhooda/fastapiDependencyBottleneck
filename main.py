import time
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from config import create_db_and_tables, get_session
from logger import get_logger
from model import Todo, TodoCreate

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting fastapi")
    create_db_and_tables()
    logger.info("DB and tables ready")
    yield


app = FastAPI(title="Dependency Bottleneck Test", lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "I am root"}


@app.get("/health")
def health():
    return {"message": "Server is healthy"}


@app.get("/todos")
def get_todos(session: Session = Depends(get_session)):
    start = time.time()

    todos = session.exec(select(Todo)).all()

    # Simulates post-DB work (external API call, enrichment, serialization).
    # The DB connection is still held open by the dependency during this entire sleep.
    time.sleep(0.5)

    logger.info(f"GET /todos took {time.time() - start:.3f}s")
    return {"message": "All todos", "todos": todos}


@app.post("/todos")
def create_todo(todo: TodoCreate, session: Session = Depends(get_session)):
    start = time.time()

    existing = session.exec(
        select(Todo).where(Todo.task == todo.task, Todo.description == todo.description)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Todo with same task and description already exists")

    new_todo = Todo(task=todo.task, description=todo.description)
    session.add(new_todo)
    session.commit()
    session.refresh(new_todo)

    # Simulates post-DB work (sending a webhook, calling an external API, etc.).
    # The DB connection is still held open during this sleep — this is the bottleneck.
    time.sleep(0.5)

    logger.info(f"POST /todos took {time.time() - start:.3f}s")
    return {"message": "Todo created successfully", "todo": new_todo}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
