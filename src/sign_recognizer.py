import math

class SignLanguageInterpreter:
    """
    Interpréteur de langue des signes (ASL) basé sur la géométrie des landmarks MediaPipe.
    Ne nécessite PAS TensorFlow/Keras.
    """
    def __init__(self):
        self.finger_tips = [4, 8, 12, 16, 20]
        self.finger_pips = [2, 6, 10, 14, 18]

    def predict(self, hand_crop_unused, landmarks):
        """
        Prediit la lettre ASL basée sur les landmarks normalisés.
        
        Args:
            hand_crop_unused: Ignoré (legacy CNN signature)
            landmarks: Liste des objets landmarks (x, y, z) de MediaPipe
            
        Returns:
            label (str), confidence (float)
        """
        if not landmarks:
            return "Unknown", 0.0

        # Analyse des doigts (Ouvert/Fermé)
        fingers = []
        
        # Pouce (Axe X pour la main droite, inverser si main gauche - supposons main droite pour l'instant)
        # Pouce ouvert si tip à droite de IP
        if landmarks[4].x > landmarks[3].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 autres doigts (Axe Y)
        for i in range(1, 5):
            if landmarks[self.finger_tips[i]].y < landmarks[self.finger_pips[i]].y:
                fingers.append(1)
            else:
                fingers.append(0)

        # Classification simple basée sur les doigts levés
        # [Pouce, Index, Majeur, Annulaire, Auriculaire]
        
        # A: Poing fermé, pouce contre index (FIST avec pouce sur le côté)
        # B: 4 doigts levés, pouce plié sur paume
        # C: Main en C
        # D: Index levé, autres ronds
        # E: Tous pliés (griffes)
        # F: OK sign (Index+Pouce joints, 3 levés)
        # L: L shape (Pouce+Index levés)
        # V: V (Index+Majeur)
        # W: 3 doigts
        # Y: Pouce + Auriculaire (Telephone)
        
        total_fingers = sum(fingers)
        gesture = "Unknown"
        conf = 0.8
        
        # Logique simplifiée (A améliorer avec des angles)
        if fingers == [0, 1, 0, 0, 0]:
            gesture = "D" # Ou POINTING
        elif fingers == [0, 1, 1, 0, 0]:
            gesture = "V"
        elif fingers == [0, 1, 1, 1, 0]:
            gesture = "W"
        elif fingers == [0, 1, 1, 1, 1]:
            gesture = "B" 
        elif fingers == [1, 1, 0, 0, 0]:
            gesture = "L"
        elif fingers == [1, 0, 0, 0, 1]:
            gesture = "Y"
        elif fingers == [1, 1, 1, 1, 1]:
            gesture = "FIVE" # ou P (Palm)
        elif fingers == [0, 0, 0, 0, 0]:
            # A, E, S, M, N se ressemblent en '00000', faut regarder le pouce et la position des tips
            gesture = "A/E/S"
            
            # Raffinement E vs A
            # E: Tips proches du bas de la paume
            # A: Pouce vertical contre la main
            thumb_tip = landmarks[4]
            index_mcp = landmarks[5]
            
            if thumb_tip.y < index_mcp.y: # Pouce un peu haut
                gesture = "A"
            else:
                gesture = "E"
                
        elif fingers == [1, 0, 0, 0, 0]:
             # Pouce levé ?
             gesture = "THUMBS_UP" # Ou A ouvert
        
        # Detection PINCH / F (OK sign)
        # Distance Pouce-Index faible + 3 doigts levés (Majeur, Annulaire, Auric)
        dist_thumb_index = math.hypot(landmarks[4].x - landmarks[8].x, landmarks[4].y - landmarks[8].y)
        if dist_thumb_index < 0.05 and fingers[2]==1 and fingers[3]==1 and fingers[4]==1:
            gesture = "F"

        return gesture, conf

    def preprocess_hand_region(self, frame, landmarks):
        """Pass-through pour compatibilité."""
        return frame # On n'a pas besoin de crop pour l'approche géométrique
