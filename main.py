import os
import logging

# Suppress TensorFlow/MediaPipe logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['ABSL_LOGGING_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'

# Suppress X11/Xlib warnings if possible via env
os.environ['PYTHONWARNINGS'] = 'ignore'

import flet as ft
from src.gui import main

if __name__ == "__main__":
    # Fix DeprecationWarning: app() is deprecated since version 0.80.0. Use run() instead.
    try:
        ft.run(main)
    except AttributeError:
        # Fallback if 'run' is not found (though the warning suggests it exists)
        ft.app(target=main)


