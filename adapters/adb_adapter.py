"""
ADB Adapter - ADB over TCP/IP and USB for Android
"""

import asyncio
import socket
import re
import time
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum

from ..platform_adapter import platform


class ADBConnectionType(Enum):
    """Tipo de conexión ADB"""

    USB = "usb"
    TCP = "tcp"
    DISABLED = "disabled"


class ADBAdapter:
    """Adaptador ADB para Android (TCP/IP + USB)"""

    def __init__(self):
        self.platform = platform
        self.connection_type = ADBConnectionType.TCP
        self._adb_process = None
        self._connection_cache = {}
        self._timeout = 3000  # 3 segundos

        if self.platform.is_android():
            self._init_android()

    def _init_android(self):
        """Inicializar en Android"""
        # En Android, usar TCP/IP por defecto
        self.connection_type = ADBConnectionType.TCP

    def set_connection_type(self, connection_type: ADBConnectionType):
        """Establecer tipo de conexión"""
        self.connection_type = connection_type

    def set_timeout(self, timeout_ms: int):
        """Establecer timeout en milisegundos"""
        self._timeout = timeout_ms

    async def connect_device(
        self, serial: str
    ) -> Tuple[bool, Optional[asyncio.StreamReader], Optional[asyncio.StreamWriter]]:
        """Conectar a dispositivo"""
        if self.connection_type == ADBConnectionType.TCP:
            return await self._connect_tcp(serial)
        elif self.connection_type == ADBConnectionType.USB:
            return await self._connect_usb(serial)
        else:
            return False, None, None

    async def _connect_tcp(
        self, serial: str
    ) -> Tuple[bool, Optional[asyncio.StreamReader], Optional[asyncio.StreamWriter]]:
        """Conectar vía TCP/IP"""
        # Si serial es IP, usarlo directamente
        ip = serial
        port = 5555

        # Si serial es un nombre de dispositivo, intentar resolver
        if not self._is_ip_address(serial):
            # Intentar resolver nombre de dispositivo a IP
            ip = await self._resolve_device_ip(serial)
            if not ip:
                return False, None, None

        try:
            reader, writer = await asyncio.open_connection(
                ip, port, limit=1024 * 1024  # 1MB buffer
            )
            return True, reader, writer
        except Exception as e:
            print(f"Error connecting to {ip}:{port} - {e}")
            return False, None, None

    async def _connect_usb(
        self, serial: str
    ) -> Tuple[bool, Optional[asyncio.StreamReader], Optional[asyncio.StreamWriter]]:
        """Conectar vía USB (requiere jnius)"""
        # En Android, la conexión USB se maneja a través de UsbDeviceConnection
        # Esta implementación es un placeholder

        try:
            jnius = self.platform.get_jnius()
            if not jnius:
                return False, None, None

            # Obtener el dispositivo USB
            usb_manager = self.platform.get_android_usb_manager()
            if not usb_manager:
                return False, None, None

            # Buscar el dispositivo por serial
            device_list = usb_manager.getDeviceList()
            target_device = None

            for device in device_list:
                if serial in device.getDeviceName():
                    target_device = device
                    break

            if not target_device:
                return False, None, None

            # Obtener conexión
            connection = usb_manager.openDevice(target_device)
            if not connection:
                return False, None, None

            # Configurar interfaces
            # ... implementación compleja con UsbInterface y UsbEndpoint

            return False, None, None  # Placeholder

        except Exception as e:
            print(f"Error connecting via USB: {e}")
            return False, None, None

    def _is_ip_address(self, value: str) -> bool:
        """Verificar si un string es una dirección IP"""
        pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        return bool(re.match(pattern, value))

    async def _resolve_device_ip(self, device_name: str) -> Optional[str]:
        """Resolver nombre de dispositivo a IP"""
        # Intentar resolver por mDNS (Bonjour)
        try:
            import socket

            return socket.gethostbyname(f"{device_name}.local")
        except:
            pass

        # Intentar resolver por el nombre
        try:
            import socket

            return socket.gethostbyname(device_name)
        except:
            pass

        return None

    async def execute_command(self, serial: str, command: str) -> Tuple[bool, str]:
        """Ejecutar comando ADB"""
        if self.connection_type == ADBConnectionType.TCP:
            return await self._execute_tcp_command(serial, command)
        elif self.connection_type == ADBConnectionType.USB:
            return await self._execute_usb_command(serial, command)
        else:
            return False, "ADB disabled"

    async def _execute_tcp_command(self, serial: str, command: str) -> Tuple[bool, str]:
        """Ejecutar comando vía TCP/IP"""
        reader, writer = None, None
        try:
            # Conectar
            connected, reader, writer = await self.connect_device(serial)
            if not connected:
                return False, "Connection failed"

            # Enviar comando
            if not command.endswith("\n"):
                command += "\n"

            writer.write(command.encode())
            await writer.drain()

            # Leer respuesta
            response = b""
            while True:
                try:
                    chunk = await asyncio.wait_for(reader.read(4096), timeout=self._timeout / 1000)
                    if not chunk:
                        break
                    response += chunk
                except asyncio.TimeoutError:
                    break

            writer.close()
            await writer.wait_closed()

            return True, response.decode()

        except Exception as e:
            if writer:
                try:
                    writer.close()
                except:
                    pass
            return False, str(e)

    async def _execute_usb_command(self, serial: str, command: str) -> Tuple[bool, str]:
        """Ejecutar comando vía USB"""
        # Placeholder - implementación real requiere UsbDeviceConnection
        return False, "USB ADB not fully implemented yet"

    async def get_devices_tcp(self) -> List[Dict[str, Any]]:
        """Obtener dispositivos vía TCP/IP (escaneo de red)"""
        devices = []

        # Escanear red local para dispositivos ADB
        # Usar una IP base configurable
        base_ip = "192.168.1."

        for i in range(1, 255):
            ip = base_ip + str(i)
            try:
                # Intentar conectar al puerto ADB
                connected, reader, writer = await self.connect_device(ip)
                if connected:
                    # Verificar si responde a comandos ADB
                    success, response = await self._execute_tcp_command(ip, "host:version")
                    if success and "OKAY" in response:
                        # Obtener información del dispositivo
                        device_info = await self._get_device_info_tcp(ip)
                        devices.append(
                            {
                                "serial": ip,
                                "connection_type": "tcp",
                                "status": "device",
                                "model": device_info.get("model", "Unknown"),
                                "android_version": device_info.get("android_version", "Unknown"),
                                "manufacturer": device_info.get("manufacturer", "Unknown"),
                            }
                        )

                    if writer:
                        writer.close()
                        await writer.wait_closed()
            except:
                continue

        return devices

    async def _get_device_info_tcp(self, ip: str) -> Dict[str, Any]:
        """Obtener información del dispositivo vía TCP"""
        info = {
            "model": "Unknown",
            "android_version": "Unknown",
            "manufacturer": "Unknown",
            "frp_status": "Unknown",
        }

        # Obtener modelo
        success, output = await self._execute_tcp_command(ip, "shell getprop ro.product.model")
        if success and output.strip():
            info["model"] = output.strip()

        # Obtener versión de Android
        success, output = await self._execute_tcp_command(
            ip, "shell getprop ro.build.version.release"
        )
        if success and output.strip():
            info["android_version"] = output.strip()

        # Obtener fabricante
        success, output = await self._execute_tcp_command(
            ip, "shell getprop ro.product.manufacturer"
        )
        if success and output.strip():
            info["manufacturer"] = output.strip()

        # Obtener estado FRP
        success, output = await self._execute_tcp_command(ip, "shell getprop ro.frp.pst")
        if success and output.strip():
            info["frp_status"] = "enabled"
        else:
            info["frp_status"] = "disabled"

        return info

    async def get_devices_usb(self) -> List[Dict[str, Any]]:
        """Obtener dispositivos vía USB"""
        devices = []

        from .usb_adapter import USBAdapter

        usb = USBAdapter()

        adb_serials = usb.get_adb_devices()
        for serial in adb_serials:
            try:
                # Usar TCP localhost para comunicación
                # En Android, podemos usar un socket Unix o TCP local
                success, output = await self._execute_tcp_command(
                    "127.0.0.1", f"host:transport:{serial}"
                )
                if success:
                    # Obtener información
                    device_info = await self._get_device_info_tcp("127.0.0.1")
                    devices.append(
                        {
                            "serial": serial,
                            "connection_type": "usb",
                            "status": "device",
                            "model": device_info.get("model", "Unknown"),
                            "android_version": device_info.get("android_version", "Unknown"),
                            "manufacturer": device_info.get("manufacturer", "Unknown"),
                        }
                    )
            except:
                continue

        return devices

    async def get_all_devices(self) -> List[Dict[str, Any]]:
        """Obtener todos los dispositivos disponibles"""
        devices = []

        # Dispositivos TCP
        if self.connection_type == ADBConnectionType.TCP:
            tcp_devices = await self.get_devices_tcp()
            devices.extend(tcp_devices)

        # Dispositivos USB
        if self.connection_type == ADBConnectionType.USB:
            usb_devices = await self.get_devices_usb()
            devices.extend(usb_devices)

        return devices

    async def ping_device(self, serial: str) -> bool:
        """Verificar si el dispositivo responde"""
        success, _ = await self.execute_command(serial, "host:version")
        return success

    def get_connection_type(self) -> str:
        """Obtener tipo de conexión actual"""
        return self.connection_type.value
