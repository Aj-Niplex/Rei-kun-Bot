"""
Enhanced VPS Logger with health tracking and detailed system logging.
This logger tracks bot health, errors, and important events.
"""

import logging
import sys
import traceback
from pathlib import Path
from typing import Optional

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Multiple log files for different purposes
MAIN_LOG = LOG_DIR / "vps_main.log"
ERROR_LOG = LOG_DIR / "vps_errors.log"
HEALTH_LOG = LOG_DIR / "vps_health.log"


class HealthLogger:
    """
    Dedicated health logger that tracks bot status, module loads, and system health.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("rei_health")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            
            # Health log file
            health_handler = logging.FileHandler(HEALTH_LOG, encoding="utf-8")
            health_handler.setFormatter(formatter)
            health_handler.setLevel(logging.INFO)
            
            # Console output
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            
            self.logger.addHandler(health_handler)
            self.logger.addHandler(console_handler)
    
    def log_startup(self, bot_name: str, bot_id: int, servers: int, users: int):
        """Log successful bot startup."""
        msg = f"🚀 BOT STARTED | {bot_name} (ID: {bot_id}) | Servers: {servers} | Users: {users}"
        self.logger.info(msg)
    
    def log_module_load(self, module_name: str, success: bool, error: Optional[str] = None):
        """Log module load attempt."""
        if success:
            self.logger.info(f"✅ MODULE LOADED | {module_name}")
        else:
            self.logger.error(f"❌ MODULE FAILED | {module_name} | Error: {error}")
    
    def log_command_sync(self, count: int):
        """Log slash command sync."""
        self.logger.info(f"🔄 COMMANDS SYNCED | {count} slash commands registered")
    
    def log_health_check(self, status: str, details: Optional[str] = None):
        """Log periodic health check."""
        msg = f"🏥 HEALTH CHECK | Status: {status}"
        if details:
            msg += f" | {details}"
        self.logger.info(msg)
    
    def log_error(self, error_type: str, error_msg: str, trace: Optional[str] = None):
        """Log an error with optional traceback."""
        msg = f"⚠️ ERROR | {error_type} | {error_msg}"
        self.logger.error(msg)
        if trace:
            self.logger.error(f"Traceback:\n{trace}")
    
    def log_action(self, action: str, user: Optional[str] = None, extra: Optional[str] = None):
        """Log a user action."""
        msg = f"📝 ACTION | {action}"
        if user:
            msg += f" | User: {user}"
        if extra:
            msg += f" | {extra}"
        self.logger.info(msg)


class VPSLogger:
    """
    Main VPS logger for general operations and errors.
    """
    
    def __init__(self):
        # Main logger
        self.main_logger = logging.getLogger("rei_vps_main")
        self.main_logger.setLevel(logging.INFO)
        
        # Error logger
        self.error_logger = logging.getLogger("rei_vps_error")
        self.error_logger.setLevel(logging.ERROR)
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up file and console handlers."""
        formatter = logging.Formatter(
            "%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        
        # Main log file
        if not self.main_logger.handlers:
            main_handler = logging.FileHandler(MAIN_LOG, encoding="utf-8")
            main_handler.setFormatter(formatter)
            
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            
            self.main_logger.addHandler(main_handler)
            self.main_logger.addHandler(console_handler)
        
        # Error log file
        if not self.error_logger.handlers:
            error_handler = logging.FileHandler(ERROR_LOG, encoding="utf-8")
            error_handler.setFormatter(formatter)
            error_handler.setLevel(logging.ERROR)
            
            self.error_logger.addHandler(error_handler)
    
    def info(self, message: str):
        """Log info message."""
        self.main_logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.main_logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """Log error message with optional exception."""
        self.error_logger.error(message)
        if exception:
            tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            self.error_logger.error(f"Exception traceback:\n{tb}")
    
    def critical(self, message: str):
        """Log critical message."""
        self.main_logger.critical(message)
        self.error_logger.critical(message)


# Global instances
health_logger = HealthLogger()
vps_logger = VPSLogger()


# Convenience functions for backward compatibility
def log_action(action: str, user=None, extra: str = ""):
    """Log a user action (backward compatible)."""
    user_text = "Unknown User"
    if user:
        user_text = f"{getattr(user, 'name', 'Unknown')} ({getattr(user, 'id', 'N/A')})"
    
    health_logger.log_action(action, user=user_text, extra=extra or None)


def log_success(action: str, extra: str = ""):
    """Log a successful action."""
    vps_logger.info(f"✅ SUCCESS | {action}" + (f" | {extra}" if extra else ""))


def log_error(action: str, extra: str = ""):
    """Log an error action."""
    vps_logger.error(f"❌ ERROR | {action}" + (f" | {extra}" if extra else ""))


# Export all
__all__ = [
    "health_logger",
    "vps_logger",
    "log_action",
    "log_success",
    "log_error",
    "HealthLogger",
    "VPSLogger",
]
