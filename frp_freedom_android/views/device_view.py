"""
Device View - Selección de dispositivo
"""

import flet as ft
from typing import Callable, Optional, List

from ..models.device_model import DeviceInfo


class DeviceView(ft.View):
    """Pantalla de selección de dispositivo"""

    def __init__(
        self,
        page: ft.Page,
        devices: List[DeviceInfo],
        on_device_selected: Optional[Callable] = None,
        on_scan: Optional[Callable] = None,
        on_back: Optional[Callable] = None,
    ):
        super().__init__(route="/device")
        self.page = page
        self.devices = devices
        self.on_device_selected = on_device_selected
        self.on_scan = on_scan
        self.on_back = on_back

        self.selected_index = -1
        self.device_list = None
        self.status_text = None
        self.is_scanning = False

        self.scroll = ft.ScrollMode.AUTO
        self.controls = self._build_ui()

        # Auto-scroll al inicio
        self.page.update()

    def _build_ui(self):
        """Construir la interfaz"""
        return [
            ft.AppBar(
                title=ft.Text("Seleccionar Dispositivo"),
                bgcolor=ft.colors.PRIMARY,
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: self.on_back() if self.on_back else None,
                ),
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Conecta tu dispositivo vía USB y habilita USB Debugging",
                                        size=14,
                                    ),
                                    ft.Text(
                                        "Acepta la autorización en el dispositivo cuando aparezca",
                                        size=12,
                                        color=ft.colors.GREY_400,
                                    ),
                                ],
                                spacing=4,
                            ),
                            padding=ft.padding.all(16),
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            border_radius=ft.border_radius.all(12),
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    text="ESCANEAR DISPOSITIVOS",
                                    icon=ft.icons.REFRESH,
                                    on_click=self._on_scan_click,
                                    width=float("inf"),
                                    height=40,
                                    disabled=self.is_scanning,
                                )
                            ]
                        ),
                        self._build_device_list(),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Text(
                                        f"{len(self.devices)} dispositivo(s) encontrado(s)",
                                        id="status_text",
                                        size=13,
                                        color=ft.colors.GREY_400,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.HELP_OUTLINE,
                                        tooltip="Ayuda de conexión",
                                        icon_size=20,
                                        on_click=self._show_help,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=ft.padding.symmetric(vertical=10),
                        ),
                    ]
                ),
                padding=ft.padding.all(16),
                expand=True,
            ),
        ]

    def _build_device_list(self):
        """Construir lista de dispositivos"""
        self.device_list = ft.ListView(
            spacing=8, padding=ft.padding.symmetric(vertical=8), height=300
        )

        if self.devices:
            for i, device in enumerate(self.devices):
                self.device_list.controls.append(self._build_device_item(device, i))
        else:
            self.device_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No se encontraron dispositivos.\nConecta un dispositivo y presiona Escanear.",
                        color=ft.colors.GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=ft.padding.all(30),
                    alignment=ft.alignment.center,
                )
            )

        return self.device_list

    def _build_device_item(self, device: DeviceInfo, index: int):
        """Construir item de dispositivo"""
        is_selected = index == self.selected_index

        # Color según estado
        status_color = (
            ft.colors.GREEN if device.connection_type in ["adb", "fastboot"] else ft.colors.ORANGE
        )

        # Estado FRP
        frp_color = ft.colors.RED if device.frp_status == "locked" else ft.colors.GREEN

        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.icons.PHONE_ANDROID,
                        color=ft.colors.PRIMARY if is_selected else ft.colors.GREY_400,
                        size=32,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                device.model or "Dispositivo Desconocido",
                                size=15,
                                weight=ft.FontWeight.W_500,
                                color=ft.colors.ON_BACKGROUND,
                            ),
                            ft.Text(
                                f"Serial: {device.serial[:8]}... | {device.connection_type.upper()}",
                                size=12,
                                color=ft.colors.GREY_400,
                            ),
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(f"FRP: {device.frp_status}", size=10),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        bgcolor=frp_color,
                                        border_radius=ft.border_radius.all(10),
                                    ),
                                    ft.Text(
                                        f"Android {device.android_version or '?'}",
                                        size=11,
                                        color=ft.colors.GREY_400,
                                    ),
                                ],
                                spacing=8,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.icons.CHECK_CIRCLE if is_selected else ft.icons.CIRCLE_OUTLINED,
                        color=ft.colors.PRIMARY if is_selected else ft.colors.GREY_400,
                        size=24,
                    ),
                ]
            ),
            padding=ft.padding.all(12),
            bgcolor=ft.colors.PRIMARY_CONTAINER if is_selected else ft.colors.SURFACE,
            border_radius=ft.border_radius.all(12),
            border=ft.border.all(1, ft.colors.PRIMARY if is_selected else ft.colors.TRANSPARENT),
            on_click=lambda e, idx=index: self._select_device(idx),
        )

    def _select_device(self, index: int):
        """Seleccionar un dispositivo"""
        if index < len(self.devices):
            self.selected_index = index
            self._update_device_list()

            if self.on_device_selected:
                self.on_device_selected(self.devices[index])

    async def _on_scan_click(self, e):
        """Manejar click en escanear"""
        if self.is_scanning or not self.on_scan:
            return

        self.is_scanning = True
        self._update_status("Escaneando dispositivos...")
        self.page.update()

        try:
            await self.on_scan()
        except Exception as e:
            print(f"Error en escaneo: {e}")
        finally:
            self.is_scanning = False
            self._update_status(f"{len(self.devices)} dispositivo(s) encontrado(s)")
            self.page.update()

    def _update_status(self, text: str):
        """Actualizar texto de estado"""
        # Buscar el texto de estado
        for control in self.controls:
            if isinstance(control, ft.Container):
                for child in control.content.controls:
                    if isinstance(child, ft.Container):
                        if hasattr(child.content, "controls"):
                            for row_child in child.content.controls:
                                if hasattr(row_child, "id") and row_child.id == "status_text":
                                    row_child.value = text
                                    return

    def _update_device_list(self):
        """Actualizar la lista de dispositivos"""
        if self.device_list:
            self.device_list.controls.clear()

            if self.devices:
                for i, device in enumerate(self.devices):
                    self.device_list.controls.append(self._build_device_item(device, i))
            else:
                self.device_list.controls.append(
                    ft.Container(
                        content=ft.Text(
                            "No se encontraron dispositivos.\nConecta un dispositivo y presiona Escanear.",
                            color=ft.colors.GREY_400,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        padding=ft.padding.all(30),
                        alignment=ft.alignment.center,
                    )
                )

            self._update_status(f"{len(self.devices)} dispositivo(s) encontrado(s)")
            self.page.update()

    def update_devices(self, devices: List[DeviceInfo]):
        """Actualizar lista de dispositivos desde fuera"""
        self.devices = devices
        self.selected_index = -1
        self._update_device_list()

    def _show_help(self, e):
        """Mostrar ayuda de conexión"""
        help_dialog = ft.AlertDialog(
            title=ft.Text("Ayuda de Conexión"),
            content=ft.Column(
                [
                    ft.Text("1. Habilitar Opciones de Desarrollador:", weight=ft.FontWeight.BOLD),
                    ft.Text("Ajustes → Acerca del teléfono → Toca 7 veces Número de compilación"),
                    ft.Text("2. Habilitar USB Debugging:", weight=ft.FontWeight.BOLD),
                    ft.Text("Ajustes → Opciones de Desarrollador → Habilitar USB Debugging"),
                    ft.Text("3. Conectar Dispositivo:", weight=ft.FontWeight.BOLD),
                    ft.Text("Conecta vía USB y acepta la autorización en el dispositivo"),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[ft.TextButton("Cerrar", on_click=self._close_dialog)],
        )
        self.page.dialog = help_dialog
        help_dialog.open = True
        self.page.update()

    def _close_dialog(self, e):
        """Cerrar diálogo"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
