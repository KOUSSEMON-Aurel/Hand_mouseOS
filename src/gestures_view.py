import flet as ft
from src.skeleton_assets import SkeletonAssets

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
                            (255, 255, 0) # Cyan BGR
                        ),
                        
                        # --- CLIC ---
                        self._build_premium_card(
                            "CLIC GAUCHE", 
                            "PINCEMENT", 
                            "Rapprochez le pouce et l'index (< 4cm).",
                            "M",
                            ft.Colors.AMBER_400,
                            (0, 200, 255) # Amber/Orange BGR
                        ),
                        
                        # --- FIST (Future Scroll) ---
                        self._build_premium_card(
                            "SCROLL / ACTIONS", 
                            "POING FERMÉ", 
                            "Fermez la main pour activer le défilement (Secondary Hand).",
                            "S",
                            ft.Colors.PURPLE_400,
                            (255, 0, 255) # Purple BGR
                        ),
                        
                        # --- PEACE ---
                        self._build_premium_card(
                            "RACCOURCI", 
                            "VICTOIRE / V", 
                            "Prise de screenshot ou action rapide personnalisée.",
                            "S",
                            ft.Colors.GREEN_400,
                            (0, 255, 0) # Green BGR
                        ),
                        
                        # --- THUMBS UP ---
                        self._build_premium_card(
                            "VALIDATION", 
                            "POUCE LEVÉ", 
                            "Valider une boîte de dialogue ou dire OK au système.",
                            "S",
                            ft.Colors.BLUE_400,
                            (255, 0, 0) # Blue BGR
                        ),

                        # --- STOP ---
                        self._build_premium_card(
                            "SYSTÈME", 
                            "TOUCHE 'Q'", 
                            "Quitter instantanément le moteur de détection AI.",
                            "ESC",
                            ft.Colors.RED_400,
                            ft.Icons.POWER_SETTINGS_NEW # Fallback icon
                        ),

                    ], spacing=20, run_spacing=20),
                    
                ], horizontal_alignment=ft.CrossAxisAlignment.START)
            )
        ]

    def _build_premium_card(self, title, gesture, description, tag, theme_color, image_or_color):
        """Construction d'une carte avec Squelette 3D généré ou Icône."""
        
        visual_content = None
        
        # If image_or_color is a Tuple (BGR), we generate the skeleton
        if isinstance(image_or_color, tuple):
            bgr_color = image_or_color
            # Generate Base64 Image (Ultra Max resolution)
            skel_b64 = SkeletonAssets.generate_image(
                gesture, 
                width=450, 
                height=450, 
                color=bgr_color,
                thickness=6
            )
            visual_content = ft.Image(
                src=f"data:image/png;base64,{skel_b64}",
                width=260,
                height=260,
                fit=ft.BoxFit.CONTAIN,
                gapless_playback=True 
            )
        # Else if it's an Icon (for STOP button etc)
        elif isinstance(image_or_color, str) and not image_or_color.endswith(".svg"):
             visual_content = ft.Icon(image_or_color, size=160, color=theme_color)
        else:
            # Fallback
            visual_content = ft.Icon(ft.Icons.HELP_OUTLINE, size=160, color=theme_color)

        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 4},
            height=480, # Fixed Height
            bgcolor="#232529",
            border_radius=20,
            padding=20,
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
                    # Small icon top right (Visual Flair)
                    ft.Icon(ft.Icons.AUTO_GRAPH, color=theme_color, size=24),
                ]),
                
                ft.Container(height=5), # Minimal spacing top
                
                # Visual Centerpiece (Skeleton Hand) - UBER MAXIMIZED
                ft.Container(
                    content=ft.Stack([
                        # Outer Glow
                        ft.Container(
                            width=280, height=280,
                            bgcolor=ft.Colors.with_opacity(0.05, theme_color),
                            border_radius=140,
                        ),
                        # Central Content
                        ft.Container(
                            content=visual_content,
                            alignment=ft.Alignment(0, 0),
                            width=280, height=280,
                        )
                    ]),
                    alignment=ft.Alignment(0, 0),
                ),
                
                ft.Container(height=15), # Reduced spacing bottom
                
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
