"""
Filesystem Adapter - Sistema de archivos para Android
"""

import os
import json
import shutil
import sys
from pathlib import Path
from typing import Optional, List, Any
import base64

from ..platform_adapter import platform


class FilesystemAdapter:
    """Adaptador de sistema de archivos para Android"""

    def __init__(self):
        self.platform = platform
        print("📁 Inicializando FilesystemAdapter...")
        self.base_dir = self._get_base_directory()
        self.logs_dir = self.base_dir / "logs"
        self.cache_dir = self.base_dir / "cache"
        self.backup_dir = self.base_dir / "backups"
        self.secure_dir = self.base_dir / "secure"
        self.config_dir = self.base_dir / "config"
        self.temp_dir = self.base_dir / "temp"

        # Crear directorios
        self._ensure_directories()
        print(f"✅ FilesystemAdapter inicializado en: {self.base_dir}")

    def _get_base_directory(self) -> Path:
        """Obtener directorio base de la aplicación"""
        # PRIMERO: Verificar si estamos en Android de forma directa
        is_android = self._is_definitely_android()

        if is_android:
            print("🔍 Detectado entorno Android - usando directorio de la aplicación")
            return self._get_android_directory()
        else:
            print("💻 Entorno Desktop - usando ~/.frp_freedom_android")
            return Path.home() / ".frp_freedom_android"

    def _is_definitely_android(self) -> bool:
        """Determinar si definitivamente estamos en Android"""
        # Usar el platform adapter
        if self.platform.is_android():
            return True

        # Verificaciones adicionales directas
        # 1. Variable de entorno de Flet
        if os.environ.get("FLET_APP") == "true":
            return True

        if os.environ.get("FLET_APP_PATH"):
            return True

        # 2. Verificar path de Android
        if "android" in sys.platform:
            return True

        # 3. Verificar módulos de Android
        try:
            import android

            return True
        except ImportError:
            pass

        # 4. Verificar directorio típico de Android
        if os.path.exists("/data/data") and os.path.exists("/system"):
            return True

        return False

    def _get_android_directory(self) -> Path:
        """Obtener directorio válido para Android con múltiples fallbacks"""
        # 1. Intentar obtener de la variable de entorno de Flet
        flet_app_path = os.environ.get("FLET_APP_PATH")
        if flet_app_path:
            path = Path(flet_app_path)
            print(f"✅ Usando FLET_APP_PATH: {path}")
            return path

        # 2. Intentar usar android.storage
        try:
            from android.storage import app_storage_path

            path = Path(app_storage_path())
            print(f"✅ Usando android.storage: {path}")
            return path
        except ImportError:
            pass

        # 3. Intentar usar jnius para obtener el directorio de la aplicación
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            context = PythonActivity.mActivity
            files_dir = context.getFilesDir()
            if files_dir:
                path = Path(files_dir.getAbsolutePath())
                print(f"✅ Usando jnius: {path}")
                return path
        except:
            pass

        # 4. Intentar usar el directorio de la aplicación en /data/data/
        try:
            # Obtener el nombre del paquete de la variable de entorno o contexto
            package_name = "com.flet.frp_freedom_android"
            app_dir = Path(f"/data/data/{package_name}/files")
            if app_dir.exists() or app_dir.parent.exists():
                print(f"✅ Usando directorio de paquete: {app_dir}")
                return app_dir
        except:
            pass

        # 5. Fallback - usar /data/local/tmp (tiene permisos en Android)
        fallback_dir = Path("/data/local/tmp/frp_freedom_android")
        try:
            fallback_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Usando fallback temporal: {fallback_dir}")
            return fallback_dir
        except:
            pass

        # 6. Último recurso: usar el directorio de trabajo actual
        current_dir = Path.cwd() / ".frp_freedom_android"
        print(f"⚠️ Usando directorio actual: {current_dir}")
        return current_dir

    def _ensure_directories(self):
        """Asegurar que los directorios existen"""
        directories = [
            self.base_dir,
            self.logs_dir,
            self.cache_dir,
            self.backup_dir,
            self.secure_dir,
            self.config_dir,
            self.temp_dir,
        ]

        for directory in directories:
            if not directory.exists():
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    print(f"  ✅ Directorio creado: {directory}")
                except PermissionError as e:
                    print(f"  ❌ Error de permisos al crear {directory}: {e}")
                    # Intentar con un directorio alternativo
                    self._try_alternative_directory(directory)
                except Exception as e:
                    print(f"  ❌ Error al crear {directory}: {e}")
                    self._try_alternative_directory(directory)

    def _try_alternative_directory(self, original_path: Path):
        """Intentar crear un directorio alternativo si hay problemas de permisos"""
        try:
            # Intentar en /data/local/tmp (tiene permisos en Android)
            alt_base = Path("/data/local/tmp/frp_freedom_android")
            alt_dir = alt_base / original_path.name
            alt_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Usando directorio alternativo: {alt_dir}")

            # Actualizar la referencia
            if original_path == self.base_dir:
                self.base_dir = alt_dir.parent
            elif original_path == self.logs_dir:
                self.logs_dir = alt_dir
            elif original_path == self.cache_dir:
                self.cache_dir = alt_dir
            elif original_path == self.backup_dir:
                self.backup_dir = alt_dir
            elif original_path == self.secure_dir:
                self.secure_dir = alt_dir
            elif original_path == self.config_dir:
                self.config_dir = alt_dir
            elif original_path == self.temp_dir:
                self.temp_dir = alt_dir
        except Exception as e:
            print(f"  ❌ No se pudo crear directorio alternativo: {e}")
            # Último intento: usar un directorio en el sistema de archivos actual
            try:
                alt_dir = Path.cwd() / ".frp_freedom_android" / original_path.name
                alt_dir.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ Usando directorio local: {alt_dir}")
            except:
                pass

    def get_config_path(self) -> Path:
        """Obtener ruta del archivo de configuración"""
        return self.config_dir / "config.yaml"

    def get_logs_path(self) -> Path:
        """Obtener ruta de logs"""
        return self.logs_dir

    def get_cache_path(self) -> Path:
        """Obtener ruta de cache"""
        return self.cache_dir

    def get_backup_path(self) -> Path:
        """Obtener ruta de backups"""
        return self.backup_dir

    def get_temp_path(self) -> Path:
        """Obtener ruta temporal"""
        return self.temp_dir

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
            path.parent.mkdir(parents=True, exist_ok=True)
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
            path.parent.mkdir(parents=True, exist_ok=True)
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
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            print(f"Error copying file {src} to {dst}: {e}")
            return False

    def move_file(self, src: Path, dst: Path) -> bool:
        """Mover archivo"""
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
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

    def clear_temp(self) -> bool:
        """Limpiar directorio temporal"""
        try:
            for item in self.temp_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            return True
        except Exception as e:
            print(f"Error clearing temp: {e}")
            return False

    def get_secure_storage_path(self) -> Path:
        """Obtener ruta para almacenamiento seguro"""
        return self.secure_dir

    def read_secure_data(self, key: str) -> Optional[str]:
        """Leer datos seguros"""
        secure_dir = self.get_secure_storage_path()
        secure_dir.mkdir(parents=True, exist_ok=True)
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
        secure_dir.mkdir(parents=True, exist_ok=True)
        file_path = secure_dir / f"{key}.enc"

        try:
            # Simple obfuscation (en producción usar cifrado real)
            encoded = base64.b64encode(value.encode("utf-8"))
            return self.write_binary(file_path, encoded)
        except Exception as e:
            print(f"Error writing secure data: {e}")
            return False

    def is_path_accessible(self, path: Path) -> bool:
        """Verificar si una ruta es accesible"""
        try:
            return os.access(str(path), os.R_OK | os.W_OK)
        except:
            return False

    def get_directory_size(self, path: Path) -> int:
        """Obtener tamaño de un directorio en bytes"""
        total = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
        except:
            pass
        return total
