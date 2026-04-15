from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtGui import QPalette, QColor


class ModernStatusBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 4, 10, 4)
        self.layout.setSpacing(15)
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 25))
        self.setPalette(palette)
        
        self.status_label = QLabel('就绪')
        self.status_label.setStyleSheet('color: #b0aea5; font-size: 11px;')
        
        self.data_info_label = QLabel('无数据')
        self.data_info_label.setStyleSheet('color: #788c5d; font-size: 11px;')
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                background-color: #2a2a30;
                border: 1px solid #3a3a40;
                border-radius: 3px;
                text-align: center;
                color: #faf9f5;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #6a9bcc;
                border-radius: 2px;
            }
        ''')
        
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.data_info_label)
        self.layout.addStretch()
        self.layout.addWidget(self.progress_bar)
