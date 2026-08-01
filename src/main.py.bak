"""
MiniOS - A simulated desktop operating system
Entry point for the application
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QFont, QColor, QPalette


class MainWindow(QMainWindow):
    """Main window for MiniOS desktop"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MiniOS Desktop")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set a dark theme for now (we'll make it configurable later)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create a central widget
        label = QLabel("Welcome to MiniOS!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Style the label
        font = QFont("Arial", 24, QFont.Weight.Bold)
        label.setFont(font)
        label.setStyleSheet("color: #ffffff;")
        
        self.setCentralWidget(label)
        
        # Set background color
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        self.setPalette(palette)
        
    def closeEvent(self, event):
        """Handle close event"""
        print("MiniOS is shutting down...")
        event.accept()


class MiniOSApplication:
    """Main application class for MiniOS"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("MiniOS")
        self.app.setOrganizationName("MiniOS")
        
        # Create main window
        self.main_window = MainWindow()
        
    def run(self):
        """Start the application"""
        print("MiniOS starting...")
        
        # Show the main window
        self.main_window.show()
        
        print("MiniOS is running!")
        
        # Execute the application
        sys.exit(self.app.exec())
    
    def initialize_system(self):
        """Initialize all system components"""
        # We'll add more initialization here in future steps
        pass


def main():
    """Main entry point"""
    try:
        # Create and run the application
        minios = MiniOSApplication()
        minios.initialize_system()
        minios.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()