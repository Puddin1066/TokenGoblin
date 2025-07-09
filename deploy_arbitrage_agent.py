#!/usr/bin/env python3
"""
AI Token Arbitrage Agent - Deployment Script
==========================================

This script integrates the arbitrage agent with the existing AiogramShopBot
and sets up the complete system for $10K monthly revenue generation.

Usage:
    python deploy_arbitrage_agent.py --setup
    python deploy_arbitrage_agent.py --start
    python deploy_arbitrage_agent.py --monitor
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ArbitrageDeployer:
    """Deployment and integration manager for AI Arbitrage Agent"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / "config.json"
        self.aiogramshopbot_integrated = False
        
    def check_system_requirements(self) -> bool:
        """Check if system meets requirements"""
        logger.info("🔍 Checking system requirements...")
        
        # Check Python version
        if sys.version_info < (3, 9):
            logger.error("❌ Python 3.9+ required")
            return False
        
        # Check required services
        services = {
            'redis': 'redis-server --version',
            'postgresql': 'psql --version',
            'docker': 'docker --version'
        }
        
        for service, command in services.items():
            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    logger.warning(f"⚠️ {service} not found - will use Docker")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.warning(f"⚠️ {service} not available - will use Docker")
        
        logger.info("✅ System requirements check complete")
        return True
    
    def install_dependencies(self):
        """Install required Python packages"""
        logger.info("📦 Installing dependencies...")
        
        try:
            # Install core requirements
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 
                'requirements_arbitrage.txt'
            ], check=True)
            
            # Install AiogramShopBot requirements if exists
            if (self.project_root / "requirements.txt").exists():
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', 
                    'requirements.txt'
                ], check=True)
            
            logger.info("✅ Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)
    
    def setup_configuration(self):
        """Setup configuration files"""
        logger.info("⚙️ Setting up configuration...")
        
        # Check if config exists
        if not self.config_file.exists():
            # Copy example config
            example_config = self.project_root / "config.example.json"
            if example_config.exists():
                import shutil
                shutil.copy(example_config, self.config_file)
                logger.info("📄 Created config.json from example")
            else:
                self.create_default_config()
        
        # Validate configuration
        if self.validate_config():
            logger.info("✅ Configuration validated")
        else:
            logger.error("❌ Configuration validation failed")
            self.interactive_config_setup()
    
    def create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "telegram_bot_token": "",
            "openrouter_api_key": "",
            "binance_api_key": "",
            "binance_secret_key": "",
            "coingecko_api_key": "",
            "etherscan_api_key": "",
            "database_url": "postgresql://arbitrage:password@localhost:5432/arbitrage_db",
            "redis_url": "redis://localhost:6379/0",
            "min_profit_threshold": 0.02,
            "max_position_size": 1000.0,
            "stop_loss_percentage": 0.05,
            "monthly_revenue_target": 10000.0,
            "daily_revenue_target": 333.33,
            "basic_tier_markup": 0.30,
            "premium_tier_markup": 0.20,
            "enterprise_tier_markup": 0.15
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        logger.info("📄 Created default config.json")
    
    def validate_config(self) -> bool:
        """Validate configuration file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            required_keys = [
                'telegram_bot_token',
                'openrouter_api_key',
                'database_url',
                'redis_url'
            ]
            
            missing_keys = [key for key in required_keys if not config.get(key)]
            
            if missing_keys:
                logger.warning(f"⚠️ Missing required config keys: {missing_keys}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Config validation error: {e}")
            return False
    
    def interactive_config_setup(self):
        """Interactive configuration setup"""
        logger.info("🔧 Starting interactive configuration...")
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        except:
            config = {}
        
        # Essential API keys
        api_keys = {
            'telegram_bot_token': 'Telegram Bot Token (from @BotFather)',
            'openrouter_api_key': 'OpenRouter API Key (for AI models)',
            'binance_api_key': 'Binance API Key (for trading)',
            'binance_secret_key': 'Binance Secret Key',
            'coingecko_api_key': 'CoinGecko API Key (optional)',
            'etherscan_api_key': 'Etherscan API Key (optional)'
        }
        
        print("\n" + "="*60)
        print("🔑 API KEYS CONFIGURATION")
        print("="*60)
        
        for key, description in api_keys.items():
            current_value = config.get(key, "")
            if not current_value or current_value.startswith("YOUR_"):
                value = input(f"\n{description}:\n> ").strip()
                if value:
                    config[key] = value
                else:
                    logger.warning(f"⚠️ Skipping {key} - can be set later")
        
        # Database configuration
        print("\n" + "="*60)
        print("🗄️ DATABASE CONFIGURATION")
        print("="*60)
        
        use_docker = input("\nUse Docker for services? (y/n) [y]: ").strip().lower()
        if use_docker in ['', 'y', 'yes']:
            config['database_url'] = "postgresql://arbitrage:password@localhost:5432/arbitrage_db"
            config['redis_url'] = "redis://localhost:6379/0"
            logger.info("📦 Will use Docker for database services")
        else:
            db_url = input("Database URL: ").strip()
            if db_url:
                config['database_url'] = db_url
            
            redis_url = input("Redis URL: ").strip()
            if redis_url:
                config['redis_url'] = redis_url
        
        # Save configuration
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info("✅ Configuration saved")
    
    def setup_database(self):
        """Setup database and Redis"""
        logger.info("🗄️ Setting up database...")
        
        # Check if we should use Docker
        docker_compose_file = self.project_root / "docker-compose.arbitrage.yml"
        
        if not docker_compose_file.exists():
            self.create_docker_compose()
        
        try:
            # Start database services
            subprocess.run([
                'docker-compose', '-f', str(docker_compose_file), 'up', '-d'
            ], check=True)
            
            logger.info("✅ Database services started")
            
            # Wait for services to be ready
            logger.info("⏳ Waiting for services to be ready...")
            time.sleep(10)
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Docker setup failed: {e}")
            logger.info("💡 Please ensure PostgreSQL and Redis are running manually")
    
    def create_docker_compose(self):
        """Create Docker Compose file for services"""
        docker_compose_content = """
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: arbitrage_postgres
    environment:
      POSTGRES_DB: arbitrage_db
      POSTGRES_USER: arbitrage
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
  
  redis:
    image: redis:7-alpine
    container_name: arbitrage_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
  
  # Optional: PostgreSQL Admin Interface
  pgadmin:
    image: dpage/pgadmin4
    container_name: arbitrage_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@arbitrage.local
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "8080:80"
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
"""
        
        with open(self.project_root / "docker-compose.arbitrage.yml", 'w') as f:
            f.write(docker_compose_content.strip())
        
        logger.info("📄 Created Docker Compose file")
    
    def integrate_with_aiogramshopbot(self):
        """Integrate with existing AiogramShopBot"""
        logger.info("🔗 Integrating with AiogramShopBot...")
        
        # Check if AiogramShopBot files exist
        aiogram_files = [
            'bot.py',
            'config.py',
            'db.py',
            'crypto_api/CryptoApiManager.py'
        ]
        
        existing_files = [f for f in aiogram_files if (self.project_root / f).exists()]
        
        if existing_files:
            logger.info(f"✅ Found AiogramShopBot files: {existing_files}")
            self.aiogramshopbot_integrated = True
            
            # Create integration bridge
            self.create_integration_bridge()
        else:
            logger.warning("⚠️ AiogramShopBot files not found - running standalone")
    
    def create_integration_bridge(self):
        """Create bridge between arbitrage agent and AiogramShopBot"""
        bridge_content = '''
"""
AiogramShopBot Integration Bridge
===============================

This module bridges the AI Arbitrage Agent with the existing AiogramShopBot
payment system and customer management.
"""

import sys
from pathlib import Path

# Import existing AiogramShopBot modules
try:
    from crypto_api.CryptoApiManager import CryptoApiManager
    from models.user import User
    from models.buy import Buy
    from services.user import UserService
    from services.payment import PaymentService
    
    AIOGRAMSHOPBOT_AVAILABLE = True
except ImportError:
    AIOGRAMSHOPBOT_AVAILABLE = False

class AiogramShopBotBridge:
    """Bridge for integrating with existing AiogramShopBot"""
    
    def __init__(self):
        self.crypto_manager = CryptoApiManager() if AIOGRAMSHOPBOT_AVAILABLE else None
        
    async def process_crypto_payment(self, user_id: int, amount: float, currency: str):
        """Process cryptocurrency payment through AiogramShopBot"""
        if not AIOGRAMSHOPBOT_AVAILABLE:
            raise NotImplementedError("AiogramShopBot not available")
        
        # Use existing crypto payment system
        result = await self.crypto_manager.create_payment_request(
            user_id=user_id,
            amount=amount,
            currency=currency
        )
        
        return result
    
    async def get_user_balance(self, user_id: int) -> float:
        """Get user balance from AiogramShopBot database"""
        if not AIOGRAMSHOPBOT_AVAILABLE:
            return 0.0
        
        user = await UserService.get_user_by_telegram_id(user_id)
        return float(user.balance) if user else 0.0
    
    async def update_user_balance(self, user_id: int, amount: float):
        """Update user balance in AiogramShopBot database"""
        if not AIOGRAMSHOPBOT_AVAILABLE:
            return
        
        await UserService.add_balance(user_id, amount)
'''
        
        bridge_file = self.project_root / "aiogramshopbot_bridge.py"
        with open(bridge_file, 'w') as f:
            f.write(bridge_content)
        
        logger.info("🌉 Created AiogramShopBot integration bridge")
    
    def start_services(self):
        """Start all services"""
        logger.info("🚀 Starting AI Arbitrage Agent...")
        
        # Start the arbitrage agent
        try:
            cmd = [
                sys.executable,
                'arbitrage_agent.py',
                '--config', str(self.config_file)
            ]
            
            logger.info(f"🎯 Starting with command: {' '.join(cmd)}")
            
            # Start in background for production, foreground for development
            if '--daemon' in sys.argv:
                subprocess.Popen(cmd)
                logger.info("✅ AI Arbitrage Agent started in daemon mode")
            else:
                subprocess.run(cmd)
                
        except KeyboardInterrupt:
            logger.info("⛔ Stopped by user")
        except Exception as e:
            logger.error(f"❌ Failed to start agent: {e}")
    
    def monitor_system(self):
        """Monitor system performance and revenue"""
        logger.info("📊 Starting system monitor...")
        
        try:
            # Load configuration
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            target_monthly = config.get('monthly_revenue_target', 10000)
            target_daily = target_monthly / 30
            
            print("\n" + "="*60)
            print("📊 AI ARBITRAGE AGENT MONITOR")
            print("="*60)
            print(f"🎯 Monthly Target: ${target_monthly:,.2f}")
            print(f"📅 Daily Target: ${target_daily:.2f}")
            print("="*60)
            
            # Monitor loop
            while True:
                try:
                    # Check system status
                    print(f"\n⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print("🔍 System Status: ✅ Running")
                    
                    # TODO: Add actual revenue monitoring
                    # This would connect to the database and check:
                    # - Current revenue
                    # - Active trades
                    # - Customer count
                    # - System performance
                    
                    print("💰 Revenue Tracking: Integration needed")
                    print("📈 Active Arbitrage: Monitoring enabled")
                    print("👥 Customer Count: Database required")
                    
                    time.sleep(60)  # Check every minute
                    
                except KeyboardInterrupt:
                    break
                    
        except Exception as e:
            logger.error(f"❌ Monitor error: {e}")
    
    def show_status(self):
        """Show current system status"""
        print("\n" + "="*60)
        print("📊 AI ARBITRAGE AGENT STATUS")
        print("="*60)
        
        # Check configuration
        config_status = "✅ Valid" if self.validate_config() else "❌ Invalid"
        print(f"⚙️ Configuration: {config_status}")
        
        # Check services
        services_status = "✅ Docker" if self.check_docker_services() else "⚠️ Manual"
        print(f"🗄️ Database Services: {services_status}")
        
        # Check integration
        integration_status = "✅ Integrated" if self.aiogramshopbot_integrated else "⚠️ Standalone"
        print(f"🔗 AiogramShopBot: {integration_status}")
        
        # Show revenue target
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            target = config.get('monthly_revenue_target', 10000)
            print(f"🎯 Revenue Target: ${target:,.2f}/month")
        except:
            print("🎯 Revenue Target: Not configured")
        
        print("="*60)
    
    def check_docker_services(self) -> bool:
        """Check if Docker services are running"""
        try:
            result = subprocess.run([
                'docker', 'ps', '--filter', 'name=arbitrage', '--format', 'table {{.Names}}'
            ], capture_output=True, text=True)
            
            return 'arbitrage' in result.stdout
        except:
            return False

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Token Arbitrage Agent Deployment')
    parser.add_argument('--setup', action='store_true', help='Setup the system')
    parser.add_argument('--start', action='store_true', help='Start the agent')
    parser.add_argument('--monitor', action='store_true', help='Monitor system')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    deployer = ArbitrageDeployer()
    
    if args.setup:
        print("\n🚀 AI TOKEN ARBITRAGE AGENT SETUP")
        print("=" * 40)
        
        if not deployer.check_system_requirements():
            sys.exit(1)
        
        deployer.install_dependencies()
        deployer.setup_configuration()
        deployer.setup_database()
        deployer.integrate_with_aiogramshopbot()
        
        print("\n✅ Setup complete!")
        print("🎯 Target: $10,000/month revenue")
        print("📞 Next steps:")
        print("   1. Review config.json")
        print("   2. Add your API keys")
        print("   3. Run: python deploy_arbitrage_agent.py --start")
        
    elif args.start:
        deployer.start_services()
        
    elif args.monitor:
        deployer.monitor_system()
        
    elif args.status:
        deployer.show_status()
        
    else:
        print("🤖 AI Token Arbitrage Agent Deployment Tool")
        print("\nCommands:")
        print("  --setup    Setup the complete system")
        print("  --start    Start the arbitrage agent")
        print("  --monitor  Monitor system performance")
        print("  --status   Show current status")
        print("\nTarget: $10,000 monthly revenue via AI token arbitrage")

if __name__ == "__main__":
    main()