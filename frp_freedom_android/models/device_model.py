"""
Device Model - Modelos de datos para dispositivos
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DeviceInfo:
    """Información de un dispositivo"""

    serial: str
    model: str = "Unknown"
    manufacturer: str = "Unknown"
    android_version: str = "Unknown"
    sdk_version: str = "Unknown"
    bootloader_version: str = "Unknown"
    frp_status: str = "Unknown"
    connection_type: str = "unknown"
    chipset: str = "Unknown"
    imei: str = ""
    brand: str = "Unknown"
    bootloader_status: str = "Unknown"
    root_status: str = "Unknown"
    security_patch: str = "Unknown"
    encryption_status: str = "Unknown"
    api_level: str = "Unknown"
    build_id: str = "Unknown"
    product: str = "Unknown"
    device: str = "Unknown"
    modem_port: str = ""

    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            "serial": self.serial,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "android_version": self.android_version,
            "sdk_version": self.sdk_version,
            "bootloader_version": self.bootloader_version,
            "frp_status": self.frp_status,
            "connection_type": self.connection_type,
            "chipset": self.chipset,
            "imei": self.imei[:4] + "****" + self.imei[-4:] if len(self.imei) >= 8 else "unknown",
            "brand": self.brand,
            "bootloader_status": self.bootloader_status,
            "root_status": self.root_status,
            "security_patch": self.security_patch,
            "api_level": self.api_level,
        }


@dataclass
class BypassMethod:
    """Método de bypass"""

    name: str
    description: str
    category: str  # adb, interface, system, hardware
    risk_level: str  # low, medium, high
    success_rate: float
    estimated_time: int  # minutos
    requirements: List[str] = field(default_factory=list)
    supported_devices: List[str] = field(default_factory=list)
    android_versions: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "risk_level": self.risk_level,
            "success_rate": self.success_rate,
            "estimated_time": self.estimated_time,
            "requirements": self.requirements,
            "supported_devices": self.supported_devices,
            "android_versions": self.android_versions,
        }


@dataclass
class BypassResult:
    """Resultado de un bypass"""

    method: str
    success: bool
    message: str = ""
    details: dict = field(default_factory=dict)
    execution_time: float = 0.0
