"""
Task Manager for MiniOS
View and manage running processes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QLineEdit,
    QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
import psutil
import os


class TaskManagerWidget(QWidget):
    """Task Manager application widget"""
    
    def __init__(self):
        super().__init__()
        self.processes = []
        self.setup_ui()
        self.setup_timer()
        self.refresh_processes()
        
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
            QLabel#title {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
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
            QPushButton#kill_btn {
                background: #4a2a2a;
                border: 1px solid #5a3a3a;
                color: #ff8888;
            }
            QPushButton#kill_btn:hover {
                background: #5a3a3a;
            }
            QPushButton#kill_btn:disabled {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                color: #444444;
            }
            QFrame#separator {
                background: #1a1a1a;
                max-height: 1px;
                min-height: 1px;
            }
            QTableWidget {
                background: #0d0d0d;
                border: 1px solid #1a1a1a;
                border-radius: 4px;
                color: #888888;
                gridline-color: #1a1a1a;
                font-size: 12px;
                outline: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background: #2a2a2a;
                color: #ffffff;
            }
            QHeaderView::section {
                background: #0d0d0d;
                color: #666666;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #1a1a1a;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget QTableCornerButton::section {
                background: #0d0d0d;
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
            QLineEdit {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 6px 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #3a3a3a;
            }
            QComboBox {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 5px 10px;
                font-size: 12px;
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
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Task Manager")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.count_label = QLabel("0 processes")
        self.count_label.setStyleSheet("color: #666666; font-size: 12px;")
        header_layout.addWidget(self.count_label)
        
        layout.addLayout(header_layout)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_processes)
        toolbar.addWidget(self.refresh_btn)
        
        self.kill_btn = QPushButton("✕ End Process")
        self.kill_btn.setObjectName("kill_btn")
        self.kill_btn.setEnabled(False)
        self.kill_btn.clicked.connect(self.kill_process)
        toolbar.addWidget(self.kill_btn)
        
        toolbar.addStretch()
        
        # Search
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #666666; font-size: 11px;")
        toolbar.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter processes...")
        self.search_input.setMaximumWidth(150)
        self.search_input.textChanged.connect(self.filter_processes)
        toolbar.addWidget(self.search_input)
        
        # Sort combo
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "CPU", "Memory", "PID"])
        self.sort_combo.currentIndexChanged.connect(self.refresh_processes)
        toolbar.addWidget(self.sort_combo)
        
        layout.addLayout(toolbar)
        
        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        # Process table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["PID", "Name", "CPU %", "Memory %", "Status"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Column widths
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def setup_timer(self):
        """Setup auto-refresh timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_processes)
        self.timer.start(3000)  # Update every 3 seconds
        
    def refresh_processes(self):
        """Refresh the process list"""
        try:
            self.processes = []
            sort_by = self.sort_combo.currentText().lower()
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    info = proc.info
                    info['cpu_percent'] = info.get('cpu_percent', 0) or 0
                    info['memory_percent'] = info.get('memory_percent', 0) or 0
                    self.processes.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort processes
            if sort_by == "name":
                self.processes.sort(key=lambda x: x['name'].lower() if x['name'] else '')
            elif sort_by == "cpu":
                self.processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            elif sort_by == "memory":
                self.processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            elif sort_by == "pid":
                self.processes.sort(key=lambda x: x['pid'])
            
            # Apply search filter
            self.filter_processes()
            
        except Exception as e:
            print(f"Error refreshing processes: {e}")
    
    def filter_processes(self):
        """Filter processes based on search text"""
        search_text = self.search_input.text().lower().strip()
        
        # Clear table
        self.table.setRowCount(0)
        
        filtered = self.processes
        if search_text:
            filtered = [p for p in self.processes if 
                       search_text in (p.get('name', '').lower() or '') or
                       str(p.get('pid', '')).startswith(search_text)]
        
        # Populate table
        self.table.setRowCount(len(filtered))
        
        for i, proc in enumerate(filtered):
            # PID
            pid_item = QTableWidgetItem(str(proc.get('pid', '')))
            pid_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, pid_item)
            
            # Name
            name_item = QTableWidgetItem(proc.get('name', 'Unknown'))
            self.table.setItem(i, 1, name_item)
            
            # CPU
            cpu = proc.get('cpu_percent', 0)
            cpu_item = QTableWidgetItem(f"{cpu:.1f}%")
            cpu_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if cpu > 50:
                cpu_item.setForeground(QColor(255, 107, 107))
            elif cpu > 20:
                cpu_item.setForeground(QColor(255, 217, 61))
            self.table.setItem(i, 2, cpu_item)
            
            # Memory
            mem = proc.get('memory_percent', 0)
            mem_item = QTableWidgetItem(f"{mem:.1f}%")
            mem_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if mem > 50:
                mem_item.setForeground(QColor(255, 107, 107))
            elif mem > 20:
                mem_item.setForeground(QColor(255, 217, 61))
            self.table.setItem(i, 3, mem_item)
            
            # Status
            status = proc.get('status', 'unknown')
            status_map = {
                'running': '🟢 Running',
                'sleeping': '💤 Sleeping',
                'disk-sleep': '💤 Sleeping',
                'stopped': '⏹ Stopped',
                'zombie': '🧟 Zombie',
                'idle': '💤 Idle',
                'unknown': '❓ Unknown'
            }
            status_item = QTableWidgetItem(status_map.get(status, status))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 4, status_item)
        
        # Update count
        self.count_label.setText(f"{len(filtered)} processes")
        
        # Reset selection
        self.kill_btn.setEnabled(False)
    
    def on_selection_changed(self):
        """Handle selection change"""
        selected = self.table.selectedItems()
        if selected:
            self.kill_btn.setEnabled(True)
        else:
            self.kill_btn.setEnabled(False)
    
    def kill_process(self):
        """Kill the selected process"""
        selected = self.table.selectedItems()
        if not selected:
            return
        
        # Get PID from the first column
        row = selected[0].row()
        pid_item = self.table.item(row, 0)
        if not pid_item:
            return
        
        pid = int(pid_item.text())
        name_item = self.table.item(row, 1)
        name = name_item.text() if name_item else "Unknown"
        
        # Confirm before killing
        reply = QMessageBox.question(
            self, "End Process",
            f"Are you sure you want to end the process:\n\n"
            f"Name: {name}\nPID: {pid}\n\n"
            f"This will forcefully terminate the process.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                process = psutil.Process(pid)
                process.terminate()  # Try graceful termination
                # Wait a moment then force kill if needed
                gone, alive = psutil.wait_procs([process], timeout=3)
                if alive:
                    process.kill()  # Force kill
                
                QMessageBox.information(
                    self, "Process Ended",
                    f"Process '{name}' (PID: {pid}) has been terminated."
                )
                self.refresh_processes()
                
            except psutil.NoSuchProcess:
                QMessageBox.warning(self, "Error", "Process no longer exists.")
                self.refresh_processes()
            except psutil.AccessDenied:
                QMessageBox.warning(self, "Error", "Permission denied. Cannot end this process.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to end process:\n{str(e)}")
    
    def closeEvent(self, event):
        """Stop timer on close"""
        self.timer.stop()
        event.accept()