"""
Settings Manager for MiniOS
Handles loading, saving, and applying system settings
"""

import json
import os
from PySide6.QtCore import QObject, Signal


class SettingsManager(QObject):
    """Central settings management"""
    
    # Signal emitted when settings change
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
        
    def load_settings(self):
        """Load settings from file or create defaults"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    saved = json.load(f)
                    # Merge with defaults to ensure all keys exist
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
    
    def apply_settings_to_app(self, app):
        """Apply all settings to the application"""
        # Apply theme
        theme = self.get('appearance.theme', 'dark')
        self.apply_theme(app, theme)
        
        # Apply font size
        font_size = self.get('appearance.font_size', 13)
        self.apply_font_size(app, font_size)
    
    def apply_theme(self, app, theme):
        """Apply theme to the application"""
        if theme == 'dark':
            app.setStyleSheet("""
                QMainWindow, QWidget {
                    background: #000000;
                }
            """)
        elif theme == 'light':
            app.setStyleSheet("""
                QMainWindow, QWidget {
                    background: #ffffff;
                }
                QLabel { color: #000000; }
            """)
        # More themes can be added
    
    def apply_font_size(self, app, size):
        """Apply font size to the application"""
        from PySide6.QtGui import QFont
        font = QFont("Segoe UI", size)
        app.setFont(font)