"""
MiniOS - A simulated desktop operating system
Minimal Black Edition
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette

from core.splash_screen import MiniOSSplashScreen


class MainWindow(QMainWindow):
    """Main window for MiniOS - Minimal Black"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("minios")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Pure black background
        self.setStyleSheet("""
            QMainWindow {
                background: #000000;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
            }
        """)
        
        central_widget = QWidget()
        central_widget.setStyleSheet("background: #000000;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(30)
        
        # Title
        title = QLabel("minios")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 48, QFont.Weight.Light))
        title.setStyleSheet("color: #ffffff; letter-spacing: 12px;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Welcome message
        welcome = QLabel("welcome")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setFont(QFont("Segoe UI", 16, QFont.Weight.Light))
        welcome.setStyleSheet("color: #666666; letter-spacing: 4px;")
        layout.addWidget(welcome)
        
        # Status line
        status = QLabel("system ready")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setFont(QFont("Segoe UI", 11))
        status.setStyleSheet("color: #333333; letter-spacing: 2px;")
        layout.addWidget(status)
        
        layout.addStretch()
        
        # Simple divider
        divider = QLabel("— — —")
        divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        divider.setFont(QFont("Segoe UI", 10))
        divider.setStyleSheet("color: #222222;")
        layout.addWidget(divider)
        
        # Version
        version = QLabel("v0.1.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setFont(QFont("Segoe UI", 10))
        version.setStyleSheet("color: #222222;")
        layout.addWidget(version)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def closeEvent(self, event):
        print("minios shutting down...")
        event.accept()


class MiniOSApplication:
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("minios")
        self.app.setOrganizationName("minios")
        
        self.splash = MiniOSSplashScreen()
        self.splash.loadingComplete.connect(self.show_main_window)
        
        self.main_window = MainWindow()
        
    def run(self):
        print("minios starting...")
        self.splash.show()
        sys.exit(self.app.exec())
    
    def show_main_window(self):
        print("desktop ready")
        self.main_window.show()
    
    def initialize_system(self):
        pass


def main():
    try:
        minios = MiniOSApplication()
        minios.initialize_system()
        minios.run()
    except Exception as e:
        print(f"error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()