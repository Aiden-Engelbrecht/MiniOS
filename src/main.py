"""
MiniOS - A simulated desktop operating system
Minimal Black Edition
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt

from core.splash_screen import MiniOSSplashScreen
from core.login_screen import LoginScreen
from core.desktop import DesktopWidget, Taskbar
from core.start_menu import StartMenu


class DesktopWindow(QMainWindow):
    """Main desktop window with taskbar and desktop area"""
    
    def __init__(self, username="user", logout_callback=None):
        super().__init__()
        self.username = username
        self.logout_callback = logout_callback
        self.setWindowTitle("minios")
        self.setGeometry(50, 50, 1300, 850)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_widget = QWidget()
        main_widget.setStyleSheet("background: #000000;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Desktop area
        self.desktop = DesktopWidget()
        self.desktop.iconClicked.connect(self.on_icon_clicked)
        main_layout.addWidget(self.desktop, 1)
        
        # Taskbar
        self.taskbar = Taskbar()
        self.taskbar.startMenuRequested.connect(self.show_start_menu)
        main_layout.addWidget(self.taskbar)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Create start menu
        self.start_menu = StartMenu(self.taskbar)
        self.start_menu.appLaunched.connect(self.on_app_launched)
        
    def show_start_menu(self):
        """Show the start menu at the correct position"""
        self.taskbar.show_start_menu(self.start_menu)
        
    def on_icon_clicked(self, app_name):
        """Handle desktop icon clicks"""
        print(f"Desktop icon clicked: {app_name}")
        
    def on_app_launched(self, app_id):
        """Handle start menu app launches"""
        print(f"Launching: {app_id}")
        if app_id == "logout":
            self.logout()
        elif app_id == "shutdown":
            self.shutdown()
        # We'll implement actual app launching in future milestones
        
    def logout(self):
        """Logout and return to login screen"""
        print(f"logging out user: {self.username}")
        self.close()
        if self.logout_callback:
            self.logout_callback()
    
    def shutdown(self):
        """Shutdown the system"""
        print("system shutting down...")
        self.close()
        # Exit application after a moment
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, lambda: sys.exit(0))
        
    def closeEvent(self, event):
        print(f"desktop closed")
        event.accept()


class MiniOSApplication:
    """Main application class managing splash, login, and desktop"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("minios")
        self.app.setOrganizationName("minios")
        
        # Create screens
        self.splash = MiniOSSplashScreen()
        self.login_screen = LoginScreen()
        self.desktop_window = None
        
        # Connect signals
        self.splash.loadingComplete.connect(self.show_login)
        self.login_screen.loginSuccessful.connect(self.on_login_success)
        
    def run(self):
        """Start the application"""
        print("minios starting...")
        self.splash.show()
        sys.exit(self.app.exec())
    
    def show_login(self):
        """Switch from splash to login"""
        print("showing login screen...")
        self.splash.close()
        self.login_screen.show()
        self.login_screen.clear_fields()
    
    def on_login_success(self, username):
        """Handle successful login"""
        print(f"login successful: {username}")
        self.login_screen.close()
        
        # Create desktop with logout callback
        self.desktop_window = DesktopWindow(username, self.show_login)
        self.desktop_window.show()
        print("desktop ready")
    
    def initialize_system(self):
        """Initialize system components"""
        pass


def main():
    try:
        minios = MiniOSApplication()
        minios.initialize_system()
        minios.run()
    except Exception as e:
        print(f"error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()