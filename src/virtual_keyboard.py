"""
Clavier Virtuel Gestuel
Basé sur: https://github.com/MohamedAlaouiMhamdi/virtual_keyboard
Adapté pour Hand Mouse OS avec MediaPipe landmarks
"""

import cv2
import numpy as np
from pynput.keyboard import Controller
import time

class Button:
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.text = text
        self.size = size
        self.hovered = False
        self.dwell_time = 0
        self.dwell_threshold = 30  # Frames (~1.0s à 30fps) - AUGMENTÉ
        
    def contains(self, point):
        """Vérifie si le point est dans le bouton"""
        x, y = point
        px, py = self.pos
        w, h = self.size
        return px <= x <= px + w and py <= y <= py + h
    
    def draw(self, frame):
        """Dessine le bouton sur l'image"""
        x, y = self.pos
        w, h = self.size
        
        # Couleur selon état
        if self.hovered:
            color = (0, 255, 0)  # Vert si survolé
            thickness = 3
            # Barre de progression dwell
            progress = min(1.0, self.dwell_time / self.dwell_threshold)
            progress_w = int(w * progress)
            cv2.rectangle(frame, (x, y + h - 5), (x + progress_w, y + h), (0, 200, 0), -1)
        else:
            color = (200, 200, 200)  # Gris clair par défaut
            thickness = 2
            self.dwell_time = 0
            
        # Cadre du bouton
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        
        # Texte centré
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(self.text, font, 0.8, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(frame, self.text, (text_x, text_y), font, 0.8, (0, 0, 0), 2)


class VirtualKeyboard:
    def __init__(self, layout="azerty", mode="dwell"):
        """
        Args:
            layout: "azerty" ou "qwerty"
            mode: "dwell" (survol) ou "pinch" (Pouce+Index)
        """
        self.layout = layout
        self.mode = mode
        self.keyboard_controller = Controller()
        self.buttons = []
        self.last_typed = 0
        
        self._create_layout()
        
    def _create_layout(self):
        """Génère les touches du clavier"""
        keys_azerty = [
            ["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
            ["W", "X", "C", "V", "B", "N", ",", ".", "?", "!"]
        ]
        
        keys_qwerty = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "?"]
        ]
        
        keys = keys_azerty if self.layout == "azerty" else keys_qwerty
        
        start_x = 50
        start_y = 100
        gap = 10
        button_w, button_h = 85, 85
        
        for row_idx, row in enumerate(keys):
            for col_idx, key in enumerate(row):
                x = start_x + col_idx * (button_w + gap)
                y = start_y + row_idx * (button_h + gap)
                btn = Button((x, y), key, (button_w, button_h))
                self.buttons.append(btn)
                
        # Bouton ESPACE (large, en bas)
        space_btn = Button((start_x + 2 * (button_w + gap), start_y + 3 * (button_h + gap)), "SPACE", (400, button_h))
        self.buttons.append(space_btn)
        
        # Bouton BACKSPACE
        back_btn = Button((start_x + 8 * (button_w + gap), start_y + 3 * (button_h + gap)), "⌫", (150, button_h))
        self.buttons.append(back_btn)
        
    def draw(self, frame):
        """Dessine le clavier complet sur l'image"""
        # Fond semi-transparent (optionnel)
        overlay = frame.copy()
        cv2.rectangle(overlay, (20, 70), (950, 450), (50, 50, 50), -1)
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
        
        # Dessiner toutes les touches
        for btn in self.buttons:
            btn.draw(frame)
            
        # Indicateur de mode
        mode_text = f"Mode: {'SURVOL' if self.mode == 'dwell' else 'PINCH'}"
        cv2.putText(frame, mode_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def check_input(self, index_pos, is_pinching=False):
        """
        Vérifie l'interaction avec le clavier.
        
        Args:
            index_pos: (x, y) position de l'index (ou bout du doigt)
            is_pinching: True si geste PINCH détecté
        """
        if index_pos is None:
            return
            
        # Empêcher spam (0.3s minimum entre frappes)
        if time.time() - self.last_typed < 0.3:
            return
            
        for btn in self.buttons:
            if btn.contains(index_pos):
                btn.hovered = True
                
                # Mode DWELL: Attendre survol prolongé
                if self.mode == "dwell":
                    btn.dwell_time += 1
                    if btn.dwell_time >= btn.dwell_threshold:
                        self._type_key(btn.text)
                        btn.dwell_time = 0
                        
                # Mode PINCH: Clic immédiat
                elif self.mode == "pinch" and is_pinching:
                    self._type_key(btn.text)
            else:
                btn.hovered = False
                
    def _type_key(self, key):
        """Simule la frappe d'une touche"""
        self.last_typed = time.time()
        
        if key == "SPACE":
            self.keyboard_controller.press(' ')
            self.keyboard_controller.release(' ')
        elif key == "⌫":  # Backspace
            self.keyboard_controller.press('\b')
            self.keyboard_controller.release('\b')
        else:
            self.keyboard_controller.press(key.lower())
            self.keyboard_controller.release(key.lower())
            
        print(f"⌨️ Typed: {key}")
