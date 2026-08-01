"""
Window Manager for MiniOS - Minimal Black Edition
Manages application windows with title bars and dragging
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame
)
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QFont, QMouseEvent


class WindowTitleBar(QWidget):
    """Custom title bar for windows with drag support"""
    
    closeRequested = Signal()
    minimizeRequested = Signal()
    maximizeRequested = Signal()
    
    def __init__(self, title="Window"):
        super().__init__()
        self.title = title
        self.dragging = False
        self.drag_position = QPoint()
        self.setFixedHeight(35)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #0a0a0a;
                border-bottom: 1px solid #1a1a1a;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QLabel {
                color: #888888;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                font-size: 12px;
                padding: 0 10px;
            }
            QPushButton {
                background: transparent;
                border: none;
                color: #666666;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                padding: 0 12px;
                min-width: 30px;
                min-height: 30px;
            }
            QPushButton:hover {
                color: #ffffff;
                background: #1a1a1a;
            }
            QPushButton#close:hover {
                color: #ff4444;
                background: #2a0a0a;
            }
            QPushButton#maximize:hover {
                color: #66d9ef;
            }
            QPushButton#minimize:hover {
                color: #66d9ef;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(0)
        
        # Window title
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Light))
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Window controls
        self.minimize_btn = QPushButton("—")
        self.minimize_btn.setObjectName("minimize")
        self.minimize_btn.clicked.connect(self.minimizeRequested.emit)
        self.minimize_btn.setFixedSize(30, 30)
        layout.addWidget(self.minimize_btn)
        
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setObjectName("maximize")
        self.maximize_btn.clicked.connect(self.maximizeRequested.emit)
        self.maximize_btn.setFixedSize(30, 30)
        layout.addWidget(self.maximize_btn)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close")
        self.close_btn.clicked.connect(self.closeRequested.emit)
        self.close_btn.setFixedSize(30, 30)
        layout.addWidget(self.close_btn)
        
        self.setLayout(layout)
        
    def mousePressEvent(self, event: QMouseEvent):
        """Start dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.parent().frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """Move the window while dragging"""
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.parent().move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Stop dragging"""
        self.dragging = False
        event.accept()


class BaseWindow(QWidget):
    """Base window class with title bar and content area"""
    
    def __init__(self, title="Window", width=600, height=400, manager=None):
        super().__init__()
        self.title = title
        self.width = width
        self.height = height
        self.manager = manager
        self.is_maximized = False
        self.normal_geometry = None
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setup_ui()
        self.setFixedSize(width, height)
        
        # Connect signals
        self.title_bar.minimizeRequested.connect(self.minimize_window)
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)
        
        # Frame that holds everything
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background: #0d0d0d;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
            }
        """)
        
        # Frame layout
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)
        
        # Title bar
        self.title_bar = WindowTitleBar(self.title)
        self.title_bar.closeRequested.connect(self.close)
        self.title_bar.minimizeRequested.connect(self.minimize_window)
        self.title_bar.maximizeRequested.connect(self.toggle_maximize)
        frame_layout.addWidget(self.title_bar)
        
        # Content area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("""
            QWidget {
                background: #0d0d0d;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_area.setLayout(self.content_layout)
        
        frame_layout.addWidget(self.content_area, 1)
        
        self.frame.setLayout(frame_layout)
        main_layout.addWidget(self.frame)
        
        self.setLayout(main_layout)
        
    def minimize_window(self):
        """Minimize the window (hide it)"""
        self.hide()
        # Notify manager that window was minimized
        if self.manager:
            self.manager.on_window_minimized(self)
        
    def restore_window(self):
        """Restore a minimized window"""
        self.show()
        self.raise_()
        self.activateWindow()
        # Notify manager
        if self.manager:
            self.manager.on_window_restored(self)
        
    def toggle_maximize(self):
        """Toggle between normal and maximized state"""
        if not self.is_maximized:
            self.normal_geometry = self.geometry()
            self.showMaximized()
            self.is_maximized = True
        else:
            self.showNormal()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.is_maximized = False
            
    def add_widget(self, widget):
        """Add a widget to the content area - fills all space"""
        self.clear_content()
        self.content_layout.addWidget(widget)
        widget.setSizePolicy(
            widget.sizePolicy().Policy.Expanding,
            widget.sizePolicy().Policy.Expanding
        )
        
    def clear_content(self):
        """Clear all widgets from content area"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
    def set_title(self, title):
        """Update window title"""
        self.title = title
        self.title_bar.title_label.setText(title)
        
    def closeEvent(self, event):
        """Handle window close - notify manager"""
        if self.manager:
            self.manager.remove_window(self)
        event.accept()


class WindowManager:
    """Manages all open windows with taskbar integration"""
    
    def __init__(self, taskbar=None):
        self.windows = []
        self.window_counter = 0
        self.taskbar = taskbar
        self.minimized_windows = set()
        
    def set_taskbar(self, taskbar):
        """Set the taskbar reference for window buttons"""
        self.taskbar = taskbar
        if taskbar:
            taskbar.windowButtonClicked.connect(self.restore_window_from_taskbar)
        
    def create_window(self, title="Window", width=600, height=400, content_widget=None):
        """Create a new window with optional content"""
        self.window_counter += 1
        
        # Create window with manager reference
        window = BaseWindow(title, width, height, manager=self)
        
        if content_widget:
            window.add_widget(content_widget)
        else:
            label = QLabel("Window")
            label.setStyleSheet("""
                color: #666666;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            window.add_widget(label)
        
        # Position windows with offset
        offset = len(self.windows) * 30
        if offset > 200:
            offset = offset % 200
        
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        max_x = screen.width() - width - 50
        max_y = screen.height() - height - 100
        
        x_pos = min(50 + offset, max_x)
        y_pos = min(50 + offset, max_y)
        
        window.move(x_pos, y_pos)
        
        # Store reference
        self.windows.append(window)
        
        # Add to taskbar
        if self.taskbar:
            self.taskbar.add_window_button(window, title)
        
        # Bring to front
        self.raise_window(window)
        
        # Show the window
        window.show()
        
        return window
    
    def minimize_window(self, window):
        """Minimize a window"""
        if window in self.windows:
            window.hide()
            self.minimized_windows.add(window)
            if self.taskbar:
                self.taskbar.update_window_button(window, False)
    
    def restore_window_from_taskbar(self, window):
        """Restore a window from taskbar click"""
        if window in self.minimized_windows:
            # Window is minimized - restore it
            window.show()
            window.raise_()
            window.activateWindow()
            self.minimized_windows.remove(window)
            if self.taskbar:
                self.taskbar.update_window_button(window, True)
        elif window in self.windows:
            # Window is visible - bring to front
            self.raise_window(window)
            if self.taskbar:
                self.taskbar.update_window_button(window, True)
    
    def on_window_minimized(self, window):
        """Called when a window minimizes itself"""
        if window in self.windows:
            self.minimized_windows.add(window)
            if self.taskbar:
                self.taskbar.update_window_button(window, False)
    
    def on_window_restored(self, window):
        """Called when a window restores itself"""
        if window in self.minimized_windows:
            self.minimized_windows.remove(window)
            if self.taskbar:
                self.taskbar.update_window_button(window, True)
    
    def raise_window(self, window):
        """Bring a window to the front"""
        window.raise_()
        window.activateWindow()
        # Update taskbar button
        if self.taskbar:
            self.taskbar.update_window_button(window, True)
        
    def remove_window(self, window):
        """Remove a window from the manager"""
        if window in self.windows:
            self.windows.remove(window)
            if window in self.minimized_windows:
                self.minimized_windows.remove(window)
            if self.taskbar:
                self.taskbar.remove_window_button(window)
            
    def close_window(self, window):
        """Close and remove a window"""
        if window in self.windows:
            self.remove_window(window)
            window.close()
            
    def close_all_windows(self):
        """Close all open windows"""
        for window in self.windows[:]:
            window.close()
        self.windows.clear()
        self.minimized_windows.clear()
        if self.taskbar:
            # Clear all taskbar buttons
            for btn in self.taskbar.window_buttons.values():
                btn.deleteLater()
            self.taskbar.window_buttons.clear()
        
    def get_window_count(self):
        """Get number of open windows"""
        return len(self.windows)