import flet as ft
import platform

class SettingsView(ft.Column):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.expand = True
        self.scroll = "auto"
        
        # Get current sensitivity if possible
        current_sens = 10
        if hasattr(self.main_app.engine, 'mouse'):
            # This is a heuristic value 1-20
            current_sens = 10 
        
        self.slider = ft.Slider(
            min=1, max=20, divisions=19, value=current_sens,
            label="Sensibilité: {value}",
            on_change=self.on_sens_change
        )
        
        self.camera_selector = ft.Dropdown(
            label="Source Vidéo (Camera)",
            value=str(self.main_app.engine.camera_index),
            options=[
                ft.dropdown.Option("0", "Caméra 0 (Interne)"),
                ft.dropdown.Option("1", "Caméra 1 (Externe/DroidCam)"),
                ft.dropdown.Option("2", "Caméra 2"),
                ft.dropdown.Option("3", "Caméra 3"),
                ft.dropdown.Option("4", "Caméra 4"),
            ],
            width=300
        )
        self.camera_selector.on_change = self.on_camera_change
        
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text("Paramètres", size=30, weight=ft.FontWeight.BOLD),
                    ft.Text("Ajustez la réactivité du système", italic=True, color=ft.Colors.GREY_400),
                    ft.Divider(),
                    
                    ft.Container(height=20),
                    ft.Text("Vitesse / Lissage", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("Ajustez l'équilibre entre fluidité et rapidité.", size=12, color=ft.Colors.GREY_500),
                    self.slider,
                    
                    ft.Container(height=20),
                    ft.Text("Source Vidéo", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("Choisissez la caméra à utiliser.", size=12, color=ft.Colors.GREY_500),
                    self.camera_selector,
                    
                    ft.Container(height=40),
                    ft.Text("Matériel / Webcam", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("Utilisez votre téléphone comme une webcam haute qualité.", size=12, color=ft.Colors.GREY_500),
                    # Afficher le bouton DroidCam seulement sur Linux/Windows
                    ft.ElevatedButton(
                        "Installer DroidCam (Téléphone)",
                        icon=ft.Icons.PHONE_ANDROID,
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600,
                        on_click=lambda _: self.main_app.run_setup_webcam()
                    ) if platform.system() in ["Linux", "Windows"] else ft.Text(
                        "Installation DroidCam disponible sur Linux/Windows uniquement",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True
                    ),
                    
                    ft.Container(height=40),
                    ft.Text("Diagnostic", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"OS: {self.main_app.engine.mouse.os_name}"),
                            ft.Text(f"Prise en charge UInput: {'OUI' if self.main_app.engine.mouse.mode == 'uinput' else 'NON (Mode Lent)'}", 
                                    color=ft.Colors.GREEN if self.main_app.engine.mouse.mode == 'uinput' else ft.Colors.RED),
                            ft.Text("Si UInput est NON : Lancez 'sudo modprobe uinput' dans un terminal.", size=10, italic=True)
                        ]),
                        bgcolor="#222222", padding=10, border_radius=5
                    )
                    
                ], spacing=10),
                padding=20
            )
        ]

    def on_sens_change(self, e):
        val = e.control.value
        # 1 = Très lent (Beaucoup de lissage)
        # 20 = Très rapide (Peu de lissage)
        if hasattr(self.main_app.engine, 'mouse'):
             self.main_app.engine.mouse.set_smoothing(val)

    def on_camera_change(self, e):
        idx = int(e.control.value)
        self.main_app.engine.set_camera(idx)
        print(f"📷 Caméra changée vers l'index {idx}")
