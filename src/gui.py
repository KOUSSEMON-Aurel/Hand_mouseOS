import flet as ft

class AppGUI:
    def __init__(self, engine):
        self.engine = engine
        self.page = None

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Hand_mouseOS"
        page.theme_mode = ft.ThemeMode.DARK
        page.window_width = 400
        page.window_height = 600
        page.window_resizable = False
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # --- Controls ---
        
        self.status_text = ft.Text("Status: Stopped", color=ft.Colors.RED_400, size=16)
        
        def toggle_engine(e):
            if self.engine.running:
                self.engine.stop()
                btn_start.content = ft.Text("Start Camera")
                btn_start.icon = ft.Icons.PLAY_ARROW
                self.status_text.value = "Status: Stopped"
                self.status_text.color = ft.Colors.RED_400
            else:
                self.engine.start()
                btn_start.content = ft.Text("Stop Camera")
                btn_start.icon = ft.Icons.STOP
                self.status_text.value = "Status: Running"
                self.status_text.color = ft.Colors.GREEN_400
            page.update()

        def on_smooth_change(e):
            val = int(e.control.value)
            self.engine.set_smoothing(val)
            lbl_smooth.value = f"Smoothing: {val}"
            page.update()

        btn_start = ft.ElevatedButton(
            content=ft.Text("Start Camera"),
            icon=ft.Icons.PLAY_ARROW,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=20,
            ),
            on_click=toggle_engine
        )

        slider_smooth = ft.Slider(
            min=1, max=20, divisions=19, value=5, label="{value}",
            on_change=on_smooth_change
        )
        lbl_smooth = ft.Text("Smoothing: 5")

        # --- Layout ---
        
        container = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.MOUSE, size=64, color=ft.Colors.BLUE_400),
                    ft.Text("Hand_mouseOS", size=32, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20, thickness=1),
                    self.status_text,
                    ft.Container(height=20),
                    btn_start,
                    ft.Container(height=40),
                    ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD),
                    lbl_smooth,
                    slider_smooth,
                    ft.Text("Tips: Pinch to Click, Index Up to Move", size=12, italic=True, color=ft.Colors.GREY_500),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=30,
            border_radius=20,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            width=320,
            height=500,
            animate=ft.Animation(500, ft.AnimationCurve.BOUNCE_OUT),
        )

        page.add(container)

