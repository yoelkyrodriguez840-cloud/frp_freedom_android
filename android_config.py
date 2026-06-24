"""
Android Configuration - Configuración específica para Android
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional

from .platform_adapter import platform
from .adapters.filesystem_adapter import FilesystemAdapter


class AndroidConfig:
    """Configuration manager for Android"""

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
        self.config_path = self.fs.get_config_path()

        # Configuración por defecto para Android
        self.default_config = {
            "app": {
                "version": "1.0.0",
                "debug_mode": False,
                "platform": "android",
                "name": "FRP Freedom",
            },
            "android": {
                "use_tcp_adb": True,
                "auto_detect_network": True,
                "scan_network_range": "192.168.1.0/24",
                "usb_timeout": 5000,
                "tcp_timeout": 3000,
                "max_scan_retries": 3,
            },
            "security": {
                "encrypt_logs": True,
                "audit_trail": True,
                "max_attempts_per_device": 3,
                "log_retention_days": 30,
            },
            "bypass_methods": {
                "adb_exploits": True,
                "interface_exploits": True,
                "system_exploits": False,
                "hardware_methods": False,
            },
            "ui": {"theme": "dark", "show_advanced_options": False, "animations_enabled": True},
            "network": {"timeout": 30, "retry_count": 3, "use_proxy": False},
        }

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        config_data = self.fs.read_file(self.config_path)

        if config_data:
            try:
                loaded = yaml.safe_load(config_data)
                if loaded:
                    return self._merge_configs(self.default_config, loaded)
            except Exception as e:
                print(f"Error loading config: {e}")

        # Save default config
        self._save_config(self.default_config)
        return self.default_config.copy()

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            yaml_content = yaml.dump(config, default_flow_style=False, indent=2)
            return self.fs.write_file(self.config_path, yaml_content)
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation"""
        keys = key_path.split(".")
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> bool:
        """Set configuration value using dot notation"""
        keys = key_path.split(".")
        config = self.config
        try:
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            config[keys[-1]] = value
            return self._save_config(self.config)
        except Exception as e:
            print(f"Error setting config: {e}")
            return False

    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get("app.debug_mode", False)

    def use_tcp_adb(self) -> bool:
        """Check if TCP ADB should be used"""
        return self.get("android.use_tcp_adb", True)

    def get_encryption_key(self) -> Optional[bytes]:
        """Get or generate encryption key"""
        key_file = self.fs.base_dir / ".key"
        try:
            if key_file.exists():
                with open(key_file, "rb") as f:
                    return f.read()
            else:
                from cryptography.fernet import Fernet

                key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(key)
                return key
        except:
            return None


# Instancia global
config = AndroidConfig()
