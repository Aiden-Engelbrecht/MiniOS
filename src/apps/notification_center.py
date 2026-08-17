"""
Notification Center for MiniOS
View and manage all notifications
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QListWidget,
    QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.notification_manager import NotificationManager


class NotificationItemWidget(QWidget):
    """Single notification item widget"""
    
    dismissed = Signal(str)
    
    def __init__(self, notification, parent=None):
        super().__init__(parent)
        self.notification = notification
        self.setup_ui()
        
    def setup_ui(self):
        # Color based on type
        colors = {
            "info": "#4a9eff",
            "success": "#66d9ef",
            "warning": "#ffd93d",
            "error": "#ff6b6b"
        }
        color = colors.get(self.notification.type, "#4a9eff")
        
        self.setStyleSheet(f"""
            QWidget {{
                background: #0d0d0d;
                border: 1px solid #1a1a1a;
                border-radius: 6px;
                padding: 0px;
            }}
            QWidget:hover {{
                background: #1a1a1a;
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
            QLabel#time {{
                color: #444444;
                font-size: 10px;
            }}
            QPushButton {{
                background: transparent;
                border: none;
                color: #666666;
                font-size: 12px;
                padding: 2px 8px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background: #2a2a2a;
                color: #ff6666;
            }}
            QLabel#icon {{
                font-size: 24px;
                color: {color};
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 10, 10, 10)
        layout.setSpacing(12)
        
        # Icon
        self.icon_label = QLabel(self.notification.icon)
        self.icon_label.setObjectName("icon")
        layout.addWidget(self.icon_label)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        self.title_label = QLabel(self.notification.title)
        self.title_label.setObjectName("title")
        content_layout.addWidget(self.title_label)
        
        self.message_label = QLabel(self.notification.message)
        self.message_label.setObjectName("message")
        self.message_label.setWordWrap(True)
        content_layout.addWidget(self.message_label)
        
        # Time
        time_str = self.notification.timestamp.strftime("%H:%M")
        self.time_label = QLabel(f"🕐 {time_str}")
        self.time_label.setObjectName("time")
        content_layout.addWidget(self.time_label)
        
        layout.addLayout(content_layout, 1)
        
        # Dismiss button
        self.dismiss_btn = QPushButton("×")
        self.dismiss_btn.setFixedSize(25, 25)
        self.dismiss_btn.clicked.connect(lambda: self.dismissed.emit(self.notification.id))
        layout.addWidget(self.dismiss_btn)
        
        self.setLayout(layout)


class NotificationCenterWidget(QWidget):
    """Notification Center application widget"""
    
    notificationDismissed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.notification_manager = NotificationManager()
        self.setup_ui()
        self.load_notifications()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #0d0d0d;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel#title {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
            QLabel#empty {
                color: #666666;
                font-size: 14px;
                padding: 40px;
            }
            QPushButton {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #2a2a2a;
                color: #ffffff;
            }
            QPushButton#clear_btn {
                background: #4a2a2a;
                border: 1px solid #5a3a3a;
                color: #ff8888;
            }
            QPushButton#clear_btn:hover {
                background: #5a3a3a;
            }
            QScrollArea {
                background: #0d0d0d;
                border: none;
            }
            QScrollBar:vertical {
                background: #0d0d0d;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #2a2a2a;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3a3a3a;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🔔 Notifications")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.count_label = QLabel("0")
        self.count_label.setStyleSheet("color: #666666; font-size: 12px;")
        header_layout.addWidget(self.count_label)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setObjectName("clear_btn")
        self.clear_btn.clicked.connect(self.clear_all)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # Scroll area for notifications
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container widget
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(8)
        self.container_layout.addStretch()
        
        self.container.setLayout(self.container_layout)
        self.scroll_area.setWidget(self.container)
        
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
        # Connect to notification manager
        self.notification_manager.notificationAdded.connect(self.add_notification_widget)
        self.notification_manager.allNotificationsCleared.connect(self.clear_all_widgets)
    
    def load_notifications(self):
        """Load existing notifications"""
        notifications = self.notification_manager.get_notifications()
        if notifications:
            for notif in notifications:
                self.add_notification_widget(notif)
        else:
            self.show_empty_message()
    
    def add_notification_widget(self, notification):
        """Add a notification widget to the list"""
        # Remove empty message if present
        self.remove_empty_message()
        
        # Create widget
        widget = NotificationItemWidget(notification)
        widget.dismissed.connect(self.dismiss_notification)
        
        # Insert at top
        self.container_layout.insertWidget(0, widget)
        
        # Update count
        self.update_count()
    
    def dismiss_notification(self, notification_id):
        """Dismiss a notification"""
        self.notification_manager.dismiss_notification(notification_id)
        self.refresh_notifications()
        self.notificationDismissed.emit(notification_id)
    
    def clear_all(self):
        """Clear all notifications"""
        self.notification_manager.dismiss_all()
        self.clear_all_widgets()
    
    def clear_all_widgets(self):
        """Clear all notification widgets"""
        self.clear_container()
        self.show_empty_message()
        self.update_count()
    
    def refresh_notifications(self):
        """Refresh the notification list"""
        self.clear_container()
        notifications = self.notification_manager.get_notifications()
        if notifications:
            for notif in notifications:
                widget = NotificationItemWidget(notif)
                widget.dismissed.connect(self.dismiss_notification)
                self.container_layout.insertWidget(0, widget)
        else:
            self.show_empty_message()
        self.update_count()
    
    def clear_container(self):
        """Clear all widgets from container"""
        while self.container_layout.count() > 1:  # Keep the stretch
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def show_empty_message(self):
        """Show empty message"""
        empty_label = QLabel("No notifications")
        empty_label.setObjectName("empty")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.container_layout.insertWidget(0, empty_label)
    
    def remove_empty_message(self):
        """Remove empty message if present"""
        if self.container_layout.count() > 1:
            item = self.container_layout.itemAt(0)
            if item and item.widget() and item.widget().objectName() == "empty":
                item.widget().deleteLater()
    
    def update_count(self):
        """Update notification count"""
        count = len(self.notification_manager.get_notifications())
        unread = self.notification_manager.get_unread_count()
        if unread > 0:
            self.count_label.setText(f"{count} ({unread} unread)")
        else:
            self.count_label.setText(f"{count}")
    
    def closeEvent(self, event):
        """Handle close event"""
        event.accept()