from fastapi import FastAPI, Depends, HTTPException, Path, Body, Request, Response
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import os
import socket
import time

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST


# create tables if they don't exist. already use alembic
#models.Base.metadata.create_all(bind=engine)

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


# Base HTTP metrics
REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds",
    ["method", "path"],
)
INFLIGHT = Gauge(
    "http_requests_in_flight",
    "In-flight HTTP requests",
)

# Simple metrics
TODO_CREATED = Counter("todo_created_total", "Total todos created")
TODO_DELETED = Counter("todo_deleted_total", "Total todos deleted")
TODO_COMPLETED = Counter("todo_completed_total", "Total todos marked completed")


# getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# middleware 
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    route = request.scope.get("route")
    route_path = getattr(route, "path", request.url.path)

    track = route_path != "/metrics"

    if track:
        INFLIGHT.inc()
    start = time.perf_counter()
    status = 500

    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        if track:
            duration = time.perf_counter() - start
            LATENCY.labels(request.method, route_path).observe(duration)
            REQUESTS.labels(request.method, route_path, str(status)).inc()
            INFLIGHT.dec()


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

    previous_completed = bool(todo.completed)

    todo.completed = completed
    db.commit()
    db.refresh(todo)

    if completed and not previous_completed:
        TODO_COMPLETED.inc()

    return todo

# accepts json with a new task
@app.post("/todos", response_model=schemas.TodoOut, status_code=201)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    db_todo = models.Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    TODO_CREATED.inc()
    return db_todo

# deletes task by id
@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    TODO_DELETED.inc()

# app version and host IP
@app.get("/version")
def get_version():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
    except Exception:
        ip_address = "unknown"

    return {
        "version": os.getenv("BACKEND_VERSION", "unknown"),
        "host_ip": ip_address
    }

# healthcheck
@app.get("/health")
def health():
    return {"status": "ok"}

# endpoint /metrics
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)