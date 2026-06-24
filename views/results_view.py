"""
Results View - Resultados del bypass
"""

import flet as ft
from typing import Callable, Optional, List


class ResultsView(ft.View):
    """Pantalla de resultados"""

    def __init__(
        self,
        page: ft.Page,
        results: List,
        on_retry: Optional[Callable] = None,
        on_home: Optional[Callable] = None,
    ):
        super().__init__(route="/results")
        self.page = page
        self.results = results
        self.on_retry = on_retry
        self.on_home = on_home

        self.success_count = sum(1 for r in results if r.get("success", False))
        self.total_count = len(results)
        self.is_success = self.success_count > 0

        self.scroll = ft.ScrollMode.AUTO
        self.controls = self._build_ui()

    def _build_ui(self):
        """Construir la interfaz"""
        return [
            ft.AppBar(
                title=ft.Text("Resultados"),
                bgcolor=ft.colors.PRIMARY,
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: self.on_home() if self.on_home else None,
                ),
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(
                                ft.icons.CHECK_CIRCLE if self.is_success else ft.icons.ERROR,
                                size=80,
                                color=ft.colors.GREEN if self.is_success else ft.colors.RED,
                            ),
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(top=20, bottom=10),
                        ),
                        ft.Text(
                            "¡Bypass Exitoso!" if self.is_success else "Bypass Fallido",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.colors.GREEN if self.is_success else ft.colors.RED,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text("Métodos Intentados:", size=14),
                                            ft.Text(
                                                str(self.total_count),
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text("Exitosos:", size=14),
                                            ft.Text(
                                                str(self.success_count),
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.colors.GREEN,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text("Fallidos:", size=14),
                                            ft.Text(
                                                str(self.total_count - self.success_count),
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.colors.RED,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                ],
                                spacing=6,
                            ),
                            padding=ft.padding.all(16),
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            border_radius=ft.border_radius.all(12),
                        ),
                        ft.Text("Resultados por Método", size=15, weight=ft.FontWeight.W_500),
                        self._build_results_list(),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    text="REINTENTAR",
                                    icon=ft.icons.REFRESH,
                                    on_click=lambda e: self.on_retry() if self.on_retry else None,
                                    width=120,
                                    height=44,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    ),
                                ),
                                ft.ElevatedButton(
                                    text="INICIO",
                                    icon=ft.icons.HOME,
                                    on_click=lambda e: self.on_home() if self.on_home else None,
                                    width=120,
                                    height=44,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=12,
                        ),
                    ]
                ),
                padding=ft.padding.all(16),
                expand=True,
            ),
        ]

    def _build_results_list(self):
        """Construir lista de resultados"""
        results_list = ft.ListView(spacing=4, height=150, padding=ft.padding.symmetric(vertical=8))

        for result in self.results:
            method_name = result.get("method", "Desconocido")
            success = result.get("success", False)
            message = result.get("message", "")

            results_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.icons.CHECK_CIRCLE if success else ft.icons.ERROR,
                                color=ft.colors.GREEN if success else ft.colors.RED,
                                size=20,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        method_name.replace("_", " ").title(),
                                        size=13,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        message[:50] + "..." if len(message) > 50 else message,
                                        size=11,
                                        color=ft.colors.GREY_400,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "ÉXITO" if success else "FALLIDO",
                                    size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.GREEN if success else ft.colors.RED,
                                ),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                bgcolor=(
                                    ft.colors.GREEN_CONTAINER
                                    if success
                                    else ft.colors.RED_CONTAINER
                                ),
                                border_radius=ft.border_radius.all(8),
                            ),
                        ]
                    ),
                    padding=ft.padding.all(8),
                    bgcolor=ft.colors.SURFACE,
                    border_radius=ft.border_radius.all(8),
                )
            )

        return results_list
