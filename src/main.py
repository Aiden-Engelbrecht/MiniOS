"""
MiniOS - A simulated desktop operating system
Minimal Black Edition with Window Manager
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
from core.window_manager import WindowManager
from core.settings_manager import SettingsManager
from apps.sample_app import SampleAppContent
from apps.file_explorer import FileExplorerWidget
from apps.notepad import NotepadWidget
from apps.terminal import TerminalWidget
from apps.settings import SettingsWidget
from apps.calendar import CalendarWidget
from apps.image_viewer import ImageViewerWidget
from apps.recycle_bin import RecycleBinWidget
from apps.music_player import MusicPlayerWidget
from apps.system_monitor import SystemMonitorWidget
from apps.calculator import CalculatorWidget
from apps.weather_widget import WeatherWidget


class DesktopWindow(QMainWindow):
    """Main desktop window with taskbar and desktop area"""
    
    def __init__(self, username="user", logout_callback=None):
        super().__init__()
        self.username = username
        self.logout_callback = logout_callback
        self.settings_manager = SettingsManager()
        self.setWindowTitle("minios")
        self.setGeometry(50, 50, 1300, 850)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Desktop area
        self.desktop = DesktopWidget()
        self.desktop.iconClicked.connect(self.launch_application)
        main_layout.addWidget(self.desktop, 1)
        
        # Taskbar
        self.taskbar = Taskbar()
        self.taskbar.startMenuRequested.connect(self.show_start_menu)
        main_layout.addWidget(self.taskbar)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Initialize window manager with taskbar reference
        self.window_manager = WindowManager(self.taskbar)
        
        # Create start menu
        self.start_menu = StartMenu(self.taskbar)
        self.start_menu.appLaunched.connect(self.launch_application)
        
        # Create weather widget (floating desktop widget)
        self.weather_widget = None
        
    def show_start_menu(self):
        """Show the start menu at the correct position"""
        self.taskbar.show_start_menu(self.start_menu)
        
    def launch_application(self, app_id):
        """Launch an application from desktop icon or start menu"""
        print(f"Launching application: {app_id}")
        
        # Handle system actions
        if app_id == "logout":
            self.logout()
            return
        elif app_id == "shutdown":
            self.shutdown()
            return
        
        # Handle weather widget (special case - floating widget)
        if app_id == "weather":
            if self.weather_widget is None or not self.weather_widget.isVisible():
                self.weather_widget = WeatherWidget()
                # Position it in top-right corner
                screen = QApplication.primaryScreen().geometry()
                self.weather_widget.move(screen.width() - 300, 50)
                self.weather_widget.show()
                self.weather_widget.raise_()
            else:
                self.weather_widget.raise_()
                self.weather_widget.show()
            return
        
        # Map app_id to display names and content
        app_map = {
            "files": ("File Explorer", 800, 600, FileExplorerWidget()),
            "explorer": ("File Explorer", 800, 600, FileExplorerWidget()),
            "notepad": ("Notepad", 700, 500, NotepadWidget()),
            "terminal": ("Terminal", 800, 500, TerminalWidget()),
            "settings": ("Settings", 700, 550, SettingsWidget()),
            "calculator": ("Calculator", 350, 550, CalculatorWidget()),
            "calendar": ("Calendar", 500, 450, CalendarWidget()),
            "imageviewer": ("Image Viewer", 800, 600, ImageViewerWidget()),
            "recyclebin": ("Recycle Bin", 700, 500, RecycleBinWidget()),
            "musicplayer": ("Music Player", 600, 450, MusicPlayerWidget()),
            "systemmonitor": ("System Monitor", 600, 500, SystemMonitorWidget())
        }
        
        if app_id in app_map:
            title, width, height, content = app_map[app_id]
            window = self.window_manager.create_window(title, width, height, content)
            
            # If settings, pass the desktop reference
            if isinstance(content, SettingsWidget):
                content.set_desktop(self)
                content.settingsApplied.connect(self.apply_settings)
            
            print(f"Window created for: {title}")
        else:
            # Unknown app
            content = SampleAppContent("Application")
            self.window_manager.create_window("Application", 500, 300, content)
    
    def apply_settings(self):
        """Apply settings to the entire application"""
        app = QApplication.instance()
        self.settings_manager.apply_all_settings(app)
    
    def logout(self):
        """Logout and return to login screen"""
        print(f"logging out user: {self.username}")
        if self.weather_widget:
            self.weather_widget.close()
        self.window_manager.close_all_windows()
        self.close()
        if self.logout_callback:
            self.logout_callback()
    
    def shutdown(self):
        """Shutdown the system"""
        print("system shutting down...")
        if self.weather_widget:
            self.weather_widget.close()
        self.window_manager.close_all_windows()
        self.close()
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, lambda: sys.exit(0))
        
    def closeEvent(self, event):
        if self.weather_widget:
            self.weather_widget.close()
        self.window_manager.close_all_windows()
        event.accept()


class MiniOSApplication:
    """Main application class managing splash, login, and desktop"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("minios")
        self.app.setOrganizationName("minios")
        
        # Load and apply settings
        self.settings_manager = SettingsManager()
        self.settings_manager.apply_all_settings(self.app)
        
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