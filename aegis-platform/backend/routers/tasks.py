from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.user import User
from models.task import Task, TaskComment, TaskEvidence
from models.audit import AuditLog
from schemas.task import (
    TaskResponse, TaskCreate, TaskUpdate, TaskSummary,
    TaskCommentResponse, TaskCommentCreate,
    TaskEvidenceResponse, TaskEvidenceCreate
)
from auth import get_current_active_user

router = APIRouter()


@router.get("/")
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    task_type: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
    risk_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of tasks with pagination and filtering."""
    query = db.query(Task).options(
        joinedload(Task.risk),
        joinedload(Task.asset),
        joinedload(Task.assigned_to),
        joinedload(Task.created_by),
        joinedload(Task.approved_by),
        selectinload(Task.comments),
        selectinload(Task.evidence)
    )
    
    if search:
        query = query.filter(
            (Task.title.contains(search)) |
            (Task.description.contains(search))
        )
    
    if status:
        query = query.filter(Task.status == status)
    
    if priority:
        query = query.filter(Task.priority == priority)
    
    if task_type:
        query = query.filter(Task.task_type == task_type)
    
    if assigned_to_id:
        query = query.filter(Task.assigned_to_id == assigned_to_id)
    
    if risk_id:
        query = query.filter(Task.risk_id == risk_id)
    
    # Get total count for pagination
    total = query.filter(Task.is_active == True).count()
    tasks = query.filter(Task.is_active == True).offset(skip).limit(limit).all()
    
    # Return paginated response structure expected by frontend
    return {
        "items": [TaskResponse.model_validate(task) for task in tasks],
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/my-tasks", response_model=List[TaskResponse])
async def get_my_tasks(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get tasks assigned to current user."""
    query = db.query(Task).options(
        joinedload(Task.risk),
        joinedload(Task.asset),
        joinedload(Task.assigned_to),
        joinedload(Task.created_by),
        joinedload(Task.approved_by),
        selectinload(Task.comments),
        selectinload(Task.evidence)
    ).filter(Task.assigned_to_id == current_user.id, Task.is_active == True)
    
    if status:
        query = query.filter(Task.status == status)
    
    tasks = query.order_by(Task.due_date.asc().nullslast()).all()
    return tasks


@router.get("/summary", response_model=TaskSummary)
async def get_tasks_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get task summary statistics."""
    total_tasks = db.query(func.count(Task.id)).filter(Task.is_active == True).scalar()
    
    # Count by status
    by_status = {}
    status_counts = db.query(
        Task.status,
        func.count(Task.id).label('count')
    ).filter(Task.is_active == True).group_by(Task.status).all()
    
    for item in status_counts:
        by_status[item.status] = item.count
    
    # Count by priority
    by_priority = {}
    priority_counts = db.query(
        Task.priority,
        func.count(Task.id).label('count')
    ).filter(Task.is_active == True).group_by(Task.priority).all()
    
    for item in priority_counts:
        by_priority[item.priority] = item.count
    
    # Overdue count
    overdue_count = db.query(func.count(Task.id)).filter(
        Task.is_active == True,
        Task.due_date < datetime.utcnow(),
        Task.status.in_(["open", "in_progress"])
    ).scalar()
    
    # My open tasks
    my_open_tasks = db.query(func.count(Task.id)).filter(
        Task.assigned_to_id == current_user.id,
        Task.is_active == True,
        Task.status.in_(["open", "in_progress"])
    ).scalar()
    
    # Awaiting review count
    awaiting_review_count = db.query(func.count(Task.id)).filter(
        Task.is_active == True,
        Task.status == "awaiting_review"
    ).scalar()
    
    return TaskSummary(
        total_tasks=total_tasks,
        by_status=by_status,
        by_priority=by_priority,
        overdue_count=overdue_count,
        my_open_tasks=my_open_tasks,
        awaiting_review_count=awaiting_review_count
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get task by ID."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new task."""
    task_data = task.model_dump()
    task_data["created_by_id"] = current_user.id
    
    # Convert Pydantic enum values (lowercase) to database enum values (uppercase)
    if "task_type" in task_data and task_data["task_type"]:
        # Extract the string value from enum object and convert to uppercase
        task_data["task_type"] = str(task_data["task_type"].value).upper()
    if "priority" in task_data and task_data["priority"]:
        # Extract the string value from enum object and convert to uppercase
        task_data["priority"] = str(task_data["priority"].value).upper()
    if "status" in task_data and task_data["status"]:
        # Extract the string value from enum object and convert to uppercase
        task_data["status"] = str(task_data["status"].value).upper()
    
    db_task = Task(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="create",
        entity_type="task",
        entity_id=db_task.id,
        user_id=current_user.id,
        action="Task created",
        description=f"Task created: {db_task.title}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return db_task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Store old values for audit
    old_values = {
        "title": task.title,
        "status": task.status,
        "priority": task.priority,
        "progress_percentage": task.progress_percentage
    }
    
    # Update task fields
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Handle status changes
    if "status" in update_data:
        new_status = update_data["status"]
        
        # If marking as completed, set completion date and 100% progress
        if new_status == "completed" and task.status != "completed":
            update_data["completed_date"] = datetime.utcnow()
            update_data["progress_percentage"] = 100
        
        # If moving to awaiting review, require approval
        elif new_status == "awaiting_review":
            update_data["requires_approval"] = True
            update_data["approval_status"] = "pending"
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="update",
        entity_type="task",
        entity_id=task.id,
        user_id=current_user.id,
        action="Task updated",
        description=f"Task updated: {task.title}",
        old_values=old_values,
        new_values=update_data,
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return task


@router.post("/{task_id}/approve")
async def approve_task(
    task_id: int,
    approval_comments: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Approve a task that is awaiting review."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.status != "awaiting_review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not awaiting review"
        )
    
    task.approval_status = "approved"
    task.approved_by_id = current_user.id
    task.approved_at = datetime.utcnow()
    task.approval_comments = approval_comments
    task.status = "completed"
    task.completed_date = datetime.utcnow()
    task.progress_percentage = 100
    
    db.commit()
    
    # Log audit event
    audit_log = AuditLog(
        event_type="approve",
        entity_type="task",
        entity_id=task.id,
        user_id=current_user.id,
        action="Task approved",
        description=f"Task approved: {task.title}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Task approved successfully"}


@router.post("/{task_id}/reject")
async def reject_task(
    task_id: int,
    rejection_comments: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reject a task that is awaiting review."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.status != "awaiting_review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not awaiting review"
        )
    
    if not rejection_comments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection comments are required"
        )
    
    task.approval_status = "rejected"
    task.approved_by_id = current_user.id
    task.approved_at = datetime.utcnow()
    task.approval_comments = rejection_comments
    task.status = "in_progress"  # Send back to in progress
    
    db.commit()
    
    # Log audit event
    audit_log = AuditLog(
        event_type="reject",
        entity_type="task",
        entity_id=task.id,
        user_id=current_user.id,
        action="Task rejected",
        description=f"Task rejected: {task.title}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Task rejected and sent back for revision"}


# Task Comments
@router.get("/{task_id}/comments", response_model=List[TaskCommentResponse])
async def get_task_comments(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comments for a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    comments = db.query(TaskComment).filter(
        TaskComment.task_id == task_id
    ).order_by(TaskComment.created_at.asc()).all()
    
    return comments


@router.post("/{task_id}/comments", response_model=TaskCommentResponse)
async def create_task_comment(
    task_id: int,
    comment: TaskCommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new comment for a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    comment_data = comment.model_dump()
    comment_data["task_id"] = task_id
    comment_data["user_id"] = current_user.id
    
    db_comment = TaskComment(**comment_data)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment


# Task Evidence
@router.get("/{task_id}/evidence", response_model=List[TaskEvidenceResponse])
async def get_task_evidence(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get evidence linked to a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    evidence = db.query(TaskEvidence).filter(TaskEvidence.task_id == task_id).all()
    return evidence


@router.post("/{task_id}/evidence", response_model=TaskEvidenceResponse)
async def link_task_evidence(
    task_id: int,
    evidence: TaskEvidenceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Link evidence to a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    evidence_data = evidence.model_dump()
    evidence_data["task_id"] = task_id
    
    db_evidence = TaskEvidence(**evidence_data)
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    
    return db_evidence