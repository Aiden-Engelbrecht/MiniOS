"""
Login Screen module for MiniOS - Minimal Black Edition
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QKeyEvent


class LoginScreen(QWidget):
    """
    Minimal black login screen
    """
    
    # Signal emitted when login is successful
    loginSuccessful = Signal(str)  # emits username
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setFocus()
        
    def setup_ui(self):
        """Setup the login interface"""
        # Pure black background
        self.setStyleSheet("""
            QWidget {
                background: #000000;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
            }
            QLineEdit {
                background: #111111;
                border: 1px solid #222222;
                border-radius: 4px;
                color: #ffffff;
                padding: 10px 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #444444;
            }
            QPushButton {
                background: #111111;
                border: 1px solid #222222;
                border-radius: 4px;
                color: #ffffff;
                padding: 10px 30px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: #1a1a1a;
                border: 1px solid #333333;
            }
            QPushButton:pressed {
                background: #0a0a0a;
            }
            QFrame#divider {
                background: #1a1a1a;
                max-height: 1px;
                min-height: 1px;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Center container
        center_widget = QWidget()
        center_widget.setStyleSheet("background: #000000;")
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(50, 50, 50, 50)
        center_layout.setSpacing(40)
        
        # Spacer to center vertically
        center_layout.addStretch()
        
        # Logo/Title
        title = QLabel("minios")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 36, QFont.Weight.Light))
        title.setStyleSheet("color: #ffffff; letter-spacing: 10px;")
        center_layout.addWidget(title)
        
        center_layout.addSpacing(10)
        
        # Subtitle
        subtitle = QLabel("secure login")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 12, QFont.Weight.Light))
        subtitle.setStyleSheet("color: #444444; letter-spacing: 4px;")
        center_layout.addWidget(subtitle)
        
        center_layout.addSpacing(40)
        
        # Login form container
        form_container = QWidget()
        form_container.setStyleSheet("background: transparent;")
        form_container.setMaximumWidth(400)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Username field
        username_label = QLabel("username")
        username_label.setFont(QFont("Segoe UI", 10))
        username_label.setStyleSheet("color: #666666; letter-spacing: 2px;")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("enter username")
        self.username_input.setMinimumHeight(45)
        self.username_input.returnPressed.connect(self.attempt_login)
        form_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("password")
        password_label.setFont(QFont("Segoe UI", 10))
        password_label.setStyleSheet("color: #666666; letter-spacing: 2px;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.returnPressed.connect(self.attempt_login)
        form_layout.addWidget(self.password_input)
        
        # Error message (hidden by default)
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setFont(QFont("Segoe UI", 10))
        self.error_label.setStyleSheet("color: #ff4444; letter-spacing: 1px;")
        self.error_label.setVisible(False)
        form_layout.addWidget(self.error_label)
        
        # Login button
        form_layout.addSpacing(10)
        
        login_button = QPushButton("login")
        login_button.setMinimumHeight(45)
        login_button.clicked.connect(self.attempt_login)
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        form_layout.addWidget(login_button)
        
        form_container.setLayout(form_layout)
        
        # Center the form
        form_wrapper = QHBoxLayout()
        form_wrapper.addStretch()
        form_wrapper.addWidget(form_container)
        form_wrapper.addStretch()
        center_layout.addLayout(form_wrapper)
        
        center_layout.addStretch()
        
        # Footer
        footer = QLabel("v0.1.0")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setFont(QFont("Segoe UI", 9))
        footer.setStyleSheet("color: #222222;")
        center_layout.addWidget(footer)
        
        center_widget.setLayout(center_layout)
        main_layout.addWidget(center_widget)
        
        self.setLayout(main_layout)
        
        # Auto-focus username
        QTimer.singleShot(100, self.username_input.setFocus)
        
    def attempt_login(self):
        """Validate credentials and emit signal if successful"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Simple validation - accept any non-empty username/password
        if not username:
            self.show_error("username required")
            return
        
        if not password:
            self.show_error("password required")
            return
        
        # For now, accept any credentials (we'll add real auth later)
        # In a real system, you'd check against a user database
        if len(username) >= 3 and len(password) >= 3:
            self.error_label.setVisible(False)
            print(f"login successful: {username}")
            self.loginSuccessful.emit(username)
        else:
            self.show_error("invalid credentials")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def show_error(self, message):
        """Display an error message"""
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        # Auto-hide after 3 seconds
        QTimer.singleShot(3000, lambda: self.error_label.setVisible(False))
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle escape key to clear fields"""
        if event.key() == Qt.Key.Key_Escape:
            self.username_input.clear()
            self.password_input.clear()
            self.error_label.setVisible(False)
            self.username_input.setFocus()
        super().keyPressEvent(event)
    
    def clear_fields(self):
        """Clear all input fields"""
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.setVisible(False)
        self.username_input.setFocus()
        
    def showEvent(self, event):
        """When the login screen is shown, focus the username field"""
        super().showEvent(event)
        QTimer.singleShot(100, self.username_input.setFocus)