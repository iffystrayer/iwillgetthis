#!/usr/bin/env python3
"""
Aegis Platform - Production Secrets Generator

This script generates cryptographically secure secrets for production deployment.
Run this script to create new secrets for each environment.

Usage:
    python3 scripts/generate-secrets.py [--output-format env|json|yaml]

Security Notes:
- Generated secrets are cryptographically secure using Python's secrets module
- Store generated secrets in secure secret management systems (AWS Secrets Manager, etc.)
- Never commit generated secrets to version control
- Rotate secrets regularly according to your security policy
"""

import secrets
import string
import argparse
import json
import yaml
from datetime import datetime, timezone

class SecretGenerator:
    def __init__(self):
        self.secrets = {}
        
    def generate_secret_key(self, length=64):
        """Generate a URL-safe secret key"""
        return secrets.token_urlsafe(length)
    
    def generate_password(self, length=32, include_special=True):
        """Generate a strong password"""
        alphabet = string.ascii_letters + string.digits
        if include_special:
            alphabet += "!@#$%^&*"
        
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def generate_hex_key(self, length=32):
        """Generate a hexadecimal key"""
        return secrets.token_hex(length)
    
    def generate_all_secrets(self):
        """Generate all required secrets for Aegis Platform"""
        
        # Application secrets
        self.secrets['SECRET_KEY'] = self.generate_secret_key(64)
        self.secrets['JWT_SECRET_KEY'] = self.generate_secret_key(64)
        
        # Database secrets
        self.secrets['POSTGRES_PASSWORD'] = self.generate_password(32, include_special=False)
        self.secrets['POSTGRES_SUPERUSER_PASSWORD'] = self.generate_password(32, include_special=False)
        
        # Redis secrets
        self.secrets['REDIS_PASSWORD'] = self.generate_password(32, include_special=False)
        
        # Encryption keys
        self.secrets['BACKUP_ENCRYPTION_KEY'] = self.generate_secret_key(64)
        self.secrets['FILE_ENCRYPTION_KEY'] = self.generate_secret_key(64)
        
        # API keys placeholders (to be filled with actual keys)
        self.secrets['OPENAI_API_KEY'] = 'sk-your-openai-api-key-here'
        self.secrets['ANTHROPIC_API_KEY'] = 'your-anthropic-api-key-here'
        
        # Monitoring keys placeholders
        self.secrets['SENTRY_DSN'] = 'https://your-sentry-dsn@sentry.io/project-id'
        self.secrets['NEW_RELIC_LICENSE_KEY'] = 'your-newrelic-license-key-here'
        self.secrets['DATADOG_API_KEY'] = 'your-datadog-api-key-here'
        
        # Email configuration
        self.secrets['SMTP_PASSWORD'] = 'your-smtp-password-here'
        
        # Integration secrets
        self.secrets['NESSUS_SECRET_KEY'] = self.generate_secret_key(32)
        self.secrets['QUALYS_PASSWORD'] = self.generate_password(24)
        self.secrets['SPLUNK_HEC_TOKEN'] = self.generate_hex_key(32)
        
        # AWS secrets (placeholders)
        self.secrets['AWS_SECRET_ACCESS_KEY'] = self.generate_secret_key(40)
        
        # Session keys
        self.secrets['SESSION_ENCRYPTION_KEY'] = self.generate_secret_key(32)
        
        # Add generation metadata
        self.secrets['_metadata'] = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'generator_version': '1.0.0',
            'environment': 'production',
            'rotation_recommended': True,
            'next_rotation_date': 'Set according to your security policy'
        }
        
        return self.secrets
    
    def output_env_format(self):
        """Output secrets in .env format"""
        output = []
        output.append("# ==============================================")
        output.append("# Aegis Platform - Generated Production Secrets")
        output.append(f"# Generated: {self.secrets['_metadata']['generated_at']}")
        output.append("# ==============================================")
        output.append("# WARNING: These are production secrets!")
        output.append("# - Store securely in production secret management system")
        output.append("# - Never commit to version control")
        output.append("# - Rotate regularly according to security policy")
        output.append("# ==============================================")
        output.append("")
        
        # Group secrets by category
        categories = {
            'Application Security': ['SECRET_KEY', 'JWT_SECRET_KEY', 'SESSION_ENCRYPTION_KEY'],
            'Database': ['POSTGRES_PASSWORD', 'POSTGRES_SUPERUSER_PASSWORD'],
            'Cache': ['REDIS_PASSWORD'],
            'Encryption': ['BACKUP_ENCRYPTION_KEY', 'FILE_ENCRYPTION_KEY'],
            'External APIs': ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY'],
            'Monitoring': ['SENTRY_DSN', 'NEW_RELIC_LICENSE_KEY', 'DATADOG_API_KEY'],
            'Email': ['SMTP_PASSWORD'],
            'Integrations': ['NESSUS_SECRET_KEY', 'QUALYS_PASSWORD', 'SPLUNK_HEC_TOKEN'],
            'Cloud Storage': ['AWS_SECRET_ACCESS_KEY']
        }
        
        for category, keys in categories.items():
            output.append(f"# {category}")
            output.append("# " + "=" * 40)
            for key in keys:
                if key in self.secrets:
                    output.append(f"{key}={self.secrets[key]}")
            output.append("")
        
        return "\n".join(output)
    
    def output_json_format(self):
        """Output secrets in JSON format"""
        return json.dumps(self.secrets, indent=2)
    
    def output_yaml_format(self):
        """Output secrets in YAML format"""
        return yaml.dump(self.secrets, default_flow_style=False, sort_keys=True)

