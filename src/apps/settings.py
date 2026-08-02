"""
Settings Application for MiniOS
System preferences and configuration
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QListWidget, QListWidgetItem,
    QStackedWidget, QSlider, QComboBox,
    QLineEdit, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.settings_manager import SettingsManager


class SettingsWidget(QWidget):
    """Settings application widget"""
    
    settingsApplied = Signal()
    
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.desktop = None
        self.setup_ui()
        self.load_settings()
        
    def set_desktop(self, desktop):
        """Set the desktop reference for system actions"""
        self.desktop = desktop
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #0d0d0d;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #cccccc;
            }
            QLabel {
                color: #888888;
                background: transparent;
            }
            QLabel#title {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
            QLabel#section_title {
                color: #cccccc;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 0;
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
            QPushButton#apply_btn {
                background: #2a4a2a;
                border: 1px solid #3a5a3a;
                color: #88ff88;
            }
            QPushButton#apply_btn:hover {
                background: #3a5a3a;
            }
            QPushButton#danger_btn {
                background: #4a2a2a;
                border: 1px solid #5a3a3a;
                color: #ff8888;
            }
            QPushButton#danger_btn:hover {
                background: #5a3a3a;
            }
            QListWidget {
                background: #0d0d0d;
                border: none;
                color: #888888;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 15px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #1a1a1a;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background: #2a2a2a;
                color: #ffffff;
            }
            QFrame#separator {
                background: #1a1a1a;
                max-height: 1px;
                min-height: 1px;
            }
            QFrame#content_frame {
                background: #0d0d0d;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
                padding: 10px;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #1a1a1a;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #888888;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QComboBox {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 5px 10px;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 1px solid #3a3a3a;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                color: #888888;
                selection-background-color: #2a2a2a;
            }
            QLineEdit {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 8px 12px;
                font-size: 13px;
            }
        """)
        
        # Main layout
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Left sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(2)
        
        title = QLabel("Settings")
        title.setObjectName("title")
        sidebar_layout.addWidget(title)
        
        sep = QFrame()
        sep.setObjectName("separator")
        sidebar_layout.addWidget(sep)
        
        self.category_list = QListWidget()
        self.category_list.setFixedWidth(180)
        categories = [
            ("General", "⚙"),
            ("Appearance", "🎨"),
            ("System", "💻"),
            ("About", "ℹ")
        ]
        for name, icon in categories:
            item = QListWidgetItem(f"{icon}  {name}")
            self.category_list.addItem(item)
        self.category_list.setCurrentRow(0)
        self.category_list.itemClicked.connect(self.switch_category)
        sidebar_layout.addWidget(self.category_list)
        
        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)
        layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        
        self.general_page = self.create_general_page()
        self.appearance_page = self.create_appearance_page()
        self.system_page = self.create_system_page()
        self.about_page = self.create_about_page()
        
        self.content_stack.addWidget(self.general_page)
        self.content_stack.addWidget(self.appearance_page)
        self.content_stack.addWidget(self.system_page)
        self.content_stack.addWidget(self.about_page)
        
        layout.addWidget(self.content_stack, 1)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #444444; font-size: 11px; padding: 5px 10px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def load_settings(self):
        """Load settings from manager"""
        username = self.settings_manager.get('general.username', 'minios_user')
        self.username_input.setText(username)
        
        lang = self.settings_manager.get('general.language', 'English (US)')
        index = self.lang_combo.findText(lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        
        theme = self.settings_manager.get('appearance.theme', 'dark')
        index = self.theme_combo.findText(theme.capitalize())
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        font_size = self.settings_manager.get('appearance.font_size', 13)
        self.font_slider.setValue(font_size)
        self.font_size_label.setText(f"{font_size}px")
        
    def switch_category(self, item):
        index = self.category_list.row(item)
        self.content_stack.setCurrentIndex(index)
        
    def create_general_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        name_label = QLabel("Username")
        name_label.setObjectName("section_title")
        layout.addWidget(name_label)
        
        self.username_input = QLineEdit()
        self.username_input.setMaximumWidth(250)
        layout.addWidget(self.username_input)
        
        lang_label = QLabel("Language")
        lang_label.setObjectName("section_title")
        layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English (US)", "Spanish", "French", "German", "Japanese"])
        self.lang_combo.setMaximumWidth(200)
        layout.addWidget(self.lang_combo)
        
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        apply_btn = QPushButton("Apply Changes")
        apply_btn.setObjectName("apply_btn")
        apply_btn.clicked.connect(self.apply_general_settings)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_appearance_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        theme_label = QLabel("Theme")
        theme_label.setObjectName("section_title")
        layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setMaximumWidth(200)
        layout.addWidget(self.theme_combo)
        
        font_label = QLabel("Font Size")
        font_label.setObjectName("section_title")
        layout.addWidget(font_label)
        
        font_layout = QHBoxLayout()
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(10, 20)
        self.font_slider.setValue(13)
        self.font_slider.setMaximumWidth(200)
        font_layout.addWidget(self.font_slider)
        
        self.font_size_label = QLabel("13px")
        self.font_size_label.setStyleSheet("color: #888888;")
        font_layout.addWidget(self.font_size_label)
        
        self.font_slider.valueChanged.connect(
            lambda v: self.font_size_label.setText(f"{v}px")
        )
        layout.addLayout(font_layout)
        
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        apply_btn = QPushButton("Apply Changes")
        apply_btn.setObjectName("apply_btn")
        apply_btn.clicked.connect(self.apply_appearance_settings)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_system_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        info_label = QLabel("System Information")
        info_label.setObjectName("section_title")
        layout.addWidget(info_label)
        
        info_frame = QFrame()
        info_frame.setObjectName("content_frame")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        
        username = self.settings_manager.get('general.username', 'minios_user')
        info_items = [
            ("OS:", "MiniOS 1.0"),
            ("Kernel:", "minios-kernel 3.7.1"),
            ("Architecture:", "x86_64"),
            ("Python:", "3.13+"),
            ("UI Framework:", "PySide6"),
            ("User:", username)
        ]
        
        for label, value in info_items:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(120)
            lbl.setStyleSheet("color: #666666;")
            val = QLabel(value)
            val.setStyleSheet("color: #aaaaaa;")
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            info_layout.addLayout(row)
        
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        actions_label = QLabel("System Actions")
        actions_label.setObjectName("section_title")
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("danger_btn")
        logout_btn.clicked.connect(self.logout_system)
        actions_layout.addWidget(logout_btn)
        
        shutdown_btn = QPushButton("Shutdown")
        shutdown_btn.setObjectName("danger_btn")
        shutdown_btn.clicked.connect(self.shutdown_system)
        actions_layout.addWidget(shutdown_btn)
        
        restart_btn = QPushButton("Restart")
        restart_btn.clicked.connect(self.restart_system)
        actions_layout.addWidget(restart_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_about_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        title = QLabel("About MiniOS")
        title.setObjectName("section_title")
        title.setStyleSheet("font-size: 24px; color: #ffffff;")
        layout.addWidget(title)
        
        name = QLabel("minios")
        name.setStyleSheet("""
            font-size: 48px;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
            letter-spacing: 8px;
        """)
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)
        
        version = QLabel("Version 1.0")
        version.setStyleSheet("color: #666666; font-size: 16px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        desc = QLabel(
            "A simulated desktop operating system built with Python and PySide6.\n"
            "Minimal, clean, and fully functional."
        )
        desc.setStyleSheet("color: #888888; font-size: 13px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        credits = QLabel(
            "© 2026 MiniOS Corp.\n"
            "Built with ❤️ by the MiniOS Team"
        )
        credits.setStyleSheet("color: #444444; font-size: 11px;")
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credits)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def apply_general_settings(self):
        username = self.username_input.text().strip()
        lang = self.lang_combo.currentText()
        
        if not username:
            QMessageBox.warning(self, "Error", "Username cannot be empty")
            return
        
        self.settings_manager.set('general.username', username)
        self.settings_manager.set('general.language', lang)
        
        self.status_label.setText(f"✓ Settings saved")
        self.status_label.setStyleSheet("color: #88ff88; font-size: 11px; padding: 5px 10px;")
        
        QMessageBox.information(
            self, "Settings Applied",
            f"Settings updated!\n\nUsername: {username}\nLanguage: {lang}\n\n(Changes will take effect after restart)"
        )
        
        self.settingsApplied.emit()
    
    def apply_appearance_settings(self):
        theme = self.theme_combo.currentText().lower()
        font_size = self.font_slider.value()
        
        # Save settings
        self.settings_manager.set('appearance.theme', theme)
        self.settings_manager.set('appearance.font_size', font_size)
        
        # Apply to the ENTIRE application
        app = QApplication.instance()
        self.settings_manager.apply_theme_to_app(app, theme)
        self.settings_manager.apply_font_size_to_app(app, font_size)
        
        self.status_label.setText(f"✓ Theme: {theme.capitalize()}, Font Size: {font_size}px")
        self.status_label.setStyleSheet("color: #88ff88; font-size: 11px; padding: 5px 10px;")
        
        QMessageBox.information(
            self, "Settings Applied",
            f"Theme: {theme.capitalize()}\nFont Size: {font_size}px\n\nChanges applied to entire system!"
        )
        
        self.settingsApplied.emit()
    
    def logout_system(self):
        reply = QMessageBox.question(
            self, "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.desktop:
                self.desktop.logout()
            else:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'logout'):
                        parent.logout()
                        break
                    parent = parent.parent()
    
    def shutdown_system(self):
        reply = QMessageBox.question(
            self, "Shutdown",
            "Are you sure you want to shutdown the system?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.desktop:
                self.desktop.shutdown()
            else:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'shutdown'):
                        parent.shutdown()
                        break
                    parent = parent.parent()
    
    def restart_system(self):
        reply = QMessageBox.question(
            self, "Restart",
            "Are you sure you want to restart the system?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.desktop:
                self.desktop.logout()
            else:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'logout'):
                        parent.logout()
                        break
                    parent = parent.parent()
    
    def showEvent(self, event):
        self.load_settings()
        super().showEvent(event)