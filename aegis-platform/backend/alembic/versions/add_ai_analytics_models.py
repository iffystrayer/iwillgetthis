"""Add AI analytics models for predictive risk management

Revision ID: ai_analytics_001
Revises: d814291bbae3
Create Date: 2025-08-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ai_analytics_001'
down_revision = 'd814291bbae3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add AI analytics models"""
    
    # Create ai_models table
    op.create_table('ai_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('model_type', sa.Enum('RISK_PREDICTION', 'THREAT_DETECTION', 'ANOMALY_DETECTION', 'COMPLIANCE_FORECASTING', 'VULNERABILITY_ASSESSMENT', 'INCIDENT_PREDICTION', 'ASSET_RISK_SCORING', 'CONTROL_EFFECTIVENESS', 'BUSINESS_IMPACT', 'TREND_ANALYSIS', name='modeltype'), nullable=False),
        sa.Column('algorithm', sa.String(length=100), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True, default='1.0'),
        sa.Column('status', sa.Enum('TRAINING', 'ACTIVE', 'DEPRECATED', 'FAILED', 'TESTING', name='modelstatus'), nullable=True, default='TRAINING'),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('training_data_sources', sa.JSON(), nullable=True),
        sa.Column('feature_columns', sa.JSON(), nullable=True),
        sa.Column('target_column', sa.String(length=100), nullable=True),
        sa.Column('training_parameters', sa.JSON(), nullable=True),
        sa.Column('accuracy_score', sa.Float(), nullable=True),
        sa.Column('precision_score', sa.Float(), nullable=True),
        sa.Column('recall_score', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('roc_auc_score', sa.Float(), nullable=True),
        sa.Column('mean_squared_error', sa.Float(), nullable=True),
        sa.Column('r2_score', sa.Float(), nullable=True),
        sa.Column('trained_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_evaluated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_retrain_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('model_path', sa.String(length=500), nullable=True),
        sa.Column('feature_importance', sa.JSON(), nullable=True),
        sa.Column('model_metadata', sa.JSON(), nullable=True),
        sa.Column('prediction_threshold', sa.Float(), nullable=True, default=0.5),
        sa.Column('is_production', sa.Boolean(), nullable=True, default=False),
        sa.Column('auto_retrain', sa.Boolean(), nullable=True, default=True),
        sa.Column('retrain_frequency_days', sa.Integer(), nullable=True, default=30),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_models_id'), 'ai_models', ['id'], unique=False)
    
    # Create ai_predictions table
    op.create_table('ai_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('prediction_type', sa.String(length=100), nullable=False),
        sa.Column('predicted_value', sa.Float(), nullable=True),
        sa.Column('predicted_category', sa.String(length=100), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('confidence_level', sa.Enum('HIGH', 'MEDIUM', 'LOW', 'UNKNOWN', name='predictionconfidence'), nullable=True, default='MEDIUM'),
        sa.Column('input_features', sa.JSON(), nullable=True),
        sa.Column('prediction_reason', sa.Text(), nullable=True),
        sa.Column('contributing_factors', sa.JSON(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('impact_assessment', sa.Text(), nullable=True),
        sa.Column('likelihood_assessment', sa.Text(), nullable=True),
        sa.Column('prediction_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('prediction_horizon_days', sa.Integer(), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_outcome', sa.Float(), nullable=True),
        sa.Column('outcome_recorded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('prediction_accuracy', sa.Float(), nullable=True),
        sa.Column('prediction_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_predictions_id'), 'ai_predictions', ['id'], unique=False)
    
    # Create model_evaluations table
    op.create_table('model_evaluations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=False),
        sa.Column('evaluation_name', sa.String(length=255), nullable=True),
        sa.Column('evaluation_type', sa.String(length=50), nullable=True),
        sa.Column('evaluated_by_id', sa.Integer(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('precision', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('roc_auc', sa.Float(), nullable=True),
        sa.Column('mean_squared_error', sa.Float(), nullable=True),
        sa.Column('r2_score', sa.Float(), nullable=True),
        sa.Column('test_data_size', sa.Integer(), nullable=True),
        sa.Column('test_data_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('test_data_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('performance_change', sa.Float(), nullable=True),
        sa.Column('performance_trend', sa.String(length=20), nullable=True),
        sa.Column('confusion_matrix', sa.JSON(), nullable=True),
        sa.Column('classification_report', sa.JSON(), nullable=True),
        sa.Column('feature_importance_changes', sa.JSON(), nullable=True),
        sa.Column('evaluation_results', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('requires_retraining', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['evaluated_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_evaluations_id'), 'model_evaluations', ['id'], unique=False)
    
    # Create ai_alerts table
    op.create_table('ai_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=True),
        sa.Column('prediction_id', sa.Integer(), nullable=True),
        sa.Column('alert_type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.Enum('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO', name='alertseverity'), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Enum('OPEN', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE', 'ACKNOWLEDGED', name='alertstatus'), nullable=True, default='OPEN'),
        sa.Column('priority', sa.Integer(), nullable=True, default=3),
        sa.Column('trigger_condition', sa.Text(), nullable=True),
        sa.Column('threshold_exceeded', sa.Float(), nullable=True),
        sa.Column('anomaly_score', sa.Float(), nullable=True),
        sa.Column('affected_entity_type', sa.String(length=50), nullable=True),
        sa.Column('affected_entity_id', sa.Integer(), nullable=True),
        sa.Column('affected_entities', sa.JSON(), nullable=True),
        sa.Column('ai_analysis', sa.Text(), nullable=True),
        sa.Column('root_cause_analysis', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('recommended_actions', sa.JSON(), nullable=True),
        sa.Column('remediation_steps', sa.Text(), nullable=True),
        sa.Column('business_impact', sa.Text(), nullable=True),
        sa.Column('urgency_justification', sa.Text(), nullable=True),
        sa.Column('first_detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolution_actions_taken', sa.JSON(), nullable=True),
        sa.Column('false_positive_reason', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.id'], ),
        sa.ForeignKeyConstraint(['prediction_id'], ['ai_predictions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_alerts_id'), 'ai_alerts', ['id'], unique=False)
    
    # Create ai_insights table
    op.create_table('ai_insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('insight_type', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('detailed_analysis', sa.Text(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('urgency_score', sa.Float(), nullable=True),
        sa.Column('data_sources', sa.JSON(), nullable=True),
        sa.Column('analysis_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('analysis_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('key_metrics', sa.JSON(), nullable=True),
        sa.Column('supporting_data', sa.JSON(), nullable=True),
        sa.Column('visualizations', sa.JSON(), nullable=True),
        sa.Column('related_entities', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('potential_savings', sa.String(length=100), nullable=True),
        sa.Column('risk_reduction', sa.String(length=100), nullable=True),
        sa.Column('implementation_effort', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, default='active'),
        sa.Column('reviewed_by_id', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True, default=0),
        sa.Column('bookmark_count', sa.Integer(), nullable=True, default=0),
        sa.Column('sharing_count', sa.Integer(), nullable=True, default=0),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_insights_id'), 'ai_insights', ['id'], unique=False)
    
    # Create ai_datasets table
    op.create_table('ai_datasets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dataset_type', sa.String(length=50), nullable=True),
        sa.Column('data_source', sa.Enum('RISK_REGISTER', 'ASSET_INVENTORY', 'VULNERABILITY_SCANS', 'INCIDENT_LOGS', 'COMPLIANCE_DATA', 'AUDIT_REPORTS', 'THREAT_INTELLIGENCE', 'SECURITY_EVENTS', 'USER_BEHAVIOR', 'NETWORK_TRAFFIC', name='datasource'), nullable=True),
        sa.Column('total_records', sa.Integer(), nullable=True),
        sa.Column('features_count', sa.Integer(), nullable=True),
        sa.Column('missing_values_percentage', sa.Float(), nullable=True),
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        sa.Column('data_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('schema_definition', sa.JSON(), nullable=True),
        sa.Column('feature_statistics', sa.JSON(), nullable=True),
        sa.Column('data_distribution', sa.JSON(), nullable=True),
        sa.Column('outlier_analysis', sa.JSON(), nullable=True),
        sa.Column('storage_path', sa.String(length=500), nullable=True),
        sa.Column('file_format', sa.String(length=50), nullable=True),
        sa.Column('compressed_size_mb', sa.Float(), nullable=True),
        sa.Column('access_permissions', sa.JSON(), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True, default='1.0'),
        sa.Column('parent_dataset_id', sa.Integer(), nullable=True),
        sa.Column('transformation_steps', sa.JSON(), nullable=True),
        sa.Column('used_by_models', sa.JSON(), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=True, default=0),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_dataset_id'], ['ai_datasets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_datasets_id'), 'ai_datasets', ['id'], unique=False)
    
    # Create ai_experiments table
    op.create_table('ai_experiments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('experiment_type', sa.String(length=50), nullable=True),
        sa.Column('objective', sa.String(length=100), nullable=True),
        sa.Column('models_tested', sa.JSON(), nullable=True),
        sa.Column('hyperparameters', sa.JSON(), nullable=True),
        sa.Column('feature_sets', sa.JSON(), nullable=True),
        sa.Column('best_model_config', sa.JSON(), nullable=True),
        sa.Column('best_performance_score', sa.Float(), nullable=True),
        sa.Column('all_results', sa.JSON(), nullable=True),
        sa.Column('insights', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('feature_importance_ranking', sa.JSON(), nullable=True),
        sa.Column('started_by_id', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, default='running'),
        sa.Column('compute_time_minutes', sa.Integer(), nullable=True),
        sa.Column('memory_usage_mb', sa.Float(), nullable=True),
        sa.Column('storage_used_mb', sa.Float(), nullable=True),
        sa.Column('random_seed', sa.Integer(), nullable=True),
        sa.Column('environment_info', sa.JSON(), nullable=True),
        sa.Column('code_version', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['started_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_experiments_id'), 'ai_experiments', ['id'], unique=False)


def downgrade() -> None:
    """Remove AI analytics models"""
    
    # Drop tables in reverse order
    op.drop_index(op.f('ix_ai_experiments_id'), table_name='ai_experiments')
    op.drop_table('ai_experiments')
    
    op.drop_index(op.f('ix_ai_datasets_id'), table_name='ai_datasets')
    op.drop_table('ai_datasets')
    
    op.drop_index(op.f('ix_ai_insights_id'), table_name='ai_insights')
    op.drop_table('ai_insights')
    
    op.drop_index(op.f('ix_ai_alerts_id'), table_name='ai_alerts')
    op.drop_table('ai_alerts')
    
    op.drop_index(op.f('ix_model_evaluations_id'), table_name='model_evaluations')
    op.drop_table('model_evaluations')
    
    op.drop_index(op.f('ix_ai_predictions_id'), table_name='ai_predictions')
    op.drop_table('ai_predictions')
    
    op.drop_index(op.f('ix_ai_models_id'), table_name='ai_models')
    op.drop_table('ai_models')
    
    # Drop custom enums
    op.execute('DROP TYPE IF EXISTS modeltype')
    op.execute('DROP TYPE IF EXISTS modelstatus')
    op.execute('DROP TYPE IF EXISTS predictionconfidence')
    op.execute('DROP TYPE IF EXISTS alertseverity')
    op.execute('DROP TYPE IF EXISTS alertstatus')
    op.execute('DROP TYPE IF EXISTS datasource')