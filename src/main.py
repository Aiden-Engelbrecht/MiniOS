"""
MiniOS - A simulated desktop operating system
Minimal Black Edition with Window Manager
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut

from core.splash_screen import MiniOSSplashScreen
from core.login_screen import LoginScreen
from core.desktop import DesktopWidget, Taskbar
from core.start_menu import StartMenu
from core.window_manager import WindowManager
from core.settings_manager import SettingsManager
from core.notification_manager import NotificationManager
from core.system_tray import SystemTray
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
from apps.search_bar import SearchBarWidget
from apps.notification_center import NotificationCenterWidget
from apps.toast_notification import ToastNotification
from apps.task_manager import TaskManagerWidget


class DesktopWindow(QMainWindow):
    """Main desktop window with taskbar and desktop area"""
    
    def __init__(self, username="user", logout_callback=None):
        super().__init__()
        self.username = username
        self.logout_callback = logout_callback
        self.settings_manager = SettingsManager()
        self.notification_manager = NotificationManager()
        self.setWindowTitle("minios")
        self.setGeometry(50, 50, 1300, 850)
        
        self.setup_ui()
        self.setup_search_shortcut()
        self.setup_notification_timer()
        self.setup_system_tray()
        
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
        
        # Create search bar
        self.search_bar = SearchBarWidget()
        self.search_bar.appLaunched.connect(self.launch_application)
        
    def setup_system_tray(self):
        """Setup system tray"""
        self.tray = SystemTray(self)
        
        # Connect tray signals
        self.tray.showDesktopRequested.connect(self.minimize_all_windows)
        self.tray.lockScreenRequested.connect(self.lock_screen)
        self.tray.logoutRequested.connect(self.logout)
        self.tray.shutdownRequested.connect(self.shutdown)
        self.tray.settingsRequested.connect(lambda: self.launch_application("settings"))
        
        # Show tray
        self.tray.show()
        
    def minimize_all_windows(self):
        """Minimize all open windows"""
        for window in self.window_manager.windows:
            window.showMinimized()
        self.show_toast("Desktop", "All windows minimized", "🖥", "info", 2000)
        
    def lock_screen(self):
        """Lock the screen (return to login)"""
        self.show_toast("Screen Locked", "Locking screen...", "🔒", "info", 2000)
        QTimer.singleShot(1000, self.logout)
        
    def setup_search_shortcut(self):
        shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
        shortcut.activated.connect(self.show_search)
        
        shortcut2 = QShortcut(QKeySequence("Alt+Space"), self)
        shortcut2.activated.connect(self.show_search)
    
    def setup_notification_timer(self):
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.show_demo_notification)
        self.notification_timer.start(30000)
        
        QTimer.singleShot(2000, self.show_welcome_notification)
    
    def show_welcome_notification(self):
        self.show_toast(
            "Welcome to MiniOS!",
            f"Hello {self.username}! Your system is ready.",
            "👋",
            "success",
            5000
        )
    
    def show_demo_notification(self):
        import random
        messages = [
            ("System Update", "Your system is up to date.", "📦", "info"),
            ("New App Available", "Calculator has been updated.", "📱", "info"),
            ("Weather Alert", "Rain expected later today.", "🌧", "warning"),
            ("Backup Complete", "Your files have been backed up.", "✅", "success"),
            ("Security Scan", "No threats detected.", "🔒", "success"),
            ("Disk Space", "You have 5.2 GB free space.", "💾", "warning"),
            ("Network Connected", "Connected to Wi-Fi.", "🌐", "info"),
        ]
        title, message, icon, notif_type = random.choice(messages)
        self.show_toast(title, message, icon, notif_type, 4000)
    
    def show_toast(self, title, message, icon="📢", notif_type="info", duration=4000):
        toast = ToastNotification(title, message, icon, notif_type, duration)
        toast.show()
        self.notification_manager.add_notification(title, message, icon, notif_type, duration)
    
    def show_search(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 500) // 2
        y = (screen.height() - 60) // 3
        self.search_bar.move(x, y)
        self.search_bar.show_search()
    
    def show_start_menu(self):
        self.taskbar.show_start_menu(self.start_menu)
        
    def launch_application(self, app_id):
        print(f"Launching application: {app_id}")
        
        if app_id == "logout":
            self.logout()
            return
        elif app_id == "shutdown":
            self.shutdown()
            return
        
        if app_id == "weather":
            if self.weather_widget is None or not self.weather_widget.isVisible():
                self.weather_widget = WeatherWidget()
                screen = QApplication.primaryScreen().geometry()
                self.weather_widget.move(screen.width() - 300, 50)
                self.weather_widget.show()
                self.weather_widget.raise_()
            else:
                self.weather_widget.raise_()
                self.weather_widget.show()
            return
        
        if app_id == "notifications":
            content = NotificationCenterWidget()
            self.window_manager.create_window("Notification Center", 500, 500, content)
            return
        
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
            "systemmonitor": ("System Monitor", 600, 500, SystemMonitorWidget()),
            "taskmanager": ("Task Manager", 800, 500, TaskManagerWidget())
        }
        
        if app_id in app_map:
            title, width, height, content = app_map[app_id]
            window = self.window_manager.create_window(title, width, height, content)
            if isinstance(content, SettingsWidget):
                content.set_desktop(self)
                content.settingsApplied.connect(self.apply_settings)
            print(f"Window created for: {title}")
        else:
            content = SampleAppContent("Application")
            self.window_manager.create_window("Application", 500, 300, content)
    
    def apply_settings(self):
        app = QApplication.instance()
        self.settings_manager.apply_all_settings(app)
    
    def logout(self):
        print(f"logging out user: {self.username}")
        if self.weather_widget:
            self.weather_widget.close()
        if self.search_bar:
            self.search_bar.close()
        if self.tray:
            self.tray.hide()
        if hasattr(self, 'notification_timer'):
            self.notification_timer.stop()
        self.window_manager.close_all_windows()
        self.close()
        if self.logout_callback:
            self.logout_callback()
    
    def shutdown(self):
        print("system shutting down...")
        if self.weather_widget:
            self.weather_widget.close()
        if self.search_bar:
            self.search_bar.close()
        if self.tray:
            self.tray.hide()
        if hasattr(self, 'notification_timer'):
            self.notification_timer.stop()
        self.window_manager.close_all_windows()
        self.close()
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, lambda: sys.exit(0))
        
    def closeEvent(self, event):
        if self.weather_widget:
            self.weather_widget.close()
        if self.search_bar:
            self.search_bar.close()
        if self.tray:
            self.tray.hide()
        if hasattr(self, 'notification_timer'):
            self.notification_timer.stop()
        self.window_manager.close_all_windows()
        event.accept()


class MiniOSApplication:
    """Main application class managing splash, login, and desktop"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("minios")
        self.app.setOrganizationName("minios")
        
        self.settings_manager = SettingsManager()
        self.settings_manager.apply_all_settings(self.app)
        
        self.splash = MiniOSSplashScreen()
        self.login_screen = LoginScreen()
        self.desktop_window = None
        
        self.splash.loadingComplete.connect(self.show_login)
        self.login_screen.loginSuccessful.connect(self.on_login_success)
        
    def run(self):
        print("minios starting...")
        self.splash.show()
        sys.exit(self.app.exec())
    
    def show_login(self):
        print("showing login screen...")
        self.splash.close()
        self.login_screen.show()
        self.login_screen.clear_fields()
    
    def on_login_success(self, username):
        print(f"login successful: {username}")
        self.login_screen.close()
        self.desktop_window = DesktopWindow(username, self.show_login)
        self.desktop_window.show()
        print("desktop ready")
    
    def initialize_system(self):
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