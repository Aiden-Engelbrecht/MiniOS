"""
Splash Screen module for MiniOS
Displays a professional loading screen during application startup
"""

import sys
import os
from PySide6.QtWidgets import QSplashScreen, QWidget, QVBoxLayout, QLabel, QProgressBar, QApplication
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QBrush, QLinearGradient


class MiniOSSplashScreen(QSplashScreen):
    """
    Custom splash screen for MiniOS with animated loading effect
    """
    
    def __init__(self):
        # Create a pixmap to draw on
        self.splash_pixmap = QPixmap(600, 400)
        self.splash_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Initialize the splash screen with the pixmap
        super().__init__(self.splash_pixmap)
        
        # Create the widget that will be rendered onto the splash
        self.splash_widget = QWidget()
        self.splash_widget.setFixedSize(600, 400)
        self.splash_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-radius: 15px;
            }
            QLabel {
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QProgressBar {
                border: none;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                height: 6px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00b4d8, stop:1 #0077b6);
                border-radius: 5px;
            }
        """)
        
        # Setup the UI
        self.setup_ui()
        
        # Render the widget to pixmap
        self.splash_widget.render(self.splash_pixmap)
        self.setPixmap(self.splash_pixmap)
        
        # Loading progress
        self.progress = 0
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_progress)
        self.loading_timer.start(50)  # Update every 50ms
        
    def setup_ui(self):
        """Setup the splash screen UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Logo/Title
        title_label = QLabel("MiniOS")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 36, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #00b4d8; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Next Generation Desktop Experience")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont("Segoe UI", 14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #8899aa;")
        layout.addWidget(subtitle_label)
        
        layout.addStretch()
        
        # Loading status
        self.status_label = QLabel("Initializing system...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet("color: #aabbcc;")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Version info
        version_label = QLabel("Version 0.1.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setFont(QFont("Segoe UI", 9))
        version_label.setStyleSheet("color: #667788;")
        layout.addWidget(version_label)
        
        self.splash_widget.setLayout(layout)
        
    def update_progress(self):
        """Update loading progress"""
        self.progress += 2
        
        # Update progress bar
        self.progress_bar.setValue(self.progress)
        
        # Update status text based on progress
        if self.progress <= 20:
            self.status_label.setText("Loading system components...")
        elif self.progress <= 40:
            self.status_label.setText("Initializing core services...")
        elif self.progress <= 60:
            self.status_label.setText("Loading user environment...")
        elif self.progress <= 80:
            self.status_label.setText("Starting desktop services...")
        elif self.progress <= 95:
            self.status_label.setText("Finalizing setup...")
        else:
            self.status_label.setText("Ready!")
        
        # Re-render the widget to update the pixmap
        self.splash_widget.render(self.splash_pixmap)
        self.setPixmap(self.splash_pixmap)
        
        # Finish loading when progress reaches 100%
        if self.progress >= 100:
            self.loading_timer.stop()
            self.status_label.setText("Loading complete!")
            QTimer.singleShot(500, self.close)
            
    def mousePressEvent(self, event):
        """Prevent clicking through splash screen"""
        pass