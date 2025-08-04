# Aegis Risk Management Platform

## 🛡️ Enterprise Cybersecurity Risk Management Platform

The Aegis Risk Management Platform is a comprehensive, AI-powered cybersecurity risk management solution designed for enterprise organizations. It provides complete risk assessment, compliance management, incident tracking, and advanced analytics capabilities.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Documentation](#documentation)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Support](#support)

## ✨ Features

### Core Risk Management
- **Asset Management**: Comprehensive inventory and classification
- **Risk Assessment**: AI-powered risk identification and scoring
- **Compliance Frameworks**: NIST CSF, CIS Controls, ISO 27001, SOC 2
- **Incident Management**: Complete incident lifecycle tracking
- **Task Management**: POA&M (Plan of Action & Milestones)
- **Evidence Management**: Secure document and artifact storage

### Advanced Capabilities
- **AI-Powered Analytics**: Machine learning-driven insights
- **Predictive Risk Analytics**: Forecast future risk trends
- **Executive Dashboards**: Real-time C-level reporting
- **Advanced Reporting Engine**: Automated compliance reports
- **Third-Party Risk Management**: Vendor and supply chain security
- **Security Training Management**: Awareness programs and tracking
- **Business Continuity**: Disaster recovery planning

### Integration & APIs
- **REST API**: Complete programmatic access
- **External Integrations**: OpenVAS, OpenCTI, SIEM systems
- **Real-time Dashboards**: Interactive data visualization
- **Automated Workflows**: Configurable business processes

## 🏗️ Architecture

### Technology Stack
- **Backend**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL / SQLite
- **AI/ML**: OpenAI GPT, Anthropic Claude, Local models
- **Authentication**: JWT-based security
- **Documentation**: OpenAPI/Swagger
- **Deployment**: Docker, Kubernetes ready

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Backend       │
│   Dashboard     │◄──►│   (FastAPI)     │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Database      │    │   AI Services   │
                       │   (PostgreSQL)  │    │   (Multi-model) │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 12+ (or SQLite for development)
- Docker and Docker Compose (recommended)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aegis-platform
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the platform**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Admin Interface: http://localhost:3000

### Manual Installation

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env  # Configure your environment
   python main.py
   ```

2. **Database Setup**
   ```bash
   # The database tables are created automatically on startup
   # For custom migrations, see docs/deployment.md
   ```

## 📚 Documentation

### For Users
- [**User Guide**](./user-guide.md) - Complete end-user documentation
- [**Dashboard Guide**](./dashboard-guide.md) - Using dashboards and analytics
- [**Compliance Guide**](./compliance-guide.md) - Framework implementation
- [**Reporting Guide**](./reporting-guide.md) - Generating and scheduling reports

### For Administrators
- [**Admin Guide**](./admin-guide.md) - System administration
- [**API Reference**](./api-reference.md) - Complete API documentation
- [**Deployment Guide**](./deployment-guide.md) - Production deployment
- [**Security Guide**](./security-guide.md) - Security configuration
- [**Integration Guide**](./integration-guide.md) - External system integration

### For Developers
- [**Developer Guide**](./developer-guide.md) - Development setup and guidelines
- [**API Development**](./api-development.md) - Extending the API
- [**Database Schema**](./database-schema.md) - Data model documentation
- [**Testing Guide**](./testing-guide.md) - Testing procedures

## 📖 API Reference

The Aegis Platform provides a comprehensive REST API with the following endpoints:

### Core Endpoints
- **Authentication**: `/api/v1/auth/*` - User authentication and authorization
- **Users**: `/api/v1/users/*` - User management
- **Assets**: `/api/v1/assets/*` - Asset inventory and management
- **Risks**: `/api/v1/risks/*` - Risk assessment and tracking
- **Assessments**: `/api/v1/assessments/*` - Compliance assessments
- **Tasks**: `/api/v1/tasks/*` - Task and POA&M management
- **Evidence**: `/api/v1/evidence/*` - Document and evidence management

### Advanced Endpoints
- **Analytics**: `/api/v1/analytics/*` - Advanced analytics and reporting
- **Dashboards**: `/api/v1/dashboards/*` - Dashboard configuration
- **Reports**: `/api/v1/reports/*` - Report generation and management
- **AI Services**: `/api/v1/ai/*` - AI-powered features
- **Integrations**: `/api/v1/integrations/*` - External system integration
- **Frameworks**: `/api/v1/frameworks/*` - Compliance framework management

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚢 Deployment

### Development Environment
```bash
# Using Docker Compose
docker-compose -f docker-compose.dev.yml up -d

# Or manual setup
cd backend && python main.py
```

### Production Environment
```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or Kubernetes
kubectl apply -f k8s/
```

### Environment Configuration
Key environment variables:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT signing key
- `OPENAI_API_KEY`: OpenAI integration (optional)
- `ANTHROPIC_API_KEY`: Anthropic Claude integration (optional)

See [Deployment Guide](./deployment-guide.md) for complete configuration options.

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key authentication for integrations
- Session management and timeout

### Data Protection
- Encryption at rest and in transit
- Audit logging for all operations
- Data retention and privacy controls
- Secure file upload and storage

### Compliance
- SOC 2 Type II ready
- GDPR compliance features
- HIPAA security controls
- FedRAMP moderate baseline alignment

## 🧪 Testing

### Running Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/

# All tests with coverage
pytest --cov=. tests/
```

### Test Coverage
Current test coverage: 85%+
- Unit tests: Core business logic
- Integration tests: API endpoints
- E2E tests: Complete workflows

## 📊 Monitoring & Observability

### Health Checks
- `/health` - Basic health status
- `/health/detailed` - Comprehensive system status
- Database connectivity monitoring
- External service health checks

### Metrics & Logging
- Structured logging with correlation IDs
- Prometheus metrics export
- OpenTelemetry tracing support
- Performance monitoring

## 🤝 Support

### Getting Help
- **Documentation**: Complete guides in `/docs`
- **API Reference**: Interactive Swagger documentation
- **GitHub Issues**: Bug reports and feature requests
- **Community**: Discussion forums and support

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

### License
This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

## 📋 Changelog

### Version 1.0.0 (Current)
- Complete risk management platform
- AI-powered analytics engine
- Advanced reporting and dashboards
- Multi-framework compliance support
- Enterprise-ready security features

See [CHANGELOG.md](../CHANGELOG.md) for detailed release notes.

---

**Aegis Risk Management Platform** - Securing your digital future with intelligent risk management.