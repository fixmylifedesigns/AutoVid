# src/main.py

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import VideoCreatorApp

def main():
    """
    Main entry point of the application.
    Initializes and runs the main window.
    """
    app = QApplication(sys.argv)
    window = VideoCreatorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()