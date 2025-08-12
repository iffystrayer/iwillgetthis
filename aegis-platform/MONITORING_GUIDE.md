# Aegis Platform Monitoring Guide

## Overview
The Aegis Platform includes comprehensive monitoring infrastructure with Prometheus, Grafana, and Alertmanager for production-grade observability.

## Monitoring Stack Components

### 1. Prometheus (Metrics Collection)
- **Location**: Container `aegis-prometheus`  
- **Port**: 9090 (internal)
- **Configuration**: `monitoring/prometheus.yml`
- **Data Storage**: Persistent volume with 30-day retention

**Monitored Metrics**:
- HTTP request rates and response times
- System resource usage (CPU, memory, disk)
- Database connection and query performance  
- Authentication attempts and failures
- Business logic metrics (risks, assessments, tasks)
- AI/LLM service performance

### 2. Grafana (Visualization)
- **Location**: Container `aegis-grafana`
- **Port**: 3000 (internal), accessible via Nginx proxy
- **Default Credentials**: admin/admin123
- **Dashboard Storage**: Persistent volume

**Pre-configured Dashboards**:
- Aegis Application Metrics
- System Resource Usage
- Database Performance  
- Security Events
- Business Intelligence

### 3. Alertmanager (Alert Management)
- **Location**: `monitoring/alertmanager.yml`
- **Port**: 9093 (internal)
- **Features**: Email, Slack, PagerDuty notifications

**Alert Categories**:
- **Critical**: Service down, high error rates, security breaches
- **Warning**: Performance degradation, resource usage
- **Info**: Business metrics, maintenance events

### 4. Alert Rules
- **Location**: `monitoring/alert_rules/aegis_alerts.yml`
- **Categories**: Application, Infrastructure, Database, Security, Business

## Monitoring Setup

### Prerequisites  
- Docker and Docker Compose
- Persistent volumes for data storage
- Network access between services

### Quick Start
```bash
# Start monitoring services
cd aegis-platform
docker-compose -f docker/docker-compose.yml up -d prometheus grafana

# Validate setup
./scripts/validate-performance.sh
```

### Full Production Setup
```bash  
# Run comprehensive monitoring setup
./scripts/setup-monitoring.sh --domain yourdomain.com --grafana-password <secure-password>

# Validate all components
./scripts/validate-monitoring.sh
```

## Access Points

### Web Interfaces
- **Grafana Dashboards**: https://monitoring.yourdomain.com
- **Prometheus**: http://localhost:9090 (development only)
- **Alertmanager**: http://localhost:9093 (development only)

### API Endpoints
- **Health Check**: `/health`
- **System Metrics**: `/health/metrics`  
- **Application Status**: `/api/v1/health`

## Key Performance Indicators (KPIs)

### System Health
- **Uptime**: > 99.9%
- **Response Time**: < 2 seconds (95th percentile)
- **Error Rate**: < 1%
- **CPU Usage**: < 80%
- **Memory Usage**: < 85%
- **Disk Usage**: < 85%

### Application Performance
- **Authentication Success Rate**: > 99%
- **Database Query Time**: < 500ms
- **API Throughput**: > 100 requests/minute
- **Background Job Processing**: < 5 minute queue time

### Security Metrics
- **Failed Login Rate**: < 5 per minute
- **Security Event Detection**: Real-time alerting
- **SSL Certificate Expiry**: 7-day warning

### Business Metrics
- **Risk Assessment Completion**: Track daily/weekly rates
- **Evidence Upload Success**: > 98%
- **Report Generation Time**: < 30 seconds
- **User Session Duration**: Average tracking

## Alert Configuration

### Notification Channels
1. **Email Notifications**
   - Critical alerts: immediate
   - Warning alerts: grouped (15 min)
   - Info alerts: daily digest

2. **Slack Integration**
   - Real-time critical alerts
   - Channel routing by severity
   - Alert acknowledgment

3. **PagerDuty Integration**  
   - Critical service outages
   - Security incidents
   - Escalation policies

