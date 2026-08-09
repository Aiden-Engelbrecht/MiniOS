"""
Calculator Application for MiniOS
Basic and scientific calculator
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import math


class CalculatorWidget(QWidget):
    """Calculator application widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.clear_all()
        
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
            QLabel#display {
                color: #ffffff;
                font-size: 32px;
                font-weight: bold;
                background: #0d0d0d;
                border: none;
                padding: 10px 15px;
                min-height: 60px;
                qproperty-alignment: AlignRight;
            }
            QLabel#expression {
                color: #666666;
                font-size: 16px;
                background: #0d0d0d;
                border: none;
                padding: 5px 15px;
                min-height: 30px;
                qproperty-alignment: AlignRight;
            }
            QPushButton {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                font-size: 18px;
                padding: 12px;
                min-height: 40px;
            }
            QPushButton:hover {
                background: #2a2a2a;
                color: #ffffff;
            }
            QPushButton#number {
                background: #1a1a1a;
                color: #cccccc;
            }
            QPushButton#number:hover {
                background: #2a2a2a;
                color: #ffffff;
            }
            QPushButton#operator {
                background: #1a2a3a;
                color: #66d9ef;
            }
            QPushButton#operator:hover {
                background: #2a3a4a;
                color: #88ffef;
            }
            QPushButton#equals {
                background: #2a4a2a;
                color: #88ff88;
            }
            QPushButton#equals:hover {
                background: #3a5a3a;
                color: #aaffaa;
            }
            QPushButton#clear {
                background: #3a1a1a;
                color: #ff6666;
            }
            QPushButton#clear:hover {
                background: #4a2a2a;
                color: #ff8888;
            }
            QPushButton#function {
                background: #1a2a2a;
                color: #66d9ef;
                font-size: 14px;
            }
            QPushButton#function:hover {
                background: #2a3a3a;
                color: #88ffef;
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
        layout.setSpacing(8)
        
        # Display
        self.expression_label = QLabel("")
        self.expression_label.setObjectName("expression")
        layout.addWidget(self.expression_label)
        
        self.display_label = QLabel("0")
        self.display_label.setObjectName("display")
        layout.addWidget(self.display_label)
        
        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)
        
        # Scientific buttons row
        sci_layout = QHBoxLayout()
        sci_layout.setSpacing(5)
        
        sci_buttons = [
            ("sin", "sin"), ("cos", "cos"), ("tan", "tan"),
            ("log", "log"), ("ln", "ln"), ("√", "sqrt")
        ]
        
        for text, value in sci_buttons:
            btn = QPushButton(text)
            btn.setObjectName("function")
            btn.clicked.connect(lambda checked, v=value: self.add_function(v))
            sci_layout.addWidget(btn)
        
        layout.addLayout(sci_layout)
        
        # Main calculator grid
        grid = QGridLayout()
        grid.setSpacing(5)
        
        # Row 0: Clear, Backspace, Parentheses
        buttons = [
            ("(", "(", "function"), (")", ")", "function"),
            ("C", "clear", "clear"), ("⌫", "backspace", "clear")
        ]
        
        for col, (text, value, style) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setObjectName(style)
            btn.clicked.connect(lambda checked, v=value: self.handle_input(v))
            grid.addWidget(btn, 0, col)
        
        # Row 1: 7, 8, 9, ÷
        buttons = [
            ("7", "7", "number"), ("8", "8", "number"), ("9", "9", "number"),
            ("÷", "/", "operator")
        ]
        
        for col, (text, value, style) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setObjectName(style)
            btn.clicked.connect(lambda checked, v=value: self.handle_input(v))
            grid.addWidget(btn, 1, col)
        
        # Row 2: 4, 5, 6, ×
        buttons = [
            ("4", "4", "number"), ("5", "5", "number"), ("6", "6", "number"),
            ("×", "*", "operator")
        ]
        
        for col, (text, value, style) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setObjectName(style)
            btn.clicked.connect(lambda checked, v=value: self.handle_input(v))
            grid.addWidget(btn, 2, col)
        
        # Row 3: 1, 2, 3, −
        buttons = [
            ("1", "1", "number"), ("2", "2", "number"), ("3", "3", "number"),
            ("−", "-", "operator")
        ]
        
        for col, (text, value, style) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setObjectName(style)
            btn.clicked.connect(lambda checked, v=value: self.handle_input(v))
            grid.addWidget(btn, 3, col)
        
        # Row 4: 0, ., ±, +
        buttons = [
            ("0", "0", "number"), (".", ".", "number"),
            ("±", "negate", "function"), ("+", "+", "operator")
        ]
        
        for col, (text, value, style) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setObjectName(style)
            btn.clicked.connect(lambda checked, v=value: self.handle_input(v))
            grid.addWidget(btn, 4, col)
        
        # Row 5: = (span 4 columns)
        equals_btn = QPushButton("=")
        equals_btn.setObjectName("equals")
        equals_btn.clicked.connect(self.calculate)
        grid.addWidget(equals_btn, 5, 0, 1, 4)
        
        layout.addLayout(grid)
        
        self.setLayout(layout)
        
    def clear_all(self):
        """Clear everything"""
        self.current_input = "0"
        self.expression = ""
        self.result = None
        self.last_operation = None
        self.waiting_for_operand = False
        self.update_display()
        
    def clear_entry(self):
        """Clear current entry"""
        self.current_input = "0"
        self.update_display()
        
    def handle_input(self, value):
        """Handle button input"""
        if value == "clear":
            self.clear_all()
            return
        elif value == "backspace":
            if len(self.current_input) > 1:
                self.current_input = self.current_input[:-1]
            else:
                self.current_input = "0"
            self.update_display()
            return
        elif value == "negate":
            if self.current_input.startswith("-"):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = "-" + self.current_input
            self.update_display()
            return
        
        # Handle operators
        if value in ["+", "-", "*", "/"]:
            if self.result is None:
                self.result = float(self.current_input)
            elif self.waiting_for_operand:
                self.result = self.perform_operation(self.result, float(self.current_input))
                self.current_input = str(self.result)
            
            self.last_operation = value
            self.waiting_for_operand = True
            self.expression = f"{self.current_input} {value}"
            self.update_display()
            return
        
        # Handle parentheses
        if value in ["(", ")"]:
            # Simple: just append to current input
            if self.current_input == "0":
                self.current_input = value
            else:
                self.current_input += value
            self.update_display()
            return
        
        # Handle numbers and decimal
        if self.waiting_for_operand:
            self.current_input = "0"
            self.waiting_for_operand = False
        
        if value == "." and "." in self.current_input:
            return
        
        if self.current_input == "0" and value != ".":
            self.current_input = value
        else:
            self.current_input += value
        
        self.update_display()
    
    def add_function(self, func):
        """Add a scientific function"""
        try:
            num = float(self.current_input)
            
            if func == "sin":
                result = math.sin(math.radians(num))
            elif func == "cos":
                result = math.cos(math.radians(num))
            elif func == "tan":
                result = math.tan(math.radians(num))
            elif func == "log":
                result = math.log10(num)
            elif func == "ln":
                result = math.log(num)
            elif func == "sqrt":
                result = math.sqrt(num)
            else:
                return
            
            self.expression = f"{func}({self.current_input})"
            self.current_input = str(result)
            self.result = result
            self.update_display()
            
        except Exception as e:
            self.display_label.setText("Error")
    
    def perform_operation(self, a, b):
        """Perform arithmetic operation"""
        if self.last_operation == "+":
            return a + b
        elif self.last_operation == "-":
            return a - b
        elif self.last_operation == "*":
            return a * b
        elif self.last_operation == "/":
            if b == 0:
                self.display_label.setText("Error")
                return 0
            return a / b
        return b
    
    def calculate(self):
        """Calculate the result"""
        if self.last_operation and self.result is not None:
            try:
                b = float(self.current_input)
                self.expression = f"{self.result} {self.last_operation} {b}"
                result = self.perform_operation(self.result, b)
                self.current_input = str(result)
                self.result = result
                self.last_operation = None
                self.waiting_for_operand = False
                self.update_display()
            except Exception as e:
                self.display_label.setText("Error")
        else:
            # Just display the current value
            self.expression = ""
            self.result = float(self.current_input)
            self.update_display()
    
    def update_display(self):
        """Update the display labels"""
        # Format the number
        try:
            if "." in self.current_input:
                # Keep decimal numbers clean
                num = float(self.current_input)
                if num.is_integer():
                    display = str(int(num))
                else:
                    # Limit to 10 decimal places
                    display = f"{num:.10f}".rstrip('0').rstrip('.')
                    if len(display) > 20:
                        display = f"{num:.6e}"
                self.display_label.setText(display)
            else:
                self.display_label.setText(self.current_input)
        except:
            self.display_label.setText(self.current_input)
        
        # Update expression
        self.expression_label.setText(self.expression)
    
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        key = event.text()
        
        if key.isdigit() or key == ".":
            self.handle_input(key)
        elif key in ["+", "-", "*", "/"]:
            self.handle_input(key)
        elif key == "=" or key == "\r":
            self.calculate()
        elif key == "\b":
            self.handle_input("backspace")
        elif key == "c" or key == "C":
            self.clear_all()
        elif key == "(" or key == ")":
            self.handle_input(key)
        elif key == "s":
            self.add_function("sin")
        elif key == "r":
            self.add_function("sqrt")
        
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle close"""
        event.accept()