import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
import json
from typing import Optional

import config


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage'):
                log_entry[key] = value
        
        return json.dumps(log_entry)


class ArbitrageLogger:
    """Centralized logging configuration for the AI arbitrage system"""
    
    def __init__(self):
        self.log_level = getattr(config, 'LOG_LEVEL', 'INFO')
        self.log_file = getattr(config, 'LOG_FILE', 'logs/arbitrage.log')
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging for the entire application"""
        
        # Create logs directory if it doesn't exist
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler (structured output for production, simple for development)
        console_handler = logging.StreamHandler(sys.stdout)
        if os.getenv('RUNTIME_ENVIRONMENT') == 'prod':
            console_handler.setFormatter(JSONFormatter())
        else:
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
        
        root_logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
        
        # Error file handler (separate file for errors)
        error_file = str(Path(self.log_file).with_suffix('.error.log'))
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)
        
        # Configure specific loggers
        self.configure_module_loggers()
    
    def configure_module_loggers(self):
        """Configure logging for specific modules"""
        
        # AI Token Service
        ai_logger = logging.getLogger('services.ai_token_service')
        ai_logger.setLevel(logging.INFO)
        
        # OpenRouter API
        api_logger = logging.getLogger('services.openrouter_api')
        api_logger.setLevel(logging.INFO)
        
        # Bot handlers
        handler_logger = logging.getLogger('handlers')
        handler_logger.setLevel(logging.INFO)
        
        # Database operations
        db_logger = logging.getLogger('repositories')
        db_logger.setLevel(logging.INFO)
        
        # Crypto payments
        crypto_logger = logging.getLogger('crypto_api')
        crypto_logger.setLevel(logging.INFO)
        
        # Suppress noisy external libraries
        logging.getLogger('aiogram').setLevel(logging.WARNING)
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def log_function_call(func):
    """Decorator to log function calls with parameters and results"""
    
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Log function entry
        logger.debug(f"Calling {func_name}", extra={
            'function_call': True,
            'args_count': len(args),
            'kwargs_keys': list(kwargs.keys())
        })
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Completed {func_name}", extra={
                'function_call': True,
                'success': True
            })
            return result
        except Exception as e:
            logger.error(f"Error in {func_name}: {str(e)}", extra={
                'function_call': True,
                'error': str(e),
                'error_type': type(e).__name__
            })
            raise
    
    return wrapper


def log_async_function_call(func):
    """Decorator to log async function calls with parameters and results"""
    
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Log function entry
        logger.debug(f"Calling async {func_name}", extra={
            'function_call': True,
            'async': True,
            'args_count': len(args),
            'kwargs_keys': list(kwargs.keys())
        })
        
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Completed async {func_name}", extra={
                'function_call': True,
                'async': True,
                'success': True
            })
            return result
        except Exception as e:
            logger.error(f"Error in async {func_name}: {str(e)}", extra={
                'function_call': True,
                'async': True,
                'error': str(e),
                'error_type': type(e).__name__
            })
            raise
    
    return wrapper


def log_api_call(endpoint: str, method: str = "GET"):
    """Decorator to log API calls"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            logger = get_logger('api_calls')
            
            logger.info(f"API call: {method} {endpoint}", extra={
                'api_call': True,
                'endpoint': endpoint,
                'method': method
            })
            
            try:
                result = await func(*args, **kwargs)
                logger.info(f"API call successful: {method} {endpoint}", extra={
                    'api_call': True,
                    'endpoint': endpoint,
                    'method': method,
                    'success': True
                })
                return result
            except Exception as e:
                logger.error(f"API call failed: {method} {endpoint} - {str(e)}", extra={
                    'api_call': True,
                    'endpoint': endpoint,
                    'method': method,
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                raise
        
        return wrapper
    return decorator


def log_business_event(event_type: str, **kwargs):
    """Log important business events"""
    logger = get_logger('business_events')
    
    logger.info(f"Business event: {event_type}", extra={
        'business_event': True,
        'event_type': event_type,
        **kwargs
    })


def log_performance(operation: str):
    """Decorator to log performance metrics"""
    import time
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            logger = get_logger('performance')
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(f"Performance: {operation}", extra={
                    'performance': True,
                    'operation': operation,
                    'execution_time': execution_time,
                    'success': True
                })
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.warning(f"Performance: {operation} (failed)", extra={
                    'performance': True,
                    'operation': operation,
                    'execution_time': execution_time,
                    'success': False,
                    'error': str(e)
                })
                
                raise
        
        return wrapper
    return decorator


# Initialize logging when module is imported
arbitrage_logger = ArbitrageLogger()


# Example usage functions for different log types
def log_user_action(user_id: int, action: str, **details):
    """Log user actions for analytics"""
    logger = get_logger('user_actions')
    logger.info(f"User action: {action}", extra={
        'user_action': True,
        'user_id': user_id,
        'action': action,
        **details
    })


def log_transaction(transaction_type: str, amount: float, user_id: int, **details):
    """Log financial transactions"""
    logger = get_logger('transactions')
    logger.info(f"Transaction: {transaction_type}", extra={
        'transaction': True,
        'type': transaction_type,
        'amount': amount,
        'user_id': user_id,
        **details
    })


def log_arbitrage_operation(operation: str, model: str, tokens: int, cost: float, sell_price: float, **details):
    """Log arbitrage operations for business intelligence"""
    logger = get_logger('arbitrage')
    profit = sell_price - cost
    margin = (profit / cost) * 100 if cost > 0 else 0
    
    logger.info(f"Arbitrage: {operation}", extra={
        'arbitrage': True,
        'operation': operation,
        'model': model,
        'tokens': tokens,
        'cost': cost,
        'sell_price': sell_price,
        'profit': profit,
        'margin_percent': margin,
        **details
    })


def log_security_event(event_type: str, user_id: Optional[int] = None, ip_address: Optional[str] = None, **details):
    """Log security-related events"""
    logger = get_logger('security')
    logger.warning(f"Security event: {event_type}", extra={
        'security_event': True,
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': ip_address,
        **details
    })


def log_system_metric(metric_name: str, value: float, unit: Optional[str] = None, **tags):
    """Log system metrics for monitoring"""
    logger = get_logger('metrics')
    logger.info(f"Metric: {metric_name}={value}", extra={
        'metric': True,
        'name': metric_name,
        'value': value,
        'unit': unit,
        **tags
    })