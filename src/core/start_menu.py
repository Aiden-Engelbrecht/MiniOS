"""
Start Menu for MiniOS - Minimal Black Edition
"""

from PySide6.QtWidgets import QMenu, QWidgetAction, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QFont, QAction


class StartMenu(QMenu):
    """Minimal start menu"""
    
    appLaunched = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QMenu {
                background: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 6px;
                padding: 8px 0px;
            }
            QMenu::item {
                color: #cccccc;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 8px 30px 8px 20px;
                background: transparent;
                font-size: 13px;
            }
            QMenu::item:selected {
                background: #1a1a1a;
                color: #ffffff;
            }
            QMenu::separator {
                background: #1a1a1a;
                height: 1px;
                margin: 5px 10px;
            }
        """)
        
        # Header - User info
        header_action = QWidgetAction(self)
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            background: transparent;
            padding: 8px 20px 4px 20px;
        """)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        user_label = QLabel("◆ minios")
        user_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Light))
        user_label.setStyleSheet("color: #ffffff; letter-spacing: 2px;")
        header_layout.addWidget(user_label)
        
        user_sub = QLabel("user")
        user_sub.setFont(QFont("Segoe UI", 9))
        user_sub.setStyleSheet("color: #444444;")
        header_layout.addWidget(user_sub)
        
        header_widget.setLayout(header_layout)
        header_action.setDefaultWidget(header_widget)
        self.addAction(header_action)
        
        self.addSeparator()
        
        # Search entry
        search_action = QAction("🔍  Search... (Ctrl+Space)", self)
        search_action.triggered.connect(lambda: self.appLaunched.emit("search"))
        self.addAction(search_action)
        
        self.addSeparator()
        
        # Applications
        apps = [
            ("◈  Explorer", "explorer"),
            ("◈  Notepad", "notepad"),
            ("◈  Terminal", "terminal"),
            ("◈  Calculator", "calculator"),
            ("◈  Calendar", "calendar"),
            ("◈  Image Viewer", "imageviewer"),
            ("◈  Music Player", "musicplayer"),
            ("◈  System Monitor", "systemmonitor"),
            ("◈  Recycle Bin", "recyclebin"),
            ("◈  Notification Center", "notifications"),
            ("◈  Weather Widget", "weather"),
            ("◈  Settings", "settings")
        ]
        
        for label, app_id in apps:
            action = QAction(label, self)
            action.triggered.connect(self.create_app_launcher(app_id))
            self.addAction(action)
        
        self.addSeparator()
        
        # System actions
        logout_action = QAction("◇  Logout", self)
        logout_action.triggered.connect(lambda: self.appLaunched.emit("logout"))
        self.addAction(logout_action)
        
        shutdown_action = QAction("◇  Shutdown", self)
        shutdown_action.triggered.connect(lambda: self.appLaunched.emit("shutdown"))
        self.addAction(shutdown_action)
    
    def create_app_launcher(self, app_id):
        """Create a handler function for app launches"""
        def handler():
            print(f"Start menu launching: {app_id}")
            self.appLaunched.emit(app_id)
        return handler
    
    def showEvent(self, event):
        """Position menu above the taskbar"""
        super().showEvent(event)
        if self.parent():
            button_pos = self.parent().mapToGlobal(QPoint(0, 0))
            self.move(button_pos.x(), button_pos.y() - self.height() - 5)