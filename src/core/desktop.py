"""
Desktop Environment for MiniOS - Minimal Black Edition
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame
)
from PySide6.QtCore import Qt, QTimer, QDateTime, Signal, QPoint
from PySide6.QtGui import QFont


class Taskbar(QWidget):
    """Minimal taskbar at the bottom of the screen with window buttons"""
    
    startMenuRequested = Signal()
    windowButtonClicked = Signal(object)  # Emits window object when clicked
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)
        self.window_buttons = {}  # window -> button mapping
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
        
        # Start button
        self.start_button = QPushButton("◆ minios")
        self.start_button.setFont(QFont("Segoe UI", 9, QFont.Weight.Light))
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.clicked.connect(self.startMenuRequested.emit)
        layout.addWidget(self.start_button)
        
        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        # Window buttons container (dynamic)
        self.window_container = QWidget()
        self.window_container.setStyleSheet("background: transparent;")
        self.window_layout = QHBoxLayout()
        self.window_layout.setContentsMargins(0, 0, 0, 0)
        self.window_layout.setSpacing(5)
        self.window_container.setLayout(self.window_layout)
        layout.addWidget(self.window_container)
        
        layout.addStretch()
        
        # System tray
        self.clock_label = QLabel("--:--")
        self.clock_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Light))
        self.clock_label.setStyleSheet("color: #888888; padding: 0 6px;")
        layout.addWidget(self.clock_label)
        
        self.setLayout(layout)
        
    def setup_clock(self):
        """Setup real-time clock"""
        self.update_clock()
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
    def update_clock(self):
        """Update the clock display"""
        current_time = QDateTime.currentDateTime()
        time_str = current_time.toString("hh:mm")
        self.clock_label.setText(time_str)
    
    def show_start_menu(self, menu):
        """Show start menu at correct position"""
        button_pos = self.start_button.mapToGlobal(QPoint(0, 0))
        menu.move(button_pos.x(), button_pos.y() - menu.height() - 2)
        menu.exec_()
    
    def add_window_button(self, window, title):
        """Add a button for a window to the taskbar"""
        # Check if button already exists
        if window in self.window_buttons:
            return
        
        print(f"Adding taskbar button for: {title}")
        
        # Create button
        btn = QPushButton(f"◈ {title[:15]}")
        btn.setObjectName("window_btn")
        btn.setCheckable(True)
        btn.setChecked(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Store the window reference directly in the button
        btn.window_ref = window
        
        # Connect using a simple lambda with the window captured
        btn.clicked.connect(lambda: self.emit_window_click(window))
        
        # Store reference
        self.window_buttons[window] = btn
        
        # Add to layout
        self.window_layout.addWidget(btn)
        
        # Update container visibility
        self.window_container.setVisible(True)
    
    def emit_window_click(self, window):
        """Emit the window click signal"""
        print(f"Taskbar button clicked for: {window.title}")
        self.windowButtonClicked.emit(window)
        
    def remove_window_button(self, window):
        """Remove a window button from the taskbar"""
        if window in self.window_buttons:
            btn = self.window_buttons[window]
            self.window_layout.removeWidget(btn)
            btn.deleteLater()
            del self.window_buttons[window]
            
            # Hide container if no buttons
            if len(self.window_buttons) == 0:
                self.window_container.setVisible(False)
            
            print(f"Removed taskbar button for: {window.title}")
    
    def update_window_button(self, window, is_active):
        """Update the active state of a window button"""
        if window in self.window_buttons:
            self.window_buttons[window].setChecked(is_active)
            print(f"Updated taskbar button for: {window.title} active={is_active}")


class DesktopIcon(QWidget):
    """Desktop icon with separate icon and label for proper text display"""
    
    clicked = Signal()
    
    def __init__(self, name, icon_text="◈", color="#666666"):
        super().__init__()
        self.name = name
        self.setFixedSize(80, 90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon label (the symbol)
        self.icon_label = QLabel(icon_text)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFont(QFont("Segoe UI", 28))
        
        # Set icon color
        colors = {
            "files": "#4a9eff",
            "terminal": "#66d9ef", 
            "settings": "#a6a6a6",
            "notepad": "#f8f8f2"
        }
        icon_color = colors.get(name, "#666666")
        self.icon_label.setStyleSheet(f"""
            color: {icon_color};
            background: transparent;
            padding: 2px;
        """)
        layout.addWidget(self.icon_label)
        
        # Name label (the text)
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
        
        # Style the widget
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
        """Handle click events"""
        if event.button() == Qt.MouseButton.LeftButton:
            print(f"Desktop icon clicked: {self.name}")
            self.clicked.emit()


class DesktopWidget(QWidget):
    """Main desktop widget with wallpaper and icons"""
    
    iconClicked = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #000000;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Desktop icons area (top-left)
        icons_widget = QWidget()
        icons_widget.setStyleSheet("background: transparent;")
        icons_layout = QHBoxLayout()
        icons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        icons_layout.setSpacing(15)
        
        # Desktop icons with creative symbols
        desktop_icons = [
            ("files", "◈"),
            ("terminal", "⌘"), 
            ("notepad", "✎"),
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
        """Create a handler function for icon clicks"""
        def handler():
            self.iconClicked.emit(name)
        return handler