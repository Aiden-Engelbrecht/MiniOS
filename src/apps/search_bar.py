"""
Search Bar for MiniOS
Global search for files, applications, and system items
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem,
    QFrame, QPushButton
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QKeyEvent
import os


class SearchBarWidget(QWidget):
    """Global search bar widget"""
    
    appLaunched = Signal(str)  # Emits app_id when app is launched
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(500, 60)
        
        self.all_apps = self.get_all_apps()
        self.filtered_apps = []
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#container {
                background: rgba(13, 13, 13, 0.92);
                border: 1px solid #1a1a1a;
                border-radius: 10px;
                padding: 0px;
            }
            QLineEdit {
                background: transparent;
                border: none;
                color: #cccccc;
                font-size: 16px;
                padding: 10px 15px;
                selection-background-color: #2a2a2a;
            }
            QLineEdit:focus {
                border: none;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #555555;
                font-size: 14px;
            }
            QListWidget {
                background: rgba(13, 13, 13, 0.95);
                border: none;
                border-top: 1px solid #1a1a1a;
                border-radius: 0 0 10px 10px;
                color: #cccccc;
                font-size: 14px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 15px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #1a1a1a;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background: #2a2a2a;
                color: #ffffff;
            }
            QLabel#icon_label {
                color: #666666;
                font-size: 18px;
                padding: 0 5px;
            }
            QLabel#hint {
                color: #444444;
                font-size: 11px;
                padding: 5px 15px;
            }
            QPushButton#close_btn {
                background: transparent;
                border: none;
                color: #666666;
                font-size: 16px;
                padding: 0 10px;
                min-width: 30px;
            }
            QPushButton#close_btn:hover {
                color: #ff6666;
                background: rgba(255, 0, 0, 0.1);
                border-radius: 4px;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container
        container = QFrame()
        container.setObjectName("container")
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Search input row
        input_row = QHBoxLayout()
        input_row.setContentsMargins(5, 0, 5, 0)
        input_row.setSpacing(0)
        
        # Search icon
        search_icon = QLabel("🔍")
        search_icon.setObjectName("icon_label")
        input_row.addWidget(search_icon)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files, apps, settings...")
        self.search_input.textChanged.connect(self.on_search)
        self.search_input.returnPressed.connect(self.on_enter_pressed)
        self.search_input.setFocus()
        input_row.addWidget(self.search_input)
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close_btn")
        self.close_btn.clicked.connect(self.close)
        input_row.addWidget(self.close_btn)
        
        container_layout.addLayout(input_row)
        
        # Results list (hidden by default)
        self.results_list = QListWidget()
        self.results_list.setVisible(False)
        self.results_list.setFixedHeight(0)
        self.results_list.itemClicked.connect(self.on_result_clicked)
        self.results_list.itemDoubleClicked.connect(self.on_result_clicked)
        container_layout.addWidget(self.results_list)
        
        # Hint label
        self.hint_label = QLabel("Press Escape to close")
        self.hint_label.setObjectName("hint")
        self.hint_label.setVisible(False)
        container_layout.addWidget(self.hint_label)
        
        container.setLayout(container_layout)
        layout.addWidget(container)
        
        self.setLayout(layout)
        
        # Timer to auto-close after inactivity
        self.inactivity_timer = QTimer()
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.close)
        
    def get_all_apps(self):
        """Get all available applications"""
        return [
            {"id": "explorer", "name": "File Explorer", "icon": "📁", "category": "Apps"},
            {"id": "notepad", "name": "Notepad", "icon": "📝", "category": "Apps"},
            {"id": "terminal", "name": "Terminal", "icon": "💻", "category": "Apps"},
            {"id": "calculator", "name": "Calculator", "icon": "🧮", "category": "Apps"},
            {"id": "calendar", "name": "Calendar", "icon": "📅", "category": "Apps"},
            {"id": "imageviewer", "name": "Image Viewer", "icon": "🖼", "category": "Apps"},
            {"id": "musicplayer", "name": "Music Player", "icon": "🎵", "category": "Apps"},
            {"id": "systemmonitor", "name": "System Monitor", "icon": "📊", "category": "Apps"},
            {"id": "recyclebin", "name": "Recycle Bin", "icon": "🗑", "category": "Apps"},
            {"id": "weather", "name": "Weather Widget", "icon": "🌤", "category": "Widgets"},
            {"id": "settings", "name": "Settings", "icon": "⚙", "category": "System"},
            {"id": "logout", "name": "Logout", "icon": "🚪", "category": "System"},
            {"id": "shutdown", "name": "Shutdown", "icon": "⏻", "category": "System"},
        ]
    
    def show_search(self):
        """Show the search bar and focus on input"""
        self.show()
        self.raise_()
        self.search_input.clear()
        self.search_input.setFocus()
        self.results_list.setVisible(False)
        self.results_list.setFixedHeight(0)
        self.hint_label.setVisible(False)
        self.setFixedSize(500, 60)
        
        # Reset inactivity timer
        self.inactivity_timer.stop()
        self.inactivity_timer.start(30000)  # Auto-close after 30 seconds
    
    def on_search(self, text):
        """Handle search text changes"""
        text = text.strip().lower()
        
        # Reset inactivity timer
        self.inactivity_timer.stop()
        self.inactivity_timer.start(30000)
        
        if not text:
            self.results_list.setVisible(False)
            self.results_list.setFixedHeight(0)
            self.hint_label.setVisible(False)
            self.setFixedSize(500, 60)
            return
        
        # Filter apps
        self.filtered_apps = []
        for app in self.all_apps:
            if (text in app["name"].lower() or 
                text in app["id"].lower() or
                text in app["category"].lower()):
                self.filtered_apps.append(app)
        
        # Show results
        self.results_list.clear()
        
        if self.filtered_apps:
            for app in self.filtered_apps:
                item_text = f"{app['icon']}  {app['name']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, app["id"])
                self.results_list.addItem(item)
            
            self.results_list.setVisible(True)
            self.results_list.setFixedHeight(min(len(self.filtered_apps) * 40, 250))
            self.hint_label.setVisible(True)
            self.setFixedSize(500, 60 + self.results_list.height() + 30)
        else:
            self.results_list.setVisible(False)
            self.results_list.setFixedHeight(0)
            self.hint_label.setVisible(True)
            self.hint_label.setText("No results found")
            self.setFixedSize(500, 90)
    
    def on_enter_pressed(self):
        """Handle Enter key press"""
        if self.filtered_apps:
            # Open the first result
            app_id = self.filtered_apps[0]["id"]
            self.launch_result(app_id)
    
    def on_result_clicked(self, item):
        """Handle click on result"""
        app_id = item.data(Qt.ItemDataRole.UserRole)
        self.launch_result(app_id)
    
    def launch_result(self, app_id):
        """Launch the selected application"""
        self.close()
        self.appLaunched.emit(app_id)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Down:
            if self.results_list.isVisible() and self.results_list.count() > 0:
                self.results_list.setCurrentRow(0)
                self.results_list.setFocus()
        elif event.key() == Qt.Key.Key_Up:
            if self.results_list.isVisible() and self.results_list.count() > 0:
                self.results_list.setCurrentRow(self.results_list.count() - 1)
                self.results_list.setFocus()
        elif event.key() == Qt.Key.Key_Return and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.close()
        else:
            super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """Close when focus is lost (unless clicking on results)"""
        # Don't close if the focus is moving to the results list
        if event.reason() == Qt.FocusReason.PopupFocusReason:
            return
        # Don't close if clicking on the widget
        if event.reason() == Qt.FocusReason.MouseFocusReason:
            # Check if the click was inside our widget
            pos = self.mapFromGlobal(event.globalPos())
            if self.rect().contains(pos):
                return
        # Close after a short delay to allow clicks on results
        QTimer.singleShot(100, self.close)
    
    def closeEvent(self, event):
        """Handle close event"""
        self.inactivity_timer.stop()
        event.accept()
    
    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        self.search_input.setFocus()
        self.inactivity_timer.start(30000)