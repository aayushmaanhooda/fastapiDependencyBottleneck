import time
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from config import create_db_and_tables, engine
from logger import get_logger
from model import Todo, TodoCreate

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting fastapi")
    create_db_and_tables()
    logger.info("DB and tables ready")
    yield


app = FastAPI(title="Optimized Solution", lifespan=lifespan)


# Instead of yielding a live open session, yield a callable that CREATES one.
# The route controls exactly when the session opens and closes.
def get_session_factory():
    yield lambda: Session(engine)


@app.get("/")
def root():
    return {"message": "I am root"}


@app.get("/health")
def health():
    return {"message": "Server is healthy"}


@app.get("/todos")
def get_todos(make_session=Depends(get_session_factory)):
    start = time.time()

    # Session opens → DB work → session closes → connection returned to pool
    with make_session() as session:
        todos = session.exec(select(Todo)).all()

    # Connection is already back in the pool before the sleep starts
    time.sleep(0.5)

    logger.info(f"GET /todos took {time.time() - start:.3f}s")
    return {"message": "All todos", "todos": todos}


@app.post("/todos")
def create_todo(todo: TodoCreate, make_session=Depends(get_session_factory)):
    start = time.time()

    with make_session() as session:
        existing = session.exec(
            select(Todo).where(Todo.task == todo.task, Todo.description == todo.description)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Todo with same task and description already exists")

        new_todo = Todo(task=todo.task, description=todo.description)
        session.add(new_todo)
        session.commit()
        session.refresh(new_todo)

    # Connection is already back in the pool before the sleep starts
    time.sleep(0.5)

    logger.info(f"POST /todos took {time.time() - start:.3f}s")
    return {"message": "Todo created successfully", "todo": new_todo}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("solution:app", host="localhost", port=8001, reload=True)
