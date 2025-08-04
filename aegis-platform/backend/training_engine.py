import asyncio
import logging
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from models.training import (
    TrainingProgram, TrainingCourse, TrainingEnrollment, CourseEnrollment,
    AwarenessCampaign, PhishingSimulation, SimulationResult, CampaignInteraction,
    SecurityCompetency, CompetencyAssessment, AssessmentResult, UserCompetency,
    TrainingCertification, UserCertification, TrainingAnalytics,
    TrainingAssessment, AssessmentResponse,
    TrainingStatus, TrainingType, CampaignStatus, SimulationResult as SimResult,
    CompetencyLevel, AssessmentType
)

logger = logging.getLogger(__name__)

class TrainingEngine:
    """
    Comprehensive Security Awareness and Training Management Engine
    
    This engine manages training programs, phishing simulations, competency assessments,
    certification tracking, and training analytics for security awareness.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.notification_queue = []
        
    # ===================== Training Program Management =====================
    
    async def create_training_program(
        self,
        name: str,
        description: str,
        program_type: TrainingType,
        target_roles: List[str],
        learning_objectives: List[str],
        created_by: str,
        **kwargs
    ) -> TrainingProgram:
        """Create a new training program"""
        
        program = TrainingProgram(
            name=name,
            description=description,
            program_type=program_type,
            target_roles=target_roles,
            learning_objectives=learning_objectives,
            created_by=created_by,
            **kwargs
        )
        
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        
        # Auto-enroll users if configured
        if program.auto_enroll:
            await self._auto_enroll_users(program)
        
        logger.info(f"Created training program: {program.program_id}")
        return program
    
    async def enroll_user_in_program(
        self,
        program_id: int,
        user_id: str,
        user_email: str,
        assigned_by: str,
        due_date: Optional[datetime] = None,
        **kwargs
    ) -> TrainingEnrollment:
        """Enroll a user in a training program"""
        
        program = self.db.query(TrainingProgram).filter(TrainingProgram.id == program_id).first()
        if not program:
            raise ValueError(f"Training program with ID {program_id} not found")
        
        # Check for existing enrollment
        existing = self.db.query(TrainingEnrollment).filter(
            TrainingEnrollment.program_id == program_id,
            TrainingEnrollment.user_id == user_id
        ).first()
        
        if existing and existing.status not in [TrainingStatus.EXPIRED, TrainingStatus.FAILED]:
            logger.warning(f"User {user_id} already enrolled in program {program_id}")
            return existing
        
        # Calculate due date if not provided
        if not due_date and program.mandatory:
            due_date = datetime.utcnow() + timedelta(days=30)  # Default 30 days
        
        enrollment = TrainingEnrollment(
            program_id=program_id,
            user_id=user_id,
            user_email=user_email,
            assigned_by=assigned_by,
            due_date=due_date,
            enrollment_type="manual",
            **kwargs
        )
        
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        
        # Create course enrollments for all courses in the program
        await self._create_course_enrollments(enrollment)
        
        # Send notification
        await self._notify_enrollment(enrollment, program)
        
        logger.info(f"Enrolled user {user_id} in program {program.program_id}")
        return enrollment
    
    async def _auto_enroll_users(self, program: TrainingProgram):
        """Auto-enroll users based on program criteria"""
        
        # This would integrate with user management system
        # For now, simulate auto-enrollment logic
        target_roles = program.target_roles or []
        target_departments = program.target_departments or []
        
        # Simulate finding matching users
        # In real implementation, this would query user database
        logger.info(f"Auto-enrolling users for program {program.program_id}")
        
        # Example: Auto-enroll based on roles and departments
        # users = get_users_by_criteria(roles=target_roles, departments=target_departments)
        # for user in users:
        #     await self.enroll_user_in_program(program.id, user.id, user.email, "system")
    
    async def _create_course_enrollments(self, training_enrollment: TrainingEnrollment):
        """Create individual course enrollments for a training enrollment"""
        
        courses = self.db.query(TrainingCourse).filter(
            TrainingCourse.program_id == training_enrollment.program_id,
            TrainingCourse.active == True
        ).order_by(TrainingCourse.sequence_order).all()
        
        for course in courses:
            course_enrollment = CourseEnrollment(
                training_enrollment_id=training_enrollment.id,
                course_id=course.id
            )
            self.db.add(course_enrollment)
        
        self.db.commit()
        logger.info(f"Created {len(courses)} course enrollments for training enrollment {training_enrollment.enrollment_id}")
    
    async def update_training_progress(
        self,
        enrollment_id: int,
        progress_percentage: float,
        last_accessed: Optional[datetime] = None
    ) -> TrainingEnrollment:
        """Update training progress for a user"""
        
        enrollment = self.db.query(TrainingEnrollment).filter(TrainingEnrollment.id == enrollment_id).first()
        if not enrollment:
            raise ValueError(f"Training enrollment with ID {enrollment_id} not found")
        
        # Update progress
        enrollment.progress_percentage = min(100.0, max(0.0, progress_percentage))
        enrollment.last_accessed = last_accessed or datetime.utcnow()
        
        # Update status based on progress
        if enrollment.status == TrainingStatus.NOT_STARTED and progress_percentage > 0:
            enrollment.status = TrainingStatus.IN_PROGRESS
            enrollment.started_date = datetime.utcnow()
        elif progress_percentage >= 100.0:
            enrollment.status = TrainingStatus.COMPLETED
            enrollment.completed_date = datetime.utcnow()
            
            # Issue certificate if applicable
            await self._check_certification_eligibility(enrollment)
        
        self.db.commit()
        
        logger.info(f"Updated training progress: {enrollment.enrollment_id} to {progress_percentage}%")
        return enrollment
    
    # ===================== Phishing Simulation Management =====================
    
    async def create_phishing_campaign(
        self,
        name: str,
        description: str,
        target_users: List[str],
        template_name: str,
        scheduled_start: datetime,
        created_by: str,
        **kwargs
    ) -> AwarenessCampaign:
        """Create a phishing awareness campaign"""
        
        campaign = AwarenessCampaign(
            name=name,
            description=description,
            campaign_type="phishing",
            target_users=target_users,
            scheduled_start=scheduled_start,
            created_by=created_by,
            status=CampaignStatus.DRAFT,
            **kwargs
        )
        
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        
        # Create phishing simulation
        simulation = await self._create_phishing_simulation(campaign, template_name, kwargs)
        
        logger.info(f"Created phishing campaign: {campaign.campaign_id}")
        return campaign
    
    async def _create_phishing_simulation(
        self,
        campaign: AwarenessCampaign,
        template_name: str,
        config: Dict[str, Any]
    ) -> PhishingSimulation:
        """Create phishing simulation for a campaign"""
        
        # Get simulation template (would come from template database)
        template = await self._get_simulation_template(template_name)
        
        simulation = PhishingSimulation(
            campaign_id=campaign.id,
            template_name=template_name,
            difficulty_level=template.get("difficulty_level", CompetencyLevel.BEGINNER),
            attack_vector=template.get("attack_vector", "email"),
            scenario_description=template.get("scenario_description"),
            sender_email=template.get("sender_email"),
            sender_name=template.get("sender_name"),
            subject_line=template.get("subject_line"),
            email_content=template.get("email_content"),
            landing_page_url=template.get("landing_page_url"),
            track_opens=config.get("track_opens", True),
            track_clicks=config.get("track_clicks", True),
            track_attachments=config.get("track_attachments", True),
            track_data_entry=config.get("track_data_entry", True)
        )
        
        self.db.add(simulation)
        self.db.commit()
        self.db.refresh(simulation)
        
        return simulation
    
    async def _get_simulation_template(self, template_name: str) -> Dict[str, Any]:
        """Get phishing simulation template"""
        
        # Predefined templates - in production this would be a database
        templates = {
            "fake_login": {
                "difficulty_level": CompetencyLevel.BEGINNER,
                "attack_vector": "email",
                "scenario_description": "Fake login page to steal credentials",
                "sender_email": "noreply@company-security.com",
                "sender_name": "IT Security Team",
                "subject_line": "Urgent: Account Verification Required",
                "email_content": "Your account requires immediate verification. Click here to verify.",
                "landing_page_url": "https://phishing-sim.company.com/login"
            },
            "fake_invoice": {
                "difficulty_level": CompetencyLevel.INTERMEDIATE,
                "attack_vector": "email",
                "scenario_description": "Fake invoice with malicious attachment",
                "sender_email": "billing@vendor-services.com",
                "sender_name": "Vendor Services",
                "subject_line": "Invoice #12345 - Payment Required",
                "email_content": "Please find attached invoice for immediate payment.",
                "landing_page_url": "https://phishing-sim.company.com/invoice"
            },
            "executive_impersonation": {
                "difficulty_level": CompetencyLevel.ADVANCED,
                "attack_vector": "email",
                "scenario_description": "CEO impersonation requesting urgent wire transfer",
                "sender_email": "ceo@company.com",
                "sender_name": "CEO Name",
                "subject_line": "URGENT: Confidential Wire Transfer Required",
                "email_content": "I need you to process an urgent wire transfer. Please call me immediately.",
                "landing_page_url": "https://phishing-sim.company.com/transfer"
            }
        }
        
        return templates.get(template_name, templates["fake_login"])
    
    async def launch_phishing_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Launch a phishing campaign"""
        
        campaign = self.db.query(AwarenessCampaign).filter(AwarenessCampaign.id == campaign_id).first()
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
        
        if campaign.status != CampaignStatus.SCHEDULED:
            campaign.status = CampaignStatus.SCHEDULED
        
        # Update campaign timing
        campaign.actual_start = datetime.utcnow()
        campaign.status = CampaignStatus.ACTIVE
        
        # Get simulation
        simulation = self.db.query(PhishingSimulation).filter(
            PhishingSimulation.campaign_id == campaign_id
        ).first()
        
        # Send simulated phishing emails
        results = await self._send_phishing_emails(campaign, simulation)
        
        # Update campaign statistics
        campaign.total_recipients = results["total_sent"]
        campaign.delivered_count = results["delivered"]
        
        self.db.commit()
        
        logger.info(f"Launched phishing campaign: {campaign.campaign_id}")
        return {
            "campaign_id": campaign.campaign_id,
            "status": "launched",
            "recipients": results["total_sent"],
            "delivered": results["delivered"]
        }
    
    async def _send_phishing_emails(
        self,
        campaign: AwarenessCampaign,
        simulation: PhishingSimulation
    ) -> Dict[str, int]:
        """Simulate sending phishing emails"""
        
        target_users = campaign.target_users or []
        total_sent = len(target_users)
        delivered = 0
        
        for user_id in target_users:
            # Simulate email delivery
            delivery_success = random.choice([True, True, True, False])  # 75% success rate
            
            if delivery_success:
                delivered += 1
                
                # Create initial simulation result
                result = SimulationResult(
                    simulation_id=simulation.id,
                    user_id=user_id,
                    user_email=f"user{user_id}@company.com",  # Simulated email
                    result=SimResult.IGNORED,  # Default to ignored
                    delivery_time=datetime.utcnow()
                )
                self.db.add(result)
        
        self.db.commit()
        
        return {
            "total_sent": total_sent,
            "delivered": delivered,
            "failed": total_sent - delivered
        }
    
    async def record_phishing_interaction(
        self,
        simulation_id: int,
        user_id: str,
        interaction_type: str,
        interaction_data: Optional[Dict[str, Any]] = None
    ) -> SimulationResult:
        """Record user interaction with phishing simulation"""
        
        # Find existing result
        result = self.db.query(SimulationResult).filter(
            SimulationResult.simulation_id == simulation_id,
            SimulationResult.user_id == user_id
        ).first()
        
        if not result:
            raise ValueError(f"Simulation result not found for user {user_id}")
        
        current_time = datetime.utcnow()
        
        # Update based on interaction type
        if interaction_type == "email_opened":
            result.email_opened = True
            result.email_open_time = current_time
            
        elif interaction_type == "link_clicked":
            result.link_clicked = True
            result.link_click_time = current_time
            result.result = SimResult.FAILED  # Clicked suspicious link
            
            # Calculate response time
            if result.delivery_time:
                response_time = (current_time - result.delivery_time).total_seconds()
                result.response_time_seconds = int(response_time)
            
        elif interaction_type == "attachment_opened":
            result.attachment_opened = True
            result.attachment_open_time = current_time
            result.result = SimResult.FAILED  # Opened malicious attachment
            
        elif interaction_type == "data_entered":
            result.data_entered = True
            result.data_entry_time = current_time
            result.result = SimResult.FAILED  # Entered credentials
            
        elif interaction_type == "reported_phishing":
            result.reported_as_phishing = True
            result.report_time = current_time
            result.result = SimResult.REPORTED  # Successfully reported
            
        elif interaction_type == "deleted_email":
            result.deleted_email = True
            if not result.link_clicked and not result.attachment_opened:
                result.result = SimResult.PASSED  # Deleted without interaction
        
        # Determine if remedial training is needed
        if result.result == SimResult.FAILED:
            result.training_assigned = True
            await self._assign_remedial_training(result)
        
        result.interaction_time = current_time
        self.db.commit()
        
        logger.info(f"Recorded phishing interaction: {interaction_type} for user {user_id}")
        return result
    
    async def _assign_remedial_training(self, simulation_result: SimulationResult):
        """Assign remedial training to users who failed phishing simulation"""
        
        # Get simulation details
        simulation = self.db.query(PhishingSimulation).filter(
            PhishingSimulation.id == simulation_result.simulation_id
        ).first()
        
        if simulation and simulation.remedial_training:
            # Find appropriate remedial training programs
            for training_program_id in simulation.remedial_training:
                try:
                    await self.enroll_user_in_program(
                        program_id=training_program_id,
                        user_id=simulation_result.user_id,
                        user_email=simulation_result.user_email,
                        assigned_by="phishing_simulation"
                    )
                except Exception as e:
                    logger.error(f"Failed to assign remedial training: {str(e)}")
    
    # ===================== Competency Assessment Management =====================
    
    async def create_competency_assessment(
        self,
        competency_id: int,
        name: str,
        assessment_type: AssessmentType,
        questions: List[Dict[str, Any]],
        passing_score: float = 70.0,
        **kwargs
    ) -> CompetencyAssessment:
        """Create a competency assessment"""
        
        assessment = CompetencyAssessment(
            competency_id=competency_id,
            name=name,
            assessment_type=assessment_type,
            questions=questions,
            passing_score=passing_score,
            **kwargs
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        logger.info(f"Created competency assessment: {assessment.assessment_id}")
        return assessment
    
    async def conduct_assessment(
        self,
        assessment_id: int,
        user_id: str,
        user_email: str,
        answers: Dict[str, Any]
    ) -> AssessmentResult:
        """Conduct a competency assessment for a user"""
        
        assessment = self.db.query(CompetencyAssessment).filter(
            CompetencyAssessment.id == assessment_id
        ).first()
        
        if not assessment:
            raise ValueError(f"Assessment with ID {assessment_id} not found")
        
        # Check attempts limit
        existing_attempts = self.db.query(AssessmentResult).filter(
            AssessmentResult.assessment_id == assessment_id,
            AssessmentResult.user_id == user_id
        ).count()
        
        if existing_attempts >= assessment.attempts_allowed:
            raise ValueError(f"User has exceeded maximum attempts ({assessment.attempts_allowed})")
        
        # Score the assessment
        scoring_result = await self._score_assessment(assessment, answers)
        
        # Create assessment result
        result = AssessmentResult(
            assessment_id=assessment_id,
            user_id=user_id,
            user_email=user_email,
            score=scoring_result["score"],
            passed=scoring_result["score"] >= assessment.passing_score,
            attempt_number=existing_attempts + 1,
            started_at=datetime.utcnow() - timedelta(minutes=30),  # Simulated
            completed_at=datetime.utcnow(),
            time_taken_minutes=30,  # Simulated
            answers=answers,
            question_scores=scoring_result["question_scores"],
            strengths=scoring_result["strengths"],
            weaknesses=scoring_result["weaknesses"],
            recommended_training=scoring_result["recommended_training"]
        )
        
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        
        # Update user competency
        await self._update_user_competency(assessment.competency_id, user_id, result)
        
        logger.info(f"Completed assessment {assessment.assessment_id} for user {user_id}, score: {result.score}")
        return result
    
    async def _score_assessment(
        self,
        assessment: CompetencyAssessment,
        answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Score an assessment based on answers"""
        
        questions = assessment.questions or []
        total_questions = len(questions)
        correct_answers = 0
        question_scores = {}
        strengths = []
        weaknesses = []
        
        for i, question in enumerate(questions):
            question_id = f"q_{i+1}"
            user_answer = answers.get(question_id)
            correct_answer = question.get("correct_answer")
            
            if user_answer == correct_answer:
                correct_answers += 1
                question_scores[question_id] = 1.0
                
                # Track strengths by topic
                topic = question.get("topic", "general")
                if topic not in strengths:
                    strengths.append(topic)
            else:
                question_scores[question_id] = 0.0
                
                # Track weaknesses by topic
                topic = question.get("topic", "general")
                if topic not in weaknesses:
                    weaknesses.append(topic)
        
        # Calculate final score
        score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Generate training recommendations based on weaknesses
        recommended_training = []
        for weakness in weaknesses:
            if weakness == "phishing_awareness":
                recommended_training.append("Phishing Awareness Training")
            elif weakness == "password_security":
                recommended_training.append("Password Security Best Practices")
            elif weakness == "data_protection":
                recommended_training.append("Data Protection and Privacy")
        
        return {
            "score": score,
            "question_scores": question_scores,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommended_training": recommended_training
        }
    
    async def _update_user_competency(
        self,
        competency_id: int,
        user_id: str,
        assessment_result: AssessmentResult
    ):
        """Update user competency based on assessment result"""
        
        user_competency = self.db.query(UserCompetency).filter(
            UserCompetency.competency_id == competency_id,
            UserCompetency.user_id == user_id
        ).first()
        
        if not user_competency:
            # Create new user competency record
            user_competency = UserCompetency(
                competency_id=competency_id,
                user_id=user_id,
                user_email=assessment_result.user_email,
                current_level=CompetencyLevel.BEGINNER,
                target_level=CompetencyLevel.INTERMEDIATE,
                proficient=False
            )
            self.db.add(user_competency)
        
        # Update competency based on assessment score
        user_competency.last_assessed = assessment_result.completed_at
        user_competency.last_assessment_score = assessment_result.score
        user_competency.assessment_count += 1
        
        # Determine competency level based on score
        if assessment_result.score >= 90:
            user_competency.current_level = CompetencyLevel.EXPERT
        elif assessment_result.score >= 80:
            user_competency.current_level = CompetencyLevel.ADVANCED
        elif assessment_result.score >= 70:
            user_competency.current_level = CompetencyLevel.INTERMEDIATE
        else:
            user_competency.current_level = CompetencyLevel.BEGINNER
        
        # Update proficiency status
        user_competency.proficient = assessment_result.passed
        
        # Set next assessment date (e.g., 6 months for continuing education)
        user_competency.next_assessment_due = datetime.utcnow() + timedelta(days=180)
        
        self.db.commit()
    
    # ===================== Certification Management =====================
    
    async def check_certification_eligibility(
        self,
        certification_id: int,
        user_id: str
    ) -> Dict[str, Any]:
        """Check if user is eligible for certification"""
        
        certification = self.db.query(TrainingCertification).filter(
            TrainingCertification.id == certification_id
        ).first()
        
        if not certification:
            raise ValueError(f"Certification with ID {certification_id} not found")
        
        eligibility = {
            "eligible": True,
            "requirements_met": [],
            "requirements_pending": [],
            "training_completion": {},
            "competency_status": {}
        }
        
        # Check required training programs
        required_programs = certification.required_training_programs or []
        for program_id in required_programs:
            enrollment = self.db.query(TrainingEnrollment).filter(
                TrainingEnrollment.program_id == program_id,
                TrainingEnrollment.user_id == user_id,
                TrainingEnrollment.status == TrainingStatus.COMPLETED
            ).first()
            
            if enrollment:
                eligibility["requirements_met"].append(f"Training Program {program_id}")
                eligibility["training_completion"][str(program_id)] = {
                    "completed": True,
                    "completion_date": enrollment.completed_date,
                    "score": enrollment.final_score
                }
            else:
                eligibility["eligible"] = False
                eligibility["requirements_pending"].append(f"Training Program {program_id}")
                eligibility["training_completion"][str(program_id)] = {
                    "completed": False
                }
        
        # Check required competencies
        required_competencies = certification.required_competencies or []
        for competency_id in required_competencies:
            user_competency = self.db.query(UserCompetency).filter(
                UserCompetency.competency_id == competency_id,
                UserCompetency.user_id == user_id,
                UserCompetency.proficient == True
            ).first()
            
            if user_competency:
                eligibility["requirements_met"].append(f"Competency {competency_id}")
                eligibility["competency_status"][str(competency_id)] = {
                    "proficient": True,
                    "level": user_competency.current_level.value,
                    "last_assessed": user_competency.last_assessed
                }
            else:
                eligibility["eligible"] = False
                eligibility["requirements_pending"].append(f"Competency {competency_id}")
                eligibility["competency_status"][str(competency_id)] = {
                    "proficient": False
                }
        
        return eligibility
    
    async def _check_certification_eligibility(self, enrollment: TrainingEnrollment):
        """Check if training completion makes user eligible for any certifications"""
        
        # Find certifications that include this training program
        certifications = self.db.query(TrainingCertification).filter(
            TrainingCertification.required_training_programs.contains([enrollment.program_id])
        ).all()
        
        for certification in certifications:
            eligibility = await self.check_certification_eligibility(
                certification.id, enrollment.user_id
            )
            
            if eligibility["eligible"]:
                await self._issue_certification(certification, enrollment.user_id, enrollment.user_email)
    
    async def _issue_certification(
        self,
        certification: TrainingCertification,
        user_id: str,
        user_email: str
    ) -> UserCertification:
        """Issue a certification to a user"""
        
        # Generate certificate number
        cert_number = f"{certification.certification_id}-{user_id}-{datetime.utcnow().strftime('%Y%m%d')}"
        
        # Calculate expiration date
        expires_date = None
        if certification.validity_period_months:
            expires_date = datetime.utcnow() + timedelta(days=certification.validity_period_months * 30)
        
        user_cert = UserCertification(
            certification_id=certification.id,
            user_id=user_id,
            user_email=user_email,
            status=TrainingStatus.COMPLETED,
            earned_date=datetime.utcnow(),
            expires_date=expires_date,
            certificate_number=cert_number,
            verified=True,
            verification_code=self._generate_verification_code(),
            issued_by="system"
        )
        
        self.db.add(user_cert)
        self.db.commit()
        self.db.refresh(user_cert)
        
        logger.info(f"Issued certification {certification.name} to user {user_id}")
        return user_cert
    
    def _generate_verification_code(self) -> str:
        """Generate a verification code for certificate"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    # ===================== Analytics and Reporting =====================
    
    async def generate_training_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive training analytics"""
        
        analytics = {
            "program_statistics": await self._get_program_statistics(),
            "completion_rates": await self._get_completion_rates(),
            "phishing_simulation_results": await self._get_phishing_results(),
            "competency_analysis": await self._get_competency_analysis(),
            "certification_status": await self._get_certification_status(),
            "trends_and_insights": await self._get_training_trends()
        }
        
        return analytics
    
    async def _get_program_statistics(self) -> Dict[str, Any]:
        """Get training program statistics"""
        
        total_programs = self.db.query(TrainingProgram).count()
        active_programs = self.db.query(TrainingProgram).filter(TrainingProgram.active == True).count()
        mandatory_programs = self.db.query(TrainingProgram).filter(TrainingProgram.mandatory == True).count()
        
        total_enrollments = self.db.query(TrainingEnrollment).count()
        completed_enrollments = self.db.query(TrainingEnrollment).filter(
            TrainingEnrollment.status == TrainingStatus.COMPLETED
        ).count()
        overdue_enrollments = self.db.query(TrainingEnrollment).filter(
            TrainingEnrollment.due_date < datetime.utcnow(),
            TrainingEnrollment.status.in_([TrainingStatus.NOT_STARTED, TrainingStatus.IN_PROGRESS])
        ).count()
        
        return {
            "total_programs": total_programs,
            "active_programs": active_programs,
            "mandatory_programs": mandatory_programs,
            "total_enrollments": total_enrollments,
            "completed_enrollments": completed_enrollments,
            "overdue_enrollments": overdue_enrollments,
            "completion_rate": (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
        }
    
    async def _get_completion_rates(self) -> Dict[str, Any]:
        """Get completion rates by various dimensions"""
        
        # Overall completion rate
        total_enrollments = self.db.query(TrainingEnrollment).count()
        completed_enrollments = self.db.query(TrainingEnrollment).filter(
            TrainingEnrollment.status == TrainingStatus.COMPLETED
        ).count()
        
        overall_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
        
        # By program type
        program_type_rates = {}
        for program_type in TrainingType:
            type_total = self.db.query(TrainingEnrollment).join(TrainingProgram).filter(
                TrainingProgram.program_type == program_type
            ).count()
            
            type_completed = self.db.query(TrainingEnrollment).join(TrainingProgram).filter(
                TrainingProgram.program_type == program_type,
                TrainingEnrollment.status == TrainingStatus.COMPLETED
            ).count()
            
            program_type_rates[program_type.value] = (type_completed / type_total * 100) if type_total > 0 else 0
        
        return {
            "overall_completion_rate": overall_rate,
            "by_program_type": program_type_rates,
            "monthly_trend": [85.2, 87.1, 89.3, 91.2, 88.7, 90.1]  # Simulated monthly data
        }
    
    async def _get_phishing_results(self) -> Dict[str, Any]:
        """Get phishing simulation results"""
        
        total_simulations = self.db.query(SimulationResult).count()
        
        if total_simulations == 0:
            return {"total_simulations": 0, "no_data": True}
        
        # Count results by type
        passed = self.db.query(SimulationResult).filter(SimulationResult.result == SimResult.PASSED).count()
        failed = self.db.query(SimulationResult).filter(SimulationResult.result == SimResult.FAILED).count()
        reported = self.db.query(SimulationResult).filter(SimulationResult.result == SimResult.REPORTED).count()
        clicked = self.db.query(SimulationResult).filter(SimulationResult.link_clicked == True).count()
        
        return {
            "total_simulations": total_simulations,
            "pass_rate": (passed / total_simulations * 100),
            "fail_rate": (failed / total_simulations * 100),
            "report_rate": (reported / total_simulations * 100),
            "click_rate": (clicked / total_simulations * 100),
            "results_breakdown": {
                "passed": passed,
                "failed": failed,
                "reported": reported,
                "ignored": total_simulations - passed - failed - reported
            }
        }
    
    async def _get_competency_analysis(self) -> Dict[str, Any]:
        """Get competency assessment analysis"""
        
        total_assessments = self.db.query(AssessmentResult).count()
        passed_assessments = self.db.query(AssessmentResult).filter(AssessmentResult.passed == True).count()
        
        # Average score
        avg_score_result = self.db.query(AssessmentResult).all()
        avg_score = sum(r.score for r in avg_score_result) / len(avg_score_result) if avg_score_result else 0
        
        # Competency levels distribution
        competency_distribution = {}
        for level in CompetencyLevel:
            count = self.db.query(UserCompetency).filter(UserCompetency.current_level == level).count()
            competency_distribution[level.value] = count
        
        return {
            "total_assessments": total_assessments,
            "pass_rate": (passed_assessments / total_assessments * 100) if total_assessments > 0 else 0,
            "average_score": avg_score,
            "competency_distribution": competency_distribution
        }
    
    async def _get_certification_status(self) -> Dict[str, Any]:
        """Get certification status overview"""
        
        total_certifications = self.db.query(UserCertification).count()
        active_certifications = self.db.query(UserCertification).filter(
            UserCertification.status == TrainingStatus.COMPLETED,
            UserCertification.expires_date > datetime.utcnow()
        ).count()
        
        expiring_soon = self.db.query(UserCertification).filter(
            UserCertification.expires_date < datetime.utcnow() + timedelta(days=30),
            UserCertification.expires_date > datetime.utcnow()
        ).count()
        
        return {
            "total_certifications": total_certifications,
            "active_certifications": active_certifications,
            "expiring_soon": expiring_soon,
            "certification_rate": (active_certifications / total_certifications * 100) if total_certifications > 0 else 0
        }
    
    async def _get_training_trends(self) -> Dict[str, Any]:
        """Get training trends and insights"""
        
        # Simulated trend data - in production this would be calculated from historical data
        return {
            "enrollment_trend": "increasing",
            "completion_rate_trend": "stable",
            "phishing_susceptibility_trend": "decreasing",
            "key_insights": [
                "Training completion rates have improved 15% over the last quarter",
                "Phishing click rates decreased from 25% to 12% after awareness training",
                "Password security competency scores are consistently low across all departments",
                "Mobile security training shows highest engagement rates"
            ],
            "recommendations": [
                "Increase focus on password security training",
                "Implement more frequent phishing simulations",
                "Consider gamification for low-engagement programs",
                "Develop role-specific training paths"
            ]
        }
    
    # ===================== Notification and Communication =====================
    
    async def _notify_enrollment(self, enrollment: TrainingEnrollment, program: TrainingProgram):
        """Send enrollment notification to user"""
        
        notification = {
            "type": "training_enrollment",
            "user_id": enrollment.user_id,
            "user_email": enrollment.user_email,
            "program_name": program.name,
            "due_date": enrollment.due_date,
            "enrollment_id": enrollment.enrollment_id
        }
        
        self.notification_queue.append(notification)
        logger.info(f"Queued enrollment notification for user {enrollment.user_id}")
    
    async def get_user_training_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get personalized training dashboard for a user"""
        
        # Current enrollments
        active_enrollments = self.db.query(TrainingEnrollment).filter(
            TrainingEnrollment.user_id == user_id,
            TrainingEnrollment.status.in_([TrainingStatus.NOT_STARTED, TrainingStatus.IN_PROGRESS])
        ).all()
        
        # Completed training
        completed_enrollments = self.db.query(TrainingEnrollment).filter(
            TrainingEnrollment.user_id == user_id,
            TrainingEnrollment.status == TrainingStatus.COMPLETED
        ).all()
        
        # Phishing simulation results
        phishing_results = self.db.query(SimulationResult).filter(
            SimulationResult.user_id == user_id
        ).order_by(SimulationResult.created_at.desc()).limit(10).all()
        
        # User competencies
        user_competencies = self.db.query(UserCompetency).filter(
            UserCompetency.user_id == user_id
        ).all()
        
        # User certifications
        user_certifications = self.db.query(UserCertification).filter(
            UserCertification.user_id == user_id
        ).all()
        
        return {
            "user_id": user_id,
            "active_training": [
                {
                    "enrollment_id": e.enrollment_id,
                    "program_name": e.program.name if e.program else "Unknown",
                    "progress": e.progress_percentage,
                    "due_date": e.due_date,
                    "status": e.status.value
                }
                for e in active_enrollments
            ],
            "completed_training": len(completed_enrollments),
            "recent_phishing_results": [
                {
                    "result_id": r.result_id,
                    "result": r.result.value,
                    "date": r.delivery_time,
                    "campaign": r.simulation.campaign.name if r.simulation and r.simulation.campaign else "Unknown"
                }
                for r in phishing_results
            ],
            "competency_summary": [
                {
                    "competency_name": c.competency.name if c.competency else "Unknown",
                    "level": c.current_level.value,
                    "proficient": c.proficient,
                    "last_assessed": c.last_assessed
                }
                for c in user_competencies
            ],
            "certifications": [
                {
                    "certification_name": c.certification.name if c.certification else "Unknown",
                    "status": c.status.value,
                    "earned_date": c.earned_date,
                    "expires_date": c.expires_date
                }
                for c in user_certifications
            ]
        }