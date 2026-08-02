"""
Settings Manager for MiniOS
Handles loading, saving, and applying system settings
"""

import json
import os
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFont


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
    
    def get_theme_stylesheet(self, theme):
        """Get the stylesheet for a theme"""
        if theme == "dark":
            return """
                QMainWindow, QWidget {
                    background: #000000;
                    color: #cccccc;
                }
                QLabel {
                    color: #888888;
                }
                QPushButton {
                    background: #1a1a1a;
                    border: 1px solid #2a2a2a;
                    color: #888888;
                }
                QPushButton:hover {
                    background: #2a2a2a;
                    color: #ffffff;
                }
                QLineEdit, QTextEdit {
                    background: #1a1a1a;
                    border: 1px solid #2a2a2a;
                    color: #888888;
                }
                QListWidget {
                    background: #0d0d0d;
                    color: #888888;
                }
                QListWidget::item:selected {
                    background: #2a2a2a;
                    color: #ffffff;
                }
                QMenu {
                    background: #0a0a0a;
                    border: 1px solid #1a1a1a;
                    color: #cccccc;
                }
                QMenu::item:selected {
                    background: #1a1a1a;
                    color: #ffffff;
                }
                QFrame {
                    background: transparent;
                }
            """
        else:  # light
            return """
                QMainWindow, QWidget {
                    background: #f0f0f0;
                    color: #333333;
                }
                QLabel {
                    color: #666666;
                }
                QPushButton {
                    background: #e0e0e0;
                    border: 1px solid #cccccc;
                    color: #333333;
                }
                QPushButton:hover {
                    background: #d0d0d0;
                    color: #000000;
                }
                QLineEdit, QTextEdit {
                    background: #ffffff;
                    border: 1px solid #cccccc;
                    color: #333333;
                }
                QListWidget {
                    background: #f0f0f0;
                    color: #333333;
                }
                QListWidget::item:selected {
                    background: #cccccc;
                    color: #000000;
                }
                QMenu {
                    background: #f0f0f0;
                    border: 1px solid #cccccc;
                    color: #333333;
                }
                QMenu::item:selected {
                    background: #d0d0d0;
                    color: #000000;
                }
                QFrame {
                    background: transparent;
                }
            """
    
    def apply_theme_to_app(self, app, theme):
        """Apply theme to the entire application"""
        self.current_theme = theme
        stylesheet = self.get_theme_stylesheet(theme)
        app.setStyleSheet(stylesheet)
        
        # Also update all top-level widgets
        for widget in app.topLevelWidgets():
            widget.setStyleSheet(stylesheet)
    
    def apply_font_size_to_app(self, app, size):
        """Apply font size to the entire application"""
        self.current_font_size = size
        font = QFont("Segoe UI", size)
        app.setFont(font)
    
    def apply_all_settings(self, app):
        """Apply all settings to the application"""
        theme = self.get('appearance.theme', 'dark')
        font_size = self.get('appearance.font_size', 13)
        
        self.apply_theme_to_app(app, theme)
        self.apply_font_size_to_app(app, font_size)