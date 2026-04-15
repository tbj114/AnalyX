from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class ModernStatusBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(24, 10, 24, 10)
        self.layout.setSpacing(24)
        
        self.setFixedHeight(44)
        self.setStyleSheet('''
            ModernStatusBar {
                background-color: #f8fafc;
                border-top: 1px solid #e2e8f0;
            }
        ''')
        
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(10)
        
        status_dot = QLabel('●')
        status_dot.setStyleSheet('color: #10b981; font-size: 10px;')
        
        self.status_label = QLabel('就绪')
        self.status_label.setFont(QFont('Inter', 11))
        self.status_label.setStyleSheet('color: #475569;')
        
        status_layout.addWidget(status_dot)
        status_layout.addWidget(self.status_label)
        
        self.data_info_label = QLabel('无数据')
        self.data_info_label.setFont(QFont('Inter', 11, QFont.Weight.Medium))
        self.data_info_label.setStyleSheet('color: #6366f1;')
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(220)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                background-color: #e2e8f0;
                border: none;
                border-radius: 4px;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 4px;
            }
        ''')
        
        self.layout.addWidget(status_container)
        self.layout.addWidget(self.data_info_label)
        self.layout.addStretch()
        self.layout.addWidget(self.progress_bar)
