import math
from typing import List, Tuple, Dict
from enum import Enum

class Gesture(Enum):
    """Les gestes universels du système simplifié."""
    POINTING = "POINTING"       # 👆 Index tendu seul
    PINCH = "PINCH"            # 👌 Pouce + Index joints
    PALM = "PALM"              # ✋ Main ouverte
    FIST = "FIST"              # ✊ Poing fermé
    TWO_FINGERS = "TWO_FINGERS" # ✌️ Index + Majeur tendus
    THUMBS_UP = "THUMBS_UP"    # 👍 Pouce en l'air
    THUMBS_DOWN = "THUMBS_DOWN" # 👎 Pouce vers le bas
    UNKNOWN = "UNKNOWN"        # Pose non reconnue


class StaticGestureClassifier:
    """Classificateur de gestes statiques basé sur la géométrie des repères (landmarks).
    
    Système simplifié : 5 gestes universels uniquement.
    """
    
    # Seuils de détection
    PINCH_THRESHOLD = 0.05  # Distance normalisée pouce-index pour PINCH
    
    def __init__(self):
        # Indices des landmarks
        self.finger_tips = [4, 8, 12, 16, 20]  # Pouce, Index, Majeur, Annulaire, Auriculaire
        self.finger_pips = [2, 6, 10, 14, 18]  # Articulations intermédiaires
        
    def classify(self, landmarks: List) -> str:
        """
        Classifie la pose de la main.
        
        Args:
            landmarks: Liste des 21 points de la main (normalisés ou non)
            
        Returns:
            label (str): 'POINTING', 'PINCH', 'PALM', 'FIST', 'TWO_FINGERS', 'UNKNOWN'
        """
        if not landmarks or len(landmarks) < 21:
            return Gesture.UNKNOWN.value
        
        # 1. PINCH (priorité haute - détection fine)
        if self._is_pinching(landmarks):
            return Gesture.PINCH.value
            
        fingers_extended = self._get_extended_fingers(landmarks)
        # fingers_extended: [Pouce, Index, Majeur, Annulaire, Auriculaire]
        
        # 2. THUMBS UP / DOWN (Pouce seul tendu, autres repliés)
        if fingers_extended[0] and not any(fingers_extended[1:]):
            # Pouce seul tendu, vérifier orientation Y
            thumb_tip = landmarks[4]
            thumb_mcp = landmarks[2]  # Base du pouce
            wrist = landmarks[0]
            
            # THUMBS_UP: Pouce au-dessus du poignet (y plus petit)
            # THUMBS_DOWN: Pouce en-dessous du poignet (y plus grand)
            if thumb_tip.y < wrist.y - 0.05:  # Seuil pour éviter faux positifs
                return Gesture.THUMBS_UP.value
            elif thumb_tip.y > wrist.y + 0.05:
                return Gesture.THUMBS_DOWN.value
        
        # 3. PALM (Tous les doigts étendus)
        if all(fingers_extended):
            return Gesture.PALM.value
            
        # 4. FIST (Aucun doigt étendu sauf peut-être pouce replié)
        if not any(fingers_extended[1:]):  # Ignore le pouce
            return Gesture.FIST.value
        
        # 5. POINTING (Seul l'index étendu)
        if fingers_extended[1] and not any(fingers_extended[2:]):
            return Gesture.POINTING.value
            
        # 6. TWO_FINGERS (Index + Majeur étendus, autres repliés)
        if fingers_extended[1] and fingers_extended[2] and not any(fingers_extended[3:]):
            return Gesture.TWO_FINGERS.value
            
        return Gesture.UNKNOWN.value
    
    def _is_pinching(self, landmarks) -> bool:
        """Détecte si le pouce et l'index sont joints (pincement)."""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        # Distance euclidienne normalisée
        dx = thumb_tip.x - index_tip.x
        dy = thumb_tip.y - index_tip.y
        dz = getattr(thumb_tip, 'z', 0) - getattr(index_tip, 'z', 0)
        
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        return distance < self.PINCH_THRESHOLD

    def _get_extended_fingers(self, landmarks) -> List[bool]:
        """Détermine si chaque doigt est tendu.
        
        Returns:
            Liste de 5 booléens [Pouce, Index, Majeur, Annulaire, Auriculaire]
        """
        extended = []
        
        # 1. POUCE (Cas particulier - mouvement latéral)
        # Compare le tip au MCP sur l'axe X
        thumb_tip = landmarks[4]
        thumb_ipp = landmarks[3]
        
        # Le pouce est étendu si le tip est plus éloigné du centre de la paume
        if abs(thumb_tip.x - landmarks[5].x) > abs(thumb_ipp.x - landmarks[5].x):
            extended.append(True)
        else:
            extended.append(False)
            
        # 2. AUTRES DOIGTS (Index à Auriculaire)
        # Un doigt est tendu si son tip est plus haut que son PIP
        for i in range(1, 5):
            tip = landmarks[self.finger_tips[i]]
            pip = landmarks[self.finger_pips[i]]
            
            # En coordonnées écran, Y diminue vers le haut
            if tip.y < pip.y:
                extended.append(True)
            else:
                extended.append(False)
                
        return extended
    
    def get_gesture_emoji(self, gesture: str) -> str:
        """Retourne l'emoji correspondant au geste."""
        emojis = {
            Gesture.POINTING.value: "👆",
            Gesture.PINCH.value: "👌",
            Gesture.PALM.value: "✋",
            Gesture.FIST.value: "✊",
            Gesture.TWO_FINGERS.value: "✌️",
            Gesture.THUMBS_UP.value: "👍",
            Gesture.THUMBS_DOWN.value: "👎",
            Gesture.UNKNOWN.value: "❓"
        }
        return emojis.get(gesture, "❓")