def main():
    parser = argparse.ArgumentParser(description='Generate production secrets for Aegis Platform')
    parser.add_argument('--output-format', choices=['env', 'json', 'yaml'], 
                       default='env', help='Output format for secrets')
    parser.add_argument('--output-file', help='Save secrets to file instead of stdout')
    parser.add_argument('--rotation-notice', action='store_true',
                       help='Include rotation recommendations in output')
    
    args = parser.parse_args()
    
    # Generate secrets
    generator = SecretGenerator()
    secrets_data = generator.generate_all_secrets()
    
    # Format output
    if args.output_format == 'env':
        output = generator.output_env_format()
    elif args.output_format == 'json':
        output = generator.output_json_format()
    elif args.output_format == 'yaml':
        output = generator.output_yaml_format()
    
    # Add rotation notice if requested
    if args.rotation_notice:
        notice = """
# ==============================================
# SECRET ROTATION RECOMMENDATIONS
# ==============================================
# 1. Application secrets: Rotate every 90 days
# 2. Database passwords: Rotate every 60 days  
# 3. API keys: Rotate according to provider recommendations
# 4. Encryption keys: Rotate every 365 days
# 5. Integration secrets: Rotate every 90 days
#
# Set up automated rotation using your secret management system
# ==============================================
"""
        output = notice + output
    
    # Output results
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(output)
        print(f"Secrets generated and saved to: {args.output_file}")
        print("⚠️  SECURITY WARNING: Protect this file and transfer to secure secret management system")
    else:
        print(output)
    
    # Security reminders
    print("\n" + "="*60, file=__import__('sys').stderr)
    print("🔒 SECURITY REMINDERS:", file=__import__('sys').stderr)
    print("1. Store these secrets in a secure secret management system", file=__import__('sys').stderr)
    print("2. Never commit secrets to version control", file=__import__('sys').stderr) 
    print("3. Rotate secrets regularly according to your security policy", file=__import__('sys').stderr)
    print("4. Use separate secrets for each environment", file=__import__('sys').stderr)
    print("5. Monitor secret usage and access logs", file=__import__('sys').stderr)
    print("="*60, file=__import__('sys').stderr)

if __name__ == '__main__':
    main()