"""
System Tray for MiniOS
Minimal system tray with quick actions
"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QWidget, QMessageBox
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QFont


class SystemTray(QSystemTrayIcon):
    """System tray icon with menu"""
    
    # Signals for actions
    showDesktopRequested = Signal()
    lockScreenRequested = Signal()
    logoutRequested = Signal()
    shutdownRequested = Signal()
    settingsRequested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_tray()
        self.setup_menu()
        
    def setup_tray(self):
        """Setup the tray icon"""
        # Create a simple icon
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw circle
        painter.setBrush(QColor(13, 13, 13))
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(4, 4, 56, 56)
        
        # Draw "M" for MiniOS
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 0, 64, 64, Qt.AlignmentFlag.AlignCenter, "M")
        painter.end()
        
        self.setIcon(QIcon(pixmap))
        self.setToolTip("MiniOS System Tray")
        
    def setup_menu(self):
        """Setup the tray menu"""
        menu = QMenu()
        
        # Show desktop
        show_action = QAction("🖥 Show Desktop", self)
        show_action.triggered.connect(self.showDesktopRequested.emit)
        menu.addAction(show_action)
        
        menu.addSeparator()
        
        # Lock screen
        lock_action = QAction("🔒 Lock Screen", self)
        lock_action.triggered.connect(self.lockScreenRequested.emit)
        menu.addAction(lock_action)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("⚙ Settings", self)
        settings_action.triggered.connect(self.settingsRequested.emit)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # System info
        info_action = QAction("ℹ About", self)
        info_action.triggered.connect(self.show_about)
        menu.addAction(info_action)
        
        menu.addSeparator()
        
        # Logout
        logout_action = QAction("🚪 Logout", self)
        logout_action.triggered.connect(self.logoutRequested.emit)
        menu.addAction(logout_action)
        
        # Shutdown
        shutdown_action = QAction("⏻ Shutdown", self)
        shutdown_action.triggered.connect(self.shutdownRequested.emit)
        menu.addAction(shutdown_action)
        
        self.setContextMenu(menu)
        
        # Handle activation (click) - show desktop on left click
        self.activated.connect(self.on_activated)
        
    def on_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Left click - show desktop
            self.showDesktopRequested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            # Right click - show menu (handled by default)
            pass
            
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self.parent,
            "MiniOS",
            "<h2>MiniOS</h2>"
            "<p>Version 1.0</p>"
            "<p>A simulated desktop operating system built with Python and PySide6.</p>"
            "<p style='color: #666666;'>© 2026 MiniOS Corp.</p>"
        )