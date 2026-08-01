"""
Splash Screen module for MiniOS - Minimal Black Edition
Clean, minimalist dark theme
"""

from PySide6.QtWidgets import QSplashScreen, QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap, QColor


class MiniOSSplashScreen(QSplashScreen):
    """
    Minimal black splash screen
    """
    
    loadingComplete = Signal()
    
    def __init__(self):
        pixmap = QPixmap(500, 300)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        super().__init__(pixmap)
        
        self.widget = QWidget()
        self.widget.setFixedSize(500, 300)
        self.widget.setStyleSheet("""
            QWidget {
                background: #000000;
                border: 1px solid #333333;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
            }
            QProgressBar {
                border: none;
                background-color: #1a1a1a;
                border-radius: 2px;
                height: 2px;
            }
            QProgressBar::chunk {
                background: #888888;
                border-radius: 2px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("minios")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Light))
        title.setStyleSheet("color: #ffffff; letter-spacing: 8px;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Status
        self.status = QLabel("initializing...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(QFont("Segoe UI", 10))
        self.status.setStyleSheet("color: #888888; letter-spacing: 2px;")
        layout.addWidget(self.status)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Version
        version = QLabel("v0.1.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setFont(QFont("Segoe UI", 9))
        version.setStyleSheet("color: #444444;")
        layout.addWidget(version)
        
        self.widget.setLayout(layout)
        
        self.widget.render(pixmap)
        self.setPixmap(pixmap)
        
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)
    
    def update_progress(self):
        self.progress += 2
        self.progress_bar.setValue(self.progress)
        
        if self.progress <= 20:
            self.status.setText("loading system...")
        elif self.progress <= 40:
            self.status.setText("initializing core...")
        elif self.progress <= 60:
            self.status.setText("loading services...")
        elif self.progress <= 80:
            self.status.setText("starting desktop...")
        elif self.progress <= 95:
            self.status.setText("finalizing...")
        else:
            self.status.setText("ready")
        
        pixmap = QPixmap(500, 300)
        pixmap.fill(Qt.GlobalColor.transparent)
        self.widget.render(pixmap)
        self.setPixmap(pixmap)
        
        if self.progress >= 100:
            self.timer.stop()
            self.status.setText("ready")
            self.loadingComplete.emit()
            QTimer.singleShot(400, self.close)
    
    def mousePressEvent(self, event):
        pass