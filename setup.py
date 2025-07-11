#!/usr/bin/env python3
"""
Setup script for Automated Telegram Marketing System
"""
import os
import sys
import shutil
import secrets
import subprocess
from pathlib import Path
from typing import Dict, Any

def print_banner():
    """Print setup banner"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║        🚀 AUTOMATED TELEGRAM MARKETING SYSTEM SETUP 🚀               ║
    ║                                                                       ║
    ║     Turn your Telegram bot into an automated sales machine!          ║
    ║     Generate $100+ daily profit selling OpenRouter API tokens        ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """)

def check_prerequisites():
    """Check system prerequisites"""
    print("🔍 Checking system prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        sys.exit(1)
    
    # Check Docker
    try:
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
        print("✅ Docker is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker is not installed or not in PATH")
        print("Please install Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)
    
    # Check Docker Compose
    try:
        subprocess.run(['docker-compose', '--version'], check=True, capture_output=True)
        print("✅ Docker Compose is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker Compose is not installed or not in PATH")
        print("Please install Docker Compose: https://docs.docker.com/compose/install/")
        sys.exit(1)
    
    print("✅ All prerequisites met!")

def generate_secure_password(length: int = 32) -> str:
    """Generate a secure password"""
    return secrets.token_urlsafe(length)

def get_user_input(prompt: str, default: str = "", required: bool = False) -> str:
    """Get user input with validation"""
    while True:
        if default:
            value = input(f"{prompt} [{default}]: ").strip()
            if not value:
                value = default
        else:
            value = input(f"{prompt}: ").strip()
        
        if required and not value:
            print("❌ This field is required!")
            continue
        
        return value

def collect_configuration() -> Dict[str, Any]:
    """Collect configuration from user"""
    print("\n📋 Let's configure your automated marketing system...")
    
    config = {}
    
    # Telegram Configuration
    print("\n🔸 TELEGRAM CONFIGURATION")
    print("Get your API credentials from https://my.telegram.org/apps")
    
    config['TELEGRAM_API_ID'] = get_user_input("Telegram API ID", required=True)
    config['TELEGRAM_API_HASH'] = get_user_input("Telegram API Hash", required=True)
    config['TELEGRAM_BOT_TOKEN'] = get_user_input("Telegram Bot Token", required=True)
    config['TELEGRAM_PHONE_NUMBER'] = get_user_input("Your Telegram Phone Number (with country code)", required=True)
    config['BOT_USERNAME'] = get_user_input("Bot Username (without @)", required=True)
    
    # Webhook Configuration
    print("\n🔸 WEBHOOK CONFIGURATION")
    config['WEBHOOK_HOST'] = get_user_input("Webhook Host (e.g., https://yourdomain.com)", required=True)
    config['WEBHOOK_SECRET_TOKEN'] = generate_secure_password(32)
    
    # AI Configuration
    print("\n🔸 AI CONFIGURATION")
    print("Get your OpenAI API key from https://platform.openai.com/api-keys")
    config['OPENAI_API_KEY'] = get_user_input("OpenAI API Key", required=True)
    config['OPENAI_MODEL'] = get_user_input("OpenAI Model", default="gpt-4")
    
    # OpenRouter Configuration
    print("\n🔸 OPENROUTER CONFIGURATION")
    print("Get your OpenRouter API key from https://openrouter.ai/")
    config['OPENROUTER_API_KEY'] = get_user_input("OpenRouter API Key", required=True)
    config['OPENROUTER_PROFIT_MARGIN'] = get_user_input("Profit Margin %", default="300")
    
    # Payment Configuration
    print("\n🔸 PAYMENT CONFIGURATION")
    print("Get your Stripe keys from https://dashboard.stripe.com/apikeys")
    config['STRIPE_SECRET_KEY'] = get_user_input("Stripe Secret Key", required=True)
    config['STRIPE_PUBLISHABLE_KEY'] = get_user_input("Stripe Publishable Key", required=True)
    config['STRIPE_WEBHOOK_SECRET'] = get_user_input("Stripe Webhook Secret", required=True)
    
    # Database Configuration
    print("\n🔸 DATABASE CONFIGURATION")
    config['DATABASE_TYPE'] = get_user_input("Database Type", default="postgresql")
    config['POSTGRES_PASSWORD'] = generate_secure_password(16)
    
    # Redis Configuration
    config['REDIS_PASSWORD'] = generate_secure_password(16)
    
    # Security Configuration
    config['JWT_SECRET_KEY'] = generate_secure_password(32)
    
    # Admin Configuration
    print("\n🔸 ADMIN CONFIGURATION")
    admin_ids = get_user_input("Admin Telegram IDs (comma-separated)", required=True)
    config['ADMIN_TELEGRAM_IDS'] = admin_ids
    
    # Marketing Configuration
    print("\n🔸 MARKETING CONFIGURATION")
    config['DAILY_REVENUE_TARGET'] = get_user_input("Daily Revenue Target ($)", default="100")
    config['DAILY_PROSPECT_LIMIT'] = get_user_input("Daily Prospect Limit", default="100")
    config['TARGET_TELEGRAM_GROUPS'] = get_user_input(
        "Target Telegram Groups (comma-separated)", 
        default="AI_developers,MachineLearning,OpenAI_community,ChatGPT_developers"
    )
    
    # Monitoring Configuration
    config['GRAFANA_PASSWORD'] = generate_secure_password(16)
    
    return config

def create_env_file(config: Dict[str, Any]):
    """Create .env file from configuration"""
    print("\n📝 Creating .env file...")
    
    # Read the template
    template_path = Path('.env.example')
    if not template_path.exists():
        print("❌ .env.example file not found!")
        sys.exit(1)
    
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Replace placeholders with actual values
    env_content = template
    for key, value in config.items():
        placeholder = f"your_{key.lower().replace('_', '_')}"
        env_content = env_content.replace(placeholder, str(value))
    
    # Write the .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        'data',
        'logs',
        'temp',
        'backups',
        'data/sessions',
        'data/models',
        'data/exports',
        'docker',
        'scripts',
        'grafana/dashboards',
        'grafana/datasources'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created successfully!")

def create_docker_files():
    """Create additional Docker configuration files"""
    print("\n🐳 Creating Docker configuration files...")
    
    # Create healthcheck script
    healthcheck_script = '''#!/bin/bash
curl -f http://localhost:8000/health || exit 1
'''
    
    with open('docker/healthcheck.sh', 'w') as f:
        f.write(healthcheck_script)
    
    os.chmod('docker/healthcheck.sh', 0o755)
    
    # Create crontab
    crontab_content = '''# Automated backup every 6 hours
0 */6 * * * cd /app && python -c "from services.database import DatabaseService; import asyncio; asyncio.run(DatabaseService().backup_database())"

# Performance optimization every day at 2 AM
0 2 * * * cd /app && python -c "from services.analytics import AnalyticsService; import asyncio; asyncio.run(AnalyticsService().optimize_performance())"

# Clean up old logs every week
0 0 * * 0 find /app/logs -name "*.log" -mtime +7 -delete
'''
    
    with open('docker/crontab', 'w') as f:
        f.write(crontab_content)
    
    # Create nginx configuration
    nginx_conf = '''events {
    worker_connections 1024;
}

http {
    upstream app {
        server telegram_marketing_app:8000;
    }
    
    server {
        listen 80;
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}'''
    
    with open('nginx.conf', 'w') as f:
        f.write(nginx_conf)
    
    print("✅ Docker configuration files created!")

def create_startup_scripts():
    """Create startup and management scripts"""
    print("\n📜 Creating startup scripts...")
    
    # Create start script
    start_script = '''#!/bin/bash
echo "🚀 Starting Telegram Marketing System..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please run setup.py first."
    exit 1
fi

# Build and start services
docker-compose build
docker-compose up -d

echo "✅ System started successfully!"
echo "🌐 Access the dashboard at: http://localhost:3000"
echo "📊 View metrics at: http://localhost:9090"
echo "🔍 Check logs with: docker-compose logs -f telegram_marketing_app"
'''
    
    with open('start.sh', 'w') as f:
        f.write(start_script)
    
    os.chmod('start.sh', 0o755)
    
    # Create stop script
    stop_script = '''#!/bin/bash
echo "🛑 Stopping Telegram Marketing System..."
docker-compose down
echo "✅ System stopped successfully!"
'''
    
    with open('stop.sh', 'w') as f:
        f.write(stop_script)
    
    os.chmod('stop.sh', 0o755)
    
    # Create update script
    update_script = '''#!/bin/bash
echo "🔄 Updating Telegram Marketing System..."
git pull origin main
docker-compose build
docker-compose up -d
echo "✅ System updated successfully!"
'''
    
    with open('update.sh', 'w') as f:
        f.write(update_script)
    
    os.chmod('update.sh', 0o755)
    
    print("✅ Startup scripts created!")

def setup_monitoring():
    """Setup monitoring configuration"""
    print("\n📊 Setting up monitoring...")
    
    # Create Prometheus configuration
    prometheus_config = '''global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'telegram-marketing'
    static_configs:
      - targets: ['telegram_marketing_app:8000']
'''
    
    with open('prometheus.yml', 'w') as f:
        f.write(prometheus_config)
    
    # Create Grafana datasource
    grafana_datasource = '''apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
'''
    
    with open('grafana/datasources/prometheus.yml', 'w') as f:
        f.write(grafana_datasource)
    
    print("✅ Monitoring configuration created!")

def display_success_message():
    """Display success message and next steps"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║                   🎉 SETUP COMPLETED SUCCESSFULLY! 🎉                 ║
    ║                                                                       ║
    ║   Your automated Telegram marketing system is ready to launch!       ║
    ║                                                                       ║
    ║   NEXT STEPS:                                                         ║
    ║   1. Start the system: ./start.sh                                     ║
    ║   2. Monitor performance: http://localhost:3000                       ║
    ║   3. Check system health: http://localhost:8000/health                ║
    ║   4. View logs: docker-compose logs -f telegram_marketing_app         ║
    ║                                                                       ║
    ║   TARGET: $100+ daily profit from OpenRouter API token sales         ║
    ║                                                                       ║
    ║   Need help? Check the README.md file or contact support.            ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """)

def main():
    """Main setup function"""
    print_banner()
    
    try:
        check_prerequisites()
        config = collect_configuration()
        create_env_file(config)
        setup_directories()
        create_docker_files()
        create_startup_scripts()
        setup_monitoring()
        display_success_message()
        
        print("\n✅ Setup completed successfully!")
        print("\n🚀 Ready to start your automated marketing system!")
        print("Run: ./start.sh")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()