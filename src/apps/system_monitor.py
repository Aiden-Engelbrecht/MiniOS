"""
System Monitor for MiniOS
Real-time CPU, memory, and disk usage
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QProgressBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import psutil
import os


class SystemMonitorWidget(QWidget):
    """System Monitor application widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_timer()
        self.update_stats()
        
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
            QLabel#value {
                color: #cccccc;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#info {
                color: #666666;
                font-size: 11px;
            }
            QFrame {
                background: transparent;
            }
            QFrame#card {
                background: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
                padding: 15px;
            }
            QProgressBar {
                border: none;
                background: #1a1a1a;
                border-radius: 4px;
                height: 8px;
            }
            QProgressBar::chunk {
                border-radius: 4px;
            }
            QProgressBar#cpu_chunk {
                background: #4a9eff;
            }
            QProgressBar::chunk#cpu_chunk {
                background: #4a9eff;
            }
            QProgressBar#memory_chunk {
                background: #66d9ef;
            }
            QProgressBar::chunk#memory_chunk {
                background: #66d9ef;
            }
            QProgressBar#disk_chunk {
                background: #ff6b6b;
            }
            QProgressBar::chunk#disk_chunk {
                background: #ff6b6b;
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
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 System Monitor")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.update_stats)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # CPU Card
        cpu_card = QFrame()
        cpu_card.setObjectName("card")
        cpu_layout = QVBoxLayout()
        
        cpu_header = QHBoxLayout()
        cpu_label = QLabel("CPU Usage")
        cpu_label.setObjectName("info")
        cpu_header.addWidget(cpu_label)
        cpu_header.addStretch()
        self.cpu_percent_label = QLabel("0%")
        self.cpu_percent_label.setObjectName("value")
        cpu_header.addWidget(self.cpu_percent_label)
        cpu_layout.addLayout(cpu_header)
        
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setObjectName("cpu_chunk")
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(0)
        self.cpu_bar.setTextVisible(False)
        cpu_layout.addWidget(self.cpu_bar)
        
        cpu_info = QHBoxLayout()
        self.cpu_cores_label = QLabel("Cores: 0")
        self.cpu_cores_label.setObjectName("info")
        cpu_info.addWidget(self.cpu_cores_label)
        cpu_info.addStretch()
        self.cpu_freq_label = QLabel("0 MHz")
        self.cpu_freq_label.setObjectName("info")
        cpu_info.addWidget(self.cpu_freq_label)
        cpu_layout.addLayout(cpu_info)
        
        cpu_card.setLayout(cpu_layout)
        layout.addWidget(cpu_card)
        
        # Memory Card
        memory_card = QFrame()
        memory_card.setObjectName("card")
        memory_layout = QVBoxLayout()
        
        memory_header = QHBoxLayout()
        memory_label = QLabel("Memory Usage")
        memory_label.setObjectName("info")
        memory_header.addWidget(memory_label)
        memory_header.addStretch()
        self.memory_percent_label = QLabel("0%")
        self.memory_percent_label.setObjectName("value")
        memory_header.addWidget(self.memory_percent_label)
        memory_layout.addLayout(memory_header)
        
        self.memory_bar = QProgressBar()
        self.memory_bar.setObjectName("memory_chunk")
        self.memory_bar.setRange(0, 100)
        self.memory_bar.setValue(0)
        self.memory_bar.setTextVisible(False)
        memory_layout.addWidget(self.memory_bar)
        
        memory_info = QHBoxLayout()
        self.memory_used_label = QLabel("Used: 0 MB")
        self.memory_used_label.setObjectName("info")
        memory_info.addWidget(self.memory_used_label)
        memory_info.addStretch()
        self.memory_total_label = QLabel("Total: 0 MB")
        self.memory_total_label.setObjectName("info")
        memory_info.addWidget(self.memory_total_label)
        memory_layout.addLayout(memory_info)
        
        memory_card.setLayout(memory_layout)
        layout.addWidget(memory_card)
        
        # Disk Card
        disk_card = QFrame()
        disk_card.setObjectName("card")
        disk_layout = QVBoxLayout()
        
        disk_header = QHBoxLayout()
        disk_label = QLabel("Disk Usage")
        disk_label.setObjectName("info")
        disk_header.addWidget(disk_label)
        disk_header.addStretch()
        self.disk_percent_label = QLabel("0%")
        self.disk_percent_label.setObjectName("value")
        disk_header.addWidget(self.disk_percent_label)
        disk_layout.addLayout(disk_header)
        
        self.disk_bar = QProgressBar()
        self.disk_bar.setObjectName("disk_chunk")
        self.disk_bar.setRange(0, 100)
        self.disk_bar.setValue(0)
        self.disk_bar.setTextVisible(False)
        disk_layout.addWidget(self.disk_bar)
        
        disk_info = QHBoxLayout()
        self.disk_used_label = QLabel("Used: 0 GB")
        self.disk_used_label.setObjectName("info")
        disk_info.addWidget(self.disk_used_label)
        disk_info.addStretch()
        self.disk_total_label = QLabel("Total: 0 GB")
        self.disk_total_label.setObjectName("info")
        disk_info.addWidget(self.disk_total_label)
        disk_layout.addLayout(disk_info)
        
        disk_card.setLayout(disk_layout)
        layout.addWidget(disk_card)
        
        # Network Card
        network_card = QFrame()
        network_card.setObjectName("card")
        network_layout = QVBoxLayout()
        
        network_header = QHBoxLayout()
        network_label = QLabel("Network")
        network_label.setObjectName("info")
        network_header.addWidget(network_label)
        network_header.addStretch()
        network_layout.addLayout(network_header)
        
        network_info = QHBoxLayout()
        self.network_sent_label = QLabel("⬆ Sent: 0 MB")
        self.network_sent_label.setObjectName("info")
        network_info.addWidget(self.network_sent_label)
        network_info.addStretch()
        self.network_recv_label = QLabel("⬇ Received: 0 MB")
        self.network_recv_label.setObjectName("info")
        network_info.addWidget(self.network_recv_label)
        network_layout.addLayout(network_info)
        
        network_card.setLayout(network_layout)
        layout.addWidget(network_card)
        
        # Footer
        footer = QHBoxLayout()
        self.uptime_label = QLabel("Uptime: 0s")
        self.uptime_label.setObjectName("info")
        footer.addWidget(self.uptime_label)
        footer.addStretch()
        self.processes_label = QLabel("Processes: 0")
        self.processes_label.setObjectName("info")
        footer.addWidget(self.processes_label)
        
        layout.addLayout(footer)
        
        self.setLayout(layout)
        
    def setup_timer(self):
        """Setup auto-refresh timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)  # Update every 2 seconds
        
        # Uptime timer
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        self.uptime_timer.start(1000)
        self.uptime_seconds = 0
        
    def update_stats(self):
        """Update all system stats"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.5)
            self.cpu_bar.setValue(int(cpu_percent))
            self.cpu_percent_label.setText(f"{cpu_percent:.1f}%")
            
            # CPU cores
            cpu_count = psutil.cpu_count()
            self.cpu_cores_label.setText(f"Cores: {cpu_count}")
            
            # CPU frequency
            try:
                freq = psutil.cpu_freq()
                if freq:
                    self.cpu_freq_label.setText(f"{freq.current:.0f} MHz")
            except:
                pass
            
            # Memory
            memory = psutil.virtual_memory()
            self.memory_bar.setValue(memory.percent)
            self.memory_percent_label.setText(f"{memory.percent:.1f}%")
            
            # Format memory sizes
            used_gb = memory.used / (1024**3)
            total_gb = memory.total / (1024**3)
            self.memory_used_label.setText(f"Used: {used_gb:.1f} GB")
            self.memory_total_label.setText(f"Total: {total_gb:.1f} GB")
            
            # Disk
            disk = psutil.disk_usage('/')
            self.disk_bar.setValue(disk.percent)
            self.disk_percent_label.setText(f"{disk.percent:.1f}%")
            
            # Format disk sizes
            used_gb = disk.used / (1024**3)
            total_gb = disk.total / (1024**3)
            self.disk_used_label.setText(f"Used: {used_gb:.1f} GB")
            self.disk_total_label.setText(f"Total: {total_gb:.1f} GB")
            
            # Network
            net = psutil.net_io_counters()
            sent_mb = net.bytes_sent / (1024**2)
            recv_mb = net.bytes_recv / (1024**2)
            self.network_sent_label.setText(f"⬆ Sent: {sent_mb:.1f} MB")
            self.network_recv_label.setText(f"⬇ Received: {recv_mb:.1f} MB")
            
            # Processes
            process_count = len(psutil.pids())
            self.processes_label.setText(f"Processes: {process_count}")
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            
    def update_uptime(self):
        """Update system uptime"""
        try:
            import time
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            # Format uptime
            days = int(uptime // 86400)
            hours = int((uptime % 86400) // 3600)
            minutes = int((uptime % 3600) // 60)
            
            if days > 0:
                uptime_str = f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                uptime_str = f"{hours}h {minutes}m"
            else:
                uptime_str = f"{minutes}m"
            
            self.uptime_label.setText(f"Uptime: {uptime_str}")
        except:
            pass
    
    def closeEvent(self, event):
        """Stop timers on close"""
        self.timer.stop()
        self.uptime_timer.stop()
        event.accept()