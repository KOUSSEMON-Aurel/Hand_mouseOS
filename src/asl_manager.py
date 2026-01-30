from src.sign_recognizer import SignLanguageInterpreter

class ASLManager:
    """
    Gère la logique métier de la reconnaissance ASL.
    Encapsule l'interpréteur, l'état d'activation et le formatage des résultats.
    """
    def __init__(self):
        self.interpreter = SignLanguageInterpreter()
        self.enabled = False
        self.last_prediction = "Attente..."
        self.last_confidence = 0.0

    def set_enabled(self, enabled: bool):
        """Active ou désactive le mode ASL."""
        self.enabled = enabled
        if not enabled:
            self.last_prediction = "Désactivé"

    def process(self, landmarks):
        """
        Traite les landmarks si activé et met à jour la prédiction.
        Retourne True si une mise à jour a eu lieu.
        """
        if not self.enabled:
            return False
            
        if not landmarks:
            self.last_prediction = "Pas de main"
            self.last_confidence = 0.0
            return True

        label, conf = self.interpreter.predict(None, landmarks)
        self.last_prediction = label
        self.last_confidence = conf
        return True

    def get_display_text(self):
        """Retourne le texte formaté pour l'interface."""
        if not self.enabled:
            return ""
        return f"{self.last_prediction} ({self.last_confidence:.2f})"