### Alert Thresholds
```yaml
# Application Performance
- High Error Rate: > 5% for 5 minutes
- Slow Response: > 2s (95th percentile) for 10 minutes
- Service Down: No response for 2 minutes

# System Resources  
- High CPU: > 80% for 15 minutes
- High Memory: > 85% for 15 minutes
- Low Disk Space: < 15% available

# Security Events
- Failed Logins: > 50 attempts in 5 minutes
- Unauthorized Access: > 10 403 errors in 2 minutes
- SSL Expiry: Certificate expires in < 7 days
```

## Monitoring Best Practices

### 1. Dashboard Organization
- **Overview Dashboard**: Key metrics at-a-glance
- **Service-Specific**: Detailed metrics per component
- **Infrastructure**: System resource monitoring
- **Business**: KPI and business logic metrics

### 2. Alert Management
- **Severity Levels**: Critical, Warning, Info
- **Alert Routing**: Team-specific notifications
- **Escalation**: Automatic escalation for unacknowledged critical alerts
- **Documentation**: Every alert links to runbook

### 3. Data Retention
- **Metrics**: 30 days high-resolution, 1 year aggregated
- **Logs**: 90 days application logs, 30 days debug logs
- **Dashboards**: Version control and backup
- **Alert History**: 6 months retention for analysis

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Check for memory leaks in application
   - Review database connection pooling
   - Monitor background task accumulation

2. **Slow Database Queries**
   - Review query execution plans
   - Check index usage and optimization
   - Monitor connection pool exhaustion

3. **High Error Rates**
   - Check application logs for error patterns
   - Verify external service availability
   - Review authentication system health

### Monitoring Health Checks
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify Grafana datasources
curl -u admin:admin123 http://localhost:3000/api/datasources

# Test alertmanager
curl http://localhost:9093/api/v1/alerts
```

## Maintenance

### Regular Tasks
- **Weekly**: Review alert accuracy and update thresholds
- **Monthly**: Dashboard optimization and cleanup
- **Quarterly**: Full system performance review
- **Annually**: Monitoring infrastructure upgrades

### Backup Procedures
- Grafana dashboards and datasources
- Prometheus configuration and rules
- Alert manager configuration
- Custom monitoring scripts

## Integration Points

### External Services
- **CI/CD Pipeline**: Deployment health monitoring
- **Cloud Services**: AWS/Azure resource monitoring
- **Security Tools**: SIEM integration
- **Business Systems**: ERP/CRM metric correlation

### Development Workflow
- **Local Development**: Simplified monitoring stack
- **Staging Environment**: Full monitoring pipeline
- **Production**: Comprehensive monitoring with alerting
- **Disaster Recovery**: Cross-region monitoring

## Advanced Features

### Custom Metrics
- Application-specific business metrics
- User behavior analytics
- Performance optimization insights
- Capacity planning data

### Machine Learning Integration
- Anomaly detection for unusual patterns
- Predictive alerting for resource exhaustion
- Automated threshold adjustment
- Trend analysis and forecasting

## Support and Documentation

### Resources
- **Runbooks**: `/docs/runbooks/`
- **Configuration**: `/monitoring/`
- **Scripts**: `/scripts/`
- **Dashboards**: `/monitoring/grafana/dashboards/`

### Getting Help
- **Internal**: Check runbook documentation
- **Community**: Prometheus/Grafana forums
- **Vendor**: Support for licensed components
- **Emergency**: Follow escalation procedures

## Monitoring Maturity Roadmap

### Phase 1: Foundation (Current)
✅ Basic metrics collection  
✅ Essential dashboards  
✅ Critical alerting  
✅ Infrastructure monitoring

### Phase 2: Enhancement
🔄 Application performance monitoring  
🔄 Business intelligence metrics  
🔄 Advanced alerting rules  
🔄 Custom dashboards

### Phase 3: Optimization  
📋 Machine learning integration  
📋 Predictive analytics  
📋 Automated remediation  
📋 Advanced visualization

### Phase 4: Excellence
📋 AI-powered insights  
📋 Cross-platform correlation  
📋 Real-time optimization  
📋 Self-healing systems

---

**Status**: Production Ready ✅  
**Last Updated**: August 2025  
**Next Review**: September 2025