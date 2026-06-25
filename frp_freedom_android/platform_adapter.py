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
        self._platform = self._detect_platform()
        self._init_platform_specific()

    def _detect_platform(self) -> str:
        """Detectar plataforma actual"""
        # Verificar si estamos en Android
        if hasattr(sys, "android") or "android" in sys.platform:
            return "android"
        # Verificar si estamos en Kivy (Android)
        elif "kivy" in sys.modules:
            return "android"
        # Verificar si estamos en Flet Android
        elif os.environ.get("FLET_APP") == "true":
            return "android"
        else:
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
        except ImportError:
            print("ADVERTENCIA: No se pudieron cargar los imports de Android")
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
                # En Android (Flet), usar directorio de la aplicación
                from android.storage import app_storage_path

                return Path(app_storage_path())
            except:
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


# Instancia global
platform = PlatformAdapter()
