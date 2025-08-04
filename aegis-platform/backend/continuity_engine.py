import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from models.continuity import (
    BusinessContinuityPlan, BusinessImpactAnalysis, DisasterRecoveryProcedure,
    ContinuityTest, PlanActivation, ProcedureExecution, ContinuityMetrics,
    ContinuityResource, ContinuityPlanStatus, BusinessImpactLevel, 
    RecoveryPriority, ContinuityTestStatus, ActivationStatus
)

logger = logging.getLogger(__name__)

class ContinuityEngine:
    """
    Comprehensive Business Continuity and Disaster Recovery Engine
    
    This engine manages business continuity planning, disaster recovery procedures,
    business impact analysis, RTO/RPO tracking, testing, and plan activation.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.notification_queue = []
        
    async def create_continuity_plan(
        self,
        name: str,
        description: str,
        scope: str,
        business_units: List[str],
        geographic_scope: List[str],
        objectives: str,
        created_by: str,
        **kwargs
    ) -> BusinessContinuityPlan:
        """Create a new business continuity plan"""
        
        plan = BusinessContinuityPlan(
            name=name,
            description=description,
            scope=scope,
            business_units=business_units,
            geographic_scope=geographic_scope,
            objectives=objectives,
            created_by=created_by,
            **kwargs
        )
        
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        logger.info(f"Created business continuity plan: {plan.plan_id}")
        return plan
    
    async def conduct_business_impact_analysis(
        self,
        continuity_plan_id: int,
        business_process: str,
        process_owner: str,
        department: str,
        impact_level: BusinessImpactLevel,
        rto_hours: float,
        rpo_hours: float,
        financial_impact_hourly: Optional[float] = None,
        **kwargs
    ) -> BusinessImpactAnalysis:
        """Conduct business impact analysis for a process"""
        
        # Calculate impact metrics
        impact_assessment = self._assess_business_impact(
            impact_level, financial_impact_hourly, rto_hours, rpo_hours
        )
        
        bia = BusinessImpactAnalysis(
            continuity_plan_id=continuity_plan_id,
            business_process=business_process,
            process_owner=process_owner,
            department=department,
            impact_level=impact_level,
            rto_hours=rto_hours,
            rpo_hours=rpo_hours,
            financial_impact_hourly=financial_impact_hourly,
            **impact_assessment,
            **kwargs
        )
        
        self.db.add(bia)
        self.db.commit()
        self.db.refresh(bia)
        
        logger.info(f"Completed BIA for process: {business_process}")
        return bia
    
    def _assess_business_impact(
        self, 
        impact_level: BusinessImpactLevel, 
        financial_impact_hourly: Optional[float],
        rto_hours: float,
        rpo_hours: float
    ) -> Dict[str, Any]:
        """Assess business impact based on level and metrics"""
        
        assessment = {}
        
        # Calculate daily financial impact
        if financial_impact_hourly:
            assessment["financial_impact_daily"] = financial_impact_hourly * 24
        
        # Determine minimum service level based on impact
        service_levels = {
            BusinessImpactLevel.MINIMAL: 90.0,
            BusinessImpactLevel.MODERATE: 75.0,
            BusinessImpactLevel.SIGNIFICANT: 50.0,
            BusinessImpactLevel.SEVERE: 25.0,
            BusinessImpactLevel.CATASTROPHIC: 10.0
        }
        assessment["minimum_service_level"] = service_levels.get(impact_level, 50.0)
        
        # Generate impact descriptions
        if impact_level in [BusinessImpactLevel.SEVERE, BusinessImpactLevel.CATASTROPHIC]:
            assessment["operational_impact"] = "Critical operations severely disrupted"
            assessment["regulatory_impact"] = "Potential regulatory violations and reporting issues"
            assessment["reputational_impact"] = "Significant damage to reputation and customer trust"
        elif impact_level == BusinessImpactLevel.SIGNIFICANT:
            assessment["operational_impact"] = "Major operational disruption"
            assessment["regulatory_impact"] = "Possible compliance issues"
            assessment["reputational_impact"] = "Moderate reputational damage"
        else:
            assessment["operational_impact"] = "Limited operational impact"
            assessment["regulatory_impact"] = "Minimal regulatory concerns"
            assessment["reputational_impact"] = "Minor reputational impact"
        
        return assessment
    
    async def create_recovery_procedure(
        self,
        continuity_plan_id: int,
        name: str,
        description: str,
        category: str,
        priority: RecoveryPriority,
        target_rto_hours: float,
        target_rpo_hours: float,
        recovery_steps: List[Dict[str, Any]],
        **kwargs
    ) -> DisasterRecoveryProcedure:
        """Create a disaster recovery procedure"""
        
        procedure = DisasterRecoveryProcedure(
            continuity_plan_id=continuity_plan_id,
            name=name,
            description=description,
            category=category,
            priority=priority,
            target_rto_hours=target_rto_hours,
            target_rpo_hours=target_rpo_hours,
            recovery_steps=recovery_steps,
            **kwargs
        )
        
        self.db.add(procedure)
        self.db.commit()
        self.db.refresh(procedure)
        
        logger.info(f"Created recovery procedure: {procedure.procedure_id}")
        return procedure
    
    async def schedule_continuity_test(
        self,
        continuity_plan_id: int,
        name: str,
        description: str,
        test_type: str,
        scheduled_date: datetime,
        objectives: List[str],
        scenarios: List[Dict[str, Any]],
        participants: List[str],
        **kwargs
    ) -> ContinuityTest:
        """Schedule a business continuity test"""
        
        test = ContinuityTest(
            continuity_plan_id=continuity_plan_id,
            name=name,
            description=description,
            test_type=test_type,
            scheduled_date=scheduled_date,
            objectives=objectives,
            scenarios=scenarios,
            participants=participants,
            status=ContinuityTestStatus.PLANNED,
            **kwargs
        )
        
        self.db.add(test)
        self.db.commit()
        self.db.refresh(test)
        
        logger.info(f"Scheduled continuity test: {test.test_id}")
        return test
    
    async def execute_continuity_test(
        self,
        test_id: int,
        coordinator: str
    ) -> Dict[str, Any]:
        """Execute a scheduled continuity test"""
        
        test = self.db.query(ContinuityTest).filter(ContinuityTest.id == test_id).first()
        if not test:
            raise ValueError(f"Test with ID {test_id} not found")
        
        # Update test status
        test.status = ContinuityTestStatus.IN_PROGRESS
        test.actual_start_time = datetime.utcnow()
        test.test_coordinator = coordinator
        
        try:
            # Execute test scenarios
            results = await self._execute_test_scenarios(test)
            
            # Evaluate results
            evaluation = self._evaluate_test_results(test, results)
            
            # Update test with results
            test.status = ContinuityTestStatus.COMPLETED
            test.actual_end_time = datetime.utcnow()
            test.overall_success = evaluation["overall_success"]
            test.rto_achieved = evaluation["rto_achieved"]
            test.rpo_achieved = evaluation["rpo_achieved"]
            test.issues_identified = evaluation["issues_identified"]
            test.recommendations = evaluation["recommendations"]
            
            self.db.commit()
            
            logger.info(f"Completed continuity test: {test.test_id}")
            return evaluation
            
        except Exception as e:
            test.status = ContinuityTestStatus.FAILED
            test.actual_end_time = datetime.utcnow()
            self.db.commit()
            logger.error(f"Test execution failed: {str(e)}")
            raise
    
    async def _execute_test_scenarios(self, test: ContinuityTest) -> Dict[str, Any]:
        """Execute individual test scenarios"""
        
        results = {
            "scenario_results": [],
            "rto_measurements": [],
            "rpo_measurements": [],
            "issues": []
        }
        
        for scenario in test.scenarios:
            scenario_result = await self._execute_scenario(scenario, test)
            results["scenario_results"].append(scenario_result)
            
            if scenario_result.get("rto_measured"):
                results["rto_measurements"].append(scenario_result["rto_measured"])
            if scenario_result.get("rpo_measured"):
                results["rpo_measurements"].append(scenario_result["rpo_measured"])
            if scenario_result.get("issues"):
                results["issues"].extend(scenario_result["issues"])
        
        return results
    
    async def _execute_scenario(self, scenario: Dict[str, Any], test: ContinuityTest) -> Dict[str, Any]:
        """Execute a single test scenario"""
        
        scenario_result = {
            "scenario_name": scenario.get("name"),
            "start_time": datetime.utcnow(),
            "success": False,
            "issues": []
        }
        
        try:
            # Simulate scenario execution based on type
            if scenario.get("type") == "tabletop":
                result = await self._execute_tabletop_scenario(scenario, test)
            elif scenario.get("type") == "walkthrough":
                result = await self._execute_walkthrough_scenario(scenario, test)
            elif scenario.get("type") == "simulation":
                result = await self._execute_simulation_scenario(scenario, test)
            elif scenario.get("type") == "full_test":
                result = await self._execute_full_test_scenario(scenario, test)
            else:
                result = {"success": False, "issues": ["Unknown scenario type"]}
            
            scenario_result.update(result)
            scenario_result["end_time"] = datetime.utcnow()
            
        except Exception as e:
            scenario_result["issues"].append(f"Scenario execution error: {str(e)}")
            scenario_result["end_time"] = datetime.utcnow()
        
        return scenario_result
    
    async def _execute_tabletop_scenario(self, scenario: Dict[str, Any], test: ContinuityTest) -> Dict[str, Any]:
        """Execute tabletop exercise scenario"""
        
        # Tabletop exercises are discussion-based
        return {
            "success": True,
            "type": "discussion",
            "participants_engaged": len(test.participants),
            "decisions_made": scenario.get("expected_decisions", []),
            "rto_measured": None,  # Not measured in tabletop
            "rpo_measured": None
        }
    
    async def _execute_walkthrough_scenario(self, scenario: Dict[str, Any], test: ContinuityTest) -> Dict[str, Any]:
        """Execute walkthrough scenario"""
        
        # Walkthrough involves reviewing procedures step by step
        steps_reviewed = scenario.get("steps", [])
        issues_found = []
        
        for step in steps_reviewed:
            if not step.get("clear", True):
                issues_found.append(f"Step unclear: {step.get('description', 'Unknown step')}")
        
        return {
            "success": len(issues_found) == 0,
            "type": "walkthrough",
            "steps_reviewed": len(steps_reviewed),
            "issues": issues_found,
            "rto_measured": None,
            "rpo_measured": None
        }
    
    async def _execute_simulation_scenario(self, scenario: Dict[str, Any], test: ContinuityTest) -> Dict[str, Any]:
        """Execute simulation scenario"""
        
        start_time = datetime.utcnow()
        
        # Simulate recovery procedures
        await asyncio.sleep(1)  # Simulate time for execution
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds() / 3600  # Convert to hours
        
        target_rto = scenario.get("target_rto_hours", 4.0)
        rto_achieved = duration <= target_rto
        
        return {
            "success": rto_achieved,
            "type": "simulation",
            "rto_measured": duration,
            "rpo_measured": scenario.get("simulated_rpo", 0.5),
            "issues": [] if rto_achieved else [f"RTO exceeded: {duration:.2f}h vs {target_rto}h target"]
        }
    
    async def _execute_full_test_scenario(self, scenario: Dict[str, Any], test: ContinuityTest) -> Dict[str, Any]:
        """Execute full disaster recovery test"""
        
        start_time = datetime.utcnow()
        
        # Full test would involve actual system recovery
        # This is a simplified simulation
        await asyncio.sleep(2)  # Simulate longer execution time
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds() / 3600
        
        target_rto = scenario.get("target_rto_hours", 2.0)
        target_rpo = scenario.get("target_rpo_hours", 1.0)
        
        # Simulate measurements
        rto_achieved = duration <= target_rto
        rpo_measured = scenario.get("actual_data_loss", 0.25)
        rpo_achieved = rpo_measured <= target_rpo
        
        issues = []
        if not rto_achieved:
            issues.append(f"RTO not met: {duration:.2f}h vs {target_rto}h")
        if not rpo_achieved:
            issues.append(f"RPO not met: {rpo_measured:.2f}h vs {target_rpo}h")
        
        return {
            "success": rto_achieved and rpo_achieved,
            "type": "full_test",
            "rto_measured": duration,
            "rpo_measured": rpo_measured,
            "issues": issues
        }
    
    def _evaluate_test_results(self, test: ContinuityTest, results: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate overall test results"""
        
        scenario_results = results["scenario_results"]
        successful_scenarios = [r for r in scenario_results if r.get("success", False)]
        
        overall_success = len(successful_scenarios) == len(scenario_results)
        
        # Calculate average RTO/RPO if measured
        rto_measurements = results["rto_measurements"]
        rpo_measurements = results["rpo_measurements"]
        
        avg_rto = sum(rto_measurements) / len(rto_measurements) if rto_measurements else None
        avg_rpo = sum(rpo_measurements) / len(rpo_measurements) if rpo_measurements else None
        
        # Compile recommendations
        recommendations = []
        if not overall_success:
            recommendations.append("Review and update failed procedures")
        if avg_rto and avg_rto > 4:  # Example threshold
            recommendations.append("Improve recovery time procedures")
        if avg_rpo and avg_rpo > 1:  # Example threshold
            recommendations.append("Enhance backup and replication strategies")
        
        return {
            "overall_success": overall_success,
            "success_rate": len(successful_scenarios) / len(scenario_results),
            "rto_achieved": avg_rto,
            "rpo_achieved": avg_rpo,
            "issues_identified": results["issues"],
            "recommendations": recommendations,
            "scenarios_tested": len(scenario_results),
            "scenarios_passed": len(successful_scenarios)
        }
    
    async def activate_continuity_plan(
        self,
        continuity_plan_id: int,
        trigger_event: str,
        activation_level: ActivationStatus,
        activated_by: str,
        activation_reason: str,
        affected_business_units: List[str],
        **kwargs
    ) -> PlanActivation:
        """Activate a business continuity plan"""
        
        activation = PlanActivation(
            continuity_plan_id=continuity_plan_id,
            trigger_event=trigger_event,
            activation_level=activation_level,
            activated_by=activated_by,
            activation_reason=activation_reason,
            activation_time=datetime.utcnow(),
            affected_business_units=affected_business_units,
            current_status="Activated",
            **kwargs
        )
        
        self.db.add(activation)
        self.db.commit()
        self.db.refresh(activation)
        
        # Trigger notification workflows
        await self._notify_stakeholders(activation)
        
        # Auto-execute critical procedures if configured
        await self._execute_critical_procedures(activation)
        
        logger.info(f"Activated continuity plan: {activation.activation_id}")
        return activation
    
    async def _notify_stakeholders(self, activation: PlanActivation):
        """Notify relevant stakeholders of plan activation"""
        
        notification = {
            "type": "plan_activation",
            "activation_id": activation.activation_id,
            "trigger_event": activation.trigger_event,
            "activation_level": activation.activation_level.value,
            "timestamp": activation.activation_time,
            "affected_units": activation.affected_business_units
        }
        
        self.notification_queue.append(notification)
        logger.info(f"Stakeholder notification queued for activation: {activation.activation_id}")
    
    async def _execute_critical_procedures(self, activation: PlanActivation):
        """Auto-execute critical recovery procedures"""
        
        # Get critical procedures for this plan
        critical_procedures = self.db.query(DisasterRecoveryProcedure).filter(
            DisasterRecoveryProcedure.continuity_plan_id == activation.continuity_plan_id,
            DisasterRecoveryProcedure.priority == RecoveryPriority.CRITICAL,
            DisasterRecoveryProcedure.automated == True
        ).all()
        
        executed_procedures = []
        
        for procedure in critical_procedures:
            try:
                execution = await self.execute_recovery_procedure(
                    procedure.id, activation.id, "Automated Execution"
                )
                executed_procedures.append(procedure.procedure_id)
                logger.info(f"Auto-executed procedure: {procedure.procedure_id}")
            except Exception as e:
                logger.error(f"Failed to auto-execute procedure {procedure.procedure_id}: {str(e)}")
        
        # Update activation with executed procedures
        activation.activated_procedures = executed_procedures
        self.db.commit()
    
    async def execute_recovery_procedure(
        self,
        procedure_id: int,
        activation_id: Optional[int],
        executed_by: str,
        execution_context: str = "Manual"
    ) -> ProcedureExecution:
        """Execute a disaster recovery procedure"""
        
        procedure = self.db.query(DisasterRecoveryProcedure).filter(
            DisasterRecoveryProcedure.id == procedure_id
        ).first()
        
        if not procedure:
            raise ValueError(f"Procedure with ID {procedure_id} not found")
        
        execution = ProcedureExecution(
            procedure_id=procedure_id,
            activation_id=activation_id,
            executed_by=executed_by,
            execution_context=execution_context,
            start_time=datetime.utcnow(),
            status="Started"
        )
        
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        
        try:
            # Execute procedure steps
            result = await self._execute_procedure_steps(procedure, execution)
            
            # Update execution with results
            execution.end_time = datetime.utcnow()
            execution.duration_minutes = (execution.end_time - execution.start_time).total_seconds() / 60
            execution.status = "Completed" if result["success"] else "Failed"
            execution.successful = result["success"]
            execution.rto_met = result.get("rto_met", False)
            execution.rpo_met = result.get("rpo_met", False)
            execution.actual_recovery_time = result.get("recovery_time")
            execution.actual_data_loss = result.get("data_loss")
            execution.issues_encountered = result.get("issues", [])
            execution.execution_log = result.get("execution_log", [])
            
            self.db.commit()
            
            logger.info(f"Executed procedure: {procedure.procedure_id}")
            return execution
            
        except Exception as e:
            execution.end_time = datetime.utcnow()
            execution.status = "Failed"
            execution.successful = False
            execution.issues_encountered = [str(e)]
            self.db.commit()
            logger.error(f"Procedure execution failed: {str(e)}")
            raise
    
    async def _execute_procedure_steps(
        self, 
        procedure: DisasterRecoveryProcedure, 
        execution: ProcedureExecution
    ) -> Dict[str, Any]:
        """Execute individual steps of a recovery procedure"""
        
        start_time = datetime.utcnow()
        execution_log = []
        issues = []
        
        try:
            # Execute preparation steps
            if procedure.preparation_steps:
                prep_result = await self._execute_steps(
                    procedure.preparation_steps, "preparation", execution_log
                )
                if not prep_result["success"]:
                    issues.extend(prep_result["issues"])
            
            # Execute recovery steps
            if procedure.recovery_steps:
                recovery_result = await self._execute_steps(
                    procedure.recovery_steps, "recovery", execution_log
                )
                if not recovery_result["success"]:
                    issues.extend(recovery_result["issues"])
            
            # Execute validation steps
            if procedure.validation_steps:
                validation_result = await self._execute_steps(
                    procedure.validation_steps, "validation", execution_log
                )
                if not validation_result["success"]:
                    issues.extend(validation_result["issues"])
            
            end_time = datetime.utcnow()
            recovery_time = (end_time - start_time).total_seconds() / 3600  # Hours
            
            # Check RTO/RPO compliance
            rto_met = recovery_time <= procedure.target_rto_hours
            rpo_met = True  # Simplified - would need actual data loss measurement
            
            success = len(issues) == 0 and rto_met
            
            return {
                "success": success,
                "recovery_time": recovery_time,
                "data_loss": 0.0,  # Simplified
                "rto_met": rto_met,
                "rpo_met": rpo_met,
                "issues": issues,
                "execution_log": execution_log
            }
            
        except Exception as e:
            issues.append(f"Execution error: {str(e)}")
            return {
                "success": False,
                "issues": issues,
                "execution_log": execution_log
            }
    
    async def _execute_steps(
        self, 
        steps: List[Dict[str, Any]], 
        step_type: str, 
        execution_log: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a list of procedure steps"""
        
        issues = []
        
        for i, step in enumerate(steps):
            step_start = datetime.utcnow()
            step_log = {
                "step_number": i + 1,
                "step_type": step_type,
                "description": step.get("description", ""),
                "start_time": step_start,
                "success": False
            }
            
            try:
                # Simulate step execution
                if step.get("automated", False):
                    # Execute automation script
                    await self._execute_automation_script(step)
                else:
                    # Manual step - just simulate
                    await asyncio.sleep(0.1)  # Simulate execution time
                
                step_log["success"] = True
                step_log["end_time"] = datetime.utcnow()
                
            except Exception as e:
                step_log["success"] = False
                step_log["error"] = str(e)
                step_log["end_time"] = datetime.utcnow()
                issues.append(f"Step {i+1} failed: {str(e)}")
            
            execution_log.append(step_log)
        
        return {
            "success": len(issues) == 0,
            "issues": issues
        }
    
    async def _execute_automation_script(self, step: Dict[str, Any]):
        """Execute automation script for a step"""
        
        script_path = step.get("script_path")
        script_params = step.get("parameters", {})
        
        # This would execute actual automation scripts
        # For now, just simulate
        await asyncio.sleep(0.5)
        
        logger.info(f"Executed automation script: {script_path}")
    
    async def track_rto_rpo_metrics(self) -> Dict[str, Any]:
        """Track and update RTO/RPO metrics across all plans"""
        
        metrics_summary = {
            "plans_tracked": 0,
            "average_rto": 0.0,
            "average_rpo": 0.0,
            "compliance_rate": 0.0,
            "critical_issues": []
        }
        
        # Get all active continuity plans
        active_plans = self.db.query(BusinessContinuityPlan).filter(
            BusinessContinuityPlan.status == ContinuityPlanStatus.ACTIVE
        ).all()
        
        total_rto = 0.0
        total_rpo = 0.0
        compliant_procedures = 0
        total_procedures = 0
        
        for plan in active_plans:
            plan_metrics = await self._calculate_plan_metrics(plan)
            
            total_rto += plan_metrics["average_rto"]
            total_rpo += plan_metrics["average_rpo"]
            compliant_procedures += plan_metrics["compliant_procedures"]
            total_procedures += plan_metrics["total_procedures"]
            
            # Check for critical issues
            if plan_metrics["critical_rto_violations"]:
                metrics_summary["critical_issues"].extend(plan_metrics["critical_rto_violations"])
            if plan_metrics["critical_rpo_violations"]:
                metrics_summary["critical_issues"].extend(plan_metrics["critical_rpo_violations"])
        
        if len(active_plans) > 0:
            metrics_summary["plans_tracked"] = len(active_plans)
            metrics_summary["average_rto"] = total_rto / len(active_plans)
            metrics_summary["average_rpo"] = total_rpo / len(active_plans)
        
        if total_procedures > 0:
            metrics_summary["compliance_rate"] = (compliant_procedures / total_procedures) * 100
        
        # Update metrics in database
        await self._update_continuity_metrics(metrics_summary)
        
        return metrics_summary
    
    async def _calculate_plan_metrics(self, plan: BusinessContinuityPlan) -> Dict[str, Any]:
        """Calculate metrics for a specific continuity plan"""
        
        # Get all procedures for this plan
        procedures = self.db.query(DisasterRecoveryProcedure).filter(
            DisasterRecoveryProcedure.continuity_plan_id == plan.id
        ).all()
        
        if not procedures:
            return {
                "average_rto": 0.0,
                "average_rpo": 0.0,
                "compliant_procedures": 0,
                "total_procedures": 0,
                "critical_rto_violations": [],
                "critical_rpo_violations": []
            }
        
        total_rto = sum(p.target_rto_hours for p in procedures)
        total_rpo = sum(p.target_rpo_hours for p in procedures)
        
        avg_rto = total_rto / len(procedures)
        avg_rpo = total_rpo / len(procedures)
        
        # Check compliance based on recent test results or executions
        compliant_procedures = 0
        critical_rto_violations = []
        critical_rpo_violations = []
        
        for procedure in procedures:
            # Check recent executions
            recent_executions = self.db.query(ProcedureExecution).filter(
                ProcedureExecution.procedure_id == procedure.id,
                ProcedureExecution.start_time >= datetime.utcnow() - timedelta(days=90)
            ).order_by(ProcedureExecution.start_time.desc()).limit(3).all()
            
            if recent_executions:
                # Use latest execution results
                latest = recent_executions[0]
                if latest.rto_met and latest.rpo_met:
                    compliant_procedures += 1
                else:
                    if not latest.rto_met:
                        critical_rto_violations.append({
                            "procedure": procedure.name,
                            "target_rto": procedure.target_rto_hours,
                            "actual_rto": latest.actual_recovery_time
                        })
                    if not latest.rpo_met:
                        critical_rpo_violations.append({
                            "procedure": procedure.name,
                            "target_rpo": procedure.target_rpo_hours,
                            "actual_rpo": latest.actual_data_loss
                        })
            else:
                # No recent executions - consider as potentially non-compliant
                if procedure.priority == RecoveryPriority.CRITICAL:
                    critical_rto_violations.append({
                        "procedure": procedure.name,
                        "issue": "No recent test executions",
                        "target_rto": procedure.target_rto_hours
                    })
        
        return {
            "average_rto": avg_rto,
            "average_rpo": avg_rpo,
            "compliant_procedures": compliant_procedures,
            "total_procedures": len(procedures),
            "critical_rto_violations": critical_rto_violations,
            "critical_rpo_violations": critical_rpo_violations
        }
    
    async def _update_continuity_metrics(self, metrics_summary: Dict[str, Any]):
        """Update continuity metrics in the database"""
        
        # Update or create RTO metric
        rto_metric = self.db.query(ContinuityMetrics).filter(
            ContinuityMetrics.metric_name == "Average RTO",
            ContinuityMetrics.metric_type == "RTO"
        ).first()
        
        if not rto_metric:
            rto_metric = ContinuityMetrics(
                metric_name="Average RTO",
                metric_type="RTO",
                category="Overall",
                target_name="All Business Processes",
                target_value=4.0,  # 4 hour target
                tolerance_threshold=1.0
            )
            self.db.add(rto_metric)
        
        rto_metric.current_value = metrics_summary["average_rto"]
        rto_metric.measurement_date = datetime.utcnow()
        rto_metric.status = "Meeting Target" if metrics_summary["average_rto"] <= 4.0 else "Below Target"
        
        # Update or create RPO metric
        rpo_metric = self.db.query(ContinuityMetrics).filter(
            ContinuityMetrics.metric_name == "Average RPO",
            ContinuityMetrics.metric_type == "RPO"
        ).first()
        
        if not rpo_metric:
            rpo_metric = ContinuityMetrics(
                metric_name="Average RPO",
                metric_type="RPO",
                category="Overall",
                target_name="All Business Processes",
                target_value=1.0,  # 1 hour target
                tolerance_threshold=0.5
            )
            self.db.add(rpo_metric)
        
        rpo_metric.current_value = metrics_summary["average_rpo"]
        rpo_metric.measurement_date = datetime.utcnow()
        rpo_metric.status = "Meeting Target" if metrics_summary["average_rpo"] <= 1.0 else "Below Target"
        
        # Update compliance rate metric
        compliance_metric = self.db.query(ContinuityMetrics).filter(
            ContinuityMetrics.metric_name == "Compliance Rate",
            ContinuityMetrics.metric_type == "Test Success Rate"
        ).first()
        
        if not compliance_metric:
            compliance_metric = ContinuityMetrics(
                metric_name="Compliance Rate",
                metric_type="Test Success Rate",
                category="Overall",
                target_name="All Recovery Procedures",
                target_value=95.0,  # 95% target
                tolerance_threshold=5.0
            )
            self.db.add(compliance_metric)
        
        compliance_metric.current_value = metrics_summary["compliance_rate"]
        compliance_metric.measurement_date = datetime.utcnow()
        compliance_metric.status = "Meeting Target" if metrics_summary["compliance_rate"] >= 95.0 else "Below Target"
        
        self.db.commit()
        logger.info("Updated continuity metrics in database")
    
    async def get_continuity_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive continuity management dashboard data"""
        
        dashboard = {
            "summary": {},
            "active_plans": [],
            "recent_tests": [],
            "active_activations": [],
            "metrics": {},
            "upcoming_tests": [],
            "overdue_reviews": []
        }
        
        # Summary statistics
        total_plans = self.db.query(BusinessContinuityPlan).count()
        active_plans = self.db.query(BusinessContinuityPlan).filter(
            BusinessContinuityPlan.status == ContinuityPlanStatus.ACTIVE
        ).count()
        
        total_procedures = self.db.query(DisasterRecoveryProcedure).count()
        recent_tests = self.db.query(ContinuityTest).filter(
            ContinuityTest.actual_start_time >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        dashboard["summary"] = {
            "total_plans": total_plans,
            "active_plans": active_plans,
            "total_procedures": total_procedures,
            "recent_tests": recent_tests
        }
        
        # Get active plan details
        active_plan_list = self.db.query(BusinessContinuityPlan).filter(
            BusinessContinuityPlan.status == ContinuityPlanStatus.ACTIVE
        ).limit(10).all()
        
        dashboard["active_plans"] = [
            {
                "plan_id": plan.plan_id,
                "name": plan.name,
                "business_units": plan.business_units,
                "last_tested": None,  # Would need to calculate
                "next_review": plan.next_review_date
            }
            for plan in active_plan_list
        ]
        
        # Recent test results
        recent_test_list = self.db.query(ContinuityTest).filter(
            ContinuityTest.status == ContinuityTestStatus.COMPLETED,
            ContinuityTest.actual_end_time >= datetime.utcnow() - timedelta(days=30)
        ).order_by(ContinuityTest.actual_end_time.desc()).limit(5).all()
        
        dashboard["recent_tests"] = [
            {
                "test_id": test.test_id,
                "name": test.name,
                "test_type": test.test_type,
                "date": test.actual_end_time,
                "success": test.overall_success,
                "rto_achieved": test.rto_achieved
            }
            for test in recent_test_list
        ]
        
        # Active plan activations
        active_activations = self.db.query(PlanActivation).filter(
            PlanActivation.deactivation_time.is_(None),
            PlanActivation.activation_time >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        dashboard["active_activations"] = [
            {
                "activation_id": activation.activation_id,
                "trigger_event": activation.trigger_event,
                "activation_level": activation.activation_level.value,
                "activation_time": activation.activation_time,
                "affected_units": activation.affected_business_units
            }
            for activation in active_activations
        ]
        
        # Current metrics
        metrics = await self.track_rto_rpo_metrics()
        dashboard["metrics"] = metrics
        
        return dashboard