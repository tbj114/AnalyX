from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QPalette, QColor


class ModernTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(36)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 0, 15, 0)
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 25))
        self.setPalette(palette)
        
        self.logo_label = QLabel('AnalyX')
        self.logo_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        self.logo_label.setStyleSheet('color: #6a9bcc;')
        
        self.title_label = QLabel('学术统计软件')
        self.title_label.setFont(QFont('Arial', 10))
        self.title_label.setStyleSheet('color: #faf9f5;')
        
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.logo_label)
        title_layout.addWidget(QLabel(' - '))
        title_layout.addWidget(self.title_label)
        title_layout.setSpacing(4)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)
        
        self.min_button = QPushButton('—')
        self.min_button.setFixedSize(24, 24)
        self.min_button.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                color: #b0aea5;
                border: 1px solid #333333;
                border-radius: 3px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #faf9f5;
            }
        ''')
        self.min_button.clicked.connect(self.parent.showMinimized)
        
        self.max_button = QPushButton('□')
        self.max_button.setFixedSize(24, 24)
        self.max_button.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                color: #b0aea5;
                border: 1px solid #333333;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #faf9f5;
            }
        ''')
        self.max_button.clicked.connect(self.toggle_maximize)
        
        self.close_button = QPushButton('✕')
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                color: #d97757;
                border: 1px solid #443333;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d97757;
                color: #141413;
            }
        ''')
        self.close_button.clicked.connect(self.parent.close)
        
        button_layout.addWidget(self.min_button)
        button_layout.addWidget(self.max_button)
        button_layout.addWidget(self.close_button)
        
        self.layout.addLayout(title_layout)
        self.layout.addStretch()
        self.layout.addLayout(button_layout)
        
        self.is_moving = False
        self.start_pos = QPoint()
    
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.max_button.setText('□')
        else:
            self.parent.showMaximized()
            self.max_button.setText('▢')
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_moving = True
            self.start_pos = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if self.is_moving:
            self.parent.move(event.globalPosition().toPoint() - self.start_pos)
    
    def mouseReleaseEvent(self, event):
        self.is_moving = False
