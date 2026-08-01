"""
Sample application content for MiniOS
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SampleAppContent(QWidget):
    """Sample content for a window - fills the entire space"""
    
    def __init__(self, app_name="Application"):
        super().__init__()
        self.app_name = app_name
        self.setup_ui()
        
    def setup_ui(self):
        # Make this widget expand to fill parent
        self.setSizePolicy(
            self.sizePolicy().Policy.Expanding,
            self.sizePolicy().Policy.Expanding
        )
        
        self.setStyleSheet("""
            QWidget {
                background: #0d0d0d;
            }
            QLabel {
                color: #888888;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
            }
            QPushButton {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 10px 20px;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
            }
        """)
        
        # Main layout - with padding for content
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # App title
        title = QLabel(f"{self.app_name}")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Light))
        title.setStyleSheet("color: #cccccc; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Divider
        divider = QLabel("— — —")
        divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        divider.setStyleSheet("color: #1a1a1a; font-size: 16px;")
        layout.addWidget(divider)
        
        # Description
        desc = QLabel(f"This is the {self.app_name} application.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setFont(QFont("Segoe UI", 13))
        desc.setStyleSheet("color: #666666;")
        layout.addWidget(desc)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet("color: #444444;")
        layout.addWidget(self.status_label)
        
        # Buttons - centered
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(15)
        
        btn1 = QPushButton("Click Me")
        btn1.clicked.connect(lambda: self.status_label.setText("Button clicked!"))
        button_layout.addWidget(btn1)
        
        btn2 = QPushButton("Reset")
        btn2.clicked.connect(lambda: self.status_label.setText("Ready"))
        button_layout.addWidget(btn2)
        
        layout.addLayout(button_layout)
        
        # Push everything up
        layout.addStretch()
        
        self.setLayout(layout)