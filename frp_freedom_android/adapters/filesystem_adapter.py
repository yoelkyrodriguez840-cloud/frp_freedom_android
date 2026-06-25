"""
Filesystem Adapter - Sistema de archivos para Android
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, List, Any
import base64

from ..platform_adapter import platform


class FilesystemAdapter:
    """Adaptador de sistema de archivos para Android"""

    def __init__(self):
        self.platform = platform
        self.base_dir = self._get_base_directory()
        self.logs_dir = self.base_dir / "logs"
        self.cache_dir = self.base_dir / "cache"
        self.backup_dir = self.base_dir / "backups"

        # Crear directorios
        self._ensure_directories()

    def _get_base_directory(self) -> Path:
        """Obtener directorio base de la aplicación"""
        if self.platform.is_android():
            try:
                # En Android (Flet), usar directorio de la aplicación
                from android.storage import app_storage_path

                return Path(app_storage_path())
            except:
                # Fallback para Android
                return Path("/data/data/org.frpfreedom.app/files")
        else:
            # Desktop
            return Path.home() / ".frp_freedom_android"

    def _ensure_directories(self):
        """Asegurar que los directorios existen"""
        self.base_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)

    def get_config_path(self) -> Path:
        """Obtener ruta del archivo de configuración"""
        return self.base_dir / "config.yaml"

    def get_logs_path(self) -> Path:
        """Obtener ruta de logs"""
        return self.logs_dir

    def get_cache_path(self) -> Path:
        """Obtener ruta de cache"""
        return self.cache_dir

    def get_backup_path(self) -> Path:
        """Obtener ruta de backups"""
        return self.backup_dir

    def read_file(self, path: Path) -> Optional[str]:
        """Leer archivo de texto"""
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            print(f"Error reading file {path}: {e}")
        return None

    def write_file(self, path: Path, content: str) -> bool:
        """Escribir archivo de texto"""
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file {path}: {e}")
            return False

    def read_binary(self, path: Path) -> Optional[bytes]:
        """Leer archivo binario"""
        try:
            if path.exists():
                with open(path, "rb") as f:
                    return f.read()
        except Exception as e:
            print(f"Error reading binary file {path}: {e}")
        return None

    def write_binary(self, path: Path, data: bytes) -> bool:
        """Escribir archivo binario"""
        try:
            with open(path, "wb") as f:
                f.write(data)
            return True
        except Exception as e:
            print(f"Error writing binary file {path}: {e}")
            return False

    def delete_file(self, path: Path) -> bool:
        """Eliminar archivo"""
        try:
            if path.exists():
                path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting file {path}: {e}")
            return False

    def list_files(self, directory: Path, pattern: str = "*") -> List[Path]:
        """Listar archivos en un directorio"""
        try:
            return list(directory.glob(pattern))
        except Exception as e:
            print(f"Error listing files in {directory}: {e}")
            return []

    def copy_file(self, src: Path, dst: Path) -> bool:
        """Copiar archivo"""
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            print(f"Error copying file {src} to {dst}: {e}")
            return False

    def move_file(self, src: Path, dst: Path) -> bool:
        """Mover archivo"""
        try:
            shutil.move(src, dst)
            return True
        except Exception as e:
            print(f"Error moving file {src} to {dst}: {e}")
            return False

    def get_available_space(self) -> int:
        """Obtener espacio disponible en bytes"""
        try:
            stat = os.statvfs(str(self.base_dir))
            return stat.f_frsize * stat.f_bavail
        except:
            return 0

    def get_total_space(self) -> int:
        """Obtener espacio total en bytes"""
        try:
            stat = os.statvfs(str(self.base_dir))
            return stat.f_frsize * stat.f_blocks
        except:
            return 0

    def clear_cache(self) -> bool:
        """Limpiar directorio de cache"""
        try:
            for item in self.cache_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

    def get_secure_storage_path(self) -> Path:
        """Obtener ruta para almacenamiento seguro"""
        return self.base_dir / "secure"

    def read_secure_data(self, key: str) -> Optional[str]:
        """Leer datos seguros"""
        secure_dir = self.get_secure_storage_path()
        secure_dir.mkdir(exist_ok=True)
        file_path = secure_dir / f"{key}.enc"

        data = self.read_binary(file_path)
        if data:
            try:
                # Simple obfuscation (en producción usar cifrado real)
                decoded = base64.b64decode(data).decode("utf-8")
                return decoded
            except:
                pass
        return None

    def write_secure_data(self, key: str, value: str) -> bool:
        """Escribir datos seguros"""
        secure_dir = self.get_secure_storage_path()
        secure_dir.mkdir(exist_ok=True)
        file_path = secure_dir / f"{key}.enc"

        try:
            # Simple obfuscation (en producción usar cifrado real)
            encoded = base64.b64encode(value.encode("utf-8"))
            return self.write_binary(file_path, encoded)
        except Exception as e:
            print(f"Error writing secure data: {e}")
            return False
