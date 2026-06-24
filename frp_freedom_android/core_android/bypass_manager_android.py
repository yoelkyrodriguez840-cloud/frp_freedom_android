"""
Bypass Manager Android - Versión Android del BypassManager
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, Any

from ..models.device_model import DeviceInfo, BypassMethod
from ..android_config import config
from .adb_exploits_android import ADBExploitManagerAndroid
from .interface_exploits_android import InterfaceExploitManagerAndroid
from .system_exploits_android import SystemExploitManagerAndroid
from .hardware_exploits_android import HardwareExploitManagerAndroid
from .logger_android import logger, AuditLoggerAndroid


class BypassManagerAndroid:
    """Gestor de bypass para Android"""

    def __init__(self, device_manager):
        self.config = config
        self.device_manager = device_manager
        self.logger = logger

        # Inicializar gestores de exploits
        self.adb_exploits = ADBExploitManagerAndroid()
        self.interface_exploits = InterfaceExploitManagerAndroid()
        self.system_exploits = SystemExploitManagerAndroid()
        self.hardware_exploits = HardwareExploitManagerAndroid()

        # Logger de auditoría
        self.audit_logger = AuditLoggerAndroid()

        # Estado
        self.is_executing = False
        self.is_cancelled = False
        self.current_method_index = 0
        self.results = []

        # Métodos disponibles
        self.available_methods = self._initialize_methods()

    def _initialize_methods(self) -> List[BypassMethod]:
        """Inicializar métodos de bypass disponibles"""
        methods = []

        # Métodos ADB
        if self.config.get("bypass_methods.adb_exploits", True):
            methods.extend(
                [
                    BypassMethod(
                        name="adb_setup_wizard",
                        description="Exploit del asistente de configuración",
                        category="adb",
                        risk_level="low",
                        success_rate=0.85,
                        estimated_time=5,
                        requirements=["Conexión USB", "Asistente activo"],
                        supported_devices=["Samsung", "Google", "LG", "HTC"],
                        android_versions=["5.0", "6.0", "7.0", "8.0", "9.0", "10.0", "11.0"],
                    ),
                    BypassMethod(
                        name="adb_talkback_chrome",
                        description="TalkBack + Chrome para Android 14/15",
                        category="adb",
                        risk_level="low",
                        success_rate=0.92,
                        estimated_time=6,
                        requirements=["TalkBack disponible", "Chrome"],
                        supported_devices=["Samsung", "Google", "Xiaomi"],
                        android_versions=["14.0", "15.0"],
                    ),
                    BypassMethod(
                        name="adb_talkback_legacy",
                        description="TalkBack para versiones antiguas",
                        category="adb",
                        risk_level="low",
                        success_rate=0.75,
                        estimated_time=8,
                        requirements=["ADB", "TalkBack disponible"],
                        supported_devices=["Samsung", "Google", "Xiaomi"],
                        android_versions=["5.0", "6.0", "7.0", "8.0", "9.0", "10.0"],
                    ),
                    BypassMethod(
                        name="adb_intent_manipulation",
                        description="Manipulación de intents ADB",
                        category="adb",
                        risk_level="medium",
                        success_rate=0.88,
                        estimated_time=10,
                        requirements=["ADB", "USB debugging"],
                        supported_devices=["Samsung", "Xiaomi", "Huawei", "Google"],
                        android_versions=["12.0", "13.0", "14.0", "15.0"],
                    ),
                ]
            )

        # Métodos de interfaz
        methods.extend(
            [
                BypassMethod(
                    name="emergency_call_exploit",
                    description="Exploit de llamada de emergencia",
                    category="interface",
                    risk_level="low",
                    success_rate=0.70,
                    estimated_time=10,
                    requirements=["Acceso físico", "Llamada de emergencia"],
                    supported_devices=["Samsung", "LG", "HTC"],
                    android_versions=["5.0", "6.0", "7.0", "8.0"],
                ),
                BypassMethod(
                    name="chrome_intent_exploit",
                    description="Exploit de intents de Chrome",
                    category="interface",
                    risk_level="medium",
                    success_rate=0.65,
                    estimated_time=12,
                    requirements=["ADB", "Chrome"],
                    supported_devices=["Samsung", "Google", "Xiaomi"],
                    android_versions=["6.0", "7.0", "8.0", "9.0", "10.0"],
                ),
                BypassMethod(
                    name="apk_injection_setup",
                    description="Inyección de APK en asistente",
                    category="interface",
                    risk_level="medium",
                    success_rate=0.82,
                    estimated_time=15,
                    requirements=["Acceso físico", "Asistente activo"],
                    supported_devices=["Xiaomi", "Huawei", "Samsung"],
                    android_versions=["13.0", "14.0", "15.0"],
                ),
                BypassMethod(
                    name="samsung_setup_wizard_2025",
                    description="Exploit Samsung 2025",
                    category="interface",
                    risk_level="low",
                    success_rate=0.95,
                    estimated_time=8,
                    requirements=["Samsung", "Asistente", "Timing preciso"],
                    supported_devices=["Samsung Galaxy A04", "Samsung Galaxy S24"],
                    android_versions=["14.0", "15.0"],
                ),
            ]
        )

        # Métodos de sistema (requieren root)
        if self.config.get("bypass_methods.system_exploits", False):
            methods.extend(
                [
                    BypassMethod(
                        name="accounts_db_modification",
                        description="Modificar base de datos de cuentas",
                        category="system",
                        risk_level="medium",
                        success_rate=0.90,
                        estimated_time=15,
                        requirements=["Root", "Recovery personalizado"],
                        supported_devices=["Samsung", "Google", "Xiaomi", "OnePlus"],
                        android_versions=["5.0", "6.0", "7.0", "8.0", "9.0", "10.0"],
                    ),
                    BypassMethod(
                        name="persist_partition_edit",
                        description="Editar partición persist",
                        category="system",
                        risk_level="high",
                        success_rate=0.95,
                        estimated_time=20,
                        requirements=["Bootloader desbloqueado", "Root"],
                        supported_devices=["Samsung", "Google", "Xiaomi"],
                        android_versions=[
                            "6.0",
                            "7.0",
                            "8.0",
                            "9.0",
                            "10.0",
                            "11.0",
                            "12.0",
                            "13.0",
                        ],
                    ),
                    BypassMethod(
                        name="framework_patch_android15",
                        description="Parche framework Android 15",
                        category="system",
                        risk_level="high",
                        success_rate=0.78,
                        estimated_time=35,
                        requirements=["Root", "Framework modificable"],
                        supported_devices=["Samsung", "Google", "Xiaomi"],
                        android_versions=["15.0"],
                    ),
                ]
            )

        # Métodos de hardware (limitados en Android)
        if self.config.get("bypass_methods.hardware_methods", False):
            methods.extend(
                [
                    BypassMethod(
                        name="download_mode_flash",
                        description="Modo download (simulado)",
                        category="hardware",
                        risk_level="high",
                        success_rate=0.0,
                        estimated_time=30,
                        requirements=["Acceso físico", "Modo download"],
                        supported_devices=["Samsung"],
                        android_versions=["5.0", "6.0", "7.0", "8.0", "9.0", "10.0", "11.0"],
                    )
                ]
            )

        return methods

    def get_recommended_methods(self, device: DeviceInfo) -> List[BypassMethod]:
        """Obtener métodos recomendados"""
        compatible_methods = []

        for method in self.available_methods:
            if self._is_method_compatible(method, device):
                compatible_methods.append(method)

        # Ordenar por tasa de éxito
        compatible_methods.sort(key=lambda m: m.success_rate, reverse=True)

        return compatible_methods

    def _is_method_compatible(self, method: BypassMethod, device: DeviceInfo) -> bool:
        """Verificar si un método es compatible con el dispositivo"""
        # Verificar fabricante
        if device.manufacturer.lower() not in [d.lower() for d in method.supported_devices]:
            return False

        # Verificar versión de Android
        if device.android_version not in method.android_versions:
            return False

        # Verificar requisitos
        if "Root" in method.requirements:
            # En Android, generalmente no tenemos root
            if not self.config.get("security.root_available", False):
                return False

        return True

    async def execute_bypass(
        self,
        device: DeviceInfo,
        method_name: str,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Dict[str, Any]:
        """Ejecutar un método de bypass"""
        self.is_executing = True
        self.is_cancelled = False

        # Buscar método
        method = next((m for m in self.available_methods if m.name == method_name), None)
        if not method:
            self.is_executing = False
            return {
                "result": BypassResult.FAILED,
                "message": f"Método desconocido: {method_name}",
                "details": {},
            }

        self.logger.info(f"Iniciando bypass {method_name} en {device.serial}")

        try:
            # Ejecutar según categoría
            if method.category == "adb":
                result = await self.adb_exploits.execute_method(device, method, progress_callback)
            elif method.category == "interface":
                result = await self.interface_exploits.execute_method(
                    device, method, progress_callback
                )
            elif method.category == "system":
                result = await self.system_exploits.execute_method(
                    device, method, progress_callback
                )
            elif method.category == "hardware":
                result = await self.hardware_exploits.execute_method(
                    device, method, progress_callback
                )
            else:
                result = {
                    "result": BypassResult.FAILED,
                    "message": f"Categoría desconocida: {method.category}",
                    "details": {},
                }

            # Auditoría
            self.audit_logger.log_bypass_attempt(
                device.to_dict(),
                method_name,
                result["result"] == BypassResult.SUCCESS,
                result.get("message"),
            )

            return result

        except Exception as e:
            self.logger.error(f"Error en bypass {method_name}: {e}")
            return {
                "result": BypassResult.FAILED,
                "message": f"Error: {str(e)}",
                "details": {"error": str(e)},
            }
        finally:
            self.is_executing = False

    async def execute_methods(
        self,
        device: DeviceInfo,
        methods: List[BypassMethod],
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[Dict[str, Any]]:
        """Ejecutar múltiples métodos de bypass"""
        results = []
        total = len(methods)

        for i, method in enumerate(methods):
            if self.is_cancelled:
                break

            self.current_method_index = i

            if progress_callback:
                progress_callback(
                    f"Ejecutando {method.name} ({i+1}/{total})", int((i / total) * 100)
                )

            result = await self.execute_bypass(device, method.name, progress_callback)
            results.append(
                {
                    "method": method.name,
                    "result": result["result"],
                    "message": result.get("message", ""),
                    "details": result.get("details", {}),
                }
            )

            # Si tiene éxito, preguntar si continuar
            if result["result"] == BypassResult.SUCCESS:
                if progress_callback:
                    progress_callback("Bypass exitoso", 100)
                break

        self.results = results
        return results

    def cancel_execution(self):
        """Cancelar ejecución"""
        self.is_cancelled = True

    def get_methods(self) -> List[BypassMethod]:
        """Obtener todos los métodos disponibles"""
        return self.available_methods.copy()

    def get_method_by_name(self, name: str) -> Optional[BypassMethod]:
        """Obtener método por nombre"""
        for method in self.available_methods:
            if method.name == name:
                return method
        return None

    def get_results(self) -> List[Dict[str, Any]]:
        """Obtener resultados de la última ejecución"""
        return self.results
