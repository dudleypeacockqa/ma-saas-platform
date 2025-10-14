"""
BMAD v6 MCP Server Logging Configuration
"""

import logging
import logging.config
import os
import sys
from datetime import datetime
from pathlib import Path
import json

def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """Setup comprehensive logging configuration."""
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Generate log file names with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s - %(message)s"
            },
            "json": {
                "()": "app.core.logging_config.JSONFormatter"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "detailed",
                "stream": sys.stdout
            },
            "file_all": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": f"{log_dir}/bmad_mcp_server_{timestamp}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "file_error": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": f"{log_dir}/bmad_mcp_server_error_{timestamp}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "file_workflow": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": f"{log_dir}/bmad_workflow_{timestamp}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "file_agent": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": f"{log_dir}/bmad_agent_{timestamp}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "file_security": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "WARNING",
                "formatter": "detailed",
                "filename": f"{log_dir}/bmad_security_{timestamp}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": ["console", "file_all", "file_error"]
            },
            "app.services.workflow_engine": {
                "level": "INFO",
                "handlers": ["file_workflow"],
                "propagate": False
            },
            "app.services.agent_registry": {
                "level": "INFO", 
                "handlers": ["file_agent"],
                "propagate": False
            },
            "app.services.security_manager": {
                "level": "WARNING",
                "handlers": ["file_security"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file_all"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console", "file_all"],
                "propagate": False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("BMAD v6 MCP Server logging initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log directory: {log_path.absolute()}")

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "bmad_version": "6.0.0"
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'project_id'):
            log_entry["project_id"] = record.project_id
        if hasattr(record, 'workflow_name'):
            log_entry["workflow_name"] = record.workflow_name
        if hasattr(record, 'agent_name'):
            log_entry["agent_name"] = record.agent_name
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        return json.dumps(log_entry)

class BMadLoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter for BMAD v6 context."""
    
    def __init__(self, logger, extra=None):
        super().__init__(logger, extra or {})
    
    def process(self, msg, kwargs):
        """Process log message with BMAD context."""
        # Add BMAD context to extra
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        kwargs['extra'].update(self.extra)
        return msg, kwargs

def get_logger(name: str, **context):
    """Get a logger with BMAD context."""
    logger = logging.getLogger(name)
    return BMadLoggerAdapter(logger, context)

def log_workflow_execution(workflow_name: str, project_id: str, status: str, **kwargs):
    """Log workflow execution with structured data."""
    logger = get_logger("app.services.workflow_engine", 
                       workflow_name=workflow_name, 
                       project_id=project_id)
    
    logger.info(f"Workflow {status}: {workflow_name}", extra={
        "event_type": "workflow_execution",
        "status": status,
        **kwargs
    })

def log_agent_invocation(agent_name: str, prompt: str, response_type: str, **kwargs):
    """Log agent invocation with structured data."""
    logger = get_logger("app.services.agent_registry",
                       agent_name=agent_name)
    
    logger.info(f"Agent invoked: {agent_name}", extra={
        "event_type": "agent_invocation",
        "prompt_length": len(prompt),
        "response_type": response_type,
        **kwargs
    })

def log_security_event(event_type: str, user_id: str = None, details: dict = None):
    """Log security events."""
    logger = get_logger("app.services.security_manager",
                       user_id=user_id)
    
    logger.warning(f"Security event: {event_type}", extra={
        "event_type": "security_event",
        "security_event_type": event_type,
        "details": details or {}
    })

def log_api_request(method: str, path: str, status_code: int, duration: float, **kwargs):
    """Log API requests."""
    logger = get_logger("app.api")
    
    level = logging.INFO if status_code < 400 else logging.WARNING
    logger.log(level, f"{method} {path} - {status_code}", extra={
        "event_type": "api_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration * 1000,
        **kwargs
    })

def log_database_operation(operation: str, table: str, success: bool, **kwargs):
    """Log database operations."""
    logger = get_logger("app.db")
    
    level = logging.INFO if success else logging.ERROR
    logger.log(level, f"Database {operation} on {table}", extra={
        "event_type": "database_operation",
        "operation": operation,
        "table": table,
        "success": success,
        **kwargs
    })

def log_integration_event(service: str, event_type: str, success: bool, **kwargs):
    """Log integration events."""
    logger = get_logger("app.services.integration_service")
    
    level = logging.INFO if success else logging.ERROR
    logger.log(level, f"Integration {event_type} with {service}", extra={
        "event_type": "integration_event",
        "service": service,
        "integration_event_type": event_type,
        "success": success,
        **kwargs
    })

# Performance monitoring
class PerformanceLogger:
    """Logger for performance monitoring."""
    
    def __init__(self, operation_name: str, **context):
        self.operation_name = operation_name
        self.context = context
        self.logger = get_logger("app.performance", **context)
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed {self.operation_name}", extra={
                "event_type": "performance",
                "operation": self.operation_name,
                "duration_seconds": duration,
                "success": True
            })
        else:
            self.logger.error(f"Failed {self.operation_name}", extra={
                "event_type": "performance",
                "operation": self.operation_name,
                "duration_seconds": duration,
                "success": False,
                "error": str(exc_val)
            })

# Health check logging
def log_health_check(component: str, status: str, details: dict = None):
    """Log health check results."""
    logger = get_logger("app.health")
    
    level = logging.INFO if status == "healthy" else logging.WARNING
    logger.log(level, f"Health check {component}: {status}", extra={
        "event_type": "health_check",
        "component": component,
        "status": status,
        "details": details or {}
    })

# Startup logging
def log_startup_event(event: str, details: dict = None):
    """Log startup events."""
    logger = get_logger("app.startup")
    
    logger.info(f"Startup: {event}", extra={
        "event_type": "startup",
        "startup_event": event,
        "details": details or {}
    })
