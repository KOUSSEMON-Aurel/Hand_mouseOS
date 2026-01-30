import flet as ft
from src.skeleton_assets import SkeletonAssets

class GesturesView(ft.Column):
    """Vue du menu des gestes - Système Simplifié à 5 gestes universels."""
    
    def __init__(self, main_app=None):
        super().__init__()
        self.expand = True
        self.scroll = "auto"
        self.main_app = main_app
        
        self.controls = [
            ft.Container(
                padding=ft.padding.only(left=40, right=40, top=30, bottom=40),
                content=ft.Column([
                    # Header
                    ft.Column([
                        ft.Text("🖐️ Système Gestuel Simplifié", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("5 gestes universels • 4 modes contextuels • Apprentissage en 3 minutes", 
                               size=16, color=ft.Colors.GREY_400),
                    ], spacing=8),
                    
                    ft.Container(height=30),
                    
                    # Section: 5 Gestes Universels
                    ft.Text("🎯 Les 5 Gestes Universels", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Ces 5 formes de main changent d'action selon le contexte.", 
                           size=14, color=ft.Colors.GREY_500),
                    
                    ft.Container(height=20),
                    
                    # Gesture Cards Row
                    ft.ResponsiveRow([
                        self._build_gesture_card("POINTING", "👆 POINTER", "Index tendu", "Déplacer le curseur", ft.Colors.CYAN_400, (255, 255, 0)),
                        self._build_gesture_card("PINCH", "👌 PINCER", "Pouce + Index", "Clic / Copier", ft.Colors.AMBER_400, (0, 200, 255)),
                        self._build_gesture_card("PALM", "✋ PAUME", "Main ouverte", "Stop / Maximiser", ft.Colors.GREEN_400, (0, 255, 0)),
                        self._build_gesture_card("FIST", "✊ POING", "Poing fermé", "Clic droit / Déplacer", ft.Colors.PURPLE_400, (255, 0, 255)),
                        self._build_gesture_card("TWO_FINGERS", "✌️ DEUX DOIGTS", "Index + Majeur", "Scroll / Changer app", ft.Colors.BLUE_400, (255, 100, 0)),
                    ], spacing=15, run_spacing=15),
                    
                    ft.Container(height=40),
                    
                    # Section: 4 Modes Contextuels
                    ft.Text("🎭 Les 4 Modes Contextuels", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Le système devine automatiquement le mode selon la position de votre main.", 
                           size=14, color=ft.Colors.GREY_500),
                    
                    ft.Container(height=20),
                    
                    # Mode Cards Row
                    ft.ResponsiveRow([
                        self._build_mode_card("🖱️", "CURSEUR", "Mode par défaut", "Au centre de l'écran", ft.Colors.CYAN_400),
                        self._build_mode_card("🪟", "FENÊTRES", "Gestion des fenêtres", "Près des bords de l'écran", ft.Colors.PURPLE_400),
                        self._build_mode_card("🎵", "MULTIMÉDIA", "Contrôle lecture", "Main en haut de l'écran", ft.Colors.GREEN_400),
                        self._build_mode_card("⌨️", "RACCOURCIS", "Ctrl+C, Ctrl+V...", "Main gauche en POING fixe", ft.Colors.AMBER_400),
                    ], spacing=15, run_spacing=15),
                    
                    ft.Container(height=40),
                    
                    # Quick Reference Table
                    self._build_quick_reference(),
                    
                ], horizontal_alignment=ft.CrossAxisAlignment.START, spacing=0)
            )
        ]

    def _build_gesture_card(self, gesture_id, title, subtitle, action, theme_color, bgr_color):
        """Construit une carte pour un geste universel."""
        
        # Generate skeleton image
        skel_b64 = SkeletonAssets.generate_image(
            gesture_id, 
            width=300, 
            height=300, 
            color=bgr_color,
            thickness=4
        )
        
        return ft.Container(
            col={"xs": 6, "sm": 4, "md": 2.4},
            bgcolor="#232529",
            border_radius=16,
            padding=15,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            on_hover=lambda e: self._handle_hover(e, theme_color),
            content=ft.Column([
                # Skeleton Image
                ft.Container(
                    content=ft.Image(
                        src=f"data:image/png;base64,{skel_b64}",
                        width=100,
                        height=100,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    alignment=ft.Alignment(0, 0),
                    bgcolor=ft.Colors.with_opacity(0.05, theme_color),
                    border_radius=50,
                    width=110,
                    height=110,
                ),
                ft.Container(height=10),
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=theme_color),
                ft.Text(subtitle, size=11, color=ft.Colors.GREY_400),
                ft.Container(height=5),
                ft.Text(f"→ {action}", size=10, color=ft.Colors.GREY_500, italic=True),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)
        )

    def _build_mode_card(self, emoji, title, description, trigger, theme_color):
        """Construit une carte pour un mode contextuel."""
        
        return ft.Container(
            col={"xs": 6, "sm": 6, "md": 3},
            bgcolor="#232529",
            border_radius=16,
            padding=20,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            on_hover=lambda e: self._handle_hover(e, theme_color),
            content=ft.Column([
                ft.Row([
                    ft.Text(emoji, size=40),
                    ft.Container(width=10),
                    ft.Column([
                        ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=theme_color),
                        ft.Text(description, size=12, color=ft.Colors.GREY_400),
                    ], spacing=2)
                ]),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text(f"📍 {trigger}", size=11, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.with_opacity(0.1, theme_color),
                    padding=ft.padding.symmetric(8, 12),
                    border_radius=8,
                )
            ], spacing=5)
        )

    def _build_quick_reference(self):
        """Construit la table de référence rapide."""
        
        # Quick action rows
        actions = [
            ("👆", "POINTER", "Curseur", "Déplacer"),
            ("👌", "PINCER", "Curseur", "Clic gauche"),
            ("👌", "PINCER (maintenu)", "Curseur", "Glisser-déposer"),
            ("✊", "POING", "Curseur", "Clic droit"),
            ("✌️", "DEUX DOIGTS", "Curseur", "Scroll"),
            ("✋", "PAUME", "Fenêtres", "Maximiser"),
            ("✊", "POING + mouvement", "Fenêtres", "Déplacer fenêtre"),
            ("✋", "PAUME (tap)", "Multimédia", "Play/Pause"),
            ("👌", "PINCER", "Raccourcis", "Copier (Ctrl+C)"),
            ("✋", "PAUME", "Raccourcis", "Coller (Ctrl+V)"),
        ]
        
        rows = []
        for emoji, gesture, mode, action in actions:
            rows.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(emoji, size=16, width=30),
                        ft.Text(gesture, size=12, color=ft.Colors.WHITE, width=130),
                        ft.Container(
                            content=ft.Text(mode, size=10, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.CYAN_400),
                            padding=ft.padding.symmetric(4, 8),
                            border_radius=4,
                            width=80,
                        ),
                        ft.Text(f"→ {action}", size=12, color=ft.Colors.GREY_400, expand=True),
                    ], spacing=10),
                    padding=ft.padding.symmetric(8, 10),
                    bgcolor="#1a1c20",
                    border_radius=8,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("📋 Référence Rapide", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Container(height=10),
                ft.Column(rows, spacing=5),
            ]),
            bgcolor="#1f2125",
            border_radius=16,
            padding=20,
        )

    def _handle_hover(self, e, color):
        if e.data == "true":
            e.control.border = ft.border.all(2, color)
        else:
            e.control.border = ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))
        e.control.update()
