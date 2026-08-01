"""
Notepad Application for MiniOS
Simple text editor with open/save functionality
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence


class NotepadWidget(QWidget):
    """Notepad application widget"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #0d0d0d;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit {
                background: #0d0d0d;
                border: none;
                color: #cccccc;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                padding: 10px;
                selection-background-color: #2a2a2a;
            }
            QTextEdit:focus {
                border: none;
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
            QLabel {
                color: #444444;
                background: transparent;
                font-size: 11px;
            }
            QFrame#separator {
                background: #1a1a1a;
                max-height: 1px;
                min-height: 1px;
            }
            QScrollBar:vertical {
                background: #0d0d0d;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #2a2a2a;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3a3a3a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        # File buttons
        self.new_btn = QPushButton("📄 New")
        self.new_btn.setFixedHeight(32)
        self.new_btn.clicked.connect(self.new_file)
        toolbar.addWidget(self.new_btn)
        
        self.open_btn = QPushButton("📂 Open")
        self.open_btn.setFixedHeight(32)
        self.open_btn.clicked.connect(self.open_file)
        toolbar.addWidget(self.open_btn)
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setFixedHeight(32)
        self.save_btn.clicked.connect(self.save_file)
        toolbar.addWidget(self.save_btn)
        
        self.save_as_btn = QPushButton("💾 Save As")
        self.save_as_btn.setFixedHeight(32)
        self.save_as_btn.clicked.connect(self.save_file_as)
        toolbar.addWidget(self.save_as_btn)
        
        toolbar.addStretch()
        
        # File info
        self.file_label = QLabel("Untitled")
        self.file_label.setStyleSheet("color: #555555; font-size: 11px;")
        toolbar.addWidget(self.file_label)
        
        # Word count
        self.word_count_label = QLabel("0 words")
        self.word_count_label.setStyleSheet("color: #444444; font-size: 11px;")
        toolbar.addWidget(self.word_count_label)
        
        layout.addLayout(toolbar)
        
        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Start typing...")
        self.text_edit.textChanged.connect(self.update_word_count)
        layout.addWidget(self.text_edit)
        
        self.setLayout(layout)
        
    def new_file(self):
        """Create a new file"""
        if self.text_edit.document().isModified():
            reply = QMessageBox.question(
                self, "Save Changes",
                "Save changes to current file?",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                if not self.save_file():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.text_edit.clear()
        self.current_file = None
        self.file_label.setText("Untitled")
        self.text_edit.document().setModified(False)
        self.update_word_count()
        
    def open_file(self):
        """Open a file"""
        if self.text_edit.document().isModified():
            reply = QMessageBox.question(
                self, "Save Changes",
                "Save changes to current file?",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                if not self.save_file():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_edit.setText(content)
                self.current_file = file_path
                self.file_label.setText(file_path.split('/')[-1])
                self.text_edit.document().setModified(False)
                self.update_word_count()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file:\n{str(e)}")
    
    def save_file(self) -> bool:
        """Save the current file"""
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.text_edit.document().setModified(False)
                self.file_label.setText(self.current_file.split('/')[-1])
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{str(e)}")
                return False
        else:
            return self.save_file_as()
    
    def save_file_as(self) -> bool:
        """Save the file with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.current_file = file_path
            self.file_label.setText(file_path.split('/')[-1])
            return self.save_file()
        return False
    
    def update_word_count(self):
        """Update the word count display"""
        text = self.text_edit.toPlainText()
        words = len(text.split())
        chars = len(text)
        
        if words == 0:
            self.word_count_label.setText("0 words")
        else:
            self.word_count_label.setText(f"{words} words, {chars} characters")
    
    def closeEvent(self, event):
        """Handle close with save check"""
        if self.text_edit.document().isModified():
            reply = QMessageBox.question(
                self, "Save Changes",
                "Save changes before closing?",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                if not self.save_file():
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        event.accept()