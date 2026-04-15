from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame
from PyQt6.QtGui import QPalette, QColor, QFont


class ModernToolBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 10)
        self.layout.setSpacing(12)
        
        # Modern background
        self.setStyleSheet('''
            QWidget {
                background-color: #ffffff;
                border-bottom: 1px solid #e8e6dc;
            }
        ''')
        
        tool_buttons = [
            ('新建', 'Ctrl+N', self.parent.new_project),
            ('打开', 'Ctrl+O', self.parent.open_file),
            ('保存', 'Ctrl+S', self.parent.save_file)
        ]
        
        for text, shortcut, callback in tool_buttons:
            button = QPushButton(text)
            button.setFont(QFont('Poppins', 10, QFont.Weight.Medium))
            button.setStyleSheet('''
                QPushButton {
                    background-color: #f8f7f3;
                    color: #141413;
                    border: 1px solid #e8e6dc;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 10px;
                    font-weight: 500;
                    transition: all 0.2s ease;
                }
                QPushButton:hover {
                    background-color: #6a9bcc;
                    color: white;
                    border-color: #6a9bcc;
                }
                QPushButton:pressed {
                    background-color: #5a8bc0;
                }
            ''')
            button.clicked.connect(callback)
            self.layout.addWidget(button)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet('background-color: #e8e6dc; margin: 0 8px;')
        self.layout.addWidget(separator)
        
        search_frame = QWidget()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)
        
        search_label = QLabel('搜索:')
        search_label.setFont(QFont('Poppins', 10, QFont.Weight.Medium))
        search_label.setStyleSheet('color: #141413; font-size: 10px;')
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('搜索变量或分析...')
        self.search_edit.setFixedWidth(200)
        self.search_edit.setFont(QFont('Lora', 10))
        self.search_edit.setStyleSheet('''
            QLineEdit {
                background-color: #f8f7f3;
                color: #141413;
                border: 1px solid #e8e6dc;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 10px;
                transition: all 0.2s ease;
            }
            QLineEdit:focus {
                border-color: #6a9bcc;
                outline: none;
                box-shadow: 0 0 0 2px rgba(106, 155, 204, 0.1);
            }
        ''')
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        self.layout.addWidget(search_frame)
        
        self.layout.addStretch()
        
        # Add theme toggle button
        theme_button = QPushButton('切换主题')
        theme_button.setFont(QFont('Poppins', 10, QFont.Weight.Medium))
        theme_button.setStyleSheet('''
            QPushButton {
                background-color: #f8f7f3;
                color: #141413;
                border: 1px solid #e8e6dc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 10px;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background-color: #788c5d;
                color: white;
                border-color: #788c5d;
            }
        ''')
        theme_button.clicked.connect(self.parent.toggle_theme)
        self.layout.addWidget(theme_button)
