"""
Methods View - Selección de métodos con IA
"""

import flet as ft
from typing import Callable, Optional, List

from ..models.device_model import DeviceInfo, BypassMethod


class MethodsView(ft.View):
    """Pantalla de selección de métodos"""

    def __init__(
        self,
        page: ft.Page,
        device: DeviceInfo,
        methods: List[BypassMethod],
        on_methods_selected: Optional[Callable] = None,
        on_back: Optional[Callable] = None,
        on_ai_analyze: Optional[Callable] = None,
    ):
        super().__init__(route="/methods")
        self.page = page
        self.device = device
        self.methods = methods
        self.on_methods_selected = on_methods_selected
        self.on_back = on_back
        self.on_ai_analyze = on_ai_analyze

        self.selected_methods = []
        self.is_loading = False
        self.ai_analysis = None

        self.scroll = ft.ScrollMode.AUTO
        self.controls = self._build_ui()

    def _build_ui(self):
        """Construir la interfaz"""
        return [
            ft.AppBar(
                title=ft.Text("Seleccionar Métodos"),
                bgcolor=ft.colors.PRIMARY,
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: self.on_back() if self.on_back else None,
                ),
            ),
            ft.Container(
                content=ft.Column(
                    [
                        self._build_device_info(),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    text="ANÁLISIS IA",
                                    icon=ft.icons.BRAIN,
                                    on_click=self._on_ai_analyze,
                                    width=float("inf"),
                                    height=40,
                                    disabled=self.is_loading,
                                )
                            ]
                        ),
                        ft.Container(
                            content=self._build_ai_analysis(), visible=False, id="ai_container"
                        ),
                        ft.Text("Métodos Disponibles", size=16, weight=ft.FontWeight.BOLD),
                        self._build_method_list(),
                        self._build_selection_info(),
                        ft.ElevatedButton(
                            text="CONFIRMAR Y CONTINUAR",
                            icon=ft.icons.ARROW_FORWARD,
                            on_click=self._on_confirm,
                            width=float("inf"),
                            height=48,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=12),
                                text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
                            ),
                        ),
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
                    ft.Icon(ft.icons.PHONE_ANDROID, size=32, color=ft.colors.PRIMARY),
                    ft.Column(
                        [
                            ft.Text(
                                f"{self.device.brand} {self.device.model}",
                                size=15,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                f"Android {self.device.android_version} • {self.device.connection_type.upper()}",
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

    def _build_method_list(self):
        """Construir lista de métodos"""
        self.method_list = ft.ListView(
            spacing=8, height=250, padding=ft.padding.symmetric(vertical=8)
        )

        for method in self.methods:
            self.method_list.controls.append(self._build_method_item(method))

        return self.method_list

    def _build_method_item(self, method: BypassMethod):
        """Construir item de método"""
        is_selected = method.name in [m.name for m in self.selected_methods]

        risk_colors = {"low": ft.colors.GREEN, "medium": ft.colors.ORANGE, "high": ft.colors.RED}
        risk_color = risk_colors.get(method.risk_level, ft.colors.GREY)

        return ft.Container(
            content=ft.Row(
                [
                    ft.Checkbox(
                        value=is_selected,
                        on_change=lambda e, m=method: self._toggle_method(m),
                        active_color=ft.colors.PRIMARY,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                method.name.replace("_", " ").title(),
                                size=14,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                (
                                    method.description[:60] + "..."
                                    if len(method.description) > 60
                                    else method.description
                                ),
                                size=12,
                                color=ft.colors.GREY_400,
                            ),
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(method.category.upper(), size=9),
                                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                        bgcolor=ft.colors.PRIMARY_CONTAINER,
                                        border_radius=ft.border_radius.all(8),
                                    ),
                                    ft.Container(
                                        content=ft.Text(method.risk_level.upper(), size=9),
                                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                        bgcolor=risk_color,
                                        border_radius=ft.border_radius.all(8),
                                    ),
                                    ft.Text(
                                        f"{method.success_rate:.0%} éxito",
                                        size=10,
                                        color=ft.colors.GREY_400,
                                    ),
                                ],
                                spacing=6,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Text(f"{method.estimated_time}m", size=12, color=ft.colors.GREY_400),
                ]
            ),
            padding=ft.padding.all(10),
            bgcolor=ft.colors.SURFACE,
            border_radius=ft.border_radius.all(10),
        )

    def _build_ai_analysis(self):
        """Construir análisis IA"""
        self.ai_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.BRAIN, color=ft.colors.PRIMARY),
                            ft.Text("Análisis IA", size=15, weight=ft.FontWeight.BOLD),
                        ]
                    ),
                    ft.Text(
                        "Esperando análisis...", id="ai_result", size=13, color=ft.colors.GREY_400
                    ),
                ]
            ),
            padding=ft.padding.all(12),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=ft.border_radius.all(12),
        )
        return self.ai_container

    def _build_selection_info(self):
        """Construir información de selección"""
        self.selection_info = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "No hay métodos seleccionados",
                        id="selection_text",
                        size=13,
                        color=ft.colors.GREY_400,
                    ),
                    ft.Text("", id="selection_count", size=13, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(vertical=8),
        )
        return self.selection_info

    def _toggle_method(self, method: BypassMethod):
        """Alternar selección de método"""
        if method.name in [m.name for m in self.selected_methods]:
            self.selected_methods = [m for m in self.selected_methods if m.name != method.name]
        else:
            self.selected_methods.append(method)

        self._update_method_list()

    def _update_method_list(self):
        """Actualizar lista de métodos"""
        if self.method_list:
            self.method_list.controls.clear()
            for method in self.methods:
                self.method_list.controls.append(self._build_method_item(method))

            count = len(self.selected_methods)
            if count == 0:
                self.selection_info.content.controls[0].value = "No hay métodos seleccionados"
                self.selection_info.content.controls[1].value = ""
            else:
                self.selection_info.content.controls[0].value = "Métodos seleccionados:"
                self.selection_info.content.controls[1].value = f"{count} método(s)"

            self.page.update()

    async def _on_ai_analyze(self, e):
        """Manejar análisis IA"""
        if not self.on_ai_analyze or self.is_loading:
            return

        self.is_loading = True
        self.ai_container.visible = True
        self.ai_container.content.controls[1].value = "Analizando dispositivo..."
        self.page.update()

        try:
            analysis = await self.on_ai_analyze()
            self.ai_analysis = analysis

            if analysis:
                result_text = self._format_ai_analysis(analysis)
                self.ai_container.content.controls[1].value = result_text

                # Auto-seleccionar métodos recomendados
                recommended = analysis.get("recommended_methods", [])
                if recommended:
                    self.selected_methods = [m for m in self.methods if m.name in recommended[:3]]
                    self._update_method_list()
            else:
                self.ai_container.content.controls[1].value = (
                    "No hay análisis IA disponible para este dispositivo."
                )

        except Exception as e:
            self.ai_container.content.controls[1].value = f"Error en análisis: {str(e)}"

        self.is_loading = False
        self.page.update()

    def _format_ai_analysis(self, analysis: dict) -> str:
        """Formatear análisis IA"""
        parts = []

        security = analysis.get("security_assessment", "")
        if security:
            parts.append(f"🔒 {security}")

        recommended = analysis.get("recommended_methods", [])
        if recommended:
            parts.append(f"\n💡 Recomendados: {', '.join(recommended[:3])}")

        probs = analysis.get("success_probabilities", {})
        if probs:
            top_methods = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]
            parts.append("\n📊 Probabilidades:")
            for name, prob in top_methods:
                parts.append(f"  • {name}: {prob:.0%}")

        return "\n".join(parts)

    def _on_confirm(self, e):
        """Manejar confirmación"""
        if not self.selected_methods:
            self._show_error("Selección Requerida", "Selecciona al menos un método de bypass.")
            return

        if self.on_methods_selected:
            self.on_methods_selected(self.selected_methods)

    def _show_error(self, title: str, message: str):
        """Mostrar error"""
        dialog = ft.AlertDialog(
            title=ft.Text(title, color=ft.colors.RED),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=self._close_dialog)],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self, e):
        """Cerrar diálogo"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
