"""
Recycle Bin Application for MiniOS
View, restore, and delete items
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from system.recycle_bin import RecycleBin


class RecycleBinWidget(QWidget):
    """Recycle Bin application widget"""
    
    def __init__(self):
        super().__init__()
        self.recycle_bin = RecycleBin()
        self.setup_ui()
        self.refresh()
        
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
                padding: 10px;
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
            QPushButton#empty_btn {
                background: #4a2a2a;
                border: 1px solid #5a3a3a;
                color: #ff8888;
            }
            QPushButton#empty_btn:hover {
                background: #5a3a3a;
            }
            QPushButton#restore_btn {
                background: #2a4a2a;
                border: 1px solid #3a5a3a;
                color: #88ff88;
            }
            QPushButton#restore_btn:hover {
                background: #3a5a3a;
            }
            QListWidget {
                background: #0d0d0d;
                border: 1px solid #1a1a1a;
                border-radius: 4px;
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
            QFrame#empty_frame {
                background: #0d0d0d;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
                padding: 40px;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🗑 Recycle Bin")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.count_label = QLabel("0 items")
        self.count_label.setStyleSheet("color: #666666; font-size: 12px;")
        header_layout.addWidget(self.count_label)
        
        layout.addLayout(header_layout)
        
        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        self.restore_btn = QPushButton("♻ Restore")
        self.restore_btn.setObjectName("restore_btn")
        self.restore_btn.setEnabled(False)
        self.restore_btn.clicked.connect(self.restore_item)
        toolbar.addWidget(self.restore_btn)
        
        self.empty_btn = QPushButton("🗑 Empty")
        self.empty_btn.setObjectName("empty_btn")
        self.empty_btn.clicked.connect(self.empty_bin)
        toolbar.addWidget(self.empty_btn)
        
        toolbar.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self.refresh_btn)
        
        layout.addLayout(toolbar)
        
        # List widget
        self.item_list = QListWidget()
        self.item_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.item_list.itemDoubleClicked.connect(self.restore_item)
        layout.addWidget(self.item_list)
        
        # Empty state (hidden by default)
        self.empty_frame = QFrame()
        self.empty_frame.setObjectName("empty_frame")
        empty_layout = QVBoxLayout()
        
        empty_icon = QLabel("🗑")
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_icon.setStyleSheet("font-size: 48px;")
        empty_layout.addWidget(empty_icon)
        
        empty_text = QLabel("Recycle Bin is empty")
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_text.setStyleSheet("color: #666666; font-size: 16px;")
        empty_layout.addWidget(empty_text)
        
        empty_sub = QLabel("Deleted files will appear here")
        empty_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_sub.setStyleSheet("color: #444444; font-size: 12px;")
        empty_layout.addWidget(empty_sub)
        
        self.empty_frame.setLayout(empty_layout)
        layout.addWidget(self.empty_frame)
        
        self.setLayout(layout)
        
    def refresh(self):
        """Refresh the item list"""
        self.item_list.clear()
        items = self.recycle_bin.get_items()
        
        if not items:
            self.item_list.setVisible(False)
            self.empty_frame.setVisible(True)
            self.count_label.setText("0 items")
            self.restore_btn.setEnabled(False)
            return
        
        self.item_list.setVisible(True)
        self.empty_frame.setVisible(False)
        
        for i, item in enumerate(items):
            # Format the display text
            size_str = self.recycle_bin.format_size(item.size)
            # Truncate path if too long
            path = item.original_path
            if len(path) > 40:
                path = "..." + path[-37:]
            
            display_text = f"{item.file_name}  ({size_str})  [{path}]"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, i)
            
            # Color based on type
            if item.file_type == "folder":
                list_item.setForeground(Qt.GlobalColor.cyan)
            else:
                list_item.setForeground(Qt.GlobalColor.gray)
            
            self.item_list.addItem(list_item)
        
        self.count_label.setText(f"{len(items)} items")
        self.restore_btn.setEnabled(False)
        
    def on_selection_changed(self):
        """Handle selection changes"""
        selected = self.item_list.selectedItems()
        self.restore_btn.setEnabled(len(selected) > 0)
        
    def restore_item(self):
        """Restore the selected item"""
        selected = self.item_list.selectedItems()
        if not selected:
            return
        
        index = selected[0].data(Qt.ItemDataRole.UserRole)
        if index is None:
            return
        
        item = self.recycle_bin.get_items()[index]
        
        # Confirm restore
        reply = QMessageBox.question(
            self, "Restore Item",
            f"Restore '{item.file_name}' to its original location?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.recycle_bin.remove_item(index)
            self.refresh()
            QMessageBox.information(self, "Restored", f"'{item.file_name}' has been restored.")
    
    def empty_bin(self):
        """Empty the recycle bin"""
        count = self.recycle_bin.get_count()
        if count == 0:
            QMessageBox.information(self, "Empty Recycle Bin", "Recycle Bin is already empty.")
            return
        
        total_size = self.recycle_bin.get_total_size()
        size_str = self.recycle_bin.format_size(total_size)
        
        reply = QMessageBox.question(
            self, "Empty Recycle Bin",
            f"Permanently delete {count} item(s) ({size_str})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.recycle_bin.empty()
            self.refresh()
            QMessageBox.information(self, "Emptied", "Recycle Bin has been emptied.")
    
    def closeEvent(self, event):
        """Handle close event"""
        event.accept()