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

        print("⚙️ Inicializando AndroidConfig...")

        # Inicializar el adaptador de archivos
        try:
            self.fs = FilesystemAdapter()
            print("✅ FilesystemAdapter inicializado correctamente")
        except Exception as e:
            print(f"❌ Error inicializando FilesystemAdapter: {e}")
            # Fallback: crear manualmente
            self.fs = self._create_fallback_filesystem()

        # Obtener la ruta del archivo de configuración
        self.config_path = self.fs.get_config_path()
        print(f"📁 Config path: {self.config_path}")

        # Configuración por defecto para Android
        self.default_config = {
            "app": {
                "version": "1.0.0",
                "debug_mode": False,
                "platform": platform.get_platform_name(),
                "name": "FRP Freedom",
                "build_date": "2026-01-01",
            },
            "android": {
                "use_tcp_adb": True,
                "auto_detect_network": True,
                "scan_network_range": "192.168.1.0/24",
                "usb_timeout": 5000,
                "tcp_timeout": 3000,
                "max_scan_retries": 3,
                "base_dir": str(self.fs.base_dir),
                "logs_dir": str(self.fs.logs_dir),
                "cache_dir": str(self.fs.cache_dir),
            },
            "security": {
                "encrypt_logs": True,
                "audit_trail": True,
                "max_attempts_per_device": 3,
                "log_retention_days": 30,
                "secure_storage": str(self.fs.secure_dir),
            },
            "bypass_methods": {
                "adb_exploits": True,
                "interface_exploits": True,
                "system_exploits": False,
                "hardware_methods": False,
            },
            "ui": {
                "theme": "dark",
                "show_advanced_options": False,
                "animations_enabled": True,
                "language": "es",
            },
            "network": {
                "timeout": 30,
                "retry_count": 3,
                "use_proxy": False,
                "proxy_host": "",
                "proxy_port": 0,
            },
            "logging": {
                "level": "INFO",
                "max_file_size": 10485760,  # 10MB
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

        # Cargar configuración
        self.config = self._load_config()

        # Verificar que el directorio base existe
        self._verify_directories()

        print("✅ Configuración cargada correctamente")

    def _create_fallback_filesystem(self) -> FilesystemAdapter:
        """Crear un FilesystemAdapter de respaldo si falla la inicialización"""
        print("⚠️ Creando FilesystemAdapter de respaldo...")
        try:
            # Crear un adaptador simple manualmente
            class FallbackFilesystem:
                def __init__(self):
                    # Usar un directorio en /data/local/tmp o el directorio actual
                    fallback_path = Path("/data/local/tmp/frp_freedom_android")
                    if not fallback_path.exists():
                        try:
                            fallback_path.mkdir(parents=True, exist_ok=True)
                        except:
                            fallback_path = Path.cwd() / ".frp_freedom_android"
                            fallback_path.mkdir(parents=True, exist_ok=True)

                    self.base_dir = fallback_path
                    self.logs_dir = fallback_path / "logs"
                    self.cache_dir = fallback_path / "cache"
                    self.backup_dir = fallback_path / "backups"
                    self.secure_dir = fallback_path / "secure"
                    self.config_dir = fallback_path / "config"
                    self.temp_dir = fallback_path / "temp"

                    # Crear directorios
                    for d in [
                        self.logs_dir,
                        self.cache_dir,
                        self.backup_dir,
                        self.secure_dir,
                        self.config_dir,
                        self.temp_dir,
                    ]:
                        try:
                            d.mkdir(exist_ok=True)
                        except:
                            pass

                def get_config_path(self):
                    return self.config_dir / "config.yaml"

                def read_file(self, path):
                    try:
                        if path.exists():
                            with open(path, "r") as f:
                                return f.read()
                    except:
                        pass
                    return None

                def write_file(self, path, content):
                    try:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        with open(path, "w") as f:
                            f.write(content)
                        return True
                    except:
                        return False

            return FallbackFilesystem()
        except Exception as e:
            print(f"❌ Error creando FilesystemAdapter de respaldo: {e}")
            # Último recurso: usar un objeto simple con métodos básicos
            return self._create_minimal_filesystem()

    def _create_minimal_filesystem(self):
        """Crear un sistema de archivos mínimo"""

        class MinimalFilesystem:
            def __init__(self):
                self.base_dir = Path.cwd()
                self.config_dir = self.base_dir

            def get_config_path(self):
                return self.base_dir / "config.yaml"

            def read_file(self, path):
                try:
                    if path.exists():
                        with open(path, "r") as f:
                            return f.read()
                except:
                    pass
                return None

            def write_file(self, path, content):
                try:
                    with open(path, "w") as f:
                        f.write(content)
                    return True
                except:
                    return False

        return MinimalFilesystem()

    def _verify_directories(self):
        """Verificar que los directorios existen y son accesibles"""
        try:
            # Verificar escritura
            test_file = self.fs.base_dir / ".test_write"
            try:
                self.fs.write_file(test_file, "test")
                test_file.unlink()
                print("✅ Directorio base accesible para escritura")
            except:
                print("⚠️ Directorio base NO accesible para escritura")
        except Exception as e:
            print(f"⚠️ Error verificando directorios: {e}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        config_data = self.fs.read_file(self.config_path)

        if config_data:
            try:
                loaded = yaml.safe_load(config_data)
                if loaded:
                    print("✅ Configuración cargada desde archivo")
                    return self._merge_configs(self.default_config, loaded)
            except Exception as e:
                print(f"⚠️ Error loading config: {e}")

        # Save default config
        print("📝 Creando configuración por defecto")
        self._save_config(self.default_config)
        return self.default_config.copy()

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            yaml_content = yaml.dump(config, default_flow_style=False, indent=2, allow_unicode=True)
            result = self.fs.write_file(self.config_path, yaml_content)
            if result:
                print(f"✅ Configuración guardada en {self.config_path}")
            else:
                print(f"❌ Error guardando configuración en {self.config_path}")
            return result
        except Exception as e:
            print(f"❌ Error saving config: {e}")
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

    def reload(self) -> bool:
        """Recargar configuración desde archivo"""
        try:
            config_data = self.fs.read_file(self.config_path)
            if config_data:
                loaded = yaml.safe_load(config_data)
                if loaded:
                    self.config = self._merge_configs(self.default_config, loaded)
                    return True
        except Exception as e:
            print(f"Error reloading config: {e}")
        return False

    def reset_to_defaults(self) -> bool:
        """Restablecer configuración a valores por defecto"""
        self.config = self.default_config.copy()
        return self._save_config(self.config)

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

    def get_log_level(self) -> str:
        """Obtener nivel de log"""
        return self.get("logging.level", "INFO")

    def get_platform(self) -> str:
        """Obtener plataforma actual"""
        return self.get("app.platform", "desktop")

    def is_android(self) -> bool:
        """Verificar si estamos en Android"""
        return self.get_platform() == "android"


# Instancia global
config = AndroidConfig()
