"""
Terminal Application for MiniOS
Command-line interface for system interaction
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QLineEdit, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QTextCursor

from system.virtual_filesystem import VirtualFileSystem, Folder, File


class TerminalWidget(QWidget):
    """Terminal application widget"""
    
    def __init__(self):
        super().__init__()
        self.fs = VirtualFileSystem()
        self.command_history = []
        self.history_index = -1
        self.prompt = "minios@system:~$ "
        self.setup_ui()
        self.print_welcome()
        
        # Set focus to input after startup
        QTimer.singleShot(100, self.focus_input)
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #0a0a0a;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QTextEdit {
                background: #0a0a0a;
                border: none;
                color: #00ff41;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                padding: 10px;
                selection-background-color: #1a3a1a;
            }
            QTextEdit:focus {
                border: none;
            }
            QLineEdit {
                background: #0a0a0a;
                border: none;
                color: #00ff41;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                padding: 8px 10px;
            }
            QLineEdit:focus {
                border: none;
                outline: none;
            }
            QLabel {
                color: #00ff41;
                background: transparent;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }
            QPushButton {
                background: transparent;
                border: none;
                color: #00ff41;
                padding: 8px 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #1a3a1a;
                border-radius: 4px;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.output.setFont(QFont("Consolas", 13))
        self.output.setStyleSheet("""
            QTextEdit {
                background: #0a0a0a;
                color: #00ff41;
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        layout.addWidget(self.output, 1)
        
        # Input area
        input_container = QWidget()
        input_container.setStyleSheet("background: #0a0a0a;")
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 2, 10, 2)
        input_layout.setSpacing(5)
        
        # Prompt label
        self.prompt_label = QLabel("$ ")
        self.prompt_label.setFont(QFont("Consolas", 13))
        self.prompt_label.setStyleSheet("color: #00ff41; background: transparent;")
        input_layout.addWidget(self.prompt_label)
        
        # Command input
        self.input = QLineEdit()
        self.input.setFont(QFont("Consolas", 13))
        self.input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #00ff41;
                font-family: 'Consolas', 'Courier New', monospace;
                padding: 4px 0px;
            }
            QLineEdit:focus {
                border: none;
                outline: none;
            }
        """)
        self.input.returnPressed.connect(self.execute_command)
        self.input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        input_layout.addWidget(self.input)
        
        # Clear button
        clear_btn = QPushButton("clear")
        clear_btn.setFont(QFont("Consolas", 10))
        clear_btn.setStyleSheet("color: #00ff41; background: transparent;")
        clear_btn.clicked.connect(self.clear_output)
        input_layout.addWidget(clear_btn)
        
        input_container.setLayout(input_layout)
        layout.addWidget(input_container)
        
        self.setLayout(layout)
        
        # Update prompt
        self.update_prompt()
        
    def focus_input(self):
        """Force focus on the input field"""
        self.input.setFocus()
        self.input.setCursorPosition(len(self.input.text()))
        
    def print_welcome(self):
        """Print welcome message"""
        welcome = """
╔═══════════════════════════════════════════════╗
║              MINIOS TERMINAL                  ║
║           Version 1.0 - Minimal Edition       ║
╠═══════════════════════════════════════════════╣
║  Type 'help' for available commands           ║
║  Type 'exit' or 'logout' to close terminal    ║
╚═══════════════════════════════════════════════╝
"""
        self.append_output(welcome, "#00ff41")
        self.append_output("")
        
    def update_prompt(self):
        """Update the prompt with current path"""
        path = self.fs.pwd()
        if path == "root":
            prompt = "minios@system:/$ "
        else:
            prompt = f"minios@system:/{path}$ "
        self.prompt = prompt
        self.prompt_label.setText("$ ")
        
    def append_output(self, text, color="#00ff41"):
        """Append text to output with color"""
        if color:
            html = f'<span style="color: {color};">{text}</span>'
            self.output.append(html)
        else:
            self.output.append(text)
        # Scroll to bottom
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output.setTextCursor(cursor)
        
    def clear_output(self):
        """Clear the output area"""
        self.output.clear()
        self.focus_input()
        
    def execute_command(self):
        """Execute the entered command"""
        command = self.input.text().strip()
        self.input.clear()
        
        if not command:
            self.focus_input()
            return
        
        # Add to history
        self.command_history.append(command)
        self.history_index = -1
        
        # Display the command
        self.append_output(f"{self.prompt}{command}", "#666666")
        
        # Parse command
        parts = command.split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        # Execute command
        result = self.process_command(cmd, args)
        if result:
            self.append_output(result)
            
        # Update prompt
        self.update_prompt()
        
        # Keep focus on input
        self.focus_input()
        
    def process_command(self, cmd, args):
        """Process a command and return output"""
        cmd = cmd.lower()
        
        # Help command
        if cmd == "help":
            return """
Available commands:
  help          - Show this help message
  ls            - List directory contents
  cd <dir>      - Change directory
  pwd           - Print working directory
  mkdir <name>  - Create a new folder
  touch <name>  - Create a new file
  cat <file>    - Display file contents
  echo <text>   - Display text
  clear         - Clear the terminal
  exit/logout   - Close terminal
  whoami        - Display current user
  date          - Display current date and time
  history       - Show command history
  rm <name>     - Remove a file or folder
  tree          - Display directory structure
