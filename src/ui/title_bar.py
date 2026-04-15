from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient


class ModernTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(56)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(24, 0, 16, 0)
        self.layout.setSpacing(16)
        
        self.is_moving = False
        self.start_pos = QPoint()
        
        self.init_ui()
    
    def init_ui(self):
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(12)
        
        app_icon = QLabel('AX')
        app_icon.setFixedSize(36, 36)
        app_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_icon.setFont(QFont('Inter', 14, QFont.Weight.Bold))
        app_icon.setStyleSheet('''
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366f1, stop:1 #8b5cf6);
                color: white;
                border-radius: 10px;
            }
        ''')
        
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        
        app_name = QLabel('AnalyX')
        app_name.setFont(QFont('Inter', 14, QFont.Weight.Bold))
        app_name.setStyleSheet('color: #1e293b;')
        
        subtitle = QLabel('专业统计分析平台')
        subtitle.setFont(QFont('Inter', 10))
        subtitle.setStyleSheet('color: #64748b;')
        
        title_layout.addWidget(app_name)
        title_layout.addWidget(subtitle)
        
        logo_layout.addWidget(app_icon)
        logo_layout.addWidget(title_container)
        
        window_buttons = QWidget()
        window_buttons_layout = QHBoxLayout(window_buttons)
        window_buttons_layout.setContentsMargins(0, 0, 0, 0)
        window_buttons_layout.setSpacing(8)
        
        self.min_button = self.create_window_button('−', '#fbbf24', '#f59e0b')
        self.min_button.clicked.connect(self.parent.showMinimized)
        
        self.max_button = self.create_window_button('□', '#22c55e', '#16a34a')
        self.max_button.clicked.connect(self.toggle_maximize)
        
        self.close_button = self.create_window_button('×', '#ef4444', '#dc2626')
        self.close_button.clicked.connect(self.parent.close)
        
        window_buttons_layout.addWidget(self.min_button)
        window_buttons_layout.addWidget(self.max_button)
        window_buttons_layout.addWidget(self.close_button)
        
        self.layout.addWidget(logo_container)
        self.layout.addStretch()
        self.layout.addWidget(window_buttons)
        
        self.setStyleSheet('''
            ModernTitleBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e2e8f0;
            }
        ''')
    
    def create_window_button(self, symbol, bg_color, hover_color):
        btn = QPushButton(symbol)
        btn.setFixedSize(32, 32)
        btn.setFont(QFont('Inter', 14, QFont.Weight.Medium))
        btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
            }}
        ''')
        return btn
    
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
