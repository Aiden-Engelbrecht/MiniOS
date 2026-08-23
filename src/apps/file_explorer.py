"""
File Explorer Application for MiniOS
With context menu and drag-drop support
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem,
    QLineEdit, QFrame, QMessageBox,
    QMenu, QInputDialog, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QMimeData, QUrl
from PySide6.QtGui import QFont, QAction, QDrag, QPixmap, QPainter

from system.virtual_filesystem import VirtualFileSystem, Folder, File


class FileExplorerWidget(QWidget):
    """File Explorer application widget with context menu and drag-drop"""
    
    def __init__(self):
        super().__init__()
        self.fs = VirtualFileSystem()
        self.current_path = "/"
        self.setup_ui()
        self.refresh()
        
        # Enable drag-drop
        self.setAcceptDrops(True)
        
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
            QLineEdit {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 8px 12px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #444444;
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
                border: 1px solid #3a3a3a;
            }
            QListWidget {
                background: #0d0d0d;
                border: none;
                color: #888888;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 12px;
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
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        self.back_btn = QPushButton("◀")
        self.back_btn.setFixedSize(35, 35)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setToolTip("Back (Alt+Left)")
        toolbar.addWidget(self.back_btn)
        
        self.forward_btn = QPushButton("▶")
        self.forward_btn.setFixedSize(35, 35)
        self.forward_btn.clicked.connect(self.go_forward)
        self.forward_btn.setToolTip("Forward (Alt+Right)")
        toolbar.addWidget(self.forward_btn)
        
        self.up_btn = QPushButton("▲")
        self.up_btn.setFixedSize(35, 35)
        self.up_btn.clicked.connect(self.go_up)
        self.up_btn.setToolTip("Up (Alt+Up)")
        toolbar.addWidget(self.up_btn)
        
        # Path bar
        self.path_bar = QLineEdit()
        self.path_bar.setPlaceholderText("Enter path...")
        self.path_bar.returnPressed.connect(self.navigate_to_path)
        toolbar.addWidget(self.path_bar)
        
        # New folder button
        self.new_folder_btn = QPushButton("+ Folder")
        self.new_folder_btn.setFixedHeight(35)
        self.new_folder_btn.clicked.connect(self.create_new_folder)
        toolbar.addWidget(self.new_folder_btn)
        
        layout.addLayout(toolbar)
        
        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Enable drag from list
        self.file_list.setDragEnabled(True)
        self.file_list.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.file_list.setAcceptDrops(True)
        
        layout.addWidget(self.file_list)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #444444; font-size: 11px;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        self.item_count_label = QLabel("0 items")
        self.item_count_label.setStyleSheet("color: #444444; font-size: 11px;")
        status_layout.addWidget(self.item_count_label)
        
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
        
    def refresh(self):
        """Refresh the file list"""
        self.file_list.clear()
        
        items = self.fs.get_current_items()
        
        # Sort: folders first, then files
        folders = [i for i in items if isinstance(i, Folder)]
        files = [i for i in items if isinstance(i, File)]
        
        # Add folders
        for folder in folders:
            item = QListWidgetItem(f"📁  {folder.name}")
            item.setData(Qt.ItemDataRole.UserRole, folder)
            self.file_list.addItem(item)
        
        # Add files
        for file in files:
            size_str = self.format_size(file.size)
            item = QListWidgetItem(f"📄  {file.name}  ({size_str})")
            item.setData(Qt.ItemDataRole.UserRole, file)
            self.file_list.addItem(item)
        
        # Update path bar
        self.path_bar.setText(self.fs.pwd())
        
        # Update status
        self.item_count_label.setText(f"{len(items)} items")
        self.status_label.setText(f"Current directory: {self.fs.pwd()}")
        
        # Update navigation buttons
        self.back_btn.setEnabled(False)  # We'll use history
        self.forward_btn.setEnabled(False)
        self.up_btn.setEnabled(self.fs.current_directory.parent is not None)
        
    def format_size(self, size: int) -> str:
        """Format file size"""
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f}KB"
        else:
            return f"{size / (1024 * 1024):.1f}MB"
    
    def on_item_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on item"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, Folder):
            if self.fs.cd(data.name):
                self.refresh()
        elif isinstance(data, File):
            content = data.read()
            QMessageBox.information(self, f"File: {data.name}", content)
    
    def go_back(self):
        if self.fs.go_back():
            self.refresh()
    
    def go_forward(self):
        if self.fs.go_forward():
            self.refresh()
    
    def go_up(self):
        if self.fs.cd(".."):
            self.refresh()
    
    def navigate_to_path(self):
        path = self.path_bar.text().strip()
        if path:
            # Try to navigate to path
            parts = path.split('/')
            self.fs.current_directory = self.fs.root
            success = True
            for part in parts:
                if part and part != "/":
                    if not self.fs.cd(part):
                        success = False
                        break
            if success:
                self.refresh()
            else:
                self.refresh()
                QMessageBox.warning(self, "Error", f"Cannot navigate to: {path}")
    
    def create_new_folder(self):
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name:
            if self.fs.mkdir(name):
                self.refresh()
                self.status_label.setText(f"Created folder: {name}")
            else:
                QMessageBox.warning(self, "Error", f"Cannot create folder: {name}")
    
    def show_context_menu(self, position):
        """Show context menu for file list"""
        menu = QMenu(self)
        
        # Get selected items
        selected_items = self.file_list.selectedItems()
        has_selection = len(selected_items) > 0
        
        if has_selection:
            # Action for first selected item
            item = selected_items[0]
            data = item.data(Qt.ItemDataRole.UserRole)
            
            if data:
                if isinstance(data, Folder):
                    open_action = QAction("📁 Open", self)
                    open_action.triggered.connect(lambda: self.on_item_double_clicked(item))
                    menu.addAction(open_action)
                
                rename_action = QAction("✏️ Rename", self)
                rename_action.triggered.connect(lambda: self.rename_item(item))
                menu.addAction(rename_action)
                
                delete_action = QAction("🗑 Delete", self)
                delete_action.triggered.connect(lambda: self.delete_item(item))
                menu.addAction(delete_action)
                
                copy_action = QAction("📋 Copy", self)
                copy_action.triggered.connect(lambda: self.copy_item(item))
                menu.addAction(copy_action)
        
        # Add new actions
        menu.addSeparator()
        new_folder_action = QAction("📁 New Folder", self)
        new_folder_action.triggered.connect(self.create_new_folder)
        menu.addAction(new_folder_action)
        
        new_file_action = QAction("📄 New File", self)
        new_file_action.triggered.connect(self.create_new_file)
        menu.addAction(new_file_action)
        
        menu.addSeparator()
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.triggered.connect(self.refresh)
        menu.addAction(refresh_action)
        
        menu.exec_(self.file_list.mapToGlobal(position))
    
    def rename_item(self, item: QListWidgetItem):
        """Rename an item"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        old_name = data.name
        new_name, ok = QInputDialog.getText(
            self, "Rename",
            f"Rename '{old_name}' to:",
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            if self.fs.rename_item(old_name, new_name):
                self.refresh()
                self.status_label.setText(f"Renamed: {old_name} → {new_name}")
            else:
                QMessageBox.warning(self, "Error", f"Cannot rename: {old_name}")
    
    def delete_item(self, item: QListWidgetItem):
        """Delete an item"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Move '{data.name}' to Trash?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Move to trash
            trash = self.fs.root.get_item(".Trash")
            if not trash:
                trash = Folder(".Trash", self.fs.root)
                self.fs.root.add_item(trash)
            
            if self.fs.move_item(data.name, trash):
                self.refresh()
                self.status_label.setText(f"Moved to Trash: {data.name}")
            else:
                QMessageBox.warning(self, "Error", f"Cannot delete: {data.name}")
    
    def copy_item(self, item: QListWidgetItem):
        """Copy an item (placeholder - just show message)"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            QMessageBox.information(
                self, "Copy",
                f"Copy '{data.name}' to clipboard (simulated)"
            )
    
    def create_new_file(self):
        """Create a new file"""
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            if self.fs.touch(name, ""):
                self.refresh()
                self.status_label.setText(f"Created file: {name}")
            else:
                QMessageBox.warning(self, "Error", f"Cannot create file: {name}")
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Delete:
            # Delete selected items
            for item in self.file_list.selectedItems():
                self.delete_item(item)
        elif event.key() == Qt.Key.Key_F2:
            # Rename selected item
            items = self.file_list.selectedItems()
            if items:
                self.rename_item(items[0])
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Open selected item
            items = self.file_list.selectedItems()
            if items:
                self.on_item_double_clicked(items[0])
        super().keyPressEvent(event)
    
    def dragEnterEvent(self, event):
        """Handle drag enter for external drags"""
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop events for external files"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path:
                    # Just show a message for now
                    QMessageBox.information(
                        self, "File Dropped",
                        f"File dropped: {os.path.basename(file_path)}\n\n"
                        f"(Virtual file system doesn't support real file imports yet)"
                    )
        event.accept()
    
    def closeEvent(self, event):
        """Handle close event"""
        event.accept()