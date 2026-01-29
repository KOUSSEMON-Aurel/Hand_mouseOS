import flet as ft
import time
from optimized_utils import CalibrationSystem

class CalibrationView(ft.Column):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.calibration_system = CalibrationSystem()
        self.step = 0
        self.instructions = [
            "Cliquez sur le coin HAUT-GAUCHE",
            "Cliquez sur le coin HAUT-DROIT",
            "Cliquez sur le coin BAS-DROIT",
            "Cliquez sur le coin BAS-GAUCHE"
        ]
        
        self.status_text = ft.Text("Prêt pour la calibration...", size=20, weight=ft.FontWeight.BOLD)
        self.btn_action = ft.ElevatedButton("Commencer", on_click=self.start_calibration)
        self.progress_bar = ft.ProgressBar(width=400, value=0, visible=False)

        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text("Assistant de Calibration", size=30),
                    ft.Text("Définissez votre zone de mouvement idéale en 4 étapes.", italic=True),
                    ft.Divider(),
                    self.status_text,
                    self.btn_action,
                    self.progress_bar
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20
            )
        ]

    def start_calibration(self, e):
        self.step = 0
        self.btn_action.visible = False
        self.start_step()
    
    def start_step(self):
        if self.step < 4:
            self.status_text.value = f"Étape {self.step + 1}/4 : {self.instructions[self.step]}"
            self.status_text.update()
            # In a real scenario, we would wait for a "click" event from the engine
            # Here for simplicity, we simulate a 'Next' button, but ideally this connects to engine events
            self.btn_action.text = "J'ai cliqué (Simuler)"
            self.btn_action.visible = True
            self.btn_action.update()
        else:
            self.finish_calibration()

    def finish_calibration(self):
        self.status_text.value = "Calibration Terminée ! Matrice sauvegardée."
        self.btn_action.text = "Retour"
        self.btn_action.on_click = lambda e: self.main_app.go_home()
        self.btn_action.update()
        self.status_text.update()
