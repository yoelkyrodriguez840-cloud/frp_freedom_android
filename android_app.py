"""
FRP Freedom Android APK - Aplicación Principal
"""

import flet as ft
import asyncio
import logging
from typing import Optional, List, Dict, Any

from .android_config import config
from .core_android.device_manager_android import DeviceManagerAndroid
from .core_android.bypass_manager_android import BypassManagerAndroid
from .core_android.logger_android import logger, AuditLoggerAndroid
from .models.device_model import DeviceInfo, BypassMethod
from .views.home_view import HomeView
from .views.device_view import DeviceView
from .views.methods_view import MethodsView
from .views.execution_view import ExecutionView
from .views.results_view import ResultsView

# En android_app.py
from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "assets"
ICON_PATH = ASSETS_DIR / "icon.png"
SPLASH_PATH = ASSETS_DIR / "splash.png"


# Usar en la aplicación
def init(self, page: ft.Page):
    # Configurar icono
    # ... resto del código


class FRPFreedomApp:
    """Aplicación principal FRP Freedom para Android"""

    def __init__(self):
        self.page: Optional[ft.Page] = None
        self.config = config
        self.logger = logger
        self.audit_logger = AuditLoggerAndroid()

        # Inicializar controladores
        self.device_manager = DeviceManagerAndroid()
        self.bypass_manager = BypassManagerAndroid(self.device_manager)

        # Estado de la aplicación
        self.selected_device: Optional[DeviceInfo] = None
        self.selected_methods: List[BypassMethod] = []
        self.execution_results: List[Dict[str, Any]] = []

        # Referencias a vistas
        self.views = {}
        self.current_view = None

        # Escaneo automático
        self.scan_task = None

    async def init(self, page: ft.Page):
        """Inicializar la aplicación"""
        self.page = page
        page.icon = str(ICON_PATH)

        # Configuración de la página
        page.title = "FRP Freedom"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 0
        page.spacing = 0
        page.window_width = 400
        page.window_height = 800

        # Configurar tema
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.colors.BLUE_700,
                primary_container=ft.colors.BLUE_900,
                secondary=ft.colors.CYAN_300,
                background=ft.colors.GREY_900,
                surface=ft.colors.GREY_800,
                on_primary=ft.colors.WHITE,
            )
        )

        # Configurar navegación
        page.on_route_change = self._on_route_change

        # Iniciar escaneo de dispositivos
        await self.device_manager.start_scanning()

        # Mostrar pantalla de inicio
        page.go("/")

        self.logger.info("FRP Freedom Android inicializado")

    def _on_route_change(self, route: ft.RouteChangeEvent):
        """Manejar cambio de ruta"""
        try:
            route_path = self.page.route

            if route_path == "/":
                self._show_home()
            elif route_path == "/device":
                self._show_device_selection()
            elif route_path == "/methods":
                self._show_method_selection()
            elif route_path == "/execution":
                self._show_execution()
            elif route_path == "/results":
                self._show_results()
            elif route_path == "/settings":
                self._show_settings()
            else:
                self.page.go("/")

        except Exception as e:
            self.logger.error(f"Error en navegación: {e}")
            self.page.go("/")

    def _show_home(self):
        """Mostrar pantalla de inicio"""
        view = HomeView(
            self.page,
            on_device_select=lambda: self.page.go("/device"),
            on_settings=lambda: self.page.go("/settings"),
            on_help=self._show_help,
        )
        self._set_view(view)

    def _show_device_selection(self):
        """Mostrar selección de dispositivo"""
        devices = self.device_manager.get_devices()

        view = DeviceView(
            self.page,
            devices=devices,
            on_device_selected=self._on_device_selected,
            on_scan=self._on_scan_devices,
            on_back=lambda: self.page.go("/"),
        )
        self._set_view(view)

    def _show_method_selection(self):
        """Mostrar selección de métodos"""
        if not self.selected_device:
            self.page.go("/device")
            return

        methods = self.bypass_manager.get_recommended_methods(self.selected_device)

        view = MethodsView(
            self.page,
            device=self.selected_device,
            methods=methods,
            on_methods_selected=self._on_methods_selected,
            on_back=lambda: self.page.go("/device"),
            on_ai_analyze=self._on_ai_analyze,
        )
        self._set_view(view)

    def _show_execution(self):
        """Mostrar ejecución"""
        if not self.selected_methods:
            self.page.go("/methods")
            return

        view = ExecutionView(
            self.page,
            device=self.selected_device,
            methods=self.selected_methods,
            on_execute=self._on_execute_bypass,
            on_cancel=self._on_execution_cancel,
            on_back=lambda: self.page.go("/methods"),
        )
        self._set_view(view)

    def _show_results(self):
        """Mostrar resultados"""
        view = ResultsView(
            self.page,
            results=self.execution_results,
            on_retry=lambda: self.page.go("/methods"),
            on_home=lambda: self.page.go("/"),
        )
        self._set_view(view)

    def _show_settings(self):
        """Mostrar configuración"""
        # Simple por ahora
        settings_dialog = ft.AlertDialog(
            title=ft.Text("Configuración"),
            content=ft.Column(
                [
                    ft.Switch(
                        label="Usar ADB TCP/IP",
                        value=self.config.use_tcp_adb(),
                        on_change=self._on_tcp_switch,
                    ),
                    ft.Switch(
                        label="Modo Debug",
                        value=self.config.is_debug(),
                        on_change=self._on_debug_switch,
                    ),
                    ft.Divider(),
                    ft.Text(f"Versión: {self.config.get('app.version', '1.0.0')}"),
                ]
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: self._close_dialog())],
        )
        self.page.dialog = settings_dialog
        settings_dialog.open = True
        self.page.update()

    def _set_view(self, view: ft.View):
        """Establecer la vista actual"""
        self.page.views.clear()
        self.page.views.append(view)
        self.page.update()

    def _on_device_selected(self, device: DeviceInfo):
        """Manejar selección de dispositivo"""
        self.selected_device = device
        self.audit_logger.log_device_detection(device.to_dict())
        self.page.go("/methods")

    async def _on_scan_devices(self):
        """Manejar escaneo de dispositivos"""
        devices = await self.device_manager.scan_devices()

        # Actualizar vista de dispositivos
        if self.page.views and isinstance(self.page.views[-1], DeviceView):
            view = self.page.views[-1]
            view.update_devices(devices)
            view.page.update()

        return devices

    def _on_methods_selected(self, methods: List[BypassMethod]):
        """Manejar selección de métodos"""
        self.selected_methods = methods
        self.page.go("/execution")

    async def _on_ai_analyze(self) -> Dict[str, Any]:
        """Manejar análisis IA"""
        if not self.selected_device:
            return {}

        # Análisis simple basado en el dispositivo
        device = self.selected_device

        # Determinar complejidad
        complexity = 0.5
        if device.android_version and device.android_version.startswith("15"):
            complexity = 0.8
        elif device.android_version and device.android_version.startswith("14"):
            complexity = 0.6
        elif device.android_version and device.android_version.startswith("13"):
            complexity = 0.4

        # Determinar vulnerabilidad
        vulnerability = 0.7 - complexity

        # Métodos recomendados
        recommended = []
        for method in self.bypass_manager.get_methods():
            if method.category == "adb" and method.success_rate > 0.8:
                recommended.append(method.name)
                if len(recommended) >= 3:
                    break

        # Probabilidades de éxito
        probs = {}
        for method in self.bypass_manager.get_methods():
            base = method.success_rate
            adjusted = base * (1 + (1 - complexity) * 0.2)
            probs[method.name] = min(adjusted, 1.0)

        # Evaluación de seguridad
        if vulnerability > 0.7:
            security = "Alta vulnerabilidad - Múltiples vectores disponibles"
        elif vulnerability > 0.4:
            security = "Vulnerabilidad moderada - Varias opciones posibles"
        else:
            security = "Baja vulnerabilidad - Métodos limitados"

        return {
            "device_profile": {
                "complexity_score": complexity,
                "vulnerability_score": vulnerability,
                "recommended_methods": recommended,
                "success_probabilities": probs,
            },
            "security_assessment": security,
            "bypass_strategy": (
                "Iniciar con métodos ADB, luego interfaz"
                if complexity < 0.6
                else "Métodos de interfaz primero"
            ),
        }

    async def _on_execute_bypass(self, progress_callback):
        """Manejar ejecución de bypass"""
        if not self.selected_device or not self.selected_methods:
            return

        self.logger.info(f"Iniciando ejecución de bypass en {self.selected_device.serial}")

        # Ejecutar métodos
        results = await self.bypass_manager.execute_methods(
            self.selected_device, self.selected_methods, progress_callback
        )

        self.execution_results = results

        # Auditoría
        success = any(r.get("result") == "success" for r in results)
        self.audit_logger.log_bypass_result(
            self.selected_device.serial,
            success,
            [r.get("method", "") for r in results],
            0,  # Tiempo de ejecución
        )

        return results

    def _on_execution_cancel(self):
        """Manejar cancelación de ejecución"""
        self.bypass_manager.cancel_execution()

    def _on_tcp_switch(self, e):
        """Manejar cambio de TCP"""
        self.config.set("android.use_tcp_adb", e.control.value)

    def _on_debug_switch(self, e):
        """Manejar cambio de debug"""
        self.config.set("app.debug_mode", e.control.value)
        if e.control.value:
            self.logger.set_level(logging.DEBUG)
        else:
            self.logger.set_level(logging.INFO)

    def _show_help(self):
        """Mostrar ayuda"""
        help_dialog = ft.AlertDialog(
            title=ft.Text("Ayuda de FRP Freedom"),
            content=ft.Column(
                [
                    ft.Text("1. Conecta tu dispositivo vía USB"),
                    ft.Text("2. Habilita USB Debugging en Opciones de Desarrollador"),
                    ft.Text("3. Selecciona tu dispositivo"),
                    ft.Text("4. Elige los métodos de bypass"),
                    ft.Text("5. Ejecuta el bypass"),
                    ft.Divider(),
                    ft.Text("Para más ayuda, visita nuestra web.", italic=True),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: self._close_dialog())],
        )
        self.page.dialog = help_dialog
        help_dialog.open = True
        self.page.update()

    def _close_dialog(self):
        """Cerrar diálogo"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()


def main():
    """Punto de entrada de la aplicación"""
    app = FRPFreedomApp()
    ft.app(target=app.init)


if __name__ == "__main__":
    main()
