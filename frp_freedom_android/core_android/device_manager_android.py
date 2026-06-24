"""
Device Manager Android - Versión Android del DeviceManager
"""

import asyncio
import time
from typing import List, Optional, Dict, Any

from ..platform_adapter import platform
from ..android_config import config
from ..adapters.usb_adapter import USBAdapter
from ..adapters.adb_adapter import ADBAdapter, ADBConnectionType
from ..models.device_model import DeviceInfo


class DeviceManagerAndroid:
    """DeviceManager para Android"""

    def __init__(self):
        self.config = config
        self.usb_adapter = USBAdapter()
        self.adb_adapter = ADBAdapter()

        # Configurar tipo de conexión según configuración
        if self.config.use_tcp_adb():
            self.adb_adapter.set_connection_type(ADBConnectionType.TCP)
        else:
            self.adb_adapter.set_connection_type(ADBConnectionType.USB)

        self.devices: List[DeviceInfo] = []
        self.scanning = False
        self._scan_task = None

    async def scan_devices(self) -> List[DeviceInfo]:
        """Escanear dispositivos conectados"""
        self.scanning = True
        devices = []

        try:
            # Obtener dispositivos ADB
            adb_devices = await self.adb_adapter.get_all_devices()

            for adb_device in adb_devices:
                device_info = self._create_device_info(adb_device)
                if device_info:
                    devices.append(device_info)

            # Obtener dispositivos USB (no ADB)
            usb_devices = self.usb_adapter.get_devices()
            for usb_device in usb_devices:
                if not usb_device.get("is_adb", False):
                    # Dispositivo Android sin ADB
                    device_info = self._create_device_info_from_usb(usb_device)
                    if device_info:
                        devices.append(device_info)

            self.devices = devices

        except Exception as e:
            print(f"Error scanning devices: {e}")

        self.scanning = False
        return devices

    def _create_device_info(self, adb_device: Dict[str, Any]) -> Optional[DeviceInfo]:
        """Crear DeviceInfo desde datos ADB"""
        try:
            serial = adb_device.get("serial", "")
            if not serial:
                return None

            return DeviceInfo(
                serial=serial,
                model=adb_device.get("model", "Unknown"),
                manufacturer=adb_device.get("manufacturer", "Unknown"),
                android_version=adb_device.get("android_version", "Unknown"),
                connection_type=adb_device.get("connection_type", "adb"),
                frp_status=adb_device.get("frp_status", "Unknown"),
                brand=adb_device.get("manufacturer", "Unknown"),
            )
        except Exception as e:
            print(f"Error creating device info: {e}")
            return None

    def _create_device_info_from_usb(self, usb_device: Dict[str, Any]) -> Optional[DeviceInfo]:
        """Crear DeviceInfo desde datos USB"""
        try:
            device_name = usb_device.get("device_name", "")
            if not device_name:
                return None

            return DeviceInfo(
                serial=device_name,
                model="Android Device",
                manufacturer="Unknown",
                android_version="Unknown",
                connection_type="usb_only",
                frp_status="Unknown",
                brand="Unknown",
            )
        except Exception as e:
            print(f"Error creating USB device info: {e}")
            return None

    def get_devices(self) -> List[DeviceInfo]:
        """Obtener lista de dispositivos escaneados"""
        return self.devices

    async def refresh_devices(self) -> List[DeviceInfo]:
        """Refrescar lista de dispositivos"""
        return await self.scan_devices()

    def get_device_by_serial(self, serial: str) -> Optional[DeviceInfo]:
        """Obtener dispositivo por serial"""
        for device in self.devices:
            if device.serial == serial:
                return device
        return None

    async def get_device_info(self, serial: str) -> Optional[Dict[str, Any]]:
        """Obtener información detallada de un dispositivo"""
        try:
            # Usar ADB para obtener información
            info = {}

            # Modelo
            success, output = await self.adb_adapter.execute_command(
                serial, "shell getprop ro.product.model"
            )
            if success:
                info["model"] = output.strip()

            # Fabricante
            success, output = await self.adb_adapter.execute_command(
                serial, "shell getprop ro.product.manufacturer"
            )
            if success:
                info["manufacturer"] = output.strip()

            # Android version
            success, output = await self.adb_adapter.execute_command(
                serial, "shell getprop ro.build.version.release"
            )
            if success:
                info["android_version"] = output.strip()

            # FRP status
            success, output = await self.adb_adapter.execute_command(
                serial, "shell getprop ro.frp.pst"
            )
            if success:
                info["frp_status"] = "enabled" if output.strip() else "disabled"

            # SDK version
            success, output = await self.adb_adapter.execute_command(
                serial, "shell getprop ro.build.version.sdk"
            )
            if success:
                info["sdk_version"] = output.strip()

            return info

        except Exception as e:
            print(f"Error getting device info: {e}")
            return None

    async def is_device_available(self, serial: str) -> bool:
        """Verificar si un dispositivo está disponible"""
        return await self.adb_adapter.ping_device(serial)

    async def start_scanning(self, interval: int = 5):
        """Iniciar escaneo continuo"""
        if self._scan_task and not self._scan_task.done():
            return

        async def scan_loop():
            while True:
                await self.scan_devices()
                await asyncio.sleep(interval)

        self._scan_task = asyncio.create_task(scan_loop())

    def stop_scanning(self):
        """Detener escaneo continuo"""
        if self._scan_task:
            self._scan_task.cancel()
            self._scan_task = None