"""
        
        # List directory
        elif cmd == "ls":
            items = self.fs.ls()
            if items:
                # Format nicely with folders and files
                formatted = []
                for name in items:
                    item = self.fs.current_directory.get_item(name)
                    if item and isinstance(item, Folder):
                        formatted.append(f"{name}/")
                    else:
                        formatted.append(name)
                return "  ".join(formatted)
            return "(empty)"
        
        # Change directory
        elif cmd == "cd":
            if not args:
                self.fs.cd("/")
                return ""
            path = args[0]
            if path == "..":
                if self.fs.cd(".."):
                    return ""
                return "cd: already at root"
            elif path == "/":
                self.fs.cd("/")
                return ""
            else:
                if self.fs.cd(path):
                    return ""
                return f"cd: {path}: No such directory"
        
        # Print working directory
        elif cmd == "pwd":
            path = self.fs.pwd()
            if path == "root":
                return "/"
            return f"/{path}"
        
        # Make directory
        elif cmd == "mkdir":
            if not args:
                return "mkdir: missing operand"
            if self.fs.mkdir(args[0]):
                return f"Created folder: {args[0]}"
            return f"mkdir: cannot create directory '{args[0]}': File exists"
        
        # Touch - create file
        elif cmd == "touch":
            if not args:
                return "touch: missing file operand"
            if self.fs.touch(args[0], ""):
                return f"Created file: {args[0]}"
            return f"touch: cannot create file '{args[0]}': File exists"
        
        # Cat - display file
        elif cmd == "cat":
            if not args:
                return "cat: missing file operand"
            content = self.fs.cat(args[0])
            if content is not None:
                return content
            return f"cat: {args[0]}: No such file"
        
        # Echo - display text
        elif cmd == "echo":
            return " ".join(args) if args else ""
        
        # Clear
        elif cmd == "clear":
            self.clear_output()
            return ""
        
        # Exit/Logout
        elif cmd in ["exit", "logout"]:
            if self.parent():
                self.parent().close()
            return ""
        
        # Whoami
        elif cmd == "whoami":
            return "minios_user"
        
        # Date
        elif cmd == "date":
            from datetime import datetime
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # History
        elif cmd == "history":
            if not self.command_history:
                return "(no commands)"
            return "\n".join([f"  {i+1:3d}  {cmd}" for i, cmd in enumerate(self.command_history)])
        
        # Remove
        elif cmd == "rm":
            if not args:
                return "rm: missing operand"
            if self.fs.current_directory.remove_item(args[0]):
                return f"Removed: {args[0]}"
            return f"rm: cannot remove '{args[0]}': No such file or directory"
        
        # Tree - fixed version
        elif cmd == "tree":
            return self.build_tree()
        
        # Unknown command
        else:
            return f"command not found: {cmd} (type 'help' for available commands)"
    
    def build_tree(self):
        """Build a tree representation of the filesystem from current directory"""
        def _build_tree(folder, indent="", is_last=True):
            lines = []
            items = folder.list_items()
            
            # Sort: folders first
            folders = [i for i in items if isinstance(i, Folder)]
            files = [i for i in items if isinstance(i, File)]
            sorted_items = folders + files
            
            for i, item in enumerate(sorted_items):
                is_last_item = (i == len(sorted_items) - 1)
                
                # Choose the prefix
                prefix = "└── " if is_last_item else "├── "
                line = indent + prefix + item.name
                
                if isinstance(item, Folder):
                    line += "/"
                    lines.append(line)
                    # Recurse into folder
                    child_indent = indent + ("    " if is_last_item else "│   ")
                    lines.extend(_build_tree(item, child_indent, is_last_item))
                else:
                    lines.append(line)
            
            return lines
        
        # Start from current directory
        lines = [f"{self.fs.current_directory.name}/"]
        lines.extend(_build_tree(self.fs.current_directory))
        return "\n".join(lines)
    
    def keyPressEvent(self, event):
        """Handle key events for command history"""
        if event.key() == Qt.Key.Key_Up:
            # Previous command
            if self.command_history:
                if self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self.input.setText(self.command_history[-1 - self.history_index])
                    self.input.selectAll()
        elif event.key() == Qt.Key.Key_Down:
            # Next command
            if self.command_history and self.history_index > -1:
                self.history_index -= 1
                if self.history_index == -1:
                    self.input.clear()
                else:
                    self.input.setText(self.command_history[-1 - self.history_index])
                    self.input.selectAll()
        elif event.key() == Qt.Key.Key_Escape:
            self.input.clear()
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """Focus input when clicking anywhere"""
        self.focus_input()
        super().mousePressEvent(event)
    
    def showEvent(self, event):
        """Focus input when shown"""
        super().showEvent(event)
        QTimer.singleShot(100, self.focus_input)
    
    def closeEvent(self, event):
        """Handle terminal close"""
        self.append_output("\nTerminal session ended", "#666666")
        event.accept()