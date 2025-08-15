from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from auth import get_current_user
from models.user import User
from models.workflow import (
    Workflow, WorkflowStep, WorkflowInstance, WorkflowStepInstance, 
    WorkflowAction, WorkflowTemplate, WorkflowRole
)
from schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowStepCreate, WorkflowStepUpdate, WorkflowStepResponse,
    WorkflowInstanceCreate, WorkflowInstanceUpdate, WorkflowInstanceResponse,
    WorkflowStepInstanceCreate, WorkflowStepInstanceUpdate, WorkflowStepInstanceResponse,
    WorkflowActionCreate, WorkflowActionResponse,
    WorkflowTemplateCreate, WorkflowTemplateUpdate, WorkflowTemplateResponse,
    WorkflowRoleCreate, WorkflowRoleUpdate, WorkflowRoleResponse,
    WorkflowExecutionRequest, WorkflowTriggerRequest,
    WorkflowSummary, WorkflowDashboard, BulkWorkflowAction, BulkWorkflowActionResult,
    WorkflowType, WorkflowInstanceStatus, ActionType
)
from services.workflow_service import WorkflowService
import json
from datetime import datetime


router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


# Workflow CRUD operations
@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow template"""
    workflow_service = WorkflowService(db)
    return await workflow_service.create_workflow(workflow, current_user.id)


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    workflow_type: Optional[WorkflowType] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all workflows with optional filtering"""
    workflow_service = WorkflowService(db)
    return await workflow_service.list_workflows(
        skip=skip, limit=limit, workflow_type=workflow_type,
        status=status, category=category
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific workflow by ID"""
    workflow_service = WorkflowService(db)
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_update: WorkflowUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a workflow"""
    workflow_service = WorkflowService(db)
    workflow = await workflow_service.update_workflow(workflow_id, workflow_update)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workflow"""
    workflow_service = WorkflowService(db)
    success = await workflow_service.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return {"message": "Workflow deleted successfully"}


# Workflow Step operations
@router.post("/{workflow_id}/steps", response_model=WorkflowStepResponse)
async def create_workflow_step(
    workflow_id: int,
    step: WorkflowStepCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a step to a workflow"""
    step.workflow_id = workflow_id
    workflow_service = WorkflowService(db)
    return await workflow_service.create_workflow_step(step)


@router.get("/{workflow_id}/steps", response_model=List[WorkflowStepResponse])
async def list_workflow_steps(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all steps for a workflow"""
    workflow_service = WorkflowService(db)
    return await workflow_service.list_workflow_steps(workflow_id)


@router.put("/steps/{step_id}", response_model=WorkflowStepResponse)
async def update_workflow_step(
    step_id: int,
    step_update: WorkflowStepUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a workflow step"""
    workflow_service = WorkflowService(db)
    step = await workflow_service.update_workflow_step(step_id, step_update)
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow step not found"
        )
    return step


@router.delete("/steps/{step_id}")
async def delete_workflow_step(
    step_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workflow step"""
    workflow_service = WorkflowService(db)
    success = await workflow_service.delete_workflow_step(step_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow step not found"
        )
    return {"message": "Workflow step deleted successfully"}


# Workflow Instance operations
@router.post("/instances", response_model=WorkflowInstanceResponse)
async def create_workflow_instance(
    instance: WorkflowInstanceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow instance"""
    workflow_service = WorkflowService(db)
    return await workflow_service.create_workflow_instance(instance, current_user.id)


@router.post("/trigger", response_model=WorkflowInstanceResponse)
async def trigger_workflow(
    trigger_request: WorkflowTriggerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger a workflow for an entity"""
    workflow_service = WorkflowService(db)
    return await workflow_service.trigger_workflow(trigger_request, current_user.id)


@router.get("/instances", response_model=List[WorkflowInstanceResponse])
async def list_workflow_instances(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[WorkflowInstanceStatus] = None,
    entity_type: Optional[str] = None,
    assigned_to_me: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List workflow instances with optional filtering"""
    workflow_service = WorkflowService(db)
    return await workflow_service.list_workflow_instances(
        skip=skip, limit=limit, status=status, entity_type=entity_type,
        user_id=current_user.id if assigned_to_me else None
    )


@router.get("/instances/{instance_id}", response_model=WorkflowInstanceResponse)
async def get_workflow_instance(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific workflow instance"""
    workflow_service = WorkflowService(db)
    instance = await workflow_service.get_workflow_instance(instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow instance not found"
        )
    return instance


@router.put("/instances/{instance_id}", response_model=WorkflowInstanceResponse)
async def update_workflow_instance(
    instance_id: int,
    instance_update: WorkflowInstanceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a workflow instance"""
    workflow_service = WorkflowService(db)
    instance = await workflow_service.update_workflow_instance(instance_id, instance_update)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow instance not found"
        )
    return instance


# Workflow execution
@router.post("/instances/{instance_id}/execute", response_model=WorkflowActionResponse)
async def execute_workflow_action(
    instance_id: int,
    execution_request: WorkflowExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute an action on a workflow instance"""
    workflow_service = WorkflowService(db)
    return await workflow_service.execute_workflow_action(
        instance_id, execution_request, current_user.id
    )


@router.get("/instances/{instance_id}/actions", response_model=List[WorkflowActionResponse])
async def list_workflow_actions(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all actions for a workflow instance"""
    workflow_service = WorkflowService(db)
    return await workflow_service.list_workflow_actions(instance_id)


@router.get("/instances/{instance_id}/steps", response_model=List[WorkflowStepInstanceResponse])
async def list_workflow_step_instances(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all step instances for a workflow instance"""
    workflow_service = WorkflowService(db)
    return await workflow_service.list_workflow_step_instances(instance_id)


# Dashboard and summary
@router.get("/dashboard/summary", response_model=WorkflowSummary)
async def get_workflow_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workflow summary statistics"""
    workflow_service = WorkflowService(db)
    return await workflow_service.get_workflow_summary()


@router.get("/dashboard/my-tasks", response_model=List[WorkflowStepInstanceResponse])
async def get_my_workflow_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workflow tasks assigned to current user"""
    workflow_service = WorkflowService(db)
    return await workflow_service.get_user_pending_tasks(current_user.id)


@router.get("/dashboard/overdue", response_model=List[WorkflowInstanceResponse])
async def get_overdue_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overdue workflow instances"""
    workflow_service = WorkflowService(db)
    return await workflow_service.get_overdue_workflows()


# Workflow Templates
@router.post("/templates", response_model=WorkflowTemplateResponse)
async def create_workflow_template(
    template: WorkflowTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow template"""
    workflow_service = WorkflowService(db)
    return await workflow_service.create_workflow_template(template, current_user.id)


@router.get("/templates", response_model=List[WorkflowTemplateResponse])
async def list_workflow_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    workflow_type: Optional[WorkflowType] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List workflow templates"""
    workflow_service = WorkflowService(db)
    return await workflow_service.list_workflow_templates(
        skip=skip, limit=limit, category=category, workflow_type=workflow_type
    )


@router.get("/templates/{template_id}", response_model=WorkflowTemplateResponse)
async def get_workflow_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific workflow template"""
    workflow_service = WorkflowService(db)
    template = await workflow_service.get_workflow_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )
    return template


@router.post("/templates/{template_id}/apply", response_model=WorkflowResponse)
async def apply_workflow_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a workflow from a template"""
    workflow_service = WorkflowService(db)
    workflow = await workflow_service.apply_workflow_template(template_id, current_user.id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )
    return workflow


# Workflow Roles
@router.post("/roles", response_model=WorkflowRoleResponse)
async def create_workflow_role(
    role: WorkflowRoleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow role"""
    workflow_service = WorkflowService(db)
    return await workflow_service.create_workflow_role(role)


@router.get("/roles", response_model=List[WorkflowRoleResponse])
async def list_workflow_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all workflow roles"""
    workflow_service = WorkflowService(db)
    return await workflow_service.list_workflow_roles()


# Bulk operations
@router.post("/instances/bulk-action", response_model=BulkWorkflowActionResult)
async def bulk_workflow_action(
    bulk_action: BulkWorkflowAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute bulk action on multiple workflow instances"""
    workflow_service = WorkflowService(db)
    return await workflow_service.execute_bulk_workflow_action(bulk_action, current_user.id)


# Entity-specific workflow triggers
@router.post("/trigger/risk/{risk_id}")
async def trigger_risk_workflow(
    risk_id: int,
    workflow_type: WorkflowType = WorkflowType.RISK_APPROVAL,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger a workflow for a specific risk"""
    workflow_service = WorkflowService(db)
    trigger_request = WorkflowTriggerRequest(
        workflow_id=0,  # Will be resolved by service
        entity_type="risk",
        entity_id=risk_id
    )
    return await workflow_service.trigger_workflow_by_type(
        workflow_type, trigger_request, current_user.id
    )


@router.post("/trigger/task/{task_id}")
async def trigger_task_workflow(
    task_id: int,
    workflow_type: WorkflowType = WorkflowType.TASK_APPROVAL,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger a workflow for a specific task"""
    workflow_service = WorkflowService(db)
    trigger_request = WorkflowTriggerRequest(
        workflow_id=0,  # Will be resolved by service
        entity_type="task",
        entity_id=task_id
    )
    return await workflow_service.trigger_workflow_by_type(
        workflow_type, trigger_request, current_user.id
    )


@router.post("/trigger/assessment/{assessment_id}")
async def trigger_assessment_workflow(
    assessment_id: int,
    workflow_type: WorkflowType = WorkflowType.ASSESSMENT_APPROVAL,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger a workflow for a specific assessment"""
    workflow_service = WorkflowService(db)
    trigger_request = WorkflowTriggerRequest(
        workflow_id=0,  # Will be resolved by service
        entity_type="assessment",
        entity_id=assessment_id
    )
    return await workflow_service.trigger_workflow_by_type(
        workflow_type, trigger_request, current_user.id
    )