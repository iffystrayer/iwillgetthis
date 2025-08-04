from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import logging
import numpy as np
import pandas as pd
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.analytics import (
    MetricDefinition, MetricValue, KPIConfiguration, PredictionConfiguration,
    PredictionResult, AnalyticsJob, DataQualityMetric,
    MetricType, AggregationType, TimeGranularity, PredictionModel
)

logger = logging.getLogger(__name__)

class TrendDirection(Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"

class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"

@dataclass
class PredictionOutput:
    predicted_value: float
    confidence_score: float
    confidence_interval: Tuple[float, float]
    trend_direction: TrendDirection
    risk_indicators: List[str]
    recommendations: List[str]
    model_accuracy: float

@dataclass
class AnalyticsInsight:
    insight_type: str
    title: str
    description: str
    impact_level: str
    confidence: float
    data_points: List[Dict[str, Any]]
    recommendations: List[str]
    related_metrics: List[str]

@dataclass
class RiskForecast:
    metric_name: str
    current_value: float
    forecast_periods: List[Dict[str, Any]]
    risk_scenarios: Dict[str, float]  # scenario_name -> probability
    mitigation_impact: Dict[str, float]  # mitigation -> expected_impact
    confidence_level: float

class AdvancedAnalyticsEngine:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.models = {}  # Cache for trained models
        self.feature_engineering = FeatureEngineering()
        self.anomaly_detector = AnomalyDetector()
        self.trend_analyzer = TrendAnalyzer()
        
    def calculate_metric(
        self,
        metric_id: str,
        time_range: Tuple[datetime, datetime],
        dimensions: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate a metric value for given time range and dimensions"""
        
        try:
            metric_def = self.db.query(MetricDefinition).filter(
                MetricDefinition.metric_id == metric_id
            ).first()
            
            if not metric_def:
                raise ValueError(f"Metric definition not found: {metric_id}")
            
            # Build query based on metric definition
            query = self._build_metric_query(metric_def, time_range, dimensions)
            
            # Execute query and get result
            result = self.db.execute(text(query)).fetchone()
            
            if result is None:
                return 0.0
            
            value = float(result[0]) if result[0] is not None else 0.0
            
            # Store metric value
            self._store_metric_value(metric_def, value, dimensions, time_range[1])
            
            return value
            
        except Exception as e:
            logger.error(f"Error calculating metric {metric_id}: {str(e)}")
            raise
    
    def _build_metric_query(
        self,
        metric_def: MetricDefinition,
        time_range: Tuple[datetime, datetime],
        dimensions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build SQL query for metric calculation"""
        
        formula = metric_def.calculation_formula
        start_date, end_date = time_range
        
        # Replace placeholders in formula
        query = formula.replace("{start_date}", f"'{start_date}'")
        query = query.replace("{end_date}", f"'{end_date}'")
        
        # Add dimension filters
        if dimensions:
            for dim_key, dim_value in dimensions.items():
                query = query.replace(f"{{{dim_key}}}", f"'{dim_value}'")
        
        return query
    
    def _store_metric_value(
        self,
        metric_def: MetricDefinition,
        value: float,
        dimensions: Optional[Dict[str, Any]],
        timestamp: datetime
    ):
        """Store calculated metric value"""
        
        # Check for previous value to calculate trend
        previous_value = self._get_previous_metric_value(
            metric_def.id, dimensions, timestamp
        )
        
        # Detect anomalies
        anomaly_score = self.anomaly_detector.detect_anomaly(
            metric_def.metric_id, value, timestamp
        )
        
        metric_value = MetricValue(
            metric_definition_id=metric_def.id,
            timestamp=timestamp,
            time_granularity=TimeGranularity.DAY,
            value=value,
            previous_value=previous_value,
            dimensions=dimensions or {},
            confidence_score=0.95,  # Default confidence
            data_completeness=1.0,  # Assume complete for now
            anomaly_detected=anomaly_score > 0.7,
            anomaly_score=anomaly_score,
            source_records_count=1,
            calculated_at=datetime.utcnow()
        )
        
        self.db.add(metric_value)
        self.db.commit()
    
    def _get_previous_metric_value(
        self,
        metric_def_id: int,
        dimensions: Optional[Dict[str, Any]],
        current_timestamp: datetime
    ) -> Optional[float]:
        """Get the previous metric value for trend calculation"""
        
        query = self.db.query(MetricValue).filter(
            MetricValue.metric_definition_id == metric_def_id,
            MetricValue.timestamp < current_timestamp
        )
        
        if dimensions:
            # Filter by dimensions (simplified - in practice would need JSON querying)
            pass
        
        previous = query.order_by(MetricValue.timestamp.desc()).first()
        return previous.value if previous else None
    
    def generate_risk_prediction(
        self,
        metric_id: str,
        prediction_horizon_days: int = 30,
        confidence_level: float = 0.95
    ) -> PredictionOutput:
        """Generate AI-powered risk predictions"""
        
        try:
            # Get historical data
            historical_data = self._get_historical_data(metric_id, days=365)
            
            if len(historical_data) < 30:
                raise ValueError("Insufficient historical data for prediction")
            
            # Feature engineering
            features = self.feature_engineering.create_features(historical_data)
            
            # Get or train prediction model
            model = self._get_or_train_model(metric_id, features)
            
            # Generate prediction
            prediction = model.predict(prediction_horizon_days)
            
            # Calculate confidence interval
            confidence_interval = model.get_confidence_interval(
                prediction, confidence_level
            )
            
            # Analyze trend
            trend = self.trend_analyzer.analyze_trend(historical_data)
            
            # Generate risk indicators
            risk_indicators = self._generate_risk_indicators(
                historical_data, prediction, trend
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                metric_id, prediction, risk_indicators, trend
            )
            
            # Store prediction result
            self._store_prediction_result(
                metric_id, prediction, confidence_interval, confidence_level
            )
            
            return PredictionOutput(
                predicted_value=prediction,
                confidence_score=confidence_level,
                confidence_interval=confidence_interval,
                trend_direction=trend,
                risk_indicators=risk_indicators,
                recommendations=recommendations,
                model_accuracy=model.accuracy
            )
            
        except Exception as e:
            logger.error(f"Error generating prediction for {metric_id}: {str(e)}")
            raise
    
    def _get_historical_data(self, metric_id: str, days: int = 365) -> List[Dict[str, Any]]:
        """Get historical data for a metric"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = text("""
            SELECT mv.timestamp, mv.value, mv.dimensions
            FROM metric_values mv
            JOIN metric_definitions md ON mv.metric_definition_id = md.id
            WHERE md.metric_id = :metric_id
            AND mv.timestamp >= :start_date
            AND mv.timestamp <= :end_date
            ORDER BY mv.timestamp
        """)
        
        results = self.db.execute(query, {
            'metric_id': metric_id,
            'start_date': start_date,
            'end_date': end_date
        }).fetchall()
        
        return [
            {
                'timestamp': row[0],
                'value': row[1],
                'dimensions': json.loads(row[2]) if row[2] else {}
            }
            for row in results
        ]
    
    def _get_or_train_model(self, metric_id: str, features: pd.DataFrame) -> 'PredictionModel':
        """Get existing model or train new one"""
        
        if metric_id in self.models:
            return self.models[metric_id]
        
        # Train new model
        model = self._train_prediction_model(metric_id, features)
        self.models[metric_id] = model
        
        return model
    
    def _train_prediction_model(self, metric_id: str, features: pd.DataFrame) -> 'PredictionModel':
        """Train a prediction model for the metric"""
        
        # For demo purposes, using a simple time series model
        model = TimeSeriesModel()
        model.train(features)
        
        return model
    
    def _generate_risk_indicators(
        self,
        historical_data: List[Dict[str, Any]],
        prediction: float,
        trend: TrendDirection
    ) -> List[str]:
        """Generate risk indicators based on data analysis"""
        
        indicators = []
        
        # Get recent values
        recent_values = [d['value'] for d in historical_data[-30:]]
        
        if not recent_values:
            return indicators
        
        current_avg = np.mean(recent_values)
        volatility = np.std(recent_values)
        
        # Trend-based indicators
        if trend == TrendDirection.DECLINING:
            indicators.append("Declining trend detected - increased monitoring recommended")
        elif trend == TrendDirection.VOLATILE:
            indicators.append("High volatility observed - stability measures needed")
        
        # Prediction-based indicators
        if prediction > current_avg * 1.2:
            indicators.append("Significant increase predicted - prepare mitigation plans")
        elif prediction < current_avg * 0.8:
            indicators.append("Significant decrease predicted - investigate root causes")
        
        # Volatility indicators
        if volatility > current_avg * 0.3:
            indicators.append("High variability detected - process standardization needed")
        
        return indicators
    
    def _generate_recommendations(
        self,
        metric_id: str,
        prediction: float,
        risk_indicators: List[str],
        trend: TrendDirection
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Trend-based recommendations  
        if trend == TrendDirection.DECLINING:
            recommendations.extend([
                "Implement immediate corrective actions",
                "Increase monitoring frequency",
                "Review and update control procedures"
            ])
        elif trend == TrendDirection.VOLATILE:
            recommendations.extend([
                "Identify sources of variability",
                "Implement process standardization",
                "Consider additional controls"
            ])
        
        # Risk level recommendations
        if len(risk_indicators) > 2:
            recommendations.extend([
                "Escalate to management attention",
                "Conduct detailed risk assessment",
                "Consider additional resources"
            ])
        
        # Metric-specific recommendations
        metric_recommendations = self._get_metric_specific_recommendations(metric_id)
        recommendations.extend(metric_recommendations)
        
        return list(set(recommendations))  # Remove duplicates
    
    def _get_metric_specific_recommendations(self, metric_id: str) -> List[str]:
        """Get recommendations specific to the metric type"""
        
        recommendations_map = {
            'risk_score': [
                "Review risk treatment plans",
                "Update risk register",
                "Consider risk transfer options"
            ],
            'vulnerability_count': [
                "Accelerate patch management",
                "Conduct security assessments",
                "Enhance vulnerability scanning"
            ],
            'compliance_rate': [
                "Review compliance procedures",
                "Provide additional training",
                "Update policy documentation"
            ],
            'incident_count': [
                "Analyze incident patterns",
                "Strengthen preventive controls",
                "Review incident response procedures"
            ]
        }
        
        # Extract metric type from ID
        for metric_type, recs in recommendations_map.items():
            if metric_type in metric_id.lower():
                return recs
        
        return []
    
    def _store_prediction_result(
        self,
        metric_id: str,
        prediction: float,
        confidence_interval: Tuple[float, float],
        confidence_level: float
    ):
        """Store prediction result in database"""
        
        # Get prediction configuration
        config = self.db.query(PredictionConfiguration).filter(
            PredictionConfiguration.target_metric == metric_id
        ).first()
        
        if not config:
            # Create default configuration
            config = PredictionConfiguration(
                name=f"Prediction for {metric_id}",
                target_metric=metric_id,
                model_type=PredictionModel.TIME_SERIES,
                prediction_horizon_days=30
            )
            self.db.add(config)
            self.db.flush()
        
        prediction_result = PredictionResult(
            prediction_configuration_id=config.id,
            prediction_date=datetime.utcnow(),
            target_date=datetime.utcnow() + timedelta(days=30),
            predicted_value=prediction,
            confidence_lower=confidence_interval[0],
            confidence_upper=confidence_interval[1],
            confidence_score=confidence_level,
            model_version="1.0"
        )
        
        self.db.add(prediction_result)
        self.db.commit()
    
    def generate_insights(
        self,
        time_range: Tuple[datetime, datetime],
        focus_areas: Optional[List[str]] = None
    ) -> List[AnalyticsInsight]:
        """Generate intelligent insights from data analysis"""
        
        insights = []
        
        try:
            # Get all active metrics
            metrics = self.db.query(MetricDefinition).filter(
                MetricDefinition.active == True
            ).all()
            
            for metric in metrics:
                if focus_areas and metric.category not in focus_areas:
                    continue
                
                # Get metric data
                metric_data = self._get_metric_time_series(
                    metric.metric_id, time_range
                )
                
                if len(metric_data) < 10:  # Need sufficient data
                    continue
                
                # Analyze patterns
                patterns = self._analyze_patterns(metric_data)
                
                # Generate insights from patterns
                metric_insights = self._patterns_to_insights(
                    metric, patterns, metric_data
                )
                
                insights.extend(metric_insights)
            
            # Cross-metric analysis
            cross_insights = self._analyze_cross_metric_relationships(
                metrics, time_range
            )
            insights.extend(cross_insights)
            
            # Sort by impact and confidence
            insights.sort(
                key=lambda x: (x.impact_level, x.confidence),
                reverse=True
            )
            
            return insights[:20]  # Return top 20 insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    def _get_metric_time_series(
        self,
        metric_id: str,
        time_range: Tuple[datetime, datetime]
    ) -> List[Dict[str, Any]]:
        """Get time series data for a metric"""
        
        query = text("""
            SELECT mv.timestamp, mv.value, mv.previous_value, mv.anomaly_detected
            FROM metric_values mv
            JOIN metric_definitions md ON mv.metric_definition_id = md.id
            WHERE md.metric_id = :metric_id
            AND mv.timestamp >= :start_date
            AND mv.timestamp <= :end_date
            ORDER BY mv.timestamp
        """)
        
        results = self.db.execute(query, {
            'metric_id': metric_id,
            'start_date': time_range[0],
            'end_date': time_range[1]
        }).fetchall()
        
        return [
            {
                'timestamp': row[0],
                'value': row[1],
                'previous_value': row[2],
                'anomaly_detected': row[3]
            }
            for row in results
        ]
    
    def _analyze_patterns(self, metric_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in metric data"""
        
        values = [d['value'] for d in metric_data]
        timestamps = [d['timestamp'] for d in metric_data]
        
        if not values:
            return {}
        
        patterns = {
            'trend': self._calculate_trend(values),
            'volatility': np.std(values),
            'mean': np.mean(values),
            'anomaly_count': sum(1 for d in metric_data if d.get('anomaly_detected')),
            'recent_change': self._calculate_recent_change(values),
            'seasonal_pattern': self._detect_seasonality(values, timestamps),
            'outliers': self._detect_outliers(values)
        }
        
        return patterns
    
    def _calculate_trend(self, values: List[float]) -> TrendDirection:
        """Calculate overall trend direction"""
        
        if len(values) < 2:
            return TrendDirection.STABLE
        
        # Simple linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        # Calculate relative slope
        mean_value = np.mean(values)
        relative_slope = slope / mean_value if mean_value != 0 else 0
        
        # Determine trend
        if relative_slope > 0.1:
            return TrendDirection.IMPROVING
        elif relative_slope < -0.1:
            return TrendDirection.DECLINING
        else:
            # Check volatility
            volatility = np.std(values) / mean_value if mean_value != 0 else 0
            if volatility > 0.3:
                return TrendDirection.VOLATILE
            else:
                return TrendDirection.STABLE
    
    def _calculate_recent_change(self, values: List[float]) -> float:
        """Calculate recent change percentage"""
        
        if len(values) < 2:
            return 0.0
        
        recent_period = min(7, len(values) // 2)
        recent_avg = np.mean(values[-recent_period:])
        previous_avg = np.mean(values[:-recent_period])
        
        if previous_avg == 0:
            return 0.0
        
        return (recent_avg - previous_avg) / previous_avg * 100
    
    def _detect_seasonality(
        self,
        values: List[float],
        timestamps: List[datetime]
    ) -> bool:
        """Detect seasonal patterns in data"""
        
        # Simplified seasonality detection
        # In practice, would use more sophisticated methods like FFT
        
        if len(values) < 30:
            return False
        
        # Check for weekly patterns (7-day cycle)
        weekly_correlation = self._calculate_autocorrelation(values, 7)
        
        # Check for monthly patterns (30-day cycle)
        monthly_correlation = self._calculate_autocorrelation(values, 30)
        
        return weekly_correlation > 0.5 or monthly_correlation > 0.5
    
    def _calculate_autocorrelation(self, values: List[float], lag: int) -> float:
        """Calculate autocorrelation at given lag"""
        
        if len(values) <= lag:
            return 0.0
        
        # Simple autocorrelation calculation
        series = np.array(values)
        n = len(series)
        
        if n <= lag:
            return 0.0
        
        series1 = series[:-lag]
        series2 = series[lag:]
        
        correlation = np.corrcoef(series1, series2)[0, 1]
        return correlation if not np.isnan(correlation) else 0.0
    
    def _detect_outliers(self, values: List[float]) -> List[int]:
        """Detect outlier indices using IQR method"""
        
        if len(values) < 4:
            return []
        
        q25 = np.percentile(values, 25)
        q75 = np.percentile(values, 75)
        iqr = q75 - q25
        
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        
        outliers = []
        for i, value in enumerate(values):
            if value < lower_bound or value > upper_bound:
                outliers.append(i)
        
        return outliers
    
    def _patterns_to_insights(
        self,
        metric: MetricDefinition,
        patterns: Dict[str, Any],
        metric_data: List[Dict[str, Any]]
    ) -> List[AnalyticsInsight]:
        """Convert patterns to actionable insights"""
        
        insights = []
        
        # Trend insights
        if patterns['trend'] == TrendDirection.DECLINING:
            insights.append(AnalyticsInsight(
                insight_type="trend_alert",
                title=f"{metric.name} showing declining trend",
                description=f"The metric has decreased by {abs(patterns['recent_change']):.1f}% recently",
                impact_level="high",
                confidence=0.8,
                data_points=[
                    {'metric': metric.name, 'trend': patterns['trend'].value, 'change': patterns['recent_change']}
                ],
                recommendations=[
                    "Investigate root causes of decline",
                    "Implement corrective measures",
                    "Increase monitoring frequency"
                ],
                related_metrics=[metric.metric_id]
            ))
        
        # Volatility insights
        if patterns['volatility'] > patterns['mean'] * 0.3:
            insights.append(AnalyticsInsight(
                insight_type="volatility_alert",
                title=f"High volatility detected in {metric.name}",
                description=f"Metric shows high variability (σ={patterns['volatility']:.2f})",
                impact_level="medium",
                confidence=0.9,
                data_points=[
                    {'metric': metric.name, 'volatility': patterns['volatility'], 'mean': patterns['mean']}
                ],
                recommendations=[
                    "Identify sources of variability",
                    "Standardize processes",
                    "Implement additional controls"
                ],
                related_metrics=[metric.metric_id]
            ))
        
        # Anomaly insights
        if patterns['anomaly_count'] > len(metric_data) * 0.1:
            insights.append(AnalyticsInsight(
                insight_type="anomaly_alert",
                title=f"Multiple anomalies detected in {metric.name}",
                description=f"Found {patterns['anomaly_count']} anomalies out of {len(metric_data)} data points",
                impact_level="medium",
                confidence=0.85,
                data_points=[
                    {'metric': metric.name, 'anomaly_count': patterns['anomaly_count'], 'total_points': len(metric_data)}
                ],
                recommendations=[
                    "Review anomalous periods in detail",
                    "Check for data quality issues",
                    "Validate measurement processes"
                ],
                related_metrics=[metric.metric_id]
            ))
        
        return insights
    
    def _analyze_cross_metric_relationships(
        self,
        metrics: List[MetricDefinition],
        time_range: Tuple[datetime, datetime]
    ) -> List[AnalyticsInsight]:
        """Analyze relationships between different metrics"""
        
        insights = []
        
        # Get correlation matrix for key metrics
        metric_data = {}
        for metric in metrics[:10]:  # Limit to avoid performance issues
            data = self._get_metric_time_series(metric.metric_id, time_range)
            if len(data) > 10:
                metric_data[metric.metric_id] = [d['value'] for d in data]
        
        # Find strong correlations
        correlations = self._calculate_correlation_matrix(metric_data)
        
        for (metric1, metric2), correlation in correlations.items():
            if abs(correlation) > 0.7 and metric1 != metric2:
                insights.append(AnalyticsInsight(
                    insight_type="correlation",
                    title=f"Strong correlation between {metric1} and {metric2}",
                    description=f"Correlation coefficient: {correlation:.2f}",
                    impact_level="medium",
                    confidence=0.75,
                    data_points=[
                        {'metric1': metric1, 'metric2': metric2, 'correlation': correlation}
                    ],
                    recommendations=[
                        "Investigate causal relationship",
                        "Consider combined analysis",
                        "Look for common root causes"
                    ],
                    related_metrics=[metric1, metric2]
                ))
        
        return insights
    
    def _calculate_correlation_matrix(
        self,
        metric_data: Dict[str, List[float]]
    ) -> Dict[Tuple[str, str], float]:
        """Calculate correlation matrix between metrics"""
        
        correlations = {}
        metric_names = list(metric_data.keys())
        
        for i, metric1 in enumerate(metric_names):
            for j, metric2 in enumerate(metric_names):
                if i < j:  # Only calculate upper triangle
                    values1 = metric_data[metric1]
                    values2 = metric_data[metric2]
                    
                    # Ensure same length
                    min_len = min(len(values1), len(values2))
                    values1 = values1[:min_len]
                    values2 = values2[:min_len]
                    
                    if min_len > 2:
                        correlation = np.corrcoef(values1, values2)[0, 1]
                        if not np.isnan(correlation):
                            correlations[(metric1, metric2)] = correlation
        
        return correlations
    
    def generate_risk_forecast(
        self,
        entity_type: str,  # 'organization', 'department', 'asset_group'
        entity_id: str,
        forecast_horizon_days: int = 90
    ) -> RiskForecast:
        """Generate comprehensive risk forecast for an entity"""
        
        try:
            # Get relevant metrics for the entity
            metrics = self._get_entity_metrics(entity_type, entity_id)
            
            # Generate predictions for each metric
            predictions = {}
            for metric in metrics:
                try:
                    prediction = self.generate_risk_prediction(
                        metric.metric_id, forecast_horizon_days
                    )
                    predictions[metric.metric_id] = prediction
                except Exception as e:
                    logger.warning(f"Failed to predict {metric.metric_id}: {str(e)}")
                    continue
            
            # Aggregate risk scenarios
            risk_scenarios = self._calculate_risk_scenarios(predictions)
            
            # Calculate mitigation impact
            mitigation_impact = self._calculate_mitigation_impact(
                entity_type, entity_id, predictions
            )
            
            # Generate forecast periods
            forecast_periods = self._generate_forecast_periods(
                predictions, forecast_horizon_days
            )
            
            # Calculate overall confidence
            confidence_level = np.mean([
                pred.confidence_score for pred in predictions.values()
            ]) if predictions else 0.0
            
            return RiskForecast(
                metric_name=f"{entity_type}_{entity_id}_composite_risk",
                current_value=self._calculate_current_risk_level(predictions),
                forecast_periods=forecast_periods,
                risk_scenarios=risk_scenarios,
                mitigation_impact=mitigation_impact,
                confidence_level=confidence_level
            )
            
        except Exception as e:
            logger.error(f"Error generating risk forecast: {str(e)}")
            raise
    
    def _get_entity_metrics(
        self,
        entity_type: str,
        entity_id: str
    ) -> List[MetricDefinition]:
        """Get relevant metrics for an entity"""
        
        # This would be configured based on entity type
        # For now, return common risk metrics
        
        return self.db.query(MetricDefinition).filter(
            MetricDefinition.active == True,
            MetricDefinition.category.in_(['risk', 'security', 'compliance'])
        ).limit(10).all()
    
    def _calculate_risk_scenarios(
        self,
        predictions: Dict[str, PredictionOutput]
    ) -> Dict[str, float]:
        """Calculate probability of different risk scenarios"""
        
        scenarios = {
            "best_case": 0.15,      # All predictions in positive direction
            "likely_case": 0.60,    # Most predictions as expected
            "worst_case": 0.20,     # Multiple negative predictions
            "black_swan": 0.05      # Extreme unexpected events
        }
        
        # Adjust probabilities based on prediction confidence and trends
        declining_count = sum(
            1 for pred in predictions.values()
            if pred.trend_direction == TrendDirection.DECLINING
        )
        
        if declining_count > len(predictions) * 0.5:
            scenarios["worst_case"] += 0.15
            scenarios["likely_case"] -= 0.10
            scenarios["best_case"] -= 0.05
        
        return scenarios
    
    def _calculate_mitigation_impact(
        self,
        entity_type: str,
        entity_id: str,
        predictions: Dict[str, PredictionOutput]
    ) -> Dict[str, float]:
        """Calculate expected impact of various mitigation strategies"""
        
        # Sample mitigation strategies and their expected impact
        mitigations = {
            "enhanced_monitoring": 0.15,       # 15% risk reduction
            "additional_controls": 0.25,       # 25% risk reduction
            "staff_training": 0.10,            # 10% risk reduction
            "technology_upgrade": 0.30,        # 30% risk reduction
            "process_improvement": 0.20,       # 20% risk reduction
            "vendor_diversification": 0.18,    # 18% risk reduction
            "incident_response_plan": 0.12     # 12% risk reduction
        }
        
        # Adjust based on prediction trends
        high_risk_predictions = sum(
            1 for pred in predictions.values()
            if len(pred.risk_indicators) > 2
        )
        
        if high_risk_predictions > len(predictions) * 0.3:
            # Increase mitigation effectiveness for high-risk situations
            mitigations = {k: min(1.0, v * 1.2) for k, v in mitigations.items()}
        
        return mitigations
    
    def _generate_forecast_periods(
        self,
        predictions: Dict[str, PredictionOutput],
        forecast_horizon_days: int
    ) -> List[Dict[str, Any]]:
        """Generate forecast data for different time periods"""
        
        periods = []
        
        # Generate weekly forecasts
        for week in range(0, forecast_horizon_days, 7):
            period_start = datetime.utcnow() + timedelta(days=week)
            period_end = period_start + timedelta(days=7)
            
            # Aggregate predictions for this period
            period_risk = np.mean([
                pred.predicted_value for pred in predictions.values()
            ]) if predictions else 0.0
            
            periods.append({
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "risk_level": period_risk,
                "confidence": np.mean([
                    pred.confidence_score for pred in predictions.values()
                ]) if predictions else 0.0,
                "key_risks": self._identify_key_risks_for_period(predictions, week)
            })
        
        return periods
    
    def _identify_key_risks_for_period(
        self,
        predictions: Dict[str, PredictionOutput],
        week_offset: int
    ) -> List[str]:
        """Identify key risks for a specific time period"""
        
        key_risks = []
        
        for metric_id, prediction in predictions.items():
            if len(prediction.risk_indicators) > 1:
                key_risks.extend(prediction.risk_indicators[:2])
        
        return list(set(key_risks))[:5]  # Return top 5 unique risks
    
    def _calculate_current_risk_level(
        self,
        predictions: Dict[str, PredictionOutput]
    ) -> float:
        """Calculate current composite risk level"""
        
        if not predictions:
            return 0.0
        
        # Simple average of predicted values
        risk_values = [pred.predicted_value for pred in predictions.values()]
        return np.mean(risk_values)


# Supporting Classes

class FeatureEngineering:
    """Feature engineering for predictive models"""
    
    def create_features(self, historical_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create features from historical data"""
        
        df = pd.DataFrame(historical_data)
        
        if df.empty:
            return df
        
        # Time-based features
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['quarter'] = df['timestamp'].dt.quarter
        
        # Lag features
        df['value_lag_1'] = df['value'].shift(1)
        df['value_lag_7'] = df['value'].shift(7)
        df['value_lag_30'] = df['value'].shift(30)
        
        # Rolling statistics
        df['rolling_mean_7'] = df['value'].rolling(window=7).mean()
        df['rolling_std_7'] = df['value'].rolling(window=7).std()
        df['rolling_mean_30'] = df['value'].rolling(window=30).mean()
        
        # Trend features
        df['value_change'] = df['value'].diff()
        df['value_change_pct'] = df['value'].pct_change()
        
        return df.fillna(0)


class AnomalyDetector:
    """Anomaly detection for metric values"""
    
    def __init__(self):
        self.baseline_cache = {}
    
    def detect_anomaly(
        self,
        metric_id: str,
        value: float,
        timestamp: datetime
    ) -> float:
        """Detect if a value is anomalous (returns anomaly score 0-1)"""
        
        # Get baseline statistics
        baseline = self._get_baseline_stats(metric_id)
        
        if not baseline:
            return 0.0  # No baseline available
        
        # Calculate z-score
        z_score = abs(value - baseline['mean']) / baseline['std'] if baseline['std'] > 0 else 0
        
        # Convert to anomaly score (0-1)
        anomaly_score = min(1.0, z_score / 3.0)  # 3-sigma rule
        
        return anomaly_score
    
    def _get_baseline_stats(self, metric_id: str) -> Optional[Dict[str, float]]:
        """Get baseline statistics for a metric"""
        
        if metric_id in self.baseline_cache:
            return self.baseline_cache[metric_id]
        
        # In practice, would calculate from historical data
        # For demo, using placeholder values
        baseline = {
            'mean': 50.0,
            'std': 15.0,
            'min': 0.0,
            'max': 100.0
        }
        
        self.baseline_cache[metric_id] = baseline
        return baseline


class TrendAnalyzer:
    """Trend analysis for time series data"""
    
    def analyze_trend(self, historical_data: List[Dict[str, Any]]) -> TrendDirection:
        """Analyze trend direction in historical data"""
        
        if len(historical_data) < 3:
            return TrendDirection.STABLE
        
        values = [d['value'] for d in historical_data]
        
        # Simple linear regression
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        # Calculate relative slope
        mean_value = np.mean(values)
        relative_slope = slope / mean_value if mean_value != 0 else 0
        
        # Calculate volatility
        volatility = np.std(values) / mean_value if mean_value != 0 else 0
        
        # Determine trend
        if volatility > 0.3:
            return TrendDirection.VOLATILE
        elif relative_slope > 0.05:
            return TrendDirection.IMPROVING
        elif relative_slope < -0.05:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.STABLE


class TimeSeriesModel:
    """Simple time series prediction model"""
    
    def __init__(self):
        self.parameters = {}
        self.accuracy = 0.0
    
    def train(self, features: pd.DataFrame):
        """Train the time series model"""
        
        if features.empty or 'value' not in features.columns:
            self.accuracy = 0.0
            return
        
        # Simple moving average model for demo
        self.parameters['window'] = 7
        self.parameters['trend'] = features['value'].diff().mean()
        
        # Calculate simple accuracy
        if len(features) > 7:
            predicted = features['value'].rolling(window=7).mean().shift(1)
            actual = features['value']
            errors = abs(predicted - actual).dropna()
            self.accuracy = max(0.0, 1.0 - (errors.mean() / actual.mean())) if actual.mean() != 0 else 0.0
        else:
            self.accuracy = 0.5  # Default accuracy
    
    def predict(self, horizon_days: int) -> float:
        """Generate prediction for future period"""
        
        # Simple trend-based prediction
        base_value = 50.0  # Placeholder
        trend = self.parameters.get('trend', 0.0)
        
        prediction = base_value + (trend * horizon_days)
        
        return max(0.0, prediction)  # Ensure non-negative
    
    def get_confidence_interval(
        self,
        prediction: float,
        confidence_level: float
    ) -> Tuple[float, float]:
        """Get confidence interval for prediction"""
        
        # Simple confidence interval based on historical volatility
        margin = prediction * 0.2  # 20% margin for demo
        
        return (
            max(0.0, prediction - margin),
            prediction + margin
        )