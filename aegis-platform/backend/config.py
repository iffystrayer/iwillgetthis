from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
import json
import os

class Settings(BaseSettings):
    """Comprehensive configuration for Aegis Risk Management Platform"""
    
    # ==============================================
    # Core Application Settings
    # ==============================================
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./aegis_development.db"
    
    # PostgreSQL Configuration (for Docker/Production)
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB_CACHE: int = 1  # Database for LLM caching
    REDIS_DB_SESSION: int = 2  # Database for sessions
    REDIS_DB_TASKS: int = 3  # Database for background tasks
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-here-change-in-production"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"
    ALGORITHM: str = "HS256"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:58533", "https://*.space.minimax.io"]
    
    # ==============================================
    # Production Security Configuration
    # ==============================================
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000
    
    # Session Security
    SESSION_TIMEOUT: int = 3600  # 1 hour
    MAX_CONCURRENT_SESSIONS: int = 5
    SESSION_ENCRYPTION_KEY: str = ""
    
    # Security Headers
    X_FRAME_OPTIONS: str = "DENY"
    X_CONTENT_TYPE_OPTIONS: str = "nosniff" 
    X_XSS_PROTECTION: str = "1; mode=block"
    REFERRER_POLICY: str = "strict-origin-when-cross-origin"
    CONTENT_SECURITY_POLICY: str = "default-src 'self'"
    
    # SSL/TLS Configuration
    SSL_REDIRECT: bool = False
    HSTS_MAX_AGE: int = 31536000  # 1 year
    SSL_CERT_PATH: str = ""
    SSL_KEY_PATH: str = ""
    
    # Database Security
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_SSL_MODE: str = "prefer"
    
    # File Upload Security
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt", "csv", "json", "png", "jpg", "jpeg"]
    UPLOAD_SCAN_ENABLED: bool = False
    VIRUS_SCAN_ENDPOINT: str = ""
    
    # Encryption
    DATA_ENCRYPTION_AT_REST: bool = False
    DATA_ENCRYPTION_IN_TRANSIT: bool = True
    FILE_ENCRYPTION_KEY: str = ""
    BACKUP_ENCRYPTION_KEY: str = ""
    
    # Application Settings
    APP_NAME: str = "Aegis Risk Management Platform"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    
    # ==============================================
    # AI/LLM Core Configuration
    # ==============================================
    
    # AI Features Toggle
    ENABLE_AI_FEATURES: bool = True
    
    # LLM Caching Configuration
    ENABLE_LLM_CACHING: bool = True
    LLM_CACHE_TTL_HOURS: int = 24  # Default TTL for cached responses
    LLM_CACHE_MAX_MEMORY_MB: int = 500  # Maximum memory usage for cache
    LLM_CACHE_CLEANUP_INTERVAL_HOURS: int = 1  # How often to run cleanup
    
    # Provider Management
    DEFAULT_LLM_PROVIDER: str = "openai"
    FALLBACK_LLM_PROVIDERS: Optional[List[str]] = ["litellm", "openrouter"]
    ENABLE_PROVIDER_ROTATION: bool = True
    
    # Cost and Performance
    ENABLE_COST_TRACKING: bool = True
    ENABLE_PERFORMANCE_MONITORING: bool = True
    ENABLE_PROVIDER_HEALTH_CHECKS: bool = True
    COST_OPTIMIZATION: bool = True
    DAILY_COST_LIMIT: float = 100.0
    MONTHLY_AI_BUDGET: float = 1000.0
    PROVIDER_DAILY_LIMITS: Dict[str, float] = {
        "openai": 50.0,
        "anthropic": 30.0,
        "azure_openai": 40.0,
        "gemini": 20.0
    }
    
    # Provider Selection Strategy
    PROVIDER_SELECTION_STRATEGY: str = "balanced"  # cost_optimized, performance_optimized, balanced
    
    # ==============================================
    # Primary Cloud Providers
    # ==============================================
    
    # OpenAI
    ENABLE_OPENAI: bool = True
    OPENAI_API_KEY: str = ""
    OPENAI_ORGANIZATION: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.7
    
    # Azure OpenAI
    ENABLE_AZURE_OPENAI: bool = False
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4-turbo"
    AZURE_OPENAI_MAX_TOKENS: int = 4096
    AZURE_OPENAI_TEMPERATURE: float = 0.7
    
    # Google Gemini
    ENABLE_GEMINI: bool = False
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_MAX_TOKENS: int = 4096
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_PROJECT_ID: Optional[str] = None
    GEMINI_LOCATION: str = "us-central1"
    
    # Anthropic Claude
    ENABLE_ANTHROPIC: bool = False
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    
    # ==============================================
    # Router and Aggregation Services
    # ==============================================
    
    # LiteLLM
    ENABLE_LITELLM: bool = False
    LITELLM_API_KEY: str = ""
    LITELLM_MODEL: str = "gpt-3.5-turbo"
    LITELLM_MAX_TOKENS: int = 4096
    LITELLM_TEMPERATURE: float = 0.7
    
    # OpenRouter
    ENABLE_OPENROUTER: bool = False
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.1-8b-instruct:free"
    OPENROUTER_MAX_TOKENS: int = 4096
    OPENROUTER_TEMPERATURE: float = 0.7
    OPENROUTER_SITE_URL: str = "https://aegis.example.com"
    OPENROUTER_APP_NAME: str = "Aegis Risk Platform"
    
    # Together AI
    ENABLE_TOGETHER: bool = False
    TOGETHER_API_KEY: str = ""
    TOGETHER_MODEL: str = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    
    # ==============================================
    # Specialized Providers
    # ==============================================
    
    # DeepSeek
    ENABLE_DEEPSEEK: bool = False
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_MAX_TOKENS: int = 4096
    DEEPSEEK_TEMPERATURE: float = 0.7
    
    # Cohere
    ENABLE_COHERE: bool = False
    COHERE_API_KEY: str = ""
    COHERE_MODEL: str = "command-r-plus"
    
    # Mistral AI
    ENABLE_MISTRAL: bool = False
    MISTRAL_API_KEY: str = ""
    MISTRAL_MODEL: str = "mistral-large-latest"
    
    # Hugging Face
    ENABLE_HUGGINGFACE: bool = False
    HUGGINGFACE_API_KEY: str = ""
    HUGGINGFACE_MODEL: str = "meta-llama/Meta-Llama-3.1-70B-Instruct"
    
    # ==============================================
    # Local and Self-Hosted Providers
    # ==============================================
    
    # Ollama
    ENABLE_OLLAMA: bool = False
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    OLLAMA_MAX_TOKENS: int = 4096
    OLLAMA_TEMPERATURE: float = 0.7
    
    # LM Studio
    ENABLE_LMSTUDIO: bool = False
    LMSTUDIO_BASE_URL: str = "http://localhost:1234/v1"
    LMSTUDIO_MODEL: str = "local-model"
    
    # Text Generation WebUI
    ENABLE_TEXTGEN_WEBUI: bool = False
    TEXTGEN_WEBUI_BASE_URL: str = "http://localhost:5000"
    TEXTGEN_WEBUI_MODEL: str = "local-model"
    
    # ==============================================
    # Custom Endpoints
    # ==============================================
    
    CUSTOM_LLM_ENDPOINTS: str = "{}"  # JSON string
    
    # ==============================================
    # External Integrations
    # ==============================================
    
    # ==============================================
    # OAuth2/OIDC Authentication
    # ==============================================
    ENABLE_OAUTH: bool = True
    FRONTEND_URL: str = "http://localhost:58533"

    # Microsoft Azure AD / Entra ID
    ENABLE_AZURE_AUTH: bool = False
    AZURE_CLIENT_ID: str = ""
    AZURE_CLIENT_SECRET: str = ""
    AZURE_TENANT_ID: str = ""

    # Google Workspace
    ENABLE_GOOGLE_AUTH: bool = False
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Okta
    ENABLE_OKTA_AUTH: bool = False
    OKTA_CLIENT_ID: str = ""
    OKTA_CLIENT_SECRET: str = ""
    OKTA_DOMAIN: str = ""  # your-domain.okta.com

    # Auth0 (optional)
    ENABLE_AUTH0: bool = False
    AUTH0_CLIENT_ID: str = ""
    AUTH0_CLIENT_SECRET: str = ""
    AUTH0_DOMAIN: str = ""
    
    # OpenVAS
    ENABLE_OPENVAS: bool = False
    OPENVAS_HOST: str = "localhost"
    OPENVAS_PORT: int = 9390
    OPENVAS_USERNAME: str = "admin"
    OPENVAS_PASSWORD: str = ""
    OPENVAS_TIMEOUT: int = 300
    
    # OpenCTI
    ENABLE_OPENCTI: bool = False
    OPENCTI_URL: str = "http://localhost:8080"
    OPENCTI_TOKEN: str = ""
    OPENCTI_VERIFY_SSL: bool = True
    
    # ==============================================
    # Email Configuration
    # ==============================================

    ENABLE_EMAIL: bool = False
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: str = "noreply@aegis.example.com"
    
    # ==============================================
    # File Storage
    # ==============================================
    
    UPLOAD_PATH: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "txt", "csv", "json"]
    
    # ==============================================
    # Logging and Monitoring
    # ==============================================
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/aegis.log"
    ENABLE_AUDIT_LOGGING: bool = True
    
    # Health Checks
    HEALTH_CHECK_INTERVAL: int = 60
    PROVIDER_HEALTH_CHECK_INTERVAL: int = 300
    
    # ==============================================
    # Performance and Limits
    # ==============================================
    
    # Rate Limiting
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Request Timeouts
    DEFAULT_REQUEST_TIMEOUT: int = 60
    LLM_REQUEST_TIMEOUT: int = 120
    
    # Cost Limits
    DAILY_COST_LIMIT: float = 50.0
    PROVIDER_DAILY_COST_LIMITS: str = '{"openai": 20.0, "anthropic": 15.0, "azure_openai": 25.0}'
    
    # ==============================================
    # Development and Testing
    # ==============================================
    
    ENABLE_MOCK_PROVIDERS: bool = False
    ENABLE_DETAILED_LOGGING: bool = False
    SKIP_PROVIDER_HEALTH_CHECKS: bool = False
    TEST_MODE: bool = False
    TEST_DATABASE_URL: str = "sqlite:///./test_aegis.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    @property
    def get_fallback_providers(self) -> List[str]:
        """Get fallback providers as a list"""
        if isinstance(self.FALLBACK_LLM_PROVIDERS, str):
            try:
                return json.loads(self.FALLBACK_LLM_PROVIDERS)
            except:
                return []
        return self.FALLBACK_LLM_PROVIDERS or []
    
    @property
    def get_custom_endpoints(self) -> Dict[str, Any]:
        """Get custom endpoints as a dictionary"""
        try:
            return json.loads(self.CUSTOM_LLM_ENDPOINTS)
        except:
            return {}
    
    @property
    def get_provider_cost_limits(self) -> Dict[str, float]:
        """Get provider cost limits as a dictionary"""
        try:
            return json.loads(self.PROVIDER_DAILY_COST_LIMITS)
        except:
            return {}
    
    @property
    def get_database_url(self) -> str:
        """Get the appropriate database URL - PostgreSQL if configured, otherwise SQLite"""
        if self.POSTGRES_USER and self.POSTGRES_PASSWORD and self.POSTGRES_DB:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return self.DATABASE_URL
    
    @property
    def allowed_origins(self) -> List[str]:
        """Get CORS allowed origins"""
        return self.CORS_ORIGINS
    
    @property 
    def jwt_access_token_expire_minutes(self) -> int:
        """Alias for JWT access token expiry"""
        return self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    @property
    def jwt_secret_key(self) -> str:
        """Alias for JWT secret key"""
        return self.JWT_SECRET_KEY
    
    @property
    def jwt_algorithm(self) -> str:
        """Alias for JWT algorithm"""
        return self.JWT_ALGORITHM
    
    @property
    def jwt_refresh_token_expire_days(self) -> int:
        """Alias for JWT refresh token expiry"""
        return self.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    
    @property
    def max_file_size(self) -> int:
        """Alias for max file size"""
        return self.MAX_FILE_SIZE
    
    @property
    def uploads_dir(self) -> str:
        """Alias for uploads directory"""
        return self.UPLOAD_PATH

# Global settings instance
settings = Settings()
