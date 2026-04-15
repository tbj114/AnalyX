from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame
from PyQt6.QtGui import QPalette, QColor


class ModernToolBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(8)
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(22, 22, 27))
        self.setPalette(palette)
        
        tool_buttons = [
            ('新建', 'Ctrl+N', self.parent.new_project),
            ('打开', 'Ctrl+O', self.parent.open_file),
            ('保存', 'Ctrl+S', self.parent.save_file)
        ]
        
        for text, shortcut, callback in tool_buttons:
            button = QPushButton(text)
            button.setStyleSheet('''
                QPushButton {
                    background-color: #2a2a30;
                    color: #faf9f5;
                    border: 1px solid #3a3a40;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 11px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #3a3a40;
                    border-color: #6a9bcc;
                }
                QPushButton:pressed {
                    background-color: #1a1a20;
                }
            ''')
            button.clicked.connect(callback)
            self.layout.addWidget(button)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet('background-color: #3a3a40; margin: 0 8px;')
        self.layout.addWidget(separator)
        
        search_frame = QWidget()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(5)
        
        search_label = QLabel('搜索:')
        search_label.setStyleSheet('color: #b0aea5; font-size: 11px;')
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('搜索变量或分析...')
        self.search_edit.setFixedWidth(150)
        self.search_edit.setStyleSheet('''
            QLineEdit {
                background-color: #2a2a30;
                color: #faf9f5;
                border: 1px solid #3a3a40;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #6a9bcc;
                outline: none;
            }
        ''')
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        self.layout.addWidget(search_frame)
        
        self.layout.addStretch()
