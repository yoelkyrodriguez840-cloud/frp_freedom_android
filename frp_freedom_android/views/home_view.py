"""
Home View - Pantalla principal
"""

import flet as ft
from typing import Callable, Optional


class HomeView(ft.View):
    """Pantalla principal de la aplicación"""

    def __init__(
        self,
        page: ft.Page,
        on_device_select: Optional[Callable] = None,
        on_settings: Optional[Callable] = None,
        on_help: Optional[Callable] = None,
    ):
        super().__init__(route="/")
        self.page = page
        self.on_device_select = on_device_select
        self.on_settings = on_settings
        self.on_help = on_help

        self.scroll = ft.ScrollMode.AUTO
        self.controls = self._build_ui()

    def _build_ui(self):
        """Construir la interfaz"""
        return [
            ft.AppBar(
                title=ft.Text("FRP Freedom", size=24, weight=ft.FontWeight.BOLD),
                center_title=False,
                bgcolor=ft.colors.PRIMARY,
                actions=[
                    ft.IconButton(
                        icon=ft.icons.HELP_OUTLINE,
                        tooltip="Ayuda",
                        on_click=lambda e: self.on_help() if self.on_help else None,
                    ),
                    ft.IconButton(
                        icon=ft.icons.SETTINGS_OUTLINED,
                        tooltip="Configuración",
                        on_click=lambda e: self.on_settings() if self.on_settings else None,
                    ),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.icons.SECURITY, size=80, color=ft.colors.PRIMARY),
                        ft.Text(
                            "Android FRP Bypass Tool",
                            size=18,
                            weight=ft.FontWeight.W_500,
                            color=ft.colors.GREY_400,
                        ),
                        ft.Text(
                            "Recupera el acceso a tu dispositivo bloqueado",
                            size=14,
                            color=ft.colors.GREY_500,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(vertical=30),
                width=float("inf"),
            ),
            ft.Container(
                content=ft.ElevatedButton(
                    text="INICIAR BYPASS",
                    icon=ft.icons.PLAY_ARROW,
                    on_click=lambda e: self.on_device_select() if self.on_device_select else None,
                    width=280,
                    height=56,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=28),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                    ),
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=20, bottom=30),
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Características", size=18, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=10),
                        self._build_feature_item(
                            ft.icons.PHONE_ANDROID,
                            "Detección de Dispositivos",
                            "Detecta automáticamente dispositivos Android conectados",
                        ),
                        self._build_feature_item(
                            ft.icons.SECURITY, "Múltiples Métodos", "ADB, Interfaz, Sistema y más"
                        ),
                        self._build_feature_item(
                            ft.icons.BRAIN,
                            "Análisis IA",
                            "Recomendaciones inteligentes para tu dispositivo",
                        ),
                        self._build_feature_item(
                            ft.icons.HISTORY, "Historial", "Seguimiento de intentos y resultados"
                        ),
                    ]
                ),
                padding=ft.padding.all(20),
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=ft.border_radius.all(16),
                margin=ft.margin.only(top=10, bottom=10),
            ),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text("Estado:", size=14, weight=ft.FontWeight.W_500),
                        ft.Text("Listo", size=14, color=ft.colors.GREEN),
                    ]
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                bgcolor=ft.colors.SURFACE,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Versión 1.0.0", size=12, color=ft.colors.GREY_500),
                        ft.Text(
                            "Solo para recuperación legítima de dispositivos",
                            size=11,
                            color=ft.colors.GREY_400,
                            italic=True,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(vertical=15),
            ),
        ]

    def _build_feature_item(self, icon, title, description):
        """Construir item de característica"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=ft.colors.PRIMARY, size=28),
                    ft.Column(
                        [
                            ft.Text(title, size=14, weight=ft.FontWeight.W_500),
                            ft.Text(description, size=12, color=ft.colors.GREY_400),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=12,
            ),
            padding=ft.padding.symmetric(vertical=8),
        )
