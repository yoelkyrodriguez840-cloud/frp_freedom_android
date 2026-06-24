"""
Logger Android - Sistema de logging para Android
"""

import logging
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from cryptography.fernet import Fernet

from ..adapters.filesystem_adapter import FilesystemAdapter
from ..android_config import config


class EncryptedFileHandler(logging.Handler):
    """Handler de logging con cifrado"""

    def __init__(self, file_path: Path, encryption_key: bytes):
        super().__init__()
        self.file_path = file_path
        self.cipher = Fernet(encryption_key)

    def emit(self, record):
        """Emitir registro cifrado"""
        try:
            msg = self.format(record)
            encrypted = self.cipher.encrypt(msg.encode("utf-8"))
            with open(self.file_path, "ab") as f:
                f.write(encrypted + b"\n")
        except Exception as e:
            self.handleError(record)


class LoggerAndroid:
    """Sistema de logging para Android"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.fs = FilesystemAdapter()
        self.config = config

        self.logs_dir = self.fs.get_logs_path()
        self.log_level = logging.DEBUG if self.config.is_debug() else logging.INFO

        self._setup_logging()

    def _setup_logging(self):
        """Configurar sistema de logging"""
        # Logger principal
        self.logger = logging.getLogger("frp_freedom")
        self.logger.setLevel(self.log_level)
        self.logger.handlers.clear()

        # Formato
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Handler de consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler de archivo (cifrado si está habilitado)
        if self.config.get("security.encrypt_logs", True):
            key = self.config.get_encryption_key()
            if key:
                log_file = self.logs_dir / "frp_freedom.log"
                file_handler = EncryptedFileHandler(log_file, key)
            else:
                file_handler = self._create_plain_file_handler()
        else:
            file_handler = self._create_plain_file_handler()

        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Logger de auditoría
        self.audit_logger = logging.getLogger("frp_freedom.audit")
        self.audit_logger.setLevel(logging.INFO)
        self.audit_logger.handlers.clear()

        audit_file = self.logs_dir / "audit.log"
        if self.config.get("security.encrypt_logs", True):
            key = self.config.get_encryption_key()
            if key:
                audit_handler = EncryptedFileHandler(audit_file, key)
            else:
                audit_handler = logging.FileHandler(audit_file)
        else:
            audit_handler = logging.FileHandler(audit_file)

        audit_formatter = logging.Formatter(
            "%(asctime)s - AUDIT - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        audit_handler.setFormatter(audit_formatter)
        self.audit_logger.addHandler(audit_handler)

    def _create_plain_file_handler(self) -> logging.Handler:
        """Crear handler de archivo sin cifrar"""
        log_file = self.logs_dir / "frp_freedom.log"
        return logging.FileHandler(log_file)

    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """Log exception message"""
        self.logger.exception(message, *args, **kwargs)

    def audit(self, event_type: str, details: Dict[str, Any]):
        """Log audit event"""
        event = {
            "event_type": event_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "details": details,
        }
        self.audit_logger.info(json.dumps(event))

    def set_level(self, level: int):
        """Establecer nivel de log"""
        self.log_level = level
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)

    def get_logs(self, limit: int = 100) -> List[str]:
        """Obtener logs recientes"""
        log_file = self.logs_dir / "frp_freedom.log"
        if not log_file.exists():
            return []

        try:
            logs = []
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return lines[-limit:]
        except Exception as e:
            print(f"Error reading logs: {e}")
            return []


# Instancia global
logger = LoggerAndroid()


class AuditLoggerAndroid:
    """Logger de auditoría para Android"""

    def __init__(self):
        self.logger = logger

    def log_device_detection(self, device_info: Dict[str, Any]):
        """Log detección de dispositivo"""
        self.logger.audit(
            "device_detection",
            {
                "device": device_info.get("model", "Unknown"),
                "serial": device_info.get("serial", "Unknown")[:8] + "****",
            },
        )

    def log_bypass_attempt(self, device_info: Dict, method: str, success: bool, error: str = None):
        """Log intento de bypass"""
        self.logger.audit(
            "bypass_attempt",
            {
                "device": device_info.get("model", "Unknown"),
                "method": method,
                "success": success,
                "error": error,
            },
        )

    def log_bypass_result(
        self, device_id: str, success: bool, methods_used: list, execution_time: float
    ):
        """Log resultado de bypass"""
        self.logger.audit(
            "bypass_result",
            {
                "device_id": device_id[:8] + "****",
                "success": success,
                "methods": methods_used,
                "execution_time": execution_time,
            },
        )

    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log evento general"""
        self.logger.audit(event_type, details)
