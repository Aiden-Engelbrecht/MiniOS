"""
Image Viewer Application for MiniOS
Simple image viewer with open and zoom capabilities
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont, QImage, QPainter
from PySide6.QtCore import QRect


class ImageViewerWidget(QWidget):
    """Image viewer application widget"""
    
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.current_path = None
        self.zoom_factor = 1.0
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #0d0d0d;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #888888;
                background: transparent;
            }
            QLabel#image_label {
                background: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 4px;
            }
            QPushButton {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #2a2a2a;
                color: #ffffff;
            }
            QFrame#separator {
                background: #1a1a1a;
                max-height: 1px;
                min-height: 1px;
            }
            QScrollArea {
                background: #0a0a0a;
                border: none;
            }
            QScrollBar:vertical {
                background: #0d0d0d;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #2a2a2a;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3a3a3a;
            }
            QScrollBar:horizontal {
                background: #0d0d0d;
                height: 10px;
            }
            QScrollBar::handle:horizontal {
                background: #2a2a2a;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #3a3a3a;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        self.open_btn = QPushButton("📂 Open")
        self.open_btn.setFixedHeight(32)
        self.open_btn.clicked.connect(self.open_image)
        toolbar.addWidget(self.open_btn)
        
        self.zoom_in_btn = QPushButton("🔍+")
        self.zoom_in_btn.setFixedHeight(32)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("🔍-")
        self.zoom_out_btn.setFixedHeight(32)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar.addWidget(self.zoom_out_btn)
        
        self.zoom_fit_btn = QPushButton("Fit")
        self.zoom_fit_btn.setFixedHeight(32)
        self.zoom_fit_btn.clicked.connect(self.zoom_fit)
        toolbar.addWidget(self.zoom_fit_btn)
        
        toolbar.addStretch()
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet("color: #444444; font-size: 11px;")
        toolbar.addWidget(self.zoom_label)
        
        self.file_label = QLabel("No image loaded")
        self.file_label.setStyleSheet("color: #444444; font-size: 11px;")
        toolbar.addWidget(self.file_label)
        
        layout.addLayout(toolbar)
        
        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        # Scroll area for image
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Image label inside scroll area
        self.image_label = QLabel()
        self.image_label.setObjectName("image_label")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setText("No image loaded\n\nClick 'Open' to select an image")
        self.image_label.setStyleSheet("""
            QLabel {
                color: #444444;
                font-size: 14px;
                background: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 4px;
            }
        """)
        
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area, 1)
        
        self.setLayout(layout)
        
    def open_image(self):
        """Open an image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.svg);;All Files (*)"
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """Load an image from file path"""
        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                QMessageBox.warning(self, "Error", "Could not load image file")
                return
            
            self.current_image = pixmap
            self.current_path = file_path
            self.zoom_factor = 1.0
            self.update_display()
            
            # Update file label
            import os
            filename = os.path.basename(file_path)
            self.file_label.setText(filename)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open image:\n{str(e)}")
    
    def update_display(self):
        """Update the displayed image with current zoom"""
        if self.current_image is None:
            return
        
        # Calculate scaled size
        scaled_width = int(self.current_image.width() * self.zoom_factor)
        scaled_height = int(self.current_image.height() * self.zoom_factor)
        
        # Scale image
        scaled_pixmap = self.current_image.scaled(
            scaled_width, scaled_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setFixedSize(scaled_pixmap.size())
        
        # Update zoom label
        self.zoom_label.setText(f"{int(self.zoom_factor * 100)}%")
    
    def zoom_in(self):
        """Zoom in by 10%"""
        if self.current_image is None:
            return
        self.zoom_factor = min(self.zoom_factor + 0.1, 5.0)
        self.update_display()
    
    def zoom_out(self):
        """Zoom out by 10%"""
        if self.current_image is None:
            return
        self.zoom_factor = max(self.zoom_factor - 0.1, 0.1)
        self.update_display()
    
    def zoom_fit(self):
        """Fit image to window"""
        if self.current_image is None:
            return
        
        # Get scroll area size
        viewport_size = self.scroll_area.viewport().size()
        
        # Calculate zoom to fit
        width_ratio = viewport_size.width() / self.current_image.width()
        height_ratio = viewport_size.height() / self.current_image.height()
        self.zoom_factor = min(width_ratio, height_ratio) * 0.9  # 90% to leave some margin
        
        self.update_display()
    
    def resizeEvent(self, event):
        """Handle window resize to update fit"""
        super().resizeEvent(event)
        # If zoom is set to fit, update on resize
        # Simple: we don't auto-fit on resize to avoid confusion
    
    def dragEnterEvent(self, event):
        """Accept drag events"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle dropped files"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.load_image(file_path)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_O and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.open_image()
        elif event.key() == Qt.Key.Key_Plus:
            self.zoom_in()
        elif event.key() == Qt.Key.Key_Minus:
            self.zoom_out()
        elif event.key() == Qt.Key.Key_0:
            self.zoom_fit()
        elif event.key() == Qt.Key.Key_F and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.zoom_fit()
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle close event"""
        event.accept()