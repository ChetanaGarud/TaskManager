from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[schemas.TaskResponse])
def read_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max number of tasks to return"),
    is_completed: Optional[bool] = Query(None, description="Filter tasks by completion status"),
    sort_by: Optional[str] = Query(None, description="Field to sort by (e.g., 'title', 'priority', 'created_at')"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Order of sorting: 'asc' or 'desc'"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Task)

    # 1. Apply Filtering
    if is_completed is not None:
        query = query.filter(models.Task.is_completed == is_completed)

    # 2. Apply Sorting
    if sort_by and hasattr(models.Task, sort_by):
        model_attr = getattr(models.Task, sort_by)
        if sort_order == "desc":
            query = query.order_by(model_attr.desc())
        else:
            query = query.order_by(model_attr.asc())
    else:
        query = query.order_by(models.Task.id.asc())

    # 3. Apply Pagination
    return query.offset(skip).limit(limit).all()

@router.get("/{task_id}", response_model=schemas.TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, updated_task: schemas.TaskCreate, db: Session = Depends(get_db)):
    task_query = db.query(models.Task).filter(models.Task.id == task_id)
    task = task_query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_query.update(updated_task.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task_query = db.query(models.Task).filter(models.Task.id == task_id)
    task = task_query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task_query.delete(synchronize_session=False)
    db.commit()
    return None