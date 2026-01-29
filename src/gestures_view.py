import flet as ft

class GesturesView(ft.Column):
    def __init__(self, main_app=None):
        super().__init__()
        self.expand = True
        self.scroll = "auto"
        self.main_app = main_app
        
        self.controls = [
            ft.Container(
                padding=ft.padding.only(left=40, right=40, top=40, bottom=40),
                content=ft.Column([
                    ft.Column([
                        ft.Text("Bibliothèque de Gestes", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("L'interface du futur, au bout de vos doigts.", size=18, color=ft.Colors.GREY_400),
                    ], spacing=10),
                    
                    ft.Container(height=40),
                    
                    ft.ResponsiveRow([
                        # --- MOUVEMENT ---
                        self._build_premium_card(
                            "PILOTAGE", 
                            "PAUME OUVERTE", 
                            "Le curseur suit votre index. Gardez la main détendue.",
                            "M", 
                            ft.Colors.CYAN_400,
                            "assets/gestures/palm.svg"
                        ),
                        
                        # --- CLIC ---
                        self._build_premium_card(
                            "CLIC GAUCHE", 
                            "PINCEMENT", 
                            "Rapprochez le pouce et l'index (< 4cm).",
                            "M",
                            ft.Colors.AMBER_400,
                            "assets/gestures/pinch.svg"
                        ),
                        
                        # --- FIST (Future Scroll) ---
                        self._build_premium_card(
                            "SCROLL / ACTIONS", 
                            "POING FERMÉ", 
                            "Fermez la main pour activer le défilement (Secondary Hand).",
                            "S",
                            ft.Colors.PURPLE_400,
                            "assets/gestures/fist.svg"
                        ),
                        
                        # --- PEACE ---
                        self._build_premium_card(
                            "RACCOURCI", 
                            "VICTOIRE / V", 
                            "Prise de screenshot ou action rapide personnalisée.",
                            "S",
                            ft.Colors.GREEN_400,
                            "assets/gestures/peace.svg"
                        ),
                        
                        # --- THUMBS UP ---
                        self._build_premium_card(
                            "VALIDATION", 
                            "POUCE LEVÉ", 
                            "Valider une boîte de dialogue ou dire OK au système.",
                            "S",
                            ft.Colors.BLUE_400,
                            "assets/gestures/thumbs_up.svg"
                        ),

                        # --- STOP ---
                        self._build_premium_card(
                            "SYSTÈME", 
                            "TOUCHE 'Q'", 
                            "Quitter instantanément le moteur de détection AI.",
                            "ESC",
                            ft.Colors.RED_400,
                            ft.Icons.POWER_SETTINGS_NEW # Fallback icon for non-hand
                        ),

                    ], spacing=20, run_spacing=20),
                    
                ], horizontal_alignment=ft.CrossAxisAlignment.START)
            )
        ]

    def _build_premium_card(self, title, gesture, description, tag, theme_color, image_path):
        """Construction d'une carte au look 'Expressif' & Moderne avec mains SVG."""
        
        # Check if image_path is an SVG file or a Material Icon name
        is_svg = isinstance(image_path, str) and image_path.endswith(".svg")
        
        visual_content = None
        if is_svg:
            visual_content = ft.Image(
                src=image_path,
                width=80,
                height=80,
                color=theme_color,
                fit=ft.ImageFit.CONTAIN,
            )
        else:
            visual_content = ft.Icon(image_path, size=60, color=theme_color)

        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 4},
            bgcolor="#232529",
            border_radius=20,
            padding=30,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            on_hover=lambda e: self._handle_hover(e, theme_color),
            shadow=ft.BoxShadow(
                blur_radius=20,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 10),
            ),
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(tag, size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        bgcolor=theme_color,
                        padding=ft.padding.symmetric(6, 12),
                        border_radius=20,
                    ),
                    ft.Spacer() if hasattr(ft, "Spacer") else ft.Container(expand=True),
                    ft.Icon(image_path if not is_svg else ft.Icons.FINGERPRINT, color=theme_color, size=20),
                ]),
                
                ft.Container(height=30),
                
                # Visual Centerpiece (SVG Hand)
                ft.Container(
                    content=ft.Stack([
                        # Outer Glow
                        ft.Container(
                            width=120, height=120,
                            bgcolor=ft.Colors.with_opacity(0.05, theme_color),
                            border_radius=60,
                        ),
                        # Central Content
                        ft.Container(
                            content=visual_content,
                            alignment=ft.alignment.center,
                            width=120, height=120,
                        )
                    ]),
                    alignment=ft.alignment.center,
                ),
                
                ft.Container(height=30),
                
                ft.Text(title, size=14, color=theme_color, weight=ft.FontWeight.BOLD),
                ft.Text(gesture, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Container(height=10),
                ft.Text(description, size=14, color=ft.Colors.GREY_400),
                
            ], spacing=0)
        )

    def _handle_hover(self, e, color):
        if e.data == "true":
            e.control.border = ft.border.all(2, color)
            # Safe shadow update
            if e.control.shadow:
                e.control.shadow.blur_radius = 40
                e.control.shadow.color = ft.Colors.with_opacity(0.15, color)
        else:
            e.control.border = ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))
            if e.control.shadow:
                e.control.shadow.blur_radius = 20
                e.control.shadow.color = ft.Colors.with_opacity(0.05, ft.Colors.BLACK)
        e.control.update()
