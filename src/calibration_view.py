import flet as ft
import time
import threading
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
        self.points = []
        self.step = 0
        self.btn_action.visible = False
        self.start_step()
    
    def start_step(self):
        if self.step < 4:
            self.status_text.value = f"Étape {self.step + 1}/4 : {self.instructions[self.step]}"
            self.status_text.update()
            
            # Disable button during countdown
            self.btn_action.disabled = True
            self.btn_action.icon = ft.Icons.TIMER
            self.btn_action.visible = True
            self.btn_action.update()
            
            # Start Countdown in a thread to not block GUI
            threading.Thread(target=self.countdown_and_capture, daemon=True).start()
        else:
            self.finish_calibration()

    def countdown_and_capture(self):
        for i in range(5, 0, -1):
            self.btn_action.text = f"AUTO-CAPTURE DANS {i} s..."
            self.btn_action.update()
            time.sleep(1)
        
        self.btn_action.text = "CAPTURE EN COURS..."
        self.btn_action.update()
        time.sleep(0.5)
        self.capture_point(None)

    def capture_point(self, e):
        # Retry mechanism: Try to catch a hand for 1.5 seconds
        detected_hand = None
        
        for _ in range(15):
            result = self.main_app.engine.latest_result
            if result and result.hand_landmarks:
                detected_hand = result.hand_landmarks[0]
                break
            time.sleep(0.1)
            
        if not detected_hand:
            self.status_text.value = "⚠️ AUCUNE MAIN ! Placez votre main et Réessayez."
            self.status_text.update()
            
            self.btn_action.text = "RÉESSAYER (5s)"
            self.btn_action.disabled = False
            self.btn_action.icon = ft.Icons.REFRESH
            self.btn_action.on_click = lambda e: self.start_step()
            self.btn_action.update()
            return
            
        # 2. Get Index Finger Tip (Landmark 8)
        finger_tip = detected_hand[8]
        
        # 3. Store point (x, y)
        self.points.append((finger_tip.x, finger_tip.y))
        print(f"DEBUG: Calibration Point {self.step+1} captured: {finger_tip.x}, {finger_tip.y}")
        
        # 4. Next step
        self.step += 1
        # Small delay before next step
        time.sleep(1)
        self.start_step()

    def finish_calibration(self):
        success = self.calibration_system.calibrate(self.points)
        
        if success:
            self.status_text.value = "✅ CALIBRATION RÉUSSIE !"
            self.calibration_system.save("calibration_matrix.npy")
            # Apply to driver
            if hasattr(self.main_app.engine, 'mouse'):
                self.main_app.engine.mouse.reload_calibration()
        else:
            self.status_text.value = "❌ ÉCHEC DE CALIBRATION. Réessayez."
            
        self.btn_action.text = "Retour"
        self.btn_action.icon = ft.Icons.HOME
        self.btn_action.on_click = lambda e: self.main_app.go_home()
        self.btn_action.update()
        self.status_text.update()
