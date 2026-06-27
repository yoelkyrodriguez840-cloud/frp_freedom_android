"""
Platform Adapter - Abstracción de plataforma para ejecutar en Android o Desktop
"""

import sys
import os
from typing import Optional, List, Tuple
from pathlib import Path


class PlatformAdapter:
    """Abstracts platform-specific operations"""

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

        # Detectar plataforma ANTES de cualquier otra operación
        self._platform = self._detect_platform()
        self._android_imports_loaded = False

        if self.is_android():
            print("📱 Plataforma detectada: Android")
        else:
            print("💻 Plataforma detectada: Desktop")

    def _detect_platform(self) -> str:
        """Detectar plataforma actual de forma robusta"""
        # 1. Verificar variable de entorno de Flet para Android
        if os.environ.get("FLET_APP") == "true":
            print("✅ Detectado Android por FLET_APP=true")
            return "android"

        # 2. Verificar directorio de la aplicación Flet
        if os.environ.get("FLET_APP_PATH"):
            print("✅ Detectado Android por FLET_APP_PATH")
            return "android"

        # 3. Verificar sys.platform
        if "android" in sys.platform:
            print("✅ Detectado Android por sys.platform")
            return "android"

        # 4. Verificar si existe el módulo android
        try:
            import android

            print("✅ Detectado Android por módulo android")
            return "android"
        except ImportError:
            pass

        # 5. Verificar si existe jnius
        try:
            import jnius

            print("✅ Detectado Android por módulo jnius")
            return "android"
        except ImportError:
            pass

        # 6. Verificar si existe el módulo android.storage
        try:
            from android import storage

            print("✅ Detectado Android por módulo android.storage")
            return "android"
        except ImportError:
            pass

        # 7. Verificar si estamos en un entorno Android típico
        if os.path.exists("/system") and os.path.exists("/data"):
            # Podría ser Android, pero verificar más
            if os.path.exists("/system/app") or os.path.exists("/system/framework"):
                # Verificar si hay un contexto de aplicación
                try:
                    from jnius import autoclass

                    PythonActivity = autoclass("org.kivy.android.PythonActivity")
                    print("✅ Detectado Android por contexto jnius")
                    return "android"
                except:
                    pass

        # 8. Verificar variables de entorno típicas de Android
        android_env_vars = ["ANDROID_ROOT", "ANDROID_DATA", "ANDROID_SOCKET"]
        for var in android_env_vars:
            if os.environ.get(var):
                print(f"✅ Detectado Android por variable de entorno {var}")
                return "android"

        # Si no se detectó Android, es desktop
        return "desktop"

    def _init_platform_specific(self):
        """Inicializar componentes específicos de plataforma"""
        self._android_imports_loaded = False

        if self.is_android():
            self._load_android_imports()

    def _load_android_imports(self):
        """Cargar imports específicos de Android"""
        if self._android_imports_loaded:
            return

        try:
            # Intentar cargar jnius para Android
            global jnius
            import jnius
            from jnius import autoclass, cast, PythonJavaClass, java_method

            self._android_imports_loaded = True
            print("✅ Imports de Android cargados correctamente")
        except ImportError as e:
            print(f"⚠️ ADVERTENCIA: No se pudieron cargar los imports de Android: {e}")
            self._android_imports_loaded = False

    def is_android(self) -> bool:
        """Check if running on Android"""
        return self._platform == "android"

    def is_desktop(self) -> bool:
        """Check if running on Desktop"""
        return self._platform == "desktop"

    def get_platform_name(self) -> str:
        """Get platform name"""
        return self._platform

    def get_jnius(self):
        """Obtener módulo jnius si está disponible"""
        if self.is_android():
            try:
                import jnius

                return jnius
            except ImportError:
                return None
        return None

    def get_android_context(self):
        """Obtener contexto de Android"""
        if not self.is_android():
            return None

        jnius = self.get_jnius()
        if jnius:
            try:
                return jnius.autoclass("org.kivy.android.PythonActivity").mActivity
            except:
                return None
        return None

    def get_android_usb_manager(self):
        """Obtener UsbManager de Android"""
        context = self.get_android_context()
        if context:
            try:
                return context.getSystemService("usb")
            except:
                return None
        return None

    def get_app_directory(self) -> Path:
        """Obtener directorio de la aplicación"""
        if self.is_android():
            try:
                # Intentar usar el directorio de Flet
                flet_app_path = os.environ.get("FLET_APP_PATH")
                if flet_app_path:
                    return Path(flet_app_path)

                # En Android (Flet), usar directorio de la aplicación
                from android.storage import app_storage_path

                return Path(app_storage_path())
            except:
                # Intentar usar jnius
                try:
                    from jnius import autoclass

                    PythonActivity = autoclass("org.kivy.android.PythonActivity")
                    context = PythonActivity.mActivity
                    files_dir = context.getFilesDir()
                    if files_dir:
                        return Path(files_dir.getAbsolutePath())
                except:
                    pass

                # Fallback para Android
                return Path("/data/data/org.frpfreedom.app/files")
        else:
            # Desktop
            return Path.home() / ".frp_freedom"

    def is_emulator(self) -> bool:
        """Verificar si estamos en un emulador Android"""
        if not self.is_android():
            return False

        try:
            # Verificar propiedades de emulador
            import subprocess

            result = subprocess.run(["getprop", "ro.kernel.qemu"], capture_output=True, text=True)
            if result.stdout.strip() == "1":
                return True
        except:
            pass
        return False

    def get_device_info(self) -> dict:
        """Obtener información del dispositivo Android"""
        if not self.is_android():
            return {}

        info = {
            "platform": "android",
            "is_emulator": self.is_emulator(),
        }

        try:
            import subprocess

            # Obtener modelo
            result = subprocess.run(["getprop", "ro.product.model"], capture_output=True, text=True)
            info["model"] = result.stdout.strip()

            # Obtener fabricante
            result = subprocess.run(
                ["getprop", "ro.product.manufacturer"], capture_output=True, text=True
            )
            info["manufacturer"] = result.stdout.strip()

            # Obtener versión de Android
            result = subprocess.run(
                ["getprop", "ro.build.version.release"], capture_output=True, text=True
            )
            info["android_version"] = result.stdout.strip()

            # Obtener SDK
            result = subprocess.run(
                ["getprop", "ro.build.version.sdk"], capture_output=True, text=True
            )
            info["sdk_version"] = result.stdout.strip()

            # Obtener API level
            result = subprocess.run(
                ["getprop", "ro.build.version.api_level"], capture_output=True, text=True
            )
            info["api_level"] = result.stdout.strip()

        except Exception as e:
            print(f"Error obteniendo información del dispositivo: {e}")

        return info


# Instancia global
platform = PlatformAdapter()
