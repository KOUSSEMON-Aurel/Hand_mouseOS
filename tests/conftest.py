import sys
from unittest.mock import MagicMock

# Mock des dépendances GUI/Hardware pour le CI (Headless)
mock_pyautogui = MagicMock()
mock_pyautogui.size.return_value = (1920, 1080)
sys.modules["pyautogui"] = mock_pyautogui

# Mock mouseinfo car pyautogui l'importe en interne
sys.modules["mouseinfo"] = MagicMock()

# Mock uinput pour éviter les erreurs de driver sur les runners GitHub
mock_uinput = MagicMock()
sys.modules["uinput"] = mock_uinput

# Mock cv2 pour éviter les dépendances système GTK/QT dans le CI
sys.modules["cv2"] = MagicMock()
