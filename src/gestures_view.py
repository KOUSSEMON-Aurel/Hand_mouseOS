import flet as ft

class GesturesView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.scroll = "auto"
        
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text("Guide des Gestes", size=30, weight=ft.FontWeight.BOLD),
                    ft.Text("Maîtrisez votre souris virtuelle en un instant.", italic=True, color=ft.Colors.GREY_400),
                    ft.Divider(),
                    
                    self._build_gesture_card(
                        "DÉPLACEMENT",
                        "Main Ouverte",
                        "Déplacez simplement votre main. L'index dirige le curseur.",
                        ft.Icons.PAN_TOOL_ALT
                    ),
                    
                    self._build_gesture_card(
                        "CLIC GAUCHE",
                        "Pincement (Index + Pouce)",
                        "Collez le bout de votre index et de votre pouce pour cliquer.",
                        ft.Icons.TOUCH_APP,
                        color=ft.Colors.BLUE_400
                    ),
                    
                    self._build_gesture_card(
                        "ARRÊT D'URGENCE",
                        "Touche 'Q'",
                        "Appuyez sur 'Q' dans la fenêtre caméra pour tout arrêter.",
                        ft.Icons.STOP_CIRCLE,
                        color=ft.Colors.RED_400
                    ),
                    
                ], spacing=20),
                padding=20
            )
        ]

    def _build_gesture_card(self, title, gesture, description, icon, color=ft.Colors.WHITE):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=40, color=color),
                ft.Container(width=20),
                ft.Column([
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(gesture, size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(description, size=12, color=ft.Colors.GREY_400),
                ], expand=True)
            ]),
            bgcolor="#2b2d31",
            padding=20,
            border_radius=10
        )
