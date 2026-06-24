"""
Permissions Adapter - Manejo de permisos Android
"""

from typing import List, Optional, Dict, Any
from enum import Enum

from ..platform_adapter import platform


class Permission(Enum):
    """Permisos de Android"""

    USB = "android.permission.USB"
    STORAGE = "android.permission.WRITE_EXTERNAL_STORAGE"
    INTERNET = "android.permission.INTERNET"
    ACCESS_NETWORK_STATE = "android.permission.ACCESS_NETWORK_STATE"
    READ_PHONE_STATE = "android.permission.READ_PHONE_STATE"


class PermissionAdapter:
    """Adaptador de permisos para Android"""

    def __init__(self):
        self.platform = platform
        self._granted_permissions = set()

        if self.platform.is_android():
            self._init_android()

    def _init_android(self):
        """Inicializar en Android"""
        try:
            jnius = self.platform.get_jnius()
            if jnius:
                self._PackageManager = jnius.autoclass("android.content.pm.PackageManager")
                self._Manifest = jnius.autoclass("android.Manifest")
        except:
            self._PackageManager = None
            self._Manifest = None

    async def check_permission(self, permission: Permission) -> bool:
        """Verificar si un permiso está concedido"""
        if not self.platform.is_android():
            return True

        # Verificar en cache
        if permission.value in self._granted_permissions:
            return True

        try:
            context = self.platform.get_android_context()
            if not context:
                return False

            result = context.checkSelfPermission(permission.value)
            granted = result == self._PackageManager.PERMISSION_GRANTED

            if granted:
                self._granted_permissions.add(permission.value)

            return granted

        except Exception as e:
            print(f"Error checking permission {permission}: {e}")
            return False

    async def request_permission(self, permission: Permission) -> bool:
        """Solicitar un permiso"""
        if not self.platform.is_android():
            return True

        try:
            # Usar el sistema de permisos de Flet/Kivy
            # En Flet, esto se maneja en la UI

            # Simular solicitud
            # En producción, usar el sistema de permisos de la plataforma
            self._granted_permissions.add(permission.value)
            return True

        except Exception as e:
            print(f"Error requesting permission {permission}: {e}")
            return False

    async def request_permissions(self, permissions: List[Permission]) -> Dict[str, bool]:
        """Solicitar múltiples permisos"""
        results = {}
        for perm in permissions:
            results[perm.value] = await self.request_permission(perm)
        return results

    async def check_all_permissions(self) -> Dict[str, bool]:
        """Verificar todos los permisos necesarios"""
        permissions = [
            Permission.USB,
            Permission.STORAGE,
            Permission.INTERNET,
            Permission.ACCESS_NETWORK_STATE,
        ]

        results = {}
        for perm in permissions:
            results[perm.value] = await self.check_permission(perm)

        return results

    def has_usb_access(self) -> bool:
        """Verificar si tiene acceso USB"""
        return Permission.USB.value in self._granted_permissions

    def has_storage_access(self) -> bool:
        """Verificar si tiene acceso a almacenamiento"""
        return Permission.STORAGE.value in self._granted_permissions

    def has_internet_access(self) -> bool:
        """Verificar si tiene acceso a internet"""
        return Permission.INTERNET.value in self._granted_permissions
