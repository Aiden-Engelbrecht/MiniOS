"""
Desktop Environment for MiniOS - Minimal Black Edition
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QMenu, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QDateTime, Signal, QPoint
from PySide6.QtGui import QFont, QAction


class Taskbar(QWidget):
    """Minimal taskbar at the bottom of the screen with window buttons"""
    
    startMenuRequested = Signal()
    windowButtonClicked = Signal(object)
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)
        self.window_buttons = {}
        self.setup_ui()
        self.setup_clock()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #0a0a0a;
                border-top: 1px solid #1a1a1a;
            }
            QLabel {
                color: #888888;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
            }
            QPushButton {
                background: transparent;
                border: none;
                color: #888888;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 4px 14px;
                font-size: 11px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                color: #ffffff;
                background: #1a1a1a;
                border-radius: 3px;
            }
            QPushButton#window_btn {
                background: #0d0d0d;
                border: 1px solid #1a1a1a;
                border-radius: 3px;
                color: #888888;
                padding: 4px 12px;
                font-size: 10px;
                max-width: 150px;
            }
            QPushButton#window_btn:hover {
                background: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
            }
            QPushButton#window_btn:checked {
                background: #1a1a1a;
                color: #ffffff;
                border: 1px solid #444444;
            }
            QFrame#separator {
                background: #1a1a1a;
                max-width: 1px;
                min-width: 1px;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 4, 14, 4)
        layout.setSpacing(8)
        
        self.start_button = QPushButton("◆ minios")
        self.start_button.setFont(QFont("Segoe UI", 9, QFont.Weight.Light))
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.clicked.connect(self.startMenuRequested.emit)
        layout.addWidget(self.start_button)
        
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        self.window_container = QWidget()
        self.window_container.setStyleSheet("background: transparent;")
        self.window_layout = QHBoxLayout()
        self.window_layout.setContentsMargins(0, 0, 0, 0)
        self.window_layout.setSpacing(5)
        self.window_container.setLayout(self.window_layout)
        layout.addWidget(self.window_container)
        
        layout.addStretch()
        
        self.clock_label = QLabel("--:--")
        self.clock_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Light))
        self.clock_label.setStyleSheet("color: #888888; padding: 0 6px;")
        layout.addWidget(self.clock_label)
        
        self.setLayout(layout)
        
    def setup_clock(self):
        self.update_clock()
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
    def update_clock(self):
        current_time = QDateTime.currentDateTime()
        time_str = current_time.toString("hh:mm")
        self.clock_label.setText(time_str)
    
    def show_start_menu(self, menu):
        button_pos = self.start_button.mapToGlobal(QPoint(0, 0))
        menu.move(button_pos.x(), button_pos.y() - menu.height() - 2)
        menu.exec_()
    
    def add_window_button(self, window, title):
        if window in self.window_buttons:
            return
        
        btn = QPushButton(f"◈ {title[:15]}")
        btn.setObjectName("window_btn")
        btn.setCheckable(True)
        btn.setChecked(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.emit_window_click(window))
        
        self.window_buttons[window] = btn
        self.window_layout.addWidget(btn)
        self.window_container.setVisible(True)
    
    def emit_window_click(self, window):
        self.windowButtonClicked.emit(window)
        
    def remove_window_button(self, window):
        if window in self.window_buttons:
            btn = self.window_buttons[window]
            self.window_layout.removeWidget(btn)
            btn.deleteLater()
            del self.window_buttons[window]
            
            if len(self.window_buttons) == 0:
                self.window_container.setVisible(False)
    
    def update_window_button(self, window, is_active):
        if window in self.window_buttons:
            self.window_buttons[window].setChecked(is_active)


class DesktopIcon(QWidget):
    clicked = Signal()
    
    def __init__(self, name, icon_text="◈", color="#666666"):
        super().__init__()
        self.name = name
        self.setFixedSize(80, 90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_label = QLabel(icon_text)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFont(QFont("Segoe UI", 28))
        
        colors = {
            "files": "#4a9eff",
            "terminal": "#66d9ef", 
            "settings": "#a6a6a6",
            "notepad": "#f8f8f2",
            "calculator": "#ffd93d",
            "calendar": "#ff6b6b",
            "imageviewer": "#ffa94d",
            "recyclebin": "#ff6b6b",
            "musicplayer": "#ff6bff",
            "systemmonitor": "#66d9ef",
            "taskmanager": "#ff6b6b",
            "weather": "#4a9eff",
            "search": "#f8f8f2",
            "notifications": "#ffd93d"
        }
        icon_color = colors.get(name, "#666666")
        self.icon_label.setStyleSheet(f"""
            color: {icon_color};
            background: transparent;
            padding: 2px;
        """)
        layout.addWidget(self.icon_label)
        
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setFont(QFont("Segoe UI", 8))
        self.name_label.setStyleSheet("""
            color: #cccccc;
            background: transparent;
            padding: 2px;
        """)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
                border-radius: 6px;
            }
            QWidget:hover {
                background: rgba(255, 255, 255, 0.04);
            }
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class DesktopWidget(QWidget):
    iconClicked = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #000000;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        icons_widget = QWidget()
        icons_widget.setStyleSheet("background: transparent;")
        icons_layout = QHBoxLayout()
        icons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        icons_layout.setSpacing(15)
        
        desktop_icons = [
            ("files", "◈"),
            ("terminal", "⌘"), 
            ("notepad", "✎"),
            ("calculator", "🧮"),
            ("calendar", "📅"),
            ("imageviewer", "🖼"),
            ("musicplayer", "🎵"),
            ("systemmonitor", "📊"),
            ("taskmanager", "📋"),
            ("recyclebin", "🗑"),
            ("notifications", "🔔"),
            ("weather", "🌤"),
            ("search", "🔍"),
            ("settings", "⚙")
        ]
        
        self.icon_widgets = []
        for name, symbol in desktop_icons:
            icon_widget = DesktopIcon(name, symbol)
            icon_widget.clicked.connect(self.create_icon_click_handler(name))
            icons_layout.addWidget(icon_widget)
            self.icon_widgets.append(icon_widget)
        
        icons_widget.setLayout(icons_layout)
        layout.addWidget(icons_widget)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def create_icon_click_handler(self, name):
        def handler():
            self.iconClicked.emit(name)
        return handler
    
    def show_context_menu(self, position):
        """Show desktop context menu"""
        menu = QMenu(self)
        
        # Appearance section
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.triggered.connect(self.refresh_desktop)
        menu.addAction(refresh_action)
        
        menu.addSeparator()
        
        # New section
        new_menu = QMenu("📁 New", self)
        
        folder_action = QAction("Folder", self)
        folder_action.triggered.connect(self.create_new_folder)
        new_menu.addAction(folder_action)
        
        file_action = QAction("File", self)
        file_action.triggered.connect(self.create_new_file)
        new_menu.addAction(file_action)
        
        menu.addMenu(new_menu)
        
        menu.addSeparator()
        
        # System actions
        search_action = QAction("🔍 Search", self)
        search_action.triggered.connect(lambda: self.iconClicked.emit("search"))
        menu.addAction(search_action)
        
        settings_action = QAction("⚙ Settings", self)
        settings_action.triggered.connect(lambda: self.iconClicked.emit("settings"))
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # System actions
        logout_action = QAction("🚪 Logout", self)
        logout_action.triggered.connect(lambda: self.iconClicked.emit("logout"))
        menu.addAction(logout_action)
        
        shutdown_action = QAction("⏻ Shutdown", self)
        shutdown_action.triggered.connect(lambda: self.iconClicked.emit("shutdown"))
        menu.addAction(shutdown_action)
        
        menu.exec_(self.mapToGlobal(position))
    
    def refresh_desktop(self):
        """Refresh the desktop"""
        self.update()
        # Emit a refresh signal if needed
    
    def create_new_folder(self):
        """Create a new folder on desktop (placeholder)"""
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name:
            QMessageBox.information(self, "Created", f"Folder '{name}' created on desktop.")
    
    def create_new_file(self):
        """Create a new file on desktop (placeholder)"""
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            QMessageBox.information(self, "Created", f"File '{name}' created on desktop.")