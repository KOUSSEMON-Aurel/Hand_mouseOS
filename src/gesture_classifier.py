import math
from typing import List, Tuple, Dict

class StaticGestureClassifier:
    """Classificateur de gestes statiques basé sur la géométrie des repères (landmarks)."""
    
    def __init__(self):
        # Noms des doigts pour la lisibilité
        self.finger_tips = [4, 8, 12, 16, 20]
        self.finger_pips = [2, 6, 10, 14, 18] # On utilise le joint 2/3 pour la flexion
        
    def classify(self, landmarks: List) -> str:
        """
        Classifie la pose de la main.
        Args:
            landmarks: Liste des 21 points de la main (normalisés ou non)
        Returns:
            label (str): 'FIST', 'PALM', 'PEACE', 'THUMBS_UP', 'POINTING', 'UNKNOWN'
        """
        if not landmarks or len(landmarks) < 21:
            return "UNKNOWN"
            
        fingers_extended = self._get_extended_fingers(landmarks)
        
        # Logique de décision
        # 0: Thumb, 1: Index, 2: Middle, 3: Ring, 4: Pinky
        
        # 1. PALM (Tous étendus)
        if all(fingers_extended):
            return "PALM"
            
        # 2. FIST (Aucun étendu - sauf peut-être le pouce)
        if not any(fingers_extended[1:]): # On ignore le pouce pour le poing pur
             if not fingers_extended[0]:
                 return "FIST"
             else:
                 return "THUMBS_UP"
                 
        # 3. POINTING (Seul l'index est étendu)
        if fingers_extended[1] and not any(fingers_extended[2:]):
            return "POINTING"
            
        # 4. PEACE (Index et Majeur étendus)
        if fingers_extended[1] and fingers_extended[2] and not any(fingers_extended[3:]):
            return "PEACE"
            
        return "UNKNOWN"

    def _get_extended_fingers(self, landmarks) -> List[bool]:
        """Détermine si chaque doigt est tendu."""
        extended = []
        
        # 1. POUCE (Cas particulier - mouvement horizontal)
        # On compare le tip au mcp sur l'axe X (plus fiable pour le pouce)
        # Note: Dépend du côté de la main, mais globalement si tip est loin du centre...
        thumb_tip = landmarks[4]
        thumb_ipp = landmarks[3]
        thumb_mcp = landmarks[2]
        
        # Distance pseudo-horizontale
        if abs(thumb_tip.x - landmarks[5].x) > abs(thumb_ipp.x - landmarks[5].x):
            extended.append(True)
        else:
            extended.append(False)
            
        # 2. AUTRES DOIGTS (Verticalité)
        # Si le Tip est plus haut (Y plus petit) que le PIP
        for i in range(1, 5): # Index à Auriculaire
            tip = landmarks[self.finger_tips[i]]
            pip = landmarks[self.finger_pips[i]]
            
            if tip.y < pip.y: # En vision ordi, Y descend vers le bas
                extended.append(True)
            else:
                extended.append(False)
                
        return extended
