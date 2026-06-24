"""
USB Adapter - Android USB Manager wrapper
"""

from typing import List, Optional, Dict, Any
import time

from ..platform_adapter import platform


class USBAdapter:
    """Adaptador USB para Android usando UsbManager"""

    def __init__(self):
        self.platform = platform
        self.usb_manager = None
        self._pending_permissions = {}
        self._device_cache = {}

        if self.platform.is_android():
            self.usb_manager = self.platform.get_android_usb_manager()
            self._init_android_usb()

    def _init_android_usb(self):
        """Inicializar USB en Android"""
        if not self.usb_manager:
            return

        try:
            jnius = self.platform.get_jnius()
            if jnius:
                # Crear broadcast receiver para permisos USB
                self.USB_PERMISSION = jnius.autoclass(
                    "android.hardware.usb.UsbManager"
                ).ACTION_USB_PERMISSION
        except Exception as e:
            print(f"Error initializing USB: {e}")

    def get_devices(self) -> List[Dict[str, Any]]:
        """Obtener dispositivos USB conectados"""
        devices = []

        if not self.usb_manager:
            return devices

        try:
            device_list = self.usb_manager.getDeviceList()

            for device in device_list:
                device_info = self._get_device_info(device)
                if device_info:
                    devices.append(device_info)

        except Exception as e:
            print(f"Error getting USB devices: {e}")

        return devices

    def _get_device_info(self, device) -> Optional[Dict[str, Any]]:
        """Obtener información de un dispositivo USB"""
        try:
            vendor_id = device.getVendorId()
            product_id = device.getProductId()
            device_name = device.getDeviceName() or "Unknown"

            # Verificar si es un dispositivo Android
            is_android = self._is_android_device(vendor_id)
            is_adb = self._is_adb_device(vendor_id, product_id)

            return {
                "device": device,
                "vendor_id": vendor_id,
                "product_id": product_id,
                "device_name": device_name,
                "is_android": is_android,
                "is_adb": is_adb,
                "has_permission": self.usb_manager.hasPermission(device),
            }

        except Exception as e:
            print(f"Error getting device info: {e}")
            return None

    def _is_android_device(self, vendor_id: int) -> bool:
        """Verificar si es dispositivo Android por VID"""
        # VIDs comunes de Android
        android_vids = [
            0x18D1,  # Google
            0x04E8,  # Samsung
            0x22B8,  # Motorola
            0x0BB4,  # HTC
            0x2B95,  # OnePlus
            0x2717,  # Xiaomi
            0x12D1,  # Huawei
            0x05C6,  # Qualcomm
            0x1004,  # LG
            0x0FCE,  # Sony
            0x1949,  # Google (Pixel)
        ]
        return vendor_id in android_vids

    def _is_adb_device(self, vendor_id: int, product_id: int) -> bool:
        """Verificar si el dispositivo soporta ADB"""
        # Combinaiones VID/PID comunes para ADB
        adb_pairs = [
            (0x18D1, 0xD001),  # Google ADB
            (0x04E8, 0x6860),  # Samsung ADB
            (0x22B8, 0x2E76),  # Motorola ADB
            (0x0BB4, 0x0C01),  # HTC ADB
            (0x2B95, 0x0011),  # OnePlus ADB
            (0x2717, 0x1280),  # Xiaomi ADB
        ]
        return (vendor_id, product_id) in adb_pairs

    def request_permission(self, device) -> bool:
        """Solicitar permiso para acceder al dispositivo USB"""
        if not self.usb_manager:
            return False

        if self.usb_manager.hasPermission(device):
            return True

        try:
            jnius = self.platform.get_jnius()
            if not jnius:
                return False

            # Obtener contexto
            context = self.platform.get_android_context()
            if not context:
                return False

            # Crear PendingIntent para permiso
            Intent = jnius.autoclass("android.content.Intent")
            PendingIntent = jnius.autoclass("android.app.PendingIntent")

            intent = Intent(self.USB_PERMISSION)
            pending_intent = PendingIntent.getBroadcast(
                context, 0, intent, PendingIntent.FLAG_IMMUTABLE
            )

            # Solicitar permiso
            self.usb_manager.requestPermission(device, pending_intent)

            # Esperar respuesta (en una implementación real, usaría un broadcast receiver)
            # Por ahora, esperamos un poco
            time.sleep(1)

            # Verificar si se concedió (puede que no funcione sin broadcast receiver)
            return self.usb_manager.hasPermission(device)

        except Exception as e:
            print(f"Error requesting USB permission: {e}")
            return False

    def get_adb_devices(self) -> List[str]:
        """Obtener lista de dispositivos ADB vía USB"""
        devices = []

        for device_info in self.get_devices():
            if device_info.get("is_adb", False):
                if self.request_permission(device_info["device"]):
                    # El nombre del dispositivo se usa como serial
                    serial = device_info["device_name"]
                    if serial:
                        devices.append(serial)

        return devices

    def get_android_devices(self) -> List[Dict[str, Any]]:
        """Obtener dispositivos Android completos"""
        devices = []

        for device_info in self.get_devices():
            if device_info.get("is_android", False):
                if self.request_permission(device_info["device"]):
                    devices.append(device_info)

        return devices
