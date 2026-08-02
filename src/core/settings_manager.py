"""
Settings Manager for MiniOS
Handles loading, saving, and applying system settings
"""

import json
import os
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFont, QPalette, QColor


class SettingsManager(QObject):
    """Central settings management"""
    
    settingsChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self.config_path = os.path.join("data", "settings.json")
        self.default_settings = {
            "general": {
                "username": "minios_user",
                "language": "English (US)"
            },
            "appearance": {
                "theme": "dark",
                "font_size": 13
            },
            "system": {
                "auto_login": False,
                "show_clock": True
            }
        }
        self.settings = self.load_settings()
        self.current_theme = self.get('appearance.theme', 'dark')
        self.current_font_size = self.get('appearance.font_size', 13)
        
    def load_settings(self):
        """Load settings from file or create defaults"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    saved = json.load(f)
                    merged = self.default_settings.copy()
                    for section in merged:
                        if section in saved:
                            merged[section].update(saved[section])
                    return merged
            except:
                return self.default_settings
        else:
            self.save_settings(self.default_settings)
            return self.default_settings
    
    def save_settings(self, settings=None):
        """Save settings to file"""
        if settings is None:
            settings = self.settings
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(settings, f, indent=4)
    
    def get(self, key, default=None):
        """Get a setting value"""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
    
    def set(self, key, value):
        """Set a setting value and save"""
        keys = key.split('.')
        config = self.settings
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_settings()
        self.settingsChanged.emit()
    
    def apply_theme_to_app(self, app, theme):
        """Apply theme to the entire application"""
        self.current_theme = theme
        
        if theme == "dark":
            # DARK THEME - Original MiniOS look
            app.setStyleSheet("""
                /* Global dark theme */
                QMainWindow, QWidget {
                    background-color: #000000;
                    color: #cccccc;
                }
                QLabel {
                    color: #888888;
                    background: transparent;
                }
                QPushButton {
                    background-color: #1a1a1a;
                    border: 1px solid #2a2a2a;
                    color: #888888;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                    color: #ffffff;
                }
                QLineEdit, QTextEdit {
                    background-color: #1a1a1a;
                    border: 1px solid #2a2a2a;
                    color: #888888;
                    padding: 5px;
                }
                QListWidget {
                    background-color: #0d0d0d;
                    color: #888888;
                    border: none;
                }
                QListWidget::item:selected {
                    background-color: #2a2a2a;
                    color: #ffffff;
                }
                QMenu {
                    background-color: #0a0a0a;
                    border: 1px solid #1a1a1a;
                    color: #cccccc;
                }
                QMenu::item:selected {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                QFrame {
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    background-color: #0d0d0d;
                    width: 10px;
                }
                QScrollBar::handle:vertical {
                    background-color: #2a2a2a;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #3a3a3a;
                }
                QTabWidget::pane {
                    background-color: #0d0d0d;
                    border: 1px solid #1a1a1a;
                }
                QTabBar::tab {
                    background-color: #0d0d0d;
                    color: #888888;
                    padding: 5px 10px;
                }
                QTabBar::tab:selected {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
            """)
            
            # Set dark palette
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(204, 204, 204))
            palette.setColor(QPalette.ColorRole.Base, QColor(13, 13, 13))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(20, 20, 20))
            palette.setColor(QPalette.ColorRole.Text, QColor(204, 204, 204))
            palette.setColor(QPalette.ColorRole.Button, QColor(26, 26, 26))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(204, 204, 204))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 42, 42))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            app.setPalette(palette)
            
        else:
            # LIGHT THEME
            app.setStyleSheet("""
                /* Light theme */
                QMainWindow, QWidget {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QLabel {
                    color: #555555;
                    background: transparent;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    border: 1px solid #cccccc;
                    color: #333333;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                    color: #000000;
                }
                QLineEdit, QTextEdit {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    color: #333333;
                    padding: 5px;
                }
                QListWidget {
                    background-color: #f0f0f0;
                    color: #333333;
                    border: none;
                }
                QListWidget::item:selected {
                    background-color: #d0d0d0;
                    color: #000000;
                }
                QMenu {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    color: #333333;
                }
                QMenu::item:selected {
                    background-color: #d0d0d0;
                    color: #000000;
                }
                QFrame {
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    background-color: #f0f0f0;
                    width: 10px;
                }
                QScrollBar::handle:vertical {
                    background-color: #cccccc;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #bbbbbb;
                }
                QTabWidget::pane {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                }
                QTabBar::tab {
                    background-color: #e8e8e8;
                    color: #555555;
                    padding: 5px 10px;
                }
                QTabBar::tab:selected {
                    background-color: #f0f0f0;
                    color: #000000;
                }
            """)
            
            # Set light palette
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(50, 50, 50))
            palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
            palette.setColor(QPalette.ColorRole.Text, QColor(50, 50, 50))
            palette.setColor(QPalette.ColorRole.Button, QColor(230, 230, 230))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(50, 50, 50))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(200, 200, 200))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
            app.setPalette(palette)
        
        # Update all top-level widgets
        for widget in app.topLevelWidgets():
            widget.update()
    
    def apply_font_size_to_app(self, app, size):
        """Apply font size to the entire application"""
        self.current_font_size = size
        font = QFont("Segoe UI", size)
        app.setFont(font)
        
        # Update all widgets
        for widget in app.allWidgets():
            widget.setFont(font)
    
    def apply_all_settings(self, app):
        """Apply all settings to the application"""
        theme = self.get('appearance.theme', 'dark')
        font_size = self.get('appearance.font_size', 13)
        
        self.apply_theme_to_app(app, theme)
        self.apply_font_size_to_app(app, font_size)