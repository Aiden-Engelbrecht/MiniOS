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
    """Minimal taskbar at the bottom of the screen"""
    
    startMenuRequested = Signal()
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)
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
            QFrame#separator {
                background: #1a1a1a;
                max-width: 1px;
                min-width: 1px;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 4, 14, 4)
        layout.setSpacing(10)
        
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
        
        # Taskbar items placeholder
        self.task_label = QLabel("desktop")
        self.task_label.setFont(QFont("Segoe UI", 9))
        self.task_label.setStyleSheet("color: #555555;")
        layout.addWidget(self.task_label)
        
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
            print(f"Desktop icon clicked: {self.name}")  # Debug output
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
            # Connect the click signal properly
            icon_widget.clicked.connect(lambda checked, n=name: self.iconClicked.emit(n))
            icons_layout.addWidget(icon_widget)
            self.icon_widgets.append(icon_widget)
            print(f"Created icon: {name}")  # Debug output
        
        icons_widget.setLayout(icons_layout)
        
        layout.addWidget(icons_widget)
        layout.addStretch()
        
        self.setLayout(layout)