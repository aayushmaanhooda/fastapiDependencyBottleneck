from sqlmodel import SQLModel, Field


class Todo(SQLModel, table=True):
    id: int = Field(primary_key=True)
    task: str
    description: str


class TodoCreate(SQLModel):
    task: str
    description: str







