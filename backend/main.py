from fastapi import FastAPI, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import os



# create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

# create fast-api app
app = FastAPI(
    title="To-Do List API"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev stage "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# returns all tasks
@app.get("/todos", response_model=list[schemas.TodoOut])
def get_todos(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()

# patch changes completed field
@app.patch("/todos/{todo_id}", response_model=schemas.TodoOut)
def update_completed_status(
    todo_id: int = Path(...),
    completed: bool = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    todo = db.query(models.Todo).get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo.completed = completed
    db.commit()
    db.refresh(todo)
    return todo

# accepts json with a new task
@app.post("/todos", response_model=schemas.TodoOut, status_code=201)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    db_todo = models.Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# deletes task by id
@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()

# app version
@app.get("/version")
def get_backend_version():
    version = os.getenv("BACKEND_VERSION", "unknown")
    return {"version": version}

# healthcheck
@app.get("/health")
def health():
    return {"status": "ok"}