from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtGui import QPalette, QColor, QFont


class ModernStatusBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 8, 20, 8)
        self.layout.setSpacing(20)
        
        # Modern background
        self.setStyleSheet('''
            QWidget {
                background-color: #f8f7f3;
                border-top: 1px solid #e8e6dc;
            }
        ''')
        
        self.status_label = QLabel('就绪')
        self.status_label.setFont(QFont('Lora', 10))
        self.status_label.setStyleSheet('color: #141413; font-size: 10px;')
        
        self.data_info_label = QLabel('无数据')
        self.data_info_label.setFont(QFont('Lora', 10))
        self.data_info_label.setStyleSheet('color: #788c5d; font-size: 10px;')
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                background-color: #e8e6dc;
                border: none;
                border-radius: 6px;
                text-align: center;
                color: #141413;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #6a9bcc;
                border-radius: 6px;
            }
        ''')
        
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.data_info_label)
        self.layout.addStretch()
        self.layout.addWidget(self.progress_bar)
