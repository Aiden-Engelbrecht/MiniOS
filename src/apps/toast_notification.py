"""
Toast Notification for MiniOS
Pop-up notification that appears at the bottom-right
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont


class ToastNotification(QWidget):
    """Toast notification popup"""
    
    def __init__(self, title: str, message: str, icon: str = "📢", 
                 notification_type: str = "info", duration: int = 4000):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.duration = duration
        self.setup_ui(title, message, icon, notification_type)
        self.animate_in()
        
    def setup_ui(self, title, message, icon, notification_type):
        # Colors based on type
        colors = {
            "info": {"border": "#4a9eff", "icon": "#4a9eff"},
            "success": {"border": "#66d9ef", "icon": "#66d9ef"},
            "warning": {"border": "#ffd93d", "icon": "#ffd93d"},
            "error": {"border": "#ff6b6b", "icon": "#ff6b6b"}
        }
        color = colors.get(notification_type, colors["info"])
        
        self.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QFrame#container {{
                background: rgba(13, 13, 13, 0.92);
                border: 1px solid {color["border"]};
                border-radius: 8px;
                padding: 10px;
            }}
            QLabel {{
                color: #cccccc;
                background: transparent;
            }}
            QLabel#title {{
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
            }}
            QLabel#message {{
                color: #888888;
                font-size: 12px;
            }}
            QLabel#icon {{
                font-size: 28px;
                color: {color["icon"]};
            }}
            QPushButton {{
                background: transparent;
                border: none;
                color: #666666;
                font-size: 14px;
                padding: 2px 6px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background: #2a2a2a;
                color: #ff6666;
            }}
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container
        container = QFrame()
        container.setObjectName("container")
        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(12, 10, 10, 10)
        container_layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setObjectName("icon")
        container_layout.addWidget(icon_label)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setObjectName("title")
        content_layout.addWidget(title_label)
        
        message_label = QLabel(message)
        message_label.setObjectName("message")
        message_label.setWordWrap(True)
        content_layout.addWidget(message_label)
        
        container_layout.addLayout(content_layout, 1)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(25, 25)
        close_btn.clicked.connect(self.close)
        container_layout.addWidget(close_btn)
        
        container.setLayout(container_layout)
        layout.addWidget(container)
        
        self.setLayout(layout)
        
        # Set fixed width
        self.setFixedWidth(350)
        self.adjustSize()
        
        # Auto-close timer
        if self.duration > 0:
            QTimer.singleShot(self.duration, self.close)
    
    def animate_in(self):
        """Animate the toast entering"""
        # Position at bottom-right of screen
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 60
        self.move(x, y)
        
        # Slide in animation
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.pos() + QPoint(0, 50))
        self.animation.setEndValue(self.pos())
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
        
        # Fade in
        self.setWindowOpacity(0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_animation.start()
    
    def closeEvent(self, event):
        """Fade out when closing"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.finished.connect(self.deleteLater)
        self.fade_animation.start()
        event.accept()