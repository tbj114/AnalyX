from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class ModernToolBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(24, 12, 24, 12)
        self.layout.setSpacing(12)
        
        self.setStyleSheet('''
            ModernToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e2e8f0;
            }
        ''')
        
        tool_buttons = [
            ('新建', 'Ctrl+N', self.parent.new_project, '#6366f1'),
            ('打开', 'Ctrl+O', self.parent.open_file, '#8b5cf6'),
            ('保存', 'Ctrl+S', self.parent.save_file, '#10b981')
        ]
        
        for text, shortcut, callback, color in tool_buttons:
            button = self.create_tool_button(text, color)
            button.clicked.connect(callback)
            self.layout.addWidget(button)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet('background-color: #e2e8f0; margin: 0 12px;')
        self.layout.addWidget(separator)
        
        search_frame = QWidget()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)
        
        search_icon = QLabel('🔍')
        search_icon.setStyleSheet('font-size: 14px;')
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('搜索变量或分析...')
        self.search_edit.setFixedWidth(280)
        self.search_edit.setFont(QFont('Inter', 11))
        self.search_edit.setStyleSheet('''
            QLineEdit {
                background-color: #f1f5f9;
                color: #1e293b;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 11px;
            }
            QLineEdit:focus {
                background-color: #ffffff;
                border: 2px solid #6366f1;
                outline: none;
            }
        ''')
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_edit)
        self.layout.addWidget(search_frame)
        
        self.layout.addStretch()
        
        theme_button = self.create_action_button('切换主题', '#0f172a')
        theme_button.clicked.connect(self.parent.toggle_theme)
        self.layout.addWidget(theme_button)
    
    def create_tool_button(self, text, color):
        btn = QPushButton(text)
        btn.setFont(QFont('Inter', 11, QFont.Weight.Medium))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {color}15;
                color: {color};
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {color}25;
            }}
            QPushButton:pressed {{
                background-color: {color}35;
            }}
        ''')
        return btn
    
    def create_action_button(self, text, color):
        btn = QPushButton(text)
        btn.setFont(QFont('Inter', 11, QFont.Weight.Medium))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #1e293b;
            }}
            QPushButton:pressed {{
                background-color: #334155;
            }}
        ''')
        return btn
