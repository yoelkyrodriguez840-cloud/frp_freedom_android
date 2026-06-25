"""
Execution View - Ejecución de bypass con progreso
"""

import flet as ft
import asyncio
from typing import Callable, Optional, List

from ..models.device_model import DeviceInfo, BypassMethod


class ExecutionView(ft.View):
    """Pantalla de ejecución de bypass"""

    def __init__(
        self,
        page: ft.Page,
        device: DeviceInfo,
        methods: List[BypassMethod],
        on_execute: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        on_back: Optional[Callable] = None,
    ):
        super().__init__(route="/execution")
        self.page = page
        self.device = device
        self.methods = methods
        self.on_execute = on_execute
        self.on_cancel = on_cancel
        self.on_back = on_back

        self.is_running = False
        self.is_cancelled = False
        self.current_method_index = 0
        self.results = []

        self.scroll = ft.ScrollMode.AUTO
        self.controls = self._build_ui()

        # Auto-iniciar ejecución
        self.page.run_task(self._start_execution)

    def _build_ui(self):
        """Construir la interfaz"""
        self.progress_value = ft.Text("0%", size=20, weight=ft.FontWeight.BOLD)
        self.progress_bar = ft.ProgressBar(value=0, width=float("inf"), height=8)
        self.status_text = ft.Text("Inicializando...", size=14)
        self.current_method_text = ft.Text("Preparando...", size=13, color=ft.colors.GREY_400)
        self.log_text = ft.Text("", size=12, color=ft.colors.GREY_400, selectable=True)
        self.time_text = ft.Text("00:00", size=13, weight=ft.FontWeight.W_500)
        self.log_container_visible = False

        return [
            ft.AppBar(
                title=ft.Text("Ejecutando Bypass"),
                bgcolor=ft.colors.PRIMARY,
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK, on_click=self._on_back, disabled=True
                ),
            ),
            ft.Container(
                content=ft.Column(
                    [
                        self._build_device_info(),
                        self._build_progress_section(),
                        self._build_method_status(),
                        self._build_log_section(),
                        self._build_action_buttons(),
                    ]
                ),
                padding=ft.padding.all(16),
                expand=True,
            ),
        ]

    def _build_device_info(self):
        """Construir información del dispositivo"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.PHONE_ANDROID, size=28, color=ft.colors.PRIMARY),
                    ft.Column(
                        [
                            ft.Text(
                                f"{self.device.brand} {self.device.model}",
                                size=14,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                f"Android {self.device.android_version} • {len(self.methods)} métodos",
                                size=12,
                                color=ft.colors.GREY_400,
                            ),
                        ],
                        spacing=2,
                    ),
                ]
            ),
            padding=ft.padding.all(12),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=ft.border_radius.all(12),
        )

    def _build_progress_section(self):
        """Construir sección de progreso"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            self.progress_value,
                            ft.Text("completado", size=14, color=ft.colors.GREY_400),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    self.progress_bar,
                    ft.Row(
                        [self.status_text, self.time_text],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.all(16),
            bgcolor=ft.colors.SURFACE,
            border_radius=ft.border_radius.all(12),
        )

    def _build_method_status(self):
        """Construir estado del método actual"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Método Actual", size=13, color=ft.colors.GREY_400),
                    self.current_method_text,
                ]
            ),
            padding=ft.padding.all(12),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=ft.border_radius.all(12),
        )

    def _build_log_section(self):
        """Construir sección de log"""
        self.log_container = ft.Container(
            content=ft.Column([self.log_text], scroll=ft.ScrollMode.AUTO),
            height=150,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=ft.border_radius.all(12),
            padding=ft.padding.all(12),
            visible=False,
        )
        return self.log_container

    def _build_action_buttons(self):
        """Construir botones de acción"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.ElevatedButton(
                        text="CANCELAR",
                        icon=ft.icons.CLOSE,
                        on_click=self._on_cancel,
                        width=150,
                        height=44,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    ),
                    ft.ElevatedButton(
                        text="VER LOG",
                        icon=ft.icons.LIST_ALT,
                        on_click=self._toggle_log,
                        width=150,
                        height=44,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
            ),
            padding=ft.padding.only(top=16),
        )

    async def _start_execution(self):
        """Iniciar ejecución"""
        if self.is_running:
            return

        self.is_running = True
        self.is_cancelled = False

        self.progress_value.value = "0%"
        self.progress_bar.value = 0
        self.status_text.value = "Iniciando bypass..."
        self.current_method_text.value = "Preparando..."
        self._update_time()

        self.start_time = asyncio.get_event_loop().time()

        try:
            if self.on_execute:
                await self.on_execute(self._on_progress_update)
            else:
                await self._simulate_execution()

        except asyncio.CancelledError:
            self.status_text.value = "Cancelado"
            self.is_running = False
            self.page.update()
            return

        except Exception as e:
            self.status_text.value = f"Error: {str(e)}"
            self.page.update()

        self.is_running = False
        self._update_ui_complete()

    async def _simulate_execution(self):
        """Simular ejecución para demostración"""
        total_methods = len(self.methods)

        for i, method in enumerate(self.methods):
            if self.is_cancelled:
                break

            self.current_method_index = i
            self.status_text.value = f"Ejecutando {method.name.replace('_', ' ').title()}..."
            self.current_method_text.value = (
                f"{method.name.replace('_', ' ').title()} ({i+1}/{total_methods})"
            )

            progress = (i + 0.5) / total_methods
            self.progress_bar.value = progress
            self.progress_value.value = f"{int(progress * 100)}%"

            self._add_log(f"Iniciando {method.name}")

            for step in range(10):
                if self.is_cancelled:
                    break

                step_progress = (i + (step + 1) / 10) / total_methods
                self.progress_bar.value = step_progress
                self.progress_value.value = f"{int(step_progress * 100)}%"

                if step % 2 == 0:
                    self._add_log(f"  Paso {step+1}/10 en progreso...")

                await asyncio.sleep(0.5)

            if not self.is_cancelled:
                self._add_log(f"✓ {method.name} completado")

        self.progress_bar.value = 1.0
        self.progress_value.value = "100%"
        self.status_text.value = "¡Bypass Completado!" if not self.is_cancelled else "Cancelado"

    def _on_progress_update(self, status: str, progress: float):
        """Actualizar progreso"""
        self.status_text.value = status
        self.progress_bar.value = progress / 100
        self.progress_value.value = f"{int(progress)}%"
        self.current_method_text.value = status
        self.page.update()

    def _add_log(self, message: str):
        """Agregar mensaje al log"""
        current = self.log_text.value or ""
        self.log_text.value = current + message + "\n"
        self.log_container.visible = True
        self.page.update()

    def _update_time(self):
        """Actualizar tiempo transcurrido"""
        if not self.is_running:
            return

        elapsed = asyncio.get_event_loop().time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        self.time_text.value = f"{minutes:02d}:{seconds:02d}"
        self.page.update()

        self.page.run_task(lambda: asyncio.sleep(1), self._update_time)

    def _update_ui_complete(self):
        """Actualizar UI al completar"""
        self.is_running = False
        self.progress_value.value = "100%" if not self.is_cancelled else "Cancelado"
        self.status_text.value = "Completado" if not self.is_cancelled else "Cancelado"
        self.page.update()

    def _on_back(self, e):
        """Volver atrás"""
        if self.is_running:
            return
        if self.on_back:
            self.on_back()

    def _on_cancel(self, e):
        """Cancelar ejecución"""
        if not self.is_running:
            return

        self.is_cancelled = True
        self.status_text.value = "Cancelando..."
        self._add_log("Cancelación solicitada por el usuario")

        if self.on_cancel:
            self.on_cancel()

    def _toggle_log(self, e):
        """Alternar visibilidad del log"""
        self.log_container.visible = not self.log_container.visible
        self.page.update()
