"""
Calendar Application for MiniOS
Simple calendar with month navigation
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont


class CalendarWidget(QWidget):
    """Calendar application widget"""
    
    def __init__(self):
        super().__init__()
        self.current_date = QDate.currentDate()
        self.setup_ui()
        self.update_calendar()
        
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
            QLabel#header {
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel#day_name {
                color: #666666;
                font-size: 12px;
                font-weight: bold;
            }
            QLabel#day_number {
                color: #cccccc;
                font-size: 16px;
            }
            QLabel#day_number_today {
                color: #00ff41;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel#day_number_other {
                color: #444444;
                font-size: 14px;
            }
            QPushButton {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 8px 16px;
                font-size: 14px;
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
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with navigation
        header_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(35, 35)
        self.prev_btn.clicked.connect(self.prev_month)
        header_layout.addWidget(self.prev_btn)
        
        self.month_label = QLabel()
        self.month_label.setObjectName("header")
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.month_label, 1)
        
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(35, 35)
        self.next_btn.clicked.connect(self.next_month)
        header_layout.addWidget(self.next_btn)
        
        layout.addLayout(header_layout)
        
        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        # Today button
        today_layout = QHBoxLayout()
        today_layout.addStretch()
        self.today_btn = QPushButton("Today")
        self.today_btn.clicked.connect(self.go_today)
        today_layout.addWidget(self.today_btn)
        layout.addLayout(today_layout)
        
        # Calendar grid
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(8)
        layout.addLayout(self.calendar_grid)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
    def update_calendar(self):
        """Update the calendar display"""
        # Clear existing grid
        while self.calendar_grid.count():
            item = self.calendar_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Update month label
        month_names = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        self.month_label.setText(f"{month_names[self.current_date.month() - 1]} {self.current_date.year()}")
        
        # Add day name headers
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, name in enumerate(day_names):
            label = QLabel(name)
            label.setObjectName("day_name")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.calendar_grid.addWidget(label, 0, i)
        
        # Get first day of month
        first_day = QDate(self.current_date.year(), self.current_date.month(), 1)
        days_in_month = first_day.daysInMonth()
        
        # Get day of week for first day (Monday = 1, Sunday = 7)
        day_of_week = first_day.dayOfWeek()
        # Convert to Monday-based (0 = Monday, 6 = Sunday)
        start_col = day_of_week - 1
        
        today = QDate.currentDate()
        
        # Add day numbers
        row = 1
        col = start_col
        
        for day in range(1, days_in_month + 1):
            date = QDate(self.current_date.year(), self.current_date.month(), day)
            
            label = QLabel(str(day))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Style the day
            if date == today:
                label.setObjectName("day_number_today")
                label.setStyleSheet("color: #00ff41; font-size: 16px; font-weight: bold;")
            elif date.month() == self.current_date.month():
                label.setObjectName("day_number")
                label.setStyleSheet("color: #cccccc; font-size: 16px;")
            else:
                label.setObjectName("day_number_other")
                label.setStyleSheet("color: #444444; font-size: 14px;")
            
            self.calendar_grid.addWidget(label, row, col)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
        
        # Add empty cells for remaining days in last week
        while col <= 6:
            label = QLabel("")
            self.calendar_grid.addWidget(label, row, col)
            col += 1
        
        # Show current date info
        self.update_status()
        
    def update_status(self):
        """Update status with current date info"""
        # Status handled by the label at bottom
        pass
        
    def prev_month(self):
        """Go to previous month"""
        self.current_date = self.current_date.addMonths(-1)
        self.update_calendar()
        
    def next_month(self):
        """Go to next month"""
        self.current_date = self.current_date.addMonths(1)
        self.update_calendar()
        
    def go_today(self):
        """Go to today's date"""
        self.current_date = QDate.currentDate()
        self.update_calendar()