"""
Notification Manager for MiniOS
Manages system notifications
"""

from PySide6.QtCore import QObject, Signal, QTimer, QDateTime
from PySide6.QtWidgets import QWidget
import json
import os
from datetime import datetime


class Notification:
    """Notification object"""
    
    def __init__(self, title: str, message: str, icon: str = "📢", notification_type: str = "info"):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.title = title
        self.message = message
        self.icon = icon
        self.type = notification_type  # info, warning, success, error
        self.timestamp = datetime.now()
        self.read = False
        
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "icon": self.icon,
            "type": self.type,
            "timestamp": self.timestamp.isoformat(),
            "read": self.read
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        notif = cls(data["title"], data["message"], data["icon"], data["type"])
        notif.id = data["id"]
        notif.timestamp = datetime.fromisoformat(data["timestamp"])
        notif.read = data["read"]
        return notif


class NotificationManager(QObject):
    """Manages system notifications"""
    
    # Signals
    notificationAdded = Signal(object)
    notificationRemoved = Signal(object)
    allNotificationsCleared = Signal()
    
    def __init__(self):
        super().__init__()
        self.notifications = []
        self.history = []
        self.max_notifications = 50
        self.load_history()
        
    def add_notification(self, title: str, message: str, icon: str = "📢", 
                        notification_type: str = "info", duration: int = 5000):
        """Add a new notification"""
        notification = Notification(title, message, icon, notification_type)
        
        # Add to current notifications
        self.notifications.insert(0, notification)
        
        # Limit notifications
        if len(self.notifications) > 20:
            self.notifications = self.notifications[:20]
        
        # Add to history
        self.history.insert(0, notification.to_dict())
        if len(self.history) > self.max_notifications:
            self.history = self.history[:self.max_notifications]
        
        # Save history
        self.save_history()
        
        # Emit signal
        self.notificationAdded.emit(notification)
        
        # Auto-dismiss after duration
        if duration > 0:
            QTimer.singleShot(duration, lambda: self.dismiss_notification(notification.id))
        
        return notification
    
    def dismiss_notification(self, notification_id: str):
        """Dismiss a specific notification"""
        for i, notif in enumerate(self.notifications):
            if notif.id == notification_id:
                removed = self.notifications.pop(i)
                self.notificationRemoved.emit(removed)
                return True
        return False
    
    def dismiss_all(self):
        """Dismiss all notifications"""
        self.notifications.clear()
        self.allNotificationsCleared.emit()
    
    def mark_as_read(self, notification_id: str):
        """Mark a notification as read"""
        for notif in self.notifications:
            if notif.id == notification_id:
                notif.read = True
                # Update in history
                for h in self.history:
                    if h["id"] == notification_id:
                        h["read"] = True
                self.save_history()
                return True
        return False
    
    def mark_all_read(self):
        """Mark all notifications as read"""
        for notif in self.notifications:
            notif.read = True
        for h in self.history:
            h["read"] = True
        self.save_history()
    
    def get_notifications(self):
        """Get all current notifications"""
        return self.notifications
    
    def get_unread_count(self):
        """Get count of unread notifications"""
        return sum(1 for n in self.notifications if not n.read)
    
    def load_history(self):
        """Load notification history from file"""
        history_path = os.path.join("data", "notifications.json")
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r') as f:
                    data = json.load(f)
                    self.history = data
            except:
                self.history = []
    
    def save_history(self):
        """Save notification history to file"""
        os.makedirs("data", exist_ok=True)
        history_path = os.path.join("data", "notifications.json")
        try:
            with open(history_path, 'w') as f:
                json.dump(self.history, f, indent=2)
        except:
            pass
    
    def clear_history(self):
        """Clear notification history"""
        self.history = []
        self.save_history()