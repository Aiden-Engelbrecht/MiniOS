"""
Weather Widget for MiniOS
Desktop widget showing simulated weather conditions
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import random


class WeatherWidget(QWidget):
    """Desktop weather widget with simulated conditions"""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(280, 160)
        
        self.weather_data = {
            "temperature": 22,
            "condition": "Sunny",
            "humidity": 65,
            "wind_speed": 12,
            "icon": "☀️"
        }
        
        self.weather_conditions = [
            ("Sunny", "☀️", 20, 30),
            ("Partly Cloudy", "⛅", 15, 25),
            ("Cloudy", "☁️", 10, 20),
            ("Rainy", "🌧️", 5, 15),
            ("Stormy", "⛈️", 0, 10),
            ("Snowy", "❄️", -5, 5),
            ("Windy", "💨", 10, 20),
            ("Foggy", "🌫️", 5, 15)
        ]
        
        self.setup_ui()
        self.setup_timer()
        self.update_weather()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#container {
                background: rgba(13, 13, 13, 0.85);
                border: 1px solid #1a1a1a;
                border-radius: 12px;
                padding: 10px;
            }
            QLabel {
                color: #cccccc;
                background: transparent;
            }
            QLabel#temp {
                color: #ffffff;
                font-size: 28px;
                font-weight: bold;
            }
            QLabel#condition {
                color: #888888;
                font-size: 14px;
            }
            QLabel#details {
                color: #666666;
                font-size: 11px;
            }
            QLabel#icon {
                font-size: 40px;
            }
            QPushButton {
                background: transparent;
                border: none;
                color: #666666;
                font-size: 12px;
                padding: 2px 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #1a1a1a;
                color: #ffffff;
            }
            QComboBox {
                background: rgba(26, 26, 26, 0.8);
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 2px 8px;
                font-size: 11px;
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
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container
        container = QFrame()
        container.setObjectName("container")
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(15, 12, 15, 12)
        container_layout.setSpacing(6)
        
        # Top row - Location and controls
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        
        self.location_label = QLabel("🌍 MiniOS City")
        self.location_label.setStyleSheet("color: #666666; font-size: 11px;")
        top_row.addWidget(self.location_label)
        
        top_row.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(20, 20)
        self.refresh_btn.clicked.connect(self.update_weather)
        self.refresh_btn.setToolTip("Refresh weather")
        top_row.addWidget(self.refresh_btn)
        
        # Settings button
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(20, 20)
        self.settings_btn.clicked.connect(self.toggle_settings)
        self.settings_btn.setToolTip("Settings")
        top_row.addWidget(self.settings_btn)
        
        container_layout.addLayout(top_row)
        
        # Weather display row
        weather_row = QHBoxLayout()
        weather_row.setSpacing(15)
        
        # Icon
        self.icon_label = QLabel("☀️")
        self.icon_label.setObjectName("icon")
        weather_row.addWidget(self.icon_label)
        
        # Temperature and condition
        temp_layout = QVBoxLayout()
        temp_layout.setSpacing(2)
        
        self.temp_label = QLabel("22°C")
        self.temp_label.setObjectName("temp")
        temp_layout.addWidget(self.temp_label)
        
        self.condition_label = QLabel("Sunny")
        self.condition_label.setObjectName("condition")
        temp_layout.addWidget(self.condition_label)
        
        weather_row.addLayout(temp_layout)
        
        weather_row.addStretch()
        
        # Details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(2)
        details_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.humidity_label = QLabel("💧 65%")
        self.humidity_label.setObjectName("details")
        details_layout.addWidget(self.humidity_label)
        
        self.wind_label = QLabel("💨 12 km/h")
        self.wind_label.setObjectName("details")
        details_layout.addWidget(self.wind_label)
        
        weather_row.addLayout(details_layout)
        
        container_layout.addLayout(weather_row)
        
        # Settings panel (hidden by default)
        self.settings_panel = QWidget()
        self.settings_panel.setVisible(False)
        settings_layout = QHBoxLayout()
        settings_layout.setContentsMargins(0, 5, 0, 0)
        settings_layout.setSpacing(8)
        
        settings_layout.addWidget(QLabel("City:"))
        
        self.city_combo = QComboBox()
        self.city_combo.addItems([
            "MiniOS City", "Metropolis", "Cyber City", 
            "Neon District", "Silicon Valley", "Tokyo", "London", "New York"
        ])
        self.city_combo.currentTextChanged.connect(self.on_city_changed)
        settings_layout.addWidget(self.city_combo)
        
        settings_layout.addStretch()
        
        self.settings_panel.setLayout(settings_layout)
        container_layout.addWidget(self.settings_panel)
        
        container.setLayout(container_layout)
        layout.addWidget(container)
        
        self.setLayout(layout)
        
    def setup_timer(self):
        """Setup auto-refresh timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(30000)  # Update every 30 seconds
        
    def toggle_settings(self):
        """Toggle settings panel visibility"""
        self.settings_panel.setVisible(not self.settings_panel.isVisible())
        
        # Resize window to fit content
        if self.settings_panel.isVisible():
            self.setFixedSize(280, 190)
        else:
            self.setFixedSize(280, 160)
    
    def on_city_changed(self, city):
        """Handle city change"""
        self.location_label.setText(f"🌍 {city}")
        self.update_weather()
    
    def update_weather(self):
        """Update weather with random data"""
        # Get random weather condition
        condition_data = random.choice(self.weather_conditions)
        condition, icon, temp_min, temp_max = condition_data
        
        # Random temperature within range
        temperature = random.randint(temp_min, temp_max)
        
        # Random humidity
        humidity = random.randint(40, 85)
        
        # Random wind speed
        wind_speed = random.randint(5, 30)
        
        # Update data
        self.weather_data = {
            "temperature": temperature,
            "condition": condition,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "icon": icon
        }
        
        # Update UI
        self.update_display()
        
        # Update tooltip
        self.setToolTip(
            f"{condition}\nTemperature: {temperature}°C\n"
            f"Humidity: {humidity}%\nWind: {wind_speed} km/h"
        )
    
    def update_display(self):
        """Update the UI with current weather data"""
        # Temperature
        temp = self.weather_data["temperature"]
        self.temp_label.setText(f"{temp}°C")
        
        # Color temperature based on value
        if temp > 25:
            self.temp_label.setStyleSheet("color: #ff6b6b; font-size: 28px; font-weight: bold;")
        elif temp > 15:
            self.temp_label.setStyleSheet("color: #ffd93d; font-size: 28px; font-weight: bold;")
        elif temp > 5:
            self.temp_label.setStyleSheet("color: #66d9ef; font-size: 28px; font-weight: bold;")
        else:
            self.temp_label.setStyleSheet("color: #4a9eff; font-size: 28px; font-weight: bold;")
        
        # Condition
        self.condition_label.setText(self.weather_data["condition"])
        
        # Icon
        self.icon_label.setText(self.weather_data["icon"])
        
        # Humidity
        self.humidity_label.setText(f"💧 {self.weather_data['humidity']}%")
        
        # Wind
        self.wind_label.setText(f"💨 {self.weather_data['wind_speed']} km/h")
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def closeEvent(self, event):
        """Stop timer on close"""
        self.timer.stop()
        event.accept()