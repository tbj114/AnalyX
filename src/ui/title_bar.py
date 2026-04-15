from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QPalette, QColor


class ModernTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(48)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 0, 20, 0)
        
        # Modern gradient background
        self.setStyleSheet('''
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6a9bcc, stop:1 #788c5d);
            }
        ''')
        
        self.logo_label = QLabel('AnalyX')
        self.logo_label.setFont(QFont('Poppins', 14, QFont.Weight.Bold))
        self.logo_label.setStyleSheet('color: #faf9f5;')
        
        self.title_label = QLabel('学术统计软件')
        self.title_label.setFont(QFont('Lora', 11))
        self.title_label.setStyleSheet('color: #faf9f5;')
        
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.logo_label)
        title_layout.addWidget(QLabel(' - '))
        title_layout.addWidget(self.title_label)
        title_layout.setSpacing(8)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # Modern minimize button
        self.min_button = QPushButton('—')
        self.min_button.setFixedSize(32, 32)
        self.min_button.setStyleSheet('''
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: #faf9f5;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        ''')
        self.min_button.clicked.connect(self.parent.showMinimized)
        
        # Modern maximize button
        self.max_button = QPushButton('□')
        self.max_button.setFixedSize(32, 32)
        self.max_button.setStyleSheet('''
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: #faf9f5;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        ''')
        self.max_button.clicked.connect(self.toggle_maximize)
        
        # Modern close button
        self.close_button = QPushButton('✕')
        self.close_button.setFixedSize(32, 32)
        self.close_button.setStyleSheet('''
            QPushButton {
                background-color: rgba(217, 119, 87, 0.7);
                color: #faf9f5;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(217, 119, 87, 0.9);
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
