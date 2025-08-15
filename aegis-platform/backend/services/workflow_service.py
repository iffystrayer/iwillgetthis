from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from models.workflow import (
    Workflow, WorkflowStep, WorkflowInstance, WorkflowStepInstance,
    WorkflowAction, WorkflowTemplate, WorkflowRole,
    WorkflowType, WorkflowStatus, WorkflowInstanceStatus, WorkflowStepStatus, ActionType
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
    WorkflowSummary, BulkWorkflowAction, BulkWorkflowActionResult
)


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db

    # Workflow CRUD operations
    async def create_workflow(self, workflow_data: WorkflowCreate, user_id: int) -> WorkflowResponse:
        """Create a new workflow"""
        # Convert tags and custom_fields to JSON strings
        tags_json = json.dumps(workflow_data.tags) if workflow_data.tags else None
        custom_fields_json = json.dumps(workflow_data.custom_fields) if workflow_data.custom_fields else None
        trigger_conditions_json = json.dumps(workflow_data.trigger_conditions) if workflow_data.trigger_conditions else None
        
        workflow = Workflow(
            name=workflow_data.name,
            description=workflow_data.description,
            workflow_type=workflow_data.workflow_type,
            category=workflow_data.category,
            version=workflow_data.version,
            status=workflow_data.status,
            is_default=workflow_data.is_default,
            trigger_conditions=trigger_conditions_json,
            auto_trigger=workflow_data.auto_trigger,
            default_timeout_hours=workflow_data.default_timeout_hours,
            escalation_enabled=workflow_data.escalation_enabled,
            escalation_timeout_hours=workflow_data.escalation_timeout_hours,
            notification_template_id=workflow_data.notification_template_id,
            notify_on_start=workflow_data.notify_on_start,
            notify_on_completion=workflow_data.notify_on_completion,
            tags=tags_json,
            custom_fields=custom_fields_json,
            created_by_id=user_id
        )
        
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        
        # Create workflow steps if provided
        for step_data in workflow_data.steps:
            await self.create_workflow_step(
                WorkflowStepCreate(**step_data.model_dump(), workflow_id=workflow.id)
            )
        
        return await self.get_workflow(workflow.id)

    async def get_workflow(self, workflow_id: int) -> Optional[WorkflowResponse]:
        """Get a workflow by ID"""
        workflow = self.db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.is_active == True
        ).first()
        
        if not workflow:
            return None
        
        return self._convert_workflow_to_response(workflow)

    async def list_workflows(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        workflow_type: Optional[WorkflowType] = None,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[WorkflowResponse]:
        """List workflows with optional filtering"""
        query = self.db.query(Workflow).filter(Workflow.is_active == True)
        
        if workflow_type:
            query = query.filter(Workflow.workflow_type == workflow_type)
        
        if status:
            query = query.filter(Workflow.status == status)
        
        if category:
            query = query.filter(Workflow.category == category)
        
        workflows = query.order_by(desc(Workflow.created_at)).offset(skip).limit(limit).all()
        
        return [self._convert_workflow_to_response(workflow) for workflow in workflows]

    async def update_workflow(self, workflow_id: int, workflow_update: WorkflowUpdate) -> Optional[WorkflowResponse]:
        """Update a workflow"""
        workflow = self.db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.is_active == True
        ).first()
        
        if not workflow:
            return None
        
        update_data = workflow_update.model_dump(exclude_unset=True)
        
        # Handle JSON fields
        if 'tags' in update_data and update_data['tags'] is not None:
            update_data['tags'] = json.dumps(update_data['tags'])
        
        if 'custom_fields' in update_data and update_data['custom_fields'] is not None:
            update_data['custom_fields'] = json.dumps(update_data['custom_fields'])
        
        if 'trigger_conditions' in update_data and update_data['trigger_conditions'] is not None:
            update_data['trigger_conditions'] = json.dumps(update_data['trigger_conditions'])
        
        for field, value in update_data.items():
            setattr(workflow, field, value)
        
        self.db.commit()
        self.db.refresh(workflow)
        
        return self._convert_workflow_to_response(workflow)

    async def delete_workflow(self, workflow_id: int) -> bool:
        """Delete a workflow (soft delete)"""
        workflow = self.db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.is_active == True
        ).first()
        
        if not workflow:
            return False
        
        workflow.is_active = False
        self.db.commit()
        
        return True

    # Workflow Step operations
    async def create_workflow_step(self, step_data: WorkflowStepCreate) -> WorkflowStepResponse:
        """Create a workflow step"""
        # Convert JSON fields
        auto_assign_rule_json = json.dumps(step_data.auto_assign_rule) if step_data.auto_assign_rule else None
        condition_expression_json = json.dumps(step_data.condition_expression) if step_data.condition_expression else None
        allowed_actions_json = json.dumps([action.value for action in step_data.allowed_actions]) if step_data.allowed_actions else None
        on_approve_action_json = json.dumps(step_data.on_approve_action) if step_data.on_approve_action else None
        on_reject_action_json = json.dumps(step_data.on_reject_action) if step_data.on_reject_action else None
        custom_fields_json = json.dumps(step_data.custom_fields) if step_data.custom_fields else None
        
        step = WorkflowStep(
            workflow_id=step_data.workflow_id,
            name=step_data.name,
            description=step_data.description,
            step_type=step_data.step_type,
            step_order=step_data.step_order,
            is_required=step_data.is_required,
            can_skip=step_data.can_skip,
            allow_parallel=step_data.allow_parallel,
            assignee_type=step_data.assignee_type,
            assignee_id=step_data.assignee_id,
            auto_assign_rule=auto_assign_rule_json,
            approval_required=step_data.approval_required,
            min_approvals=step_data.min_approvals,
            unanimous_required=step_data.unanimous_required,
            timeout_hours=step_data.timeout_hours,
            reminder_hours=step_data.reminder_hours,
            escalation_assignee_id=step_data.escalation_assignee_id,
            condition_expression=condition_expression_json,
            allowed_actions=allowed_actions_json,
            on_approve_action=on_approve_action_json,
            on_reject_action=on_reject_action_json,
            custom_fields=custom_fields_json
        )
        
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        
        return self._convert_workflow_step_to_response(step)

    async def list_workflow_steps(self, workflow_id: int) -> List[WorkflowStepResponse]:
        """List all steps for a workflow"""
        steps = self.db.query(WorkflowStep).filter(
            WorkflowStep.workflow_id == workflow_id
        ).order_by(asc(WorkflowStep.step_order)).all()
        
        return [self._convert_workflow_step_to_response(step) for step in steps]

    async def update_workflow_step(self, step_id: int, step_update: WorkflowStepUpdate) -> Optional[WorkflowStepResponse]:
        """Update a workflow step"""
        step = self.db.query(WorkflowStep).filter(WorkflowStep.id == step_id).first()
        
        if not step:
            return None
        
        update_data = step_update.model_dump(exclude_unset=True)
        
        # Handle JSON fields
        if 'auto_assign_rule' in update_data and update_data['auto_assign_rule'] is not None:
            update_data['auto_assign_rule'] = json.dumps(update_data['auto_assign_rule'])
        
        if 'condition_expression' in update_data and update_data['condition_expression'] is not None:
            update_data['condition_expression'] = json.dumps(update_data['condition_expression'])
        
        if 'allowed_actions' in update_data and update_data['allowed_actions'] is not None:
            update_data['allowed_actions'] = json.dumps([action.value for action in update_data['allowed_actions']])
        
        if 'on_approve_action' in update_data and update_data['on_approve_action'] is not None:
            update_data['on_approve_action'] = json.dumps(update_data['on_approve_action'])
        
        if 'on_reject_action' in update_data and update_data['on_reject_action'] is not None:
            update_data['on_reject_action'] = json.dumps(update_data['on_reject_action'])
        
        if 'custom_fields' in update_data and update_data['custom_fields'] is not None:
            update_data['custom_fields'] = json.dumps(update_data['custom_fields'])
        
        for field, value in update_data.items():
            setattr(step, field, value)
        
        self.db.commit()
        self.db.refresh(step)
        
        return self._convert_workflow_step_to_response(step)

    async def delete_workflow_step(self, step_id: int) -> bool:
        """Delete a workflow step"""
        step = self.db.query(WorkflowStep).filter(WorkflowStep.id == step_id).first()
        
        if not step:
            return False
        
        self.db.delete(step)
        self.db.commit()
        
        return True

    # Workflow Instance operations
    async def create_workflow_instance(self, instance_data: WorkflowInstanceCreate, user_id: int) -> WorkflowInstanceResponse:
        """Create a new workflow instance"""
        # Get the workflow to validate it exists
        workflow = self.db.query(Workflow).filter(
            Workflow.id == instance_data.workflow_id,
            Workflow.is_active == True
        ).first()
        
        if not workflow:
            raise ValueError("Workflow not found")
        
        # Convert JSON fields
        context_data_json = json.dumps(instance_data.context_data) if instance_data.context_data else None
        tags_json = json.dumps(instance_data.tags) if instance_data.tags else None
        custom_fields_json = json.dumps(instance_data.custom_fields) if instance_data.custom_fields else None
        
        instance = WorkflowInstance(
            workflow_id=instance_data.workflow_id,
            name=instance_data.name,
            description=instance_data.description,
            entity_type=instance_data.entity_type,
            entity_id=instance_data.entity_id,
            context_data=context_data_json,
            priority=instance_data.priority,
            tags=tags_json,
            custom_fields=custom_fields_json,
            initiated_by_id=user_id,
            status=WorkflowInstanceStatus.INITIATED
        )
        
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        
        # Initialize workflow step instances
        await self._initialize_workflow_steps(instance.id)
        
        return await self.get_workflow_instance(instance.id)

    async def trigger_workflow(self, trigger_request: WorkflowTriggerRequest, user_id: int) -> WorkflowInstanceResponse:
        """Trigger a workflow for an entity"""
        instance_data = WorkflowInstanceCreate(
            workflow_id=trigger_request.workflow_id,
            entity_type=trigger_request.entity_type,
            entity_id=trigger_request.entity_id,
            context_data=trigger_request.context_data,
            priority=trigger_request.priority,
            custom_fields=trigger_request.custom_fields
        )
        
        return await self.create_workflow_instance(instance_data, user_id)

    async def trigger_workflow_by_type(
        self, 
        workflow_type: WorkflowType, 
        trigger_request: WorkflowTriggerRequest, 
        user_id: int
    ) -> WorkflowInstanceResponse:
        """Trigger a workflow by type (finds default workflow)"""
        # Find default workflow for this type
        workflow = self.db.query(Workflow).filter(
            Workflow.workflow_type == workflow_type,
            Workflow.is_default == True,
            Workflow.status == WorkflowStatus.ACTIVE,
            Workflow.is_active == True
        ).first()
        
        if not workflow:
            raise ValueError(f"No default workflow found for type {workflow_type}")
        
        trigger_request.workflow_id = workflow.id
        return await self.trigger_workflow(trigger_request, user_id)

    async def get_workflow_instance(self, instance_id: int) -> Optional[WorkflowInstanceResponse]:
        """Get a workflow instance by ID"""
        instance = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id,
            WorkflowInstance.is_active == True
        ).first()
        
        if not instance:
            return None
        
        return self._convert_workflow_instance_to_response(instance)

    async def list_workflow_instances(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[WorkflowInstanceStatus] = None,
        entity_type: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[WorkflowInstanceResponse]:
        """List workflow instances with optional filtering"""
        query = self.db.query(WorkflowInstance).filter(WorkflowInstance.is_active == True)
        
        if status:
            query = query.filter(WorkflowInstance.status == status)
        
        if entity_type:
            query = query.filter(WorkflowInstance.entity_type == entity_type)
        
        if user_id:
            query = query.filter(
                or_(
                    WorkflowInstance.current_assignee_id == user_id,
                    WorkflowInstance.initiated_by_id == user_id
                )
            )
        
        instances = query.order_by(desc(WorkflowInstance.created_at)).offset(skip).limit(limit).all()
        
        return [self._convert_workflow_instance_to_response(instance) for instance in instances]

    async def update_workflow_instance(self, instance_id: int, instance_update: WorkflowInstanceUpdate) -> Optional[WorkflowInstanceResponse]:
        """Update a workflow instance"""
        instance = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id,
            WorkflowInstance.is_active == True
        ).first()
        
        if not instance:
            return None
        
        update_data = instance_update.model_dump(exclude_unset=True)
        
        # Handle JSON fields
        if 'context_data' in update_data and update_data['context_data'] is not None:
            update_data['context_data'] = json.dumps(update_data['context_data'])
        
        if 'tags' in update_data and update_data['tags'] is not None:
            update_data['tags'] = json.dumps(update_data['tags'])
        
        if 'custom_fields' in update_data and update_data['custom_fields'] is not None:
            update_data['custom_fields'] = json.dumps(update_data['custom_fields'])
        
        for field, value in update_data.items():
            setattr(instance, field, value)
        
        self.db.commit()
        self.db.refresh(instance)
        
        return self._convert_workflow_instance_to_response(instance)

    # Workflow execution
    async def execute_workflow_action(
        self, 
        instance_id: int, 
        execution_request: WorkflowExecutionRequest, 
        user_id: int
    ) -> WorkflowActionResponse:
        """Execute an action on a workflow instance"""
        instance = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id,
            WorkflowInstance.is_active == True
        ).first()
        
        if not instance:
            raise ValueError("Workflow instance not found")
        
        # Get current step instance
        current_step_instance = self.db.query(WorkflowStepInstance).filter(
            WorkflowStepInstance.workflow_instance_id == instance_id,
            WorkflowStepInstance.status == WorkflowStepStatus.IN_PROGRESS
        ).first()
        
        if not current_step_instance:
            raise ValueError("No active step found for this workflow instance")
        
        # Record the action
        action = WorkflowAction(
            workflow_instance_id=instance_id,
            step_instance_id=current_step_instance.id,
            action_type=execution_request.action_type,
            action_description=f"User {user_id} performed {execution_request.action_type.value}",
            performed_by_id=user_id,
            comment=execution_request.comment,
            attachments=json.dumps(execution_request.attachments) if execution_request.attachments else None,
            result_status="success"
        )
        
        self.db.add(action)
        
        # Process the action
        if execution_request.action_type == ActionType.APPROVE:
            await self._process_approval(instance, current_step_instance)
        elif execution_request.action_type == ActionType.REJECT:
            await self._process_rejection(instance, current_step_instance, execution_request.comment)
        elif execution_request.action_type == ActionType.REASSIGN:
            await self._process_reassignment(current_step_instance, execution_request.reassign_to_id)
        elif execution_request.action_type == ActionType.ESCALATE:
            await self._process_escalation(current_step_instance, execution_request.escalate_to_id)
        
        self.db.commit()
        self.db.refresh(action)
        
        return self._convert_workflow_action_to_response(action)

    async def list_workflow_actions(self, instance_id: int) -> List[WorkflowActionResponse]:
        """List all actions for a workflow instance"""
        actions = self.db.query(WorkflowAction).filter(
            WorkflowAction.workflow_instance_id == instance_id
        ).order_by(desc(WorkflowAction.performed_at)).all()
        
        return [self._convert_workflow_action_to_response(action) for action in actions]

    async def list_workflow_step_instances(self, instance_id: int) -> List[WorkflowStepInstanceResponse]:
        """List all step instances for a workflow instance"""
        step_instances = self.db.query(WorkflowStepInstance).filter(
            WorkflowStepInstance.workflow_instance_id == instance_id
        ).order_by(asc(WorkflowStepInstance.step_order)).all()
        
        return [self._convert_workflow_step_instance_to_response(step_instance) for step_instance in step_instances]

    # Dashboard and summary methods
    async def get_workflow_summary(self) -> WorkflowSummary:
        """Get workflow summary statistics"""
        total_workflows = self.db.query(Workflow).filter(Workflow.is_active == True).count()
        active_workflows = self.db.query(Workflow).filter(
            Workflow.is_active == True,
            Workflow.status == WorkflowStatus.ACTIVE
        ).count()
        
        pending_instances = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.is_active == True,
            WorkflowInstance.status.in_([
                WorkflowInstanceStatus.IN_PROGRESS,
                WorkflowInstanceStatus.PENDING_APPROVAL
            ])
        ).count()
        
        # Calculate overdue instances (due_date < now)
        now = datetime.utcnow()
        overdue_instances = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.is_active == True,
            WorkflowInstance.due_date < now,
            WorkflowInstance.status.in_([
                WorkflowInstanceStatus.IN_PROGRESS,
                WorkflowInstanceStatus.PENDING_APPROVAL
            ])
        ).count()
        
        # Calculate completed today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        completed_today = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.completed_at >= today_start,
            WorkflowInstance.status.in_([
                WorkflowInstanceStatus.COMPLETED,
                WorkflowInstanceStatus.APPROVED
            ])
        ).count()
        
        # Calculate approval rate (approved / (approved + rejected))
        approved_count = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.status == WorkflowInstanceStatus.APPROVED
        ).count()
        
        rejected_count = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.status == WorkflowInstanceStatus.REJECTED
        ).count()
        
        approval_rate = approved_count / (approved_count + rejected_count) if (approved_count + rejected_count) > 0 else 0.0
        
        # Calculate average completion time
        completed_instances = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.completed_at.isnot(None),
            WorkflowInstance.initiated_at.isnot(None)
        ).all()
        
        if completed_instances:
            total_hours = sum([
                (instance.completed_at - instance.initiated_at).total_seconds() / 3600
                for instance in completed_instances
            ])
            average_completion_time_hours = total_hours / len(completed_instances)
        else:
            average_completion_time_hours = 0.0
        
        return WorkflowSummary(
            total_workflows=total_workflows,
            active_workflows=active_workflows,
            pending_instances=pending_instances,
            overdue_instances=overdue_instances,
            completed_today=completed_today,
            approval_rate=approval_rate,
            average_completion_time_hours=average_completion_time_hours
        )

    async def get_user_pending_tasks(self, user_id: int) -> List[WorkflowStepInstanceResponse]:
        """Get workflow tasks assigned to a user"""
        step_instances = self.db.query(WorkflowStepInstance).filter(
            WorkflowStepInstance.assigned_to_id == user_id,
            WorkflowStepInstance.status.in_([
                WorkflowStepStatus.PENDING,
                WorkflowStepStatus.IN_PROGRESS
            ])
        ).order_by(asc(WorkflowStepInstance.due_date)).all()
        
        return [self._convert_workflow_step_instance_to_response(step_instance) for step_instance in step_instances]

    async def get_overdue_workflows(self) -> List[WorkflowInstanceResponse]:
        """Get overdue workflow instances"""
        now = datetime.utcnow()
        instances = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.is_active == True,
            WorkflowInstance.due_date < now,
            WorkflowInstance.status.in_([
                WorkflowInstanceStatus.IN_PROGRESS,
                WorkflowInstanceStatus.PENDING_APPROVAL
            ])
        ).order_by(asc(WorkflowInstance.due_date)).all()
        
        return [self._convert_workflow_instance_to_response(instance) for instance in instances]

    # Template operations
    async def create_workflow_template(self, template_data: WorkflowTemplateCreate, user_id: int) -> WorkflowTemplateResponse:
        """Create a workflow template"""
        template = WorkflowTemplate(
            name=template_data.name,
            description=template_data.description,
            category=template_data.category,
            workflow_type=template_data.workflow_type,
            template_data=json.dumps(template_data.template_data),
            version=template_data.version,
            is_system_template=template_data.is_system_template,
            is_public=template_data.is_public,
            tags=json.dumps(template_data.tags) if template_data.tags else None,
            created_by_id=user_id
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        return self._convert_workflow_template_to_response(template)

    async def list_workflow_templates(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        workflow_type: Optional[WorkflowType] = None
    ) -> List[WorkflowTemplateResponse]:
        """List workflow templates"""
        query = self.db.query(WorkflowTemplate).filter(WorkflowTemplate.is_active == True)
        
        if category:
            query = query.filter(WorkflowTemplate.category == category)
        
        if workflow_type:
            query = query.filter(WorkflowTemplate.workflow_type == workflow_type)
        
        templates = query.order_by(desc(WorkflowTemplate.created_at)).offset(skip).limit(limit).all()
        
        return [self._convert_workflow_template_to_response(template) for template in templates]

    async def get_workflow_template(self, template_id: int) -> Optional[WorkflowTemplateResponse]:
        """Get a workflow template by ID"""
        template = self.db.query(WorkflowTemplate).filter(
            WorkflowTemplate.id == template_id,
            WorkflowTemplate.is_active == True
        ).first()
        
        if not template:
            return None
        
        return self._convert_workflow_template_to_response(template)

    async def apply_workflow_template(self, template_id: int, user_id: int) -> Optional[WorkflowResponse]:
        """Create a workflow from a template"""
        template = self.db.query(WorkflowTemplate).filter(
            WorkflowTemplate.id == template_id,
            WorkflowTemplate.is_active == True
        ).first()
        
        if not template:
            return None
        
        # Parse template data and create workflow
        template_data = json.loads(template.template_data)
        workflow_data = WorkflowCreate(**template_data)
        
        # Update usage count
        template.usage_count += 1
        self.db.commit()
        
        return await self.create_workflow(workflow_data, user_id)

    # Role operations
    async def create_workflow_role(self, role_data: WorkflowRoleCreate) -> WorkflowRoleResponse:
        """Create a workflow role"""
        role = WorkflowRole(
            name=role_data.name,
            description=role_data.description,
            is_system_role=role_data.is_system_role,
            permissions=json.dumps(role_data.permissions) if role_data.permissions else None,
            members=json.dumps(role_data.members) if role_data.members else None
        )
        
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        
        return self._convert_workflow_role_to_response(role)

    async def list_workflow_roles(self) -> List[WorkflowRoleResponse]:
        """List all workflow roles"""
        roles = self.db.query(WorkflowRole).filter(WorkflowRole.is_active == True).all()
        
        return [self._convert_workflow_role_to_response(role) for role in roles]

    # Bulk operations
    async def execute_bulk_workflow_action(
        self, 
        bulk_action: BulkWorkflowAction, 
        user_id: int
    ) -> BulkWorkflowActionResult:
        """Execute bulk action on multiple workflow instances"""
        results = []
        success_count = 0
        failure_count = 0
        
        for instance_id in bulk_action.workflow_instance_ids:
            try:
                execution_request = WorkflowExecutionRequest(
                    action_type=bulk_action.action_type,
                    comment=bulk_action.comment
                )
                
                action_result = await self.execute_workflow_action(
                    instance_id, execution_request, user_id
                )
                
                results.append({
                    "instance_id": instance_id,
                    "status": "success",
                    "action_id": action_result.id
                })
                success_count += 1
                
            except Exception as e:
                results.append({
                    "instance_id": instance_id,
                    "status": "failure",
                    "error": str(e)
                })
                failure_count += 1
        
        return BulkWorkflowActionResult(
            success_count=success_count,
            failure_count=failure_count,
            results=results
        )

    # Private helper methods
    async def _initialize_workflow_steps(self, instance_id: int):
        """Initialize step instances for a workflow instance"""
        instance = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id
        ).first()
        
        if not instance:
            return
        
        workflow_steps = self.db.query(WorkflowStep).filter(
            WorkflowStep.workflow_id == instance.workflow_id
        ).order_by(asc(WorkflowStep.step_order)).all()
        
        for step in workflow_steps:
            step_instance = WorkflowStepInstance(
                workflow_instance_id=instance_id,
                workflow_step_id=step.id,
                step_order=step.step_order,
                status=WorkflowStepStatus.PENDING if step.step_order == 1 else WorkflowStepStatus.PENDING
            )
            
            # Set due date based on timeout
            if step.timeout_hours:
                step_instance.due_date = datetime.utcnow() + timedelta(hours=step.timeout_hours)
            
            self.db.add(step_instance)
        
        # Start the first step
        if workflow_steps:
            first_step_instance = self.db.query(WorkflowStepInstance).filter(
                WorkflowStepInstance.workflow_instance_id == instance_id,
                WorkflowStepInstance.step_order == 1
            ).first()
            
            if first_step_instance:
                first_step_instance.status = WorkflowStepStatus.IN_PROGRESS
                first_step_instance.started_at = datetime.utcnow()
                instance.status = WorkflowInstanceStatus.IN_PROGRESS
                instance.started_at = datetime.utcnow()
                instance.current_step_id = first_step_instance.workflow_step_id
        
        self.db.commit()

    async def _process_approval(self, instance: WorkflowInstance, step_instance: WorkflowStepInstance):
        """Process an approval action"""
        step_instance.status = WorkflowStepStatus.COMPLETED
        step_instance.completed_at = datetime.utcnow()
        step_instance.outcome = "approved"
        
        # Move to next step or complete workflow
        await self._advance_workflow(instance)

    async def _process_rejection(self, instance: WorkflowInstance, step_instance: WorkflowStepInstance, comment: Optional[str]):
        """Process a rejection action"""
        step_instance.status = WorkflowStepStatus.REJECTED
        step_instance.completed_at = datetime.utcnow()
        step_instance.outcome = "rejected"
        step_instance.outcome_reason = comment
        
        # End the workflow
        instance.status = WorkflowInstanceStatus.REJECTED
        instance.completed_at = datetime.utcnow()
        instance.final_outcome = "rejected"
        instance.outcome_reason = comment

    async def _process_reassignment(self, step_instance: WorkflowStepInstance, assignee_id: Optional[int]):
        """Process a reassignment action"""
        if assignee_id:
            step_instance.assigned_to_id = assignee_id
            step_instance.assigned_at = datetime.utcnow()

    async def _process_escalation(self, step_instance: WorkflowStepInstance, escalate_to_id: Optional[int]):
        """Process an escalation action"""
        step_instance.escalated_at = datetime.utcnow()
        if escalate_to_id:
            step_instance.escalated_to_id = escalate_to_id
            step_instance.assigned_to_id = escalate_to_id

    async def _advance_workflow(self, instance: WorkflowInstance):
        """Advance workflow to next step or complete it"""
        current_step_order = self.db.query(WorkflowStepInstance.step_order).filter(
            WorkflowStepInstance.workflow_instance_id == instance.id,
            WorkflowStepInstance.status == WorkflowStepStatus.COMPLETED
        ).order_by(desc(WorkflowStepInstance.step_order)).first()
        
        if current_step_order:
            next_step_order = current_step_order[0] + 1
            next_step_instance = self.db.query(WorkflowStepInstance).filter(
                WorkflowStepInstance.workflow_instance_id == instance.id,
                WorkflowStepInstance.step_order == next_step_order
            ).first()
            
            if next_step_instance:
                # Start next step
                next_step_instance.status = WorkflowStepStatus.IN_PROGRESS
                next_step_instance.started_at = datetime.utcnow()
                instance.current_step_id = next_step_instance.workflow_step_id
            else:
                # No more steps, complete workflow
                instance.status = WorkflowInstanceStatus.COMPLETED
                instance.completed_at = datetime.utcnow()
                instance.final_outcome = "approved"

    # Conversion helper methods
    def _convert_workflow_to_response(self, workflow: Workflow) -> WorkflowResponse:
        """Convert Workflow model to WorkflowResponse"""
        return WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            workflow_type=workflow.workflow_type,
            category=workflow.category,
            version=workflow.version,
            status=workflow.status,
            is_default=workflow.is_default,
            trigger_conditions=json.loads(workflow.trigger_conditions) if workflow.trigger_conditions else None,
            auto_trigger=workflow.auto_trigger,
            default_timeout_hours=workflow.default_timeout_hours,
            escalation_enabled=workflow.escalation_enabled,
            escalation_timeout_hours=workflow.escalation_timeout_hours,
            notification_template_id=workflow.notification_template_id,
            notify_on_start=workflow.notify_on_start,
            notify_on_completion=workflow.notify_on_completion,
            tags=json.loads(workflow.tags) if workflow.tags else None,
            custom_fields=json.loads(workflow.custom_fields) if workflow.custom_fields else None,
            created_by_id=workflow.created_by_id,
            is_active=workflow.is_active,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            steps=[]  # Steps loaded separately if needed
        )

    def _convert_workflow_step_to_response(self, step: WorkflowStep) -> WorkflowStepResponse:
        """Convert WorkflowStep model to WorkflowStepResponse"""
        return WorkflowStepResponse(
            id=step.id,
            workflow_id=step.workflow_id,
            name=step.name,
            description=step.description,
            step_type=step.step_type,
            step_order=step.step_order,
            is_required=step.is_required,
            can_skip=step.can_skip,
            allow_parallel=step.allow_parallel,
            assignee_type=step.assignee_type,
            assignee_id=step.assignee_id,
            auto_assign_rule=json.loads(step.auto_assign_rule) if step.auto_assign_rule else None,
            approval_required=step.approval_required,
            min_approvals=step.min_approvals,
            unanimous_required=step.unanimous_required,
            timeout_hours=step.timeout_hours,
            reminder_hours=step.reminder_hours,
            escalation_assignee_id=step.escalation_assignee_id,
            condition_expression=json.loads(step.condition_expression) if step.condition_expression else None,
            allowed_actions=json.loads(step.allowed_actions) if step.allowed_actions else None,
            on_approve_action=json.loads(step.on_approve_action) if step.on_approve_action else None,
            on_reject_action=json.loads(step.on_reject_action) if step.on_reject_action else None,
            custom_fields=json.loads(step.custom_fields) if step.custom_fields else None,
            created_at=step.created_at,
            updated_at=step.updated_at
        )

    def _convert_workflow_instance_to_response(self, instance: WorkflowInstance) -> WorkflowInstanceResponse:
        """Convert WorkflowInstance model to WorkflowInstanceResponse"""
        return WorkflowInstanceResponse(
            id=instance.id,
            workflow_id=instance.workflow_id,
            name=instance.name,
            description=instance.description,
            entity_type=instance.entity_type,
            entity_id=instance.entity_id,
            status=instance.status,
            current_step_id=instance.current_step_id,
            context_data=json.loads(instance.context_data) if instance.context_data else None,
            initiated_by_id=instance.initiated_by_id,
            current_assignee_id=instance.current_assignee_id,
            initiated_at=instance.initiated_at,
            started_at=instance.started_at,
            completed_at=instance.completed_at,
            due_date=instance.due_date,
            final_outcome=instance.final_outcome,
            outcome_reason=instance.outcome_reason,
            priority=instance.priority,
            escalation_level=instance.escalation_level,
            last_escalated_at=instance.last_escalated_at,
            tags=json.loads(instance.tags) if instance.tags else None,
            custom_fields=json.loads(instance.custom_fields) if instance.custom_fields else None,
            is_active=instance.is_active,
            created_at=instance.created_at,
            updated_at=instance.updated_at
        )

    def _convert_workflow_step_instance_to_response(self, step_instance: WorkflowStepInstance) -> WorkflowStepInstanceResponse:
        """Convert WorkflowStepInstance model to WorkflowStepInstanceResponse"""
        return WorkflowStepInstanceResponse(
            id=step_instance.id,
            workflow_instance_id=step_instance.workflow_instance_id,
            workflow_step_id=step_instance.workflow_step_id,
            status=step_instance.status,
            step_order=step_instance.step_order,
            assigned_to_id=step_instance.assigned_to_id,
            assigned_at=step_instance.assigned_at,
            started_at=step_instance.started_at,
            completed_at=step_instance.completed_at,
            due_date=step_instance.due_date,
            outcome=step_instance.outcome,
            outcome_reason=step_instance.outcome_reason,
            reminder_sent_at=step_instance.reminder_sent_at,
            escalated_at=step_instance.escalated_at,
            escalated_to_id=step_instance.escalated_to_id,
            step_data=json.loads(step_instance.step_data) if step_instance.step_data else None,
            created_at=step_instance.created_at,
            updated_at=step_instance.updated_at
        )

    def _convert_workflow_action_to_response(self, action: WorkflowAction) -> WorkflowActionResponse:
        """Convert WorkflowAction model to WorkflowActionResponse"""
        return WorkflowActionResponse(
            id=action.id,
            workflow_instance_id=action.workflow_instance_id,
            step_instance_id=action.step_instance_id,
            action_type=action.action_type,
            action_description=action.action_description,
            performed_by_id=action.performed_by_id,
            on_behalf_of_id=action.on_behalf_of_id,
            comment=action.comment,
            attachments=json.loads(action.attachments) if action.attachments else None,
            result_status=action.result_status,
            result_data=json.loads(action.result_data) if action.result_data else None,
            performed_at=action.performed_at
        )

    def _convert_workflow_template_to_response(self, template: WorkflowTemplate) -> WorkflowTemplateResponse:
        """Convert WorkflowTemplate model to WorkflowTemplateResponse"""
        return WorkflowTemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            category=template.category,
            workflow_type=template.workflow_type,
            template_data=json.loads(template.template_data),
            version=template.version,
            is_system_template=template.is_system_template,
            is_public=template.is_public,
            usage_count=template.usage_count,
            tags=json.loads(template.tags) if template.tags else None,
            created_by_id=template.created_by_id,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at
        )

    def _convert_workflow_role_to_response(self, role: WorkflowRole) -> WorkflowRoleResponse:
        """Convert WorkflowRole model to WorkflowRoleResponse"""
        return WorkflowRoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system_role=role.is_system_role,
            permissions=json.loads(role.permissions) if role.permissions else None,
            members=json.loads(role.members) if role.members else None,
            is_active=role.is_active,
            created_at=role.created_at,
            updated_at=role.updated_at
        )