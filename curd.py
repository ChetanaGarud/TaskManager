from sqlalchemy.orm import Session
from app import models, schemas

def get_tasks(db: Session, skip: int = 0, limit: int = 100, is_completed: bool = None, priority: str = None, sort_by: str = "created_at_desc"):
    query = db.query(models.Task)
    
    # Filtering Logic
    if is_completed is not None:
        query = query.filter(models.Task.is_completed == is_completed)
    if priority is not None:
        query = query.filter(models.Task.priority == priority)
        
    # Amazon-style Sorting Logic
    if sort_by == "created_at_asc":
        query = query.order_by(models.Task.created_at.asc())
    elif sort_by == "priority_desc":
        # Custom sorting logic mapping high -> medium -> low
        query = query.order_by(models.Task.priority.desc()) 
    else:
        # Default: Newest tasks first
        query = query.order_by(models.Task.created_at.desc())

    return query.offset(skip).limit(limit).all()

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        priority=task.priority
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_data: schemas.TaskCreate):
    db_task = get_task(db, task_id)
    if db_task:
        db_task.title = task_data.title
        db_task.description = task_data.description
        db_task.is_completed = task_data.is_completed
        db_task.priority = task_data.priority
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False