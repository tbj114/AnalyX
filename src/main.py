import sys
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
# 确保Qt界面也使用中文字体
matplotlib.rc('font', family='sans-serif')
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QSplitter, QListWidget,
    QTextEdit, QMenuBar, QToolBar, QStatusBar, QFileDialog,
    QMessageBox, QDialog, QFormLayout, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QProgressBar, QTabWidget, QDockWidget,
    QHeaderView, QInputDialog, QCheckBox, QGridLayout, QFrame,
    QLineEdit, QSizePolicy, QMenu, QAction, QStyledItemDelegate
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import (
    QAction, QIcon, QFont, QPalette, QColor, QPainter, QBrush, QPen, 
    QLinearGradient, QFontDatabase, QPixmap, QImage, QPainterPath, QRadialGradient
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class EditableHeaderView(QHeaderView):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.editing_index = -1
        self.editor = None
    
    def mouseDoubleClickEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if index >= 0:
            self.edit_header(index)
        super().mouseDoubleClickEvent(event)
    
    def edit_header(self, index):
        if self.editing_index != -1:
            self.finish_editing()
        
        self.editing_index = index
        rect = self.sectionRect(index)
        
        self.editor = QLineEdit(self)
        self.editor.setText(self.model().headerData(index, self.orientation()))
        self.editor.setGeometry(rect)
        self.editor.selectAll()
        self.editor.setFocus()
        
        self.editor.editingFinished.connect(self.finish_editing)
        self.editor.show()
    
    def finish_editing(self):
        if self.editing_index != -1 and self.editor:
            new_text = self.editor.text()
            if new_text:
                old_text = self.model().headerData(self.editing_index, self.orientation())
                if old_text != new_text:
                    self.model().setHeaderData(self.editing_index, self.orientation(), new_text)
                    self.parent().on_header_changed(self.editing_index, new_text)
            
            self.editor.deleteLater()
            self.editor = None
            self.editing_index = -1


class ModernTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(36)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 0, 15, 0)
        
        # 创建背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 25))
        self.setPalette(palette)
        
        # 软件标志
        self.logo_label = QLabel('AnalyX')
        self.logo_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        self.logo_label.setStyleSheet('color: #6a9bcc;')
        
        # 窗口标题
        self.title_label = QLabel('学术统计软件')
        self.title_label.setFont(QFont('Arial', 10))
        self.title_label.setStyleSheet('color: #faf9f5;')
        
        # 标题布局
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.logo_label)
        title_layout.addWidget(QLabel(' - '))
        title_layout.addWidget(self.title_label)
        title_layout.setSpacing(4)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)
        
        # 最小化按钮
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
        
        # 最大化/还原按钮
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
        
        # 关闭按钮
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
        
        # 鼠标事件
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


class ModernMenuBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(0)
        
        # 创建背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(25, 25, 30))
        self.setPalette(palette)
        
        # 菜单按钮
        menu_items = [
            ('文件', [
                ('新建项目', 'Ctrl+N', self.parent.new_project),
                ('打开文件', 'Ctrl+O', self.parent.open_file),
                ('-', None, None),
                ('导入', None, None, [
                    ('CSV 文件', None, self.parent.import_csv),
                    ('Excel 文件', None, self.parent.import_excel),
                    ('SPSS .sav 文件', None, self.parent.import_spss)
                ]),
                ('-', None, None),
                ('保存', 'Ctrl+S', self.parent.save_file),
                ('另存为', 'Ctrl+Shift+S', self.parent.save_file_as),
                ('-', None, None),
                ('导出', None, None, [
                    ('CSV 文件', None, self.parent.export_csv),
                    ('PDF 文档', None, self.parent.export_pdf)
                ]),
                ('-', None, None),
                ('退出', 'Ctrl+Q', self.parent.close)
            ]),
            ('分析', [
                ('描述统计', None, self.parent.show_descriptive_stats),
                ('-', None, None),
                ('t 检验', None, None, [
                    ('单样本 t 检验', None, self.parent.show_ttest_one_sample),
                    ('独立样本 t 检验', None, self.parent.show_ttest_independent),
                    ('配对样本 t 检验', None, self.parent.show_ttest_paired)
                ]),
                ('-', None, None),
                ('单因素 ANOVA', None, self.parent.show_anova),
                ('-', None, None),
                ('相关分析', None, self.parent.show_correlation),
                ('回归分析', None, self.parent.show_regression),
                ('-', None, None),
                ('信度分析', None, self.parent.show_reliability)
            ]),
            ('图表', [
                ('直方图', None, self.parent.show_histogram),
                ('箱线图', None, self.parent.show_boxplot),
                ('散点图', None, self.parent.show_scatterplot),
                ('条形图', None, self.parent.show_barchart),
                ('热力图', None, self.parent.show_heatmap)
            ]),
            ('工具', [
                ('切换主题', None, self.parent.toggle_theme),
                ('-', None, None),
                ('关于', None, self.parent.show_about)
            ])
        ]
        
        for menu_name, items in menu_items:
            menu_button = QPushButton(menu_name)
            menu_button.setStyleSheet('''
                QPushButton {
                    background-color: transparent;
                    color: #b0aea5;
                    border: none;
                    padding: 8px 16px;
                    font-size: 11px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: rgba(106, 155, 204, 0.1);
                    color: #6a9bcc;
                }
            ''')
            # 添加下拉菜单功能
            menu = QMenu(menu_button)
            self.add_menu_items(menu, items)
            menu_button.setMenu(menu)
            self.layout.addWidget(menu_button)
    
    def add_menu_items(self, menu, items):
        for item in items:
            if len(item) == 3:
                text, shortcut, callback = item
                if text == '-':
                    menu.addSeparator()
                else:
                    action = QAction(text, menu)
                    if shortcut:
                        action.setShortcut(shortcut)
                    action.triggered.connect(callback)
                    menu.addAction(action)
            elif len(item) == 4:
                text, shortcut, callback, subitems = item
                submenu = menu.addMenu(text)
                self.add_menu_items(submenu, subitems)


class ModernToolBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(8)
        
        # 创建背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(22, 22, 27))
        self.setPalette(palette)
        
        # 工具栏按钮
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
        
        # 添加分隔符
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet('background-color: #3a3a40; margin: 0 8px;')
        self.layout.addWidget(separator)
        
        # 搜索框
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


class ModernStatusBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 4, 10, 4)
        self.layout.setSpacing(15)
        
        # 创建背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 25))
        self.setPalette(palette)
        
        # 状态标签
        self.status_label = QLabel('就绪')
        self.status_label.setStyleSheet('color: #b0aea5; font-size: 11px;')
        
        # 数据信息
        self.data_info_label = QLabel('无数据')
        self.data_info_label.setStyleSheet('color: #788c5d; font-size: 11px;')
        
        # 进度条
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


class AnalyXMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 移除默认标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.df = pd.DataFrame()
        self.current_file = None
        self.dark_theme = True  # 默认使用深色主题
        self.init_ui()

    def init_ui(self):
        # 设置窗口属性
        self.setWindowTitle('AnalyX - 学术统计软件')
        self.setMinimumSize(1400, 900)
        
        # 创建主容器
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加自定义标题栏
        self.title_bar = ModernTitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # 创建菜单栏
        self.menu_bar = ModernMenuBar(self)
        self.main_layout.addWidget(self.menu_bar)
        
        # 创建工具栏
        self.tool_bar = ModernToolBar(self)
        self.main_layout.addWidget(self.tool_bar)
        
        # 创建内容区域
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # 创建侧边栏
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 侧边栏头部
        sidebar_header = QWidget()
        sidebar_header.setFixedHeight(40)
        sidebar_header_layout = QVBoxLayout(sidebar_header)
        sidebar_header_layout.setContentsMargins(15, 0, 15, 0)
        sidebar_header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sidebar_title = QLabel('分析工具')
        sidebar_title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        sidebar_title.setStyleSheet('color: #6a9bcc;')
        sidebar_header_layout.addWidget(sidebar_title)
        
        self.sidebar_layout.addWidget(sidebar_header)
        
        # 侧边栏导航
        self.nav_list = QListWidget()
        self.nav_list.addItems([
            '描述统计',
            't 检验',
            '方差分析',
            '相关分析',
            '回归分析',
            '信度分析',
            '图表绘制'
        ])
        self.nav_list.setStyleSheet('''
            QListWidget {
                background-color: #222227;
                color: #b0aea5;
                border: none;
                padding: 5px 0;
            }
            QListWidget::item {
                padding: 8px 15px;
                border-left: 2px solid transparent;
                font-size: 11px;
            }
            QListWidget::item:hover {
                background-color: rgba(106, 155, 204, 0.1);
                color: #6a9bcc;
            }
            QListWidget::item:selected {
                background-color: rgba(106, 155, 204, 0.2);
                color: #6a9bcc;
                border-left: 2px solid #6a9bcc;
            }
        ''')
        # 连接点击事件
        self.nav_list.itemClicked.connect(self.on_nav_item_clicked)
        self.sidebar_layout.addWidget(self.nav_list)
        
        # 侧边栏底部
        sidebar_footer = QWidget()
        sidebar_footer.setFixedHeight(50)
        sidebar_footer_layout = QVBoxLayout(sidebar_footer)
        sidebar_footer_layout.setContentsMargins(15, 0, 15, 0)
        
        version_label = QLabel('版本 1.0')
        version_label.setStyleSheet('color: #777777; font-size: 10px;')
        sidebar_footer_layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        
        self.sidebar_layout.addWidget(sidebar_footer)
        
        # 创建主工作区
        self.workspace = QWidget()
        self.workspace_layout = QVBoxLayout(self.workspace)
        self.workspace_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet('''
            QTabWidget {
                background-color: #1a1a20;
                color: #faf9f5;
            }
            QTabBar {
                background-color: #222227;
                height: 48px;
            }
            QTabBar::tab {
                background-color: #222227;
                color: #b0aea5;
                padding: 0 30px;
                font-size: 13px;
                font-weight: 500;
                border-bottom: 3px solid transparent;
            }
            QTabBar::tab:hover {
                background-color: #2a2a30;
                color: #faf9f5;
            }
            QTabBar::tab:selected {
                background-color: #1a1a20;
                color: #6a9bcc;
                border-bottom: 3px solid #6a9bcc;
            }
        ''')
        
        # 数据视图标签
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        # 使用自定义可编辑的表头
        self.header_view = EditableHeaderView(Qt.Orientation.Horizontal, self)
        self.data_table.setHorizontalHeader(self.header_view)
        self.data_table.setStyleSheet('''
            QTableWidget {
                background-color: #1a1a20;
                color: #faf9f5;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2a2a30;
            }
            QTableWidget::item:selected {
                background-color: rgba(106, 155, 204, 0.2);
                color: #6a9bcc;
            }
            QHeaderView::section {
                background-color: #222227;
                color: #b0aea5;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #3a3a40;
                font-size: 12px;
                font-weight: 500;
            }
        ''')
        # 连接单元格变化信号
        self.data_table.cellChanged.connect(self.on_cell_changed)
        self.tab_widget.addTab(self.data_table, '数据视图')
        
        # 分析结果标签
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont('Consolas', 11))
        self.results_text.setStyleSheet('''
            QTextEdit {
                background-color: #1a1a20;
                color: #faf9f5;
                border: none;
                padding: 20px;
            }
        ''')
        self.tab_widget.addTab(self.results_text, '分析结果')
        
        # 图表标签
        self.chart_canvas = FigureCanvas(Figure(figsize=(10, 7)))
        self.tab_widget.addTab(self.chart_canvas, '图表')
        
        self.workspace_layout.addWidget(self.tab_widget)
        
        # 添加到内容布局
        self.content_layout.addWidget(self.sidebar)
        self.content_layout.addWidget(self.workspace)
        
        # 创建状态栏
        self.status_bar = ModernStatusBar(self)
        
        # 添加到主布局
        self.main_layout.addWidget(self.content_widget)
        self.main_layout.addWidget(self.status_bar)
        
        # 应用主题
        self.apply_theme()
        
        # 加载示例数据
        self.load_sample_data()

    def create_menu_bar(self):
        self.menu_bar = QWidget()
        self.menu_bar_layout = QHBoxLayout(self.menu_bar)
        self.menu_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_bar_layout.setSpacing(0)
        
        # 创建菜单按钮
        menu_items = [
            ('文件(&F)', [
                ('新建项目(&N)', 'Ctrl+N', self.new_project),
                ('打开文件(&O)...', 'Ctrl+O', self.open_file),
                ('-', None, None),
                ('导入(&I)', None, None, [
                    ('CSV 文件...', None, self.import_csv),
                    ('Excel 文件...', None, self.import_excel),
                    ('SPSS .sav 文件...', None, self.import_spss)
                ]),
                ('-', None, None),
                ('保存(&S)', 'Ctrl+S', self.save_file),
                ('另存为(&A)...', 'Ctrl+Shift+S', self.save_file_as),
                ('-', None, None),
                ('导出(&E)', None, None, [
                    ('CSV 文件...', None, self.export_csv),
                    ('PDF 文档...', None, self.export_pdf)
                ]),
                ('-', None, None),
                ('退出(&X)', 'Ctrl+Q', self.close)
            ]),
            ('编辑(&E)', []),
            ('分析(&A)', [
                ('描述统计...', None, self.show_descriptive_stats),
                ('-', None, None),
                ('t 检验', None, None, [
                    ('单样本 t 检验...', None, self.show_ttest_one_sample),
                    ('独立样本 t 检验...', None, self.show_ttest_independent),
                    ('配对样本 t 检验...', None, self.show_ttest_paired)
                ]),
                ('-', None, None),
                ('单因素 ANOVA...', None, self.show_anova),
                ('-', None, None),
                ('相关分析...', None, self.show_correlation),
                ('回归分析...', None, self.show_regression),
                ('-', None, None),
                ('信度分析 (Cronbach α)...', None, self.show_reliability)
            ]),
            ('图表(&C)', [
                ('直方图...', None, self.show_histogram),
                ('箱线图...', None, self.show_boxplot),
                ('散点图...', None, self.show_scatterplot),
                ('条形图...', None, self.show_barchart),
                ('热力图...', None, self.show_heatmap)
            ]),
            ('工具(&T)', [
                ('切换主题(&D)', None, self.toggle_theme)
            ]),
            ('帮助(&H)', [
                ('关于 AnalyX(&A)...', None, self.show_about)
            ])
        ]
        
        for menu_name, items in menu_items:
            menu_button = QPushButton(menu_name)
            menu_button.setStyleSheet('''
                QPushButton {
                    background-color: #333333;
                    color: #ffffff;
                    border: none;
                    padding: 8px 12px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
            ''')
            self.menu_bar_layout.addWidget(menu_button)

    def create_tool_bar(self):
        self.tool_bar = QWidget()
        self.tool_bar_layout = QHBoxLayout(self.tool_bar)
        self.tool_bar_layout.setContentsMargins(10, 5, 10, 5)
        self.tool_bar_layout.setSpacing(10)
        
        # 创建工具栏按钮
        tool_buttons = [
            ('新建', self.new_project),
            ('打开', self.open_file),
            ('保存', self.save_file)
        ]
        
        for text, callback in tool_buttons:
            button = QPushButton(text)
            button.setStyleSheet('''
                QPushButton {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
            ''')
            button.clicked.connect(callback)
            self.tool_bar_layout.addWidget(button)
        
        # 添加分隔符
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet('background-color: #444444;')
        self.tool_bar_layout.addWidget(separator)

    def create_status_bar(self):
        self.status_bar = QWidget()
        self.status_bar_layout = QHBoxLayout(self.status_bar)
        self.status_bar_layout.setContentsMargins(10, 5, 10, 5)
        self.status_bar_layout.setSpacing(10)
        
        self.status_label = QLabel('就绪')
        self.status_label.setStyleSheet('color: #cccccc; font-size: 12px;')
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
                height: 16px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        ''')
        
        self.status_bar_layout.addWidget(self.status_label, 1)
        self.status_bar_layout.addWidget(self.progress_bar)

    def create_central_widget(self):
        self.central_widget = QWidget()
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(220)
        self.nav_list.addItems([
            '描述统计',
            't 检验',
            '方差分析',
            '相关分析',
            '回归分析',
            '信度分析',
            '图表绘制'
        ])
        # 连接点击事件
        self.nav_list.itemClicked.connect(self.on_nav_item_clicked)
        # 添加样式
        self.nav_list.setStyleSheet('''
            QListWidget {
                background-color: #2a2a2a;
                color: #ffffff;
                border: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
        ''')
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        # 添加样式
        self.tab_widget.setStyleSheet('''
            QTabWidget {
                background-color: #222222;
                color: #ffffff;
            }
            QTabBar {
                background-color: #2a2a2a;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #cccccc;
                padding: 10px 20px;
                border-bottom: 1px solid #333333;
            }
            QTabBar::tab:hover {
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QTabBar::tab:selected {
                background-color: #222222;
                color: #ffffff;
                border-bottom: 2px solid #3498db;
            }
        ''')
        
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        # 连接单元格变化信号
        self.data_table.cellChanged.connect(self.on_cell_changed)
        # 添加样式
        self.data_table.setStyleSheet('''
            QTableWidget {
                background-color: #222222;
                color: #ffffff;
                border: 1px solid #333333;
            }
            QTableWidget::item {
                border: 1px solid #333333;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #333333;
            }
        ''')
        self.tab_widget.addTab(self.data_table, '数据视图')
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont('Consolas', 10))
        # 添加样式
        self.results_text.setStyleSheet('''
            QTextEdit {
                background-color: #222222;
                color: #ffffff;
                border: 1px solid #333333;
                padding: 10px;
            }
        ''')
        self.tab_widget.addTab(self.results_text, '分析结果')
        
        self.chart_canvas = FigureCanvas(Figure(figsize=(10, 7)))
        self.tab_widget.addTab(self.chart_canvas, '图表')
        
        right_layout.addWidget(self.tab_widget)
        
        self.splitter.addWidget(self.nav_list)
        self.splitter.addWidget(right_widget)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(self.splitter)

    def create_dock_widgets(self):
        pass

    def apply_theme(self):
        # 应用深色主题
        palette = QPalette()
        # 主背景色
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 35))
        # 文本颜色
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        # 基础背景色
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 30))
        # 交替背景色
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 40, 45))
        # 工具提示背景
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(50, 50, 55))
        # 工具提示文本
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
        # 文本颜色
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        # 按钮背景
        palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 50))
        # 按钮文本
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        # 亮色文本
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 70, 70))
        # 链接颜色
        palette.setColor(QPalette.ColorRole.Link, QColor(70, 140, 255))
        # 高亮颜色
        palette.setColor(QPalette.ColorRole.Highlight, QColor(70, 140, 255))
        # 高亮文本
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(20, 20, 25))
        QApplication.setPalette(palette)
        # 使用更现代的深色样式
        plt.style.use('seaborn-v0_8-dark')
        # 设置内容区域样式
        self.content_widget.setStyleSheet('''
            QWidget {
                background-color: #222222;
                border: 1px solid #333333;
            }
        ''')
        # 设置主窗口样式
        self.main_widget.setStyleSheet('''
            QWidget {
                background-color: #1a1a1a;
            }
        ''')

    def load_sample_data(self):
        np.random.seed(42)
        n = 100
        self.df = pd.DataFrame({
            '年龄': np.random.randint(18, 60, n),
            '收入': np.random.normal(8000, 2000, n),
            '满意度': np.random.randint(1, 6, n),
            '工作年限': np.random.randint(0, 30, n),
            '绩效得分': np.random.normal(75, 10, n)
        })
        self.update_data_table()

    def update_data_table(self):
        self.data_table.setRowCount(len(self.df))
        self.data_table.setColumnCount(len(self.df.columns))
        self.data_table.setHorizontalHeaderLabels(self.df.columns)
        
        for row in range(len(self.df)):
            for col in range(len(self.df.columns)):
                value = self.df.iloc[row, col]
                if pd.isna(value):
                    item = QTableWidgetItem('')
                else:
                    item = QTableWidgetItem(str(value))
                self.data_table.setItem(row, col, item)
        
    def on_cell_changed(self, row, col):
        # 当单元格内容改变时更新DataFrame
        item = self.data_table.item(row, col)
        if item:
            value = item.text()
            try:
                # 尝试转换为数值
                if value == '':
                    self.df.iloc[row, col] = pd.NA
                else:
                    # 尝试转换为float，如果失败则保持为字符串
                    try:
                        self.df.iloc[row, col] = float(value)
                    except ValueError:
                        self.df.iloc[row, col] = value
            except Exception as e:
                pass
    
    def on_header_changed(self, col, new_name):
        # 当表头内容改变时更新DataFrame的列名
        if 0 <= col < len(self.df.columns):
            old_name = self.df.columns[col]
            if old_name != new_name:
                # 重命名DataFrame的列
                new_columns = list(self.df.columns)
                new_columns[col] = new_name
                self.df.columns = new_columns
    
    def on_nav_item_clicked(self, item):
        # 处理侧边栏点击事件
        text = item.text()
        if text == '描述统计':
            self.show_descriptive_stats()
        elif text == 't 检验':
            # 显示t检验子菜单或默认打开单样本t检验
            self.show_ttest_one_sample()
        elif text == '方差分析':
            self.show_anova()
        elif text == '相关分析':
            self.show_correlation()
        elif text == '回归分析':
            self.show_regression()
        elif text == '信度分析':
            self.show_reliability()
        elif text == '图表绘制':
            # 显示图表子菜单或默认打开直方图
            self.show_histogram()

    def new_project(self):
        reply = QMessageBox.question(
            self, '确认', '当前项目未保存，是否继续？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # 创建空的DataFrame，包含100列
            columns = [f'变量{i}' for i in range(1, 101)]
            data = {col: pd.Series(dtype='float64') for col in columns}
            self.df = pd.DataFrame(data)
            # 添加100行空数据
            self.df = self.df.reindex(range(100))
            self.current_file = None
            self.update_data_table()
            self.results_text.clear()
            self.status_bar.status_label.setText('新项目已创建')

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '打开文件', '',
            'CSV 文件 (*.csv);;Excel 文件 (*.xlsx *.xls);;SPSS 文件 (*.sav);;所有文件 (*.*)'
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                self.df = pd.read_csv(file_path)
            elif ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(file_path)
            elif ext == '.sav':
                import pyreadstat
                self.df, _ = pyreadstat.read_sav(file_path)
            else:
                QMessageBox.warning(self, '错误', '不支持的文件格式')
                return
            
            self.current_file = file_path
            self.update_data_table()
            self.status_bar.status_label.setText(f'已加载: {os.path.basename(file_path)}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载文件失败: {str(e)}')

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '导入 CSV', '', 'CSV 文件 (*.csv)'
        )
        if file_path:
            self.load_file(file_path)

    def import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '导入 Excel', '', 'Excel 文件 (*.xlsx *.xls)'
        )
        if file_path:
            self.load_file(file_path)

    def import_spss(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '导入 SPSS', '', 'SPSS 文件 (*.sav)'
        )
        if file_path:
            self.load_file(file_path)

    def save_file(self):
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, '另存为', '',
            'CSV 文件 (*.csv);;Excel 文件 (*.xlsx);;所有文件 (*.*)'
        )
        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path

    def save_to_file(self, file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                self.df.to_csv(file_path, index=False)
            elif ext in ['.xlsx', '.xls']:
                self.df.to_excel(file_path, index=False)
            else:
                self.df.to_csv(file_path, index=False)
            self.status_bar.status_label.setText(f'已保存: {os.path.basename(file_path)}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存文件失败: {str(e)}')

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, '导出 CSV', '', 'CSV 文件 (*.csv)'
        )
        if file_path:
            self.save_to_file(file_path)

    def export_pdf(self):
        QMessageBox.information(self, '提示', 'PDF 导出功能开发中')

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        if self.dark_theme:
            self.apply_theme()
        else:
            # 应用浅色主题
            QApplication.setPalette(QApplication.style().standardPalette())
            plt.style.use('seaborn-v0_8-whitegrid')
            # 更新样式
            self.title_bar.setStyleSheet('''
                QWidget {
                    background-color: #f0f0f0;
                }
                QLabel {
                    color: #333333;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            ''')
            self.menu_bar.setStyleSheet('''
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            ''')
            self.tool_bar.setStyleSheet('''
                QPushButton {
                    background-color: #f0f0f0;
                    color: #333333;
                    border: 1px solid #d0d0d0;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            ''')
            self.status_bar.setStyleSheet('''
                QWidget {
                    background-color: #f0f0f0;
                }
                QLabel {
                    color: #333333;
                }
            ''')
            self.content_widget.setStyleSheet('''
                QWidget {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                }
            ''')
            self.main_widget.setStyleSheet('''
                QWidget {
                    background-color: #e0e0e0;
                }
            ''')
        self.status_bar.status_label.setText('已切换主题')

    def show_about(self):
        QMessageBox.about(
            self, '关于 AnalyX',
            '<h2>AnalyX 1.0</h2>'
            '<p>学术统计分析软件</p>'
            '<p>功能全面超越 SPSS，速度更快</p>'
            '<p>支持：描述统计、t 检验、ANOVA、相关、回归、信度分析等</p>'
            '<p>© 2024 AnalyX. All rights reserved.</p>'
        )

    def show_descriptive_stats(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self, '警告', '没有数值型数据')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('描述统计')
        dialog.resize(500, 400)
        
        # 使用更现代的布局
        main_layout = QVBoxLayout(dialog)
        
        # 变量选择区域
        var_group = QWidget()
        var_layout = QVBoxLayout(var_group)
        var_layout.addWidget(QLabel('选择变量 (可多选):'))
        
        var_list = QListWidget()
        var_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        var_list.addItems(numeric_cols)
        # 默认选择第一个变量
        if numeric_cols:
            var_list.setCurrentRow(0)
        var_layout.addWidget(var_list)
        main_layout.addWidget(var_group)
        
        # 统计量选项
        stats_group = QWidget()
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.addWidget(QLabel('选择统计量:'))
        
        stats_grid = QWidget()
        grid_layout = QGridLayout(stats_grid)
        
        # 统计量复选框
        mean_check = QCheckBox('均值')
        mean_check.setChecked(True)
        median_check = QCheckBox('中位数')
        median_check.setChecked(True)
        std_check = QCheckBox('标准差')
        std_check.setChecked(True)
        var_check = QCheckBox('方差')
        var_check.setChecked(True)
        min_check = QCheckBox('最小值')
        min_check.setChecked(True)
        max_check = QCheckBox('最大值')
        max_check.setChecked(True)
        range_check = QCheckBox('全距')
        range_check.setChecked(True)
        skew_check = QCheckBox('偏度')
        skew_check.setChecked(True)
        kurtosis_check = QCheckBox('峰度')
        kurtosis_check.setChecked(True)
        percentiles_check = QCheckBox('百分位数')
        percentiles_check.setChecked(False)
        
        grid_layout.addWidget(mean_check, 0, 0)
        grid_layout.addWidget(median_check, 0, 1)
        grid_layout.addWidget(std_check, 1, 0)
        grid_layout.addWidget(var_check, 1, 1)
        grid_layout.addWidget(min_check, 2, 0)
        grid_layout.addWidget(max_check, 2, 1)
        grid_layout.addWidget(range_check, 3, 0)
        grid_layout.addWidget(skew_check, 3, 1)
        grid_layout.addWidget(kurtosis_check, 4, 0)
        grid_layout.addWidget(percentiles_check, 4, 1)
        
        stats_layout.addWidget(stats_grid)
        main_layout.addWidget(stats_group)
        
        # 置信区间选项
        ci_group = QWidget()
        ci_layout = QHBoxLayout(ci_group)
        ci_check = QCheckBox('计算95%置信区间')
        ci_check.setChecked(False)
        ci_layout.addWidget(ci_check)
        main_layout.addWidget(ci_group)
        
        # 图表选项
        chart_group = QWidget()
        chart_layout = QHBoxLayout(chart_group)
        chart_check = QCheckBox('生成直方图')
        chart_check.setChecked(False)
        chart_layout.addWidget(chart_check)
        main_layout.addWidget(chart_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        calculate_btn = QPushButton('计算')
        calculate_btn.setDefault(True)
        btn_layout.addWidget(calculate_btn)
        
        main_layout.addLayout(btn_layout)
        
        def calculate():
            selected_items = [item.text() for item in var_list.selectedItems()]
            if not selected_items:
                QMessageBox.warning(self, '警告', '请至少选择一个变量')
                return
            
            result_html = '<h2>描述统计结果</h2>'
            
            for col in selected_items:
                data = self.df[col].dropna()
                desc = stats.describe(data)
                
                result_html += f'<h3>{col}</h3>'
                result_html += '''<table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
                <tr><td><b>样本数</b></td><td>{desc.nobs}</td></tr>'''.format(desc=desc)
                
                if mean_check.isChecked():
                    result_html += f'<tr><td><b>均值</b></td><td>{desc.mean:.4f}</td></tr>'
                if median_check.isChecked():
                    result_html += f'<tr><td><b>中位数</b></td><td>{np.median(data):.4f}</td></tr>'
                if std_check.isChecked():
                    result_html += f'<tr><td><b>标准差</b></td><td>{np.std(data, ddof=1):.4f}</td></tr>'
                if var_check.isChecked():
                    result_html += f'<tr><td><b>方差</b></td><td>{desc.variance:.4f}</td></tr>'
                if min_check.isChecked():
                    result_html += f'<tr><td><b>最小值</b></td><td>{desc.minmax[0]:.4f}</td></tr>'
                if max_check.isChecked():
                    result_html += f'<tr><td><b>最大值</b></td><td>{desc.minmax[1]:.4f}</td></tr>'
                if range_check.isChecked():
                    result_html += f'<tr><td><b>全距</b></td><td>{desc.minmax[1] - desc.minmax[0]:.4f}</td></tr>'
                if skew_check.isChecked():
                    result_html += f'<tr><td><b>偏度</b></td><td>{desc.skewness:.4f}</td></tr>'
                if kurtosis_check.isChecked():
                    result_html += f'<tr><td><b>峰度</b></td><td>{desc.kurtosis:.4f}</td></tr>'
                if percentiles_check.isChecked():
                    percentiles = np.percentile(data, [25, 50, 75])
                    result_html += f'<tr><td><b>25%分位数</b></td><td>{percentiles[0]:.4f}</td></tr>'
                    result_html += f'<tr><td><b>50%分位数</b></td><td>{percentiles[1]:.4f}</td></tr>'
                    result_html += f'<tr><td><b>75%分位数</b></td><td>{percentiles[2]:.4f}</td></tr>'
                if ci_check.isChecked():
                    ci = stats.t.interval(0.95, len(data)-1, loc=np.mean(data), scale=stats.sem(data))
                    result_html += f'<tr><td><b>95%置信区间</b></td><td>[{ci[0]:.4f}, {ci[1]:.4f}]</td></tr>'
                
                result_html += '</table><br>'
                
                # 生成直方图
                if chart_check.isChecked():
                    self.chart_canvas.figure.clear()
                    ax = self.chart_canvas.figure.add_subplot(111)
                    ax.hist(data, bins='auto', edgecolor='black', alpha=0.7)
                    ax.set_title(f'直方图 - {col}')
                    ax.set_xlabel(col)
                    ax.set_ylabel('频数')
                    ax.grid(True, alpha=0.3)
                    self.chart_canvas.draw()
                    self.tab_widget.setCurrentWidget(self.chart_canvas)
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            dialog.accept()
        
        calculate_btn.clicked.connect(calculate)
        dialog.exec()

    def show_ttest_one_sample(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self, '警告', '没有数值型数据')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('单样本 t 检验')
        dialog.resize(450, 350)
        
        main_layout = QVBoxLayout(dialog)
        
        # 变量选择
        var_group = QWidget()
        var_layout = QVBoxLayout(var_group)
        var_layout.addWidget(QLabel('选择变量:'))
        
        combo = QComboBox()
        combo.addItems(numeric_cols)
        var_layout.addWidget(combo)
        main_layout.addWidget(var_group)
        
        # 检验值
        test_value_group = QWidget()
        test_value_layout = QHBoxLayout(test_value_group)
        test_value_layout.addWidget(QLabel('检验值:'))
        
        test_value = QDoubleSpinBox()
        test_value.setRange(-1e9, 1e9)
        test_value.setValue(0)
        test_value.setDecimals(4)
        test_value_layout.addWidget(test_value)
        main_layout.addWidget(test_value_group)
        
        # 选项
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        options_layout.addWidget(QLabel('选项:'))
        
        # 置信水平
        ci_group = QWidget()
        ci_layout = QHBoxLayout(ci_group)
        ci_layout.addWidget(QLabel('置信水平:'))
        
        ci_combo = QComboBox()
        ci_combo.addItems(['90%', '95%', '99%'])
        ci_combo.setCurrentText('95%')
        ci_layout.addWidget(ci_combo)
        options_layout.addWidget(ci_group)
        
        # 图表选项
        chart_check = QCheckBox('生成箱线图')
        chart_check.setChecked(False)
        options_layout.addWidget(chart_check)
        
        # 效应量
        effect_size_check = QCheckBox('计算效应量 (Cohen\'s d)')
        effect_size_check.setChecked(True)
        options_layout.addWidget(effect_size_check)
        
        main_layout.addWidget(options_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        calculate_btn = QPushButton('计算')
        calculate_btn.setDefault(True)
        btn_layout.addWidget(calculate_btn)
        
        main_layout.addLayout(btn_layout)
        
        def calculate():
            col = combo.currentText()
            data = self.df[col].dropna()
            
            # 获取置信水平
            ci_level = float(ci_combo.currentText().strip('%')) / 100
            
            # 执行t检验
            t_stat, p_val = stats.ttest_1samp(data, test_value.value())
            mean_diff = np.mean(data) - test_value.value()
            se_diff = stats.sem(data)
            ci = stats.t.interval(ci_level, len(data)-1, loc=np.mean(data), scale=se_diff)
            
            # 计算效应量
            cohens_d = mean_diff / np.std(data, ddof=1)
            
            result_html = f'''
            <h2>单样本 t 检验 - {col}</h2>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>t 值</b></td><td>{t_stat:.4f}</td></tr>
            <tr><td><b>自由度</b></td><td>{len(data)-1}</td></tr>
            <tr><td><b>P 值</b></td><td>{p_val:.6f}</td></tr>
            <tr><td><b>显著性</b></td><td>{'显著 (p < 0.05)' if p_val < 0.05 else '不显著'}</td></tr>
            <tr><td><b>均值差</b></td><td>{mean_diff:.4f}</td></tr>
            <tr><td><b>标准误差</b></td><td>{se_diff:.4f}</td></tr>
            <tr><td><b>{int(ci_level*100)}% 置信区间</b></td><td>[{ci[0]-test_value.value():.4f}, {ci[1]-test_value.value():.4f}]</td></tr>
            '''
            
            if effect_size_check.isChecked():
                result_html += f'<tr><td><b>Cohen\'s d</b></td><td>{cohens_d:.4f}</td></tr>'
            
            result_html += '</table>'
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            
            # 生成箱线图
            if chart_check.isChecked():
                self.chart_canvas.figure.clear()
                ax = self.chart_canvas.figure.add_subplot(111)
                ax.boxplot(data, vert=True)
                ax.axhline(y=test_value.value(), color='r', linestyle='--', label=f'检验值: {test_value.value()}')
                ax.set_title(f'箱线图 - {col}')
                ax.set_ylabel(col)
                ax.grid(True, alpha=0.3, axis='y')
                ax.legend()
                self.chart_canvas.draw()
                self.tab_widget.setCurrentWidget(self.chart_canvas)
            
            dialog.accept()
        
        calculate_btn.clicked.connect(calculate)
        dialog.exec()

    def show_ttest_independent(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = self.df.columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self, '警告', '没有数值型数据')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('独立样本 t 检验')
        layout = QFormLayout(dialog)
        
        test_var_combo = QComboBox()
        test_var_combo.addItems(numeric_cols)
        layout.addRow('检验变量:', test_var_combo)
        
        group_var_combo = QComboBox()
        group_var_combo.addItems(all_cols)
        layout.addRow('分组变量:', group_var_combo)
        
        btn = QPushButton('计算')
        layout.addRow(btn)
        
        def calculate():
            test_col = test_var_combo.currentText()
            group_col = group_var_combo.currentText()
            
            groups = self.df.groupby(group_col)[test_col].apply(list)
            if len(groups) != 2:
                QMessageBox.warning(self, '警告', '分组变量必须有且仅有2个组别')
                return
            
            group1 = groups.iloc[0]
            group2 = groups.iloc[1]
            group1 = [x for x in group1 if pd.notna(x)]
            group2 = [x for x in group2 if pd.notna(x)]
            
            t_stat, p_val = stats.ttest_ind(group1, group2)
            mean1 = np.mean(group1)
            mean2 = np.mean(group2)
            
            result_html = f'''
            <h2>独立样本 t 检验</h2>
            <p>检验变量: {test_col}, 分组变量: {group_col}</p>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>组1均值</b></td><td>{mean1:.4f}</td></tr>
            <tr><td><b>组2均值</b></td><td>{mean2:.4f}</td></tr>
            <tr><td><b>均值差</b></td><td>{mean1 - mean2:.4f}</td></tr>
            <tr><td><b>t 值</b></td><td>{t_stat:.4f}</td></tr>
            <tr><td><b>P 值</b></td><td>{p_val:.6f}</td></tr>
            <tr><td><b>显著性</b></td><td>{'显著 (p < 0.05)' if p_val < 0.05 else '不显著'}</td></tr>
            </table>
            '''
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            dialog.accept()
        
        btn.clicked.connect(calculate)
        dialog.exec()

    def show_ttest_paired(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('配对样本 t 检验')
        layout = QFormLayout(dialog)
        
        var1_combo = QComboBox()
        var1_combo.addItems(numeric_cols)
        layout.addRow('变量1 (前测):', var1_combo)
        
        var2_combo = QComboBox()
        var2_combo.addItems(numeric_cols)
        if len(numeric_cols) > 1:
            var2_combo.setCurrentIndex(1)
        layout.addRow('变量2 (后测):', var2_combo)
        
        btn = QPushButton('计算')
        layout.addRow(btn)
        
        def calculate():
            col1 = var1_combo.currentText()
            col2 = var2_combo.currentText()
            
            data = self.df[[col1, col2]].dropna()
            t_stat, p_val = stats.ttest_rel(data[col1], data[col2])
            
            result_html = f'''
            <h2>配对样本 t 检验</h2>
            <p>{col1} vs {col2}</p>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>t 值</b></td><td>{t_stat:.4f}</td></tr>
            <tr><td><b>P 值</b></td><td>{p_val:.6f}</td></tr>
            <tr><td><b>显著性</b></td><td>{'显著 (p < 0.05)' if p_val < 0.05 else '不显著'}</td></tr>
            </table>
            '''
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            dialog.accept()
        
        btn.clicked.connect(calculate)
        dialog.exec()

    def show_anova(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = self.df.columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self, '警告', '没有数值型数据')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('单因素 ANOVA')
        dialog.resize(450, 350)
        
        main_layout = QVBoxLayout(dialog)
        
        # 因变量选择
        dep_var_group = QWidget()
        dep_var_layout = QVBoxLayout(dep_var_group)
        dep_var_layout.addWidget(QLabel('因变量:'))
        
        dep_var_combo = QComboBox()
        dep_var_combo.addItems(numeric_cols)
        dep_var_layout.addWidget(dep_var_combo)
        main_layout.addWidget(dep_var_group)
        
        # 因子选择
        factor_group = QWidget()
        factor_layout = QVBoxLayout(factor_group)
        factor_layout.addWidget(QLabel('因子 (分组):'))
        
        factor_combo = QComboBox()
        factor_combo.addItems(all_cols)
        factor_layout.addWidget(factor_combo)
        main_layout.addWidget(factor_group)
        
        # 选项
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        options_layout.addWidget(QLabel('选项:'))
        
        # 事后检验
        post_hoc_check = QCheckBox('执行事后检验 (Tukey HSD)')
        post_hoc_check.setChecked(False)
        options_layout.addWidget(post_hoc_check)
        
        # 图表选项
        chart_check = QCheckBox('生成箱线图')
        chart_check.setChecked(False)
        options_layout.addWidget(chart_check)
        
        # 效应量
        effect_size_check = QCheckBox('计算效应量 (η²)')
        effect_size_check.setChecked(True)
        options_layout.addWidget(effect_size_check)
        
        main_layout.addWidget(options_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        calculate_btn = QPushButton('计算')
        calculate_btn.setDefault(True)
        btn_layout.addWidget(calculate_btn)
        
        main_layout.addLayout(btn_layout)
        
        def calculate():
            dep_col = dep_var_combo.currentText()
            factor_col = factor_combo.currentText()
            
            groups = [group[dep_col].dropna().values for _, group in self.df.groupby(factor_col)]
            groups = [g for g in groups if len(g) > 0]
            
            if len(groups) < 2:
                QMessageBox.warning(self, '警告', '因子至少需要2个组别')
                return
            
            # 执行方差分析
            f_stat, p_val = stats.f_oneway(*groups)
            
            # 计算效应量 η²
            grand_mean = np.mean(np.concatenate(groups))
            ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
            ss_total = sum(sum((x - grand_mean) ** 2 for x in g) for g in groups)
            eta_squared = ss_between / ss_total
            
            result_html = f'''
            <h2>单因素方差分析 (ANOVA)</h2>
            <p>因变量: {dep_col}, 因子: {factor_col}</p>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>F 值</b></td><td>{f_stat:.4f}</td></tr>
            <tr><td><b>P 值</b></td><td>{p_val:.6f}</td></tr>
            <tr><td><b>显著性</b></td><td>{'显著 (p < 0.05)' if p_val < 0.05 else '不显著'}</td></tr>
            '''
            
            if effect_size_check.isChecked():
                result_html += f'<tr><td><b>η² (效应量)</b></td><td>{eta_squared:.4f}</td></tr>'
            
            result_html += '</table>'
            
            # 执行事后检验
            if post_hoc_check.isChecked() and p_val < 0.05:
                from statsmodels.stats.multicomp import pairwise_tukeyhsd
                import pandas as pd
                
                # 准备数据
                data = []
                labels = []
                for i, group in enumerate(groups):
                    data.extend(group)
                    labels.extend([f'组{i+1}'] * len(group))
                
                # 执行Tukey HSD
                tukey = pairwise_tukeyhsd(data, labels, alpha=0.05)
                
                result_html += '<h3>事后检验 (Tukey HSD)</h3>'
                result_html += '''<table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
                <tr><th>比较组</th><th>均值差</th><th>p 值</th><th>显著性</th></tr>'''
                
                for i, (group1, group2, meandiff, p, reject) in enumerate(zip(
                    tukey.groupsunique[tukey.group1inds],
                    tukey.groupsunique[tukey.group2inds],
                    tukey.meandiffs,
                    tukey.pvalues,
                    tukey.reject
                )):
                    result_html += f'<tr><td>{group1} vs {group2}</td><td>{meandiff:.4f}</td><td>{p:.4f}</td><td>{"显著" if reject else "不显著"}</td></tr>'
                
                result_html += '</table>'
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            
            # 生成箱线图
            if chart_check.isChecked():
                self.chart_canvas.figure.clear()
                ax = self.chart_canvas.figure.add_subplot(111)
                ax.boxplot(groups, vert=True)
                ax.set_title(f'箱线图 - {dep_col} by {factor_col}')
                ax.set_ylabel(dep_col)
                ax.set_xticklabels([f'组{i+1}' for i in range(len(groups))])
                ax.grid(True, alpha=0.3, axis='y')
                self.chart_canvas.draw()
                self.tab_widget.setCurrentWidget(self.chart_canvas)
            
            dialog.accept()
        
        calculate_btn.clicked.connect(calculate)
        dialog.exec()

    def show_correlation(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('相关分析')
        dialog.resize(450, 350)
        
        main_layout = QVBoxLayout(dialog)
        
        # 变量选择
        var_group = QWidget()
        var_layout = QVBoxLayout(var_group)
        var_layout.addWidget(QLabel('变量选择:'))
        
        # 变量X
        var1_layout = QHBoxLayout()
        var1_layout.addWidget(QLabel('变量 X:'))
        var1_combo = QComboBox()
        var1_combo.addItems(numeric_cols)
        var1_layout.addWidget(var1_combo)
        var_layout.addLayout(var1_layout)
        
        # 变量Y
        var2_layout = QHBoxLayout()
        var2_layout.addWidget(QLabel('变量 Y:'))
        var2_combo = QComboBox()
        var2_combo.addItems(numeric_cols)
        if len(numeric_cols) > 1:
            var2_combo.setCurrentIndex(1)
        var2_layout.addWidget(var2_combo)
        var_layout.addLayout(var2_layout)
        
        main_layout.addWidget(var_group)
        
        # 方法选择
        method_group = QWidget()
        method_layout = QVBoxLayout(method_group)
        method_layout.addWidget(QLabel('相关方法:'))
        
        method_combo = QComboBox()
        method_combo.addItems(['Pearson', 'Spearman', 'Kendall'])
        method_layout.addWidget(method_combo)
        main_layout.addWidget(method_group)
        
        # 选项
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        options_layout.addWidget(QLabel('选项:'))
        
        # 置信水平
        ci_group = QWidget()
        ci_layout = QHBoxLayout(ci_group)
        ci_layout.addWidget(QLabel('置信水平:'))
        
        ci_combo = QComboBox()
        ci_combo.addItems(['90%', '95%', '99%'])
        ci_combo.setCurrentText('95%')
        ci_layout.addWidget(ci_combo)
        options_layout.addWidget(ci_group)
        
        # 图表选项
        chart_check = QCheckBox('生成散点图')
        chart_check.setChecked(False)
        options_layout.addWidget(chart_check)
        
        # 回归直线
        regression_check = QCheckBox('添加回归直线')
        regression_check.setChecked(False)
        regression_check.setEnabled(False)
        options_layout.addWidget(regression_check)
        
        # 当选择散点图时，启用回归直线选项
        def on_chart_check_changed(state):
            regression_check.setEnabled(state == Qt.CheckState.Checked)
        chart_check.stateChanged.connect(on_chart_check_changed)
        
        main_layout.addWidget(options_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        calculate_btn = QPushButton('计算')
        calculate_btn.setDefault(True)
        btn_layout.addWidget(calculate_btn)
        
        main_layout.addLayout(btn_layout)
        
        def calculate():
            col1 = var1_combo.currentText()
            col2 = var2_combo.currentText()
            method = method_combo.currentText()
            
            data = self.df[[col1, col2]].dropna()
            
            # 执行相关分析
            if method == 'Pearson':
                corr, p_val = stats.pearsonr(data[col1], data[col2])
            elif method == 'Spearman':
                corr, p_val = stats.spearmanr(data[col1], data[col2])
            else:  # Kendall
                corr, p_val = stats.kendalltau(data[col1], data[col2])
            
            # 获取置信水平
            ci_level = float(ci_combo.currentText().strip('%')) / 100
            
            result_html = f'''
            <h2>相关分析 - {method}</h2>
            <p>{col1} & {col2}</p>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>相关系数</b></td><td>{corr:.4f}</td></tr>
            <tr><td><b>样本量 N</b></td><td>{len(data)}</td></tr>
            <tr><td><b>P 值</b></td><td>{p_val:.6f}</td></tr>
            <tr><td><b>显著性</b></td><td>{'显著 (p < 0.05)' if p_val < 0.05 else '不显著'}</td></tr>
            '''
            
            # 计算置信区间（仅Pearson）
            if method == 'Pearson' and len(data) > 3:
                # 使用Fisher变换计算置信区间
                import math
                z = 0.5 * math.log((1 + corr) / (1 - corr))
                se = 1 / math.sqrt(len(data) - 3)
                z_ci = stats.norm.interval(ci_level, loc=z, scale=se)
                ci_lower = (math.exp(2 * z_ci[0]) - 1) / (math.exp(2 * z_ci[0]) + 1)
                ci_upper = (math.exp(2 * z_ci[1]) - 1) / (math.exp(2 * z_ci[1]) + 1)
                result_html += f'<tr><td><b>{int(ci_level*100)}% 置信区间</b></td><td>[{ci_lower:.4f}, {ci_upper:.4f}]</td></tr>'
            
            result_html += '</table>'
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            
            # 生成散点图
            if chart_check.isChecked():
                self.chart_canvas.figure.clear()
                ax = self.chart_canvas.figure.add_subplot(111)
                ax.scatter(data[col1], data[col2], alpha=0.6, edgecolor='black')
                ax.set_title(f'散点图 - {col1} vs {col2}')
                ax.set_xlabel(col1)
                ax.set_ylabel(col2)
                ax.grid(True, alpha=0.3)
                
                # 添加回归直线
                if regression_check.isChecked():
                    z = np.polyfit(data[col1], data[col2], 1)
                    p = np.poly1d(z)
                    ax.plot(data[col1], p(data[col1]), "r--", alpha=0.8, label='回归直线')
                    ax.legend()
                
                self.chart_canvas.draw()
                self.tab_widget.setCurrentWidget(self.chart_canvas)
            
            dialog.accept()
        
        calculate_btn.clicked.connect(calculate)
        dialog.exec()

    def show_regression(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('简单线性回归')
        dialog.resize(450, 350)
        
        main_layout = QVBoxLayout(dialog)
        
        # 变量选择
        var_group = QWidget()
        var_layout = QVBoxLayout(var_group)
        var_layout.addWidget(QLabel('变量选择:'))
        
        # 自变量X
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel('自变量 X:'))
        x_combo = QComboBox()
        x_combo.addItems(numeric_cols)
        x_layout.addWidget(x_combo)
        var_layout.addLayout(x_layout)
        
        # 因变量Y
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel('因变量 Y:'))
        y_combo = QComboBox()
        y_combo.addItems(numeric_cols)
        if len(numeric_cols) > 1:
            y_combo.setCurrentIndex(1)
        y_layout.addWidget(y_combo)
        var_layout.addLayout(y_layout)
        
        main_layout.addWidget(var_group)
        
        # 选项
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        options_layout.addWidget(QLabel('选项:'))
        
        # 置信水平
        ci_group = QWidget()
        ci_layout = QHBoxLayout(ci_group)
        ci_layout.addWidget(QLabel('置信水平:'))
        
        ci_combo = QComboBox()
        ci_combo.addItems(['90%', '95%', '99%'])
        ci_combo.setCurrentText('95%')
        ci_layout.addWidget(ci_combo)
        options_layout.addWidget(ci_group)
        
        # 图表选项
        chart_check = QCheckBox('生成散点图和回归直线')
        chart_check.setChecked(False)
        options_layout.addWidget(chart_check)
        
        # 残差分析
        residual_check = QCheckBox('执行残差分析')
        residual_check.setChecked(False)
        options_layout.addWidget(residual_check)
        
        main_layout.addWidget(options_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        calculate_btn = QPushButton('计算')
        calculate_btn.setDefault(True)
        btn_layout.addWidget(calculate_btn)
        
        main_layout.addLayout(btn_layout)
        
        def calculate():
            x_col = x_combo.currentText()
            y_col = y_combo.currentText()
            
            data = self.df[[x_col, y_col]].dropna()
            x = data[x_col].values
            y = data[y_col].values
            
            # 执行回归分析
            slope, intercept, r_value, p_val, std_err = stats.linregress(x, y)
            r_squared = r_value ** 2
            adjusted_r_squared = 1 - (1 - r_squared) * (len(y) - 1) / (len(y) - 2)
            
            # 获取置信水平
            ci_level = float(ci_combo.currentText().strip('%')) / 100
            
            # 计算系数的置信区间
            df = len(y) - 2
            t_critical = stats.t.ppf((1 + ci_level) / 2, df)
            intercept_ci = (intercept - t_critical * std_err, intercept + t_critical * std_err)
            slope_ci = (slope - t_critical * std_err, slope + t_critical * std_err)
            
            result_html = f'''
            <h2>简单线性回归</h2>
            <p>Y = {y_col}, X = {x_col}</p>
            <h3>模型摘要</h3>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>R</b></td><td>{r_value:.4f}</td></tr>
            <tr><td><b>R²</b></td><td>{r_squared:.4f}</td></tr>
            <tr><td><b>调整 R²</b></td><td>{adjusted_r_squared:.4f}</td></tr>
            <tr><td><b>样本量 N</b></td><td>{len(y)}</td></tr>
            </table>
            <h3>系数</h3>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><th></th><th>系数</th><th>标准误</th><th>t</th><th>P</th><th>{int(ci_level*100)}% 置信区间</th></tr>
            <tr><td><b>(截距)</b></td><td>{intercept:.4f}</td><td>{std_err:.4f}</td><td>{intercept/std_err:.4f}</td><td>{stats.t.sf(abs(intercept/std_err), df):.6f}</td><td>[{intercept_ci[0]:.4f}, {intercept_ci[1]:.4f}]</td></tr>
            <tr><td><b>{x_col}</b></td><td>{slope:.4f}</td><td>{std_err:.4f}</td><td>{slope/std_err:.4f}</td><td>{p_val:.6f}</td><td>[{slope_ci[0]:.4f}, {slope_ci[1]:.4f}]</td></tr>
            </table>
            '''
            
            # 残差分析
            if residual_check.isChecked():
                y_pred = intercept + slope * x
                residuals = y - y_pred
                residual_mean = np.mean(residuals)
                residual_std = np.std(residuals)
                
                result_html += '<h3>残差分析</h3>'
                result_html += '''<table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
                <tr><td><b>残差均值</b></td><td>{:.4f}</td></tr>
                <tr><td><b>残差标准差</b></td><td>{:.4f}</td></tr>
                <tr><td><b>残差最小值</b></td><td>{:.4f}</td></tr>
                <tr><td><b>残差最大值</b></td><td>{:.4f}</td></tr>
                </table>'''.format(residual_mean, residual_std, np.min(residuals), np.max(residuals))
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            
            # 生成散点图和回归直线
            if chart_check.isChecked():
                self.chart_canvas.figure.clear()
                ax = self.chart_canvas.figure.add_subplot(111)
                ax.scatter(x, y, alpha=0.6, edgecolor='black', label='数据点')
                ax.plot(x, y_pred, 'r--', alpha=0.8, label='回归直线')
                ax.set_title(f'回归分析 - {y_col} vs {x_col}')
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.grid(True, alpha=0.3)
                ax.legend()
                self.chart_canvas.draw()
                self.tab_widget.setCurrentWidget(self.chart_canvas)
            
            dialog.accept()
        
        calculate_btn.clicked.connect(calculate)
        dialog.exec()

    def show_reliability(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('信度分析 (Cronbach α)')
        dialog.resize(450, 350)
        
        main_layout = QVBoxLayout(dialog)
        
        # 题项选择
        item_group = QWidget()
        item_layout = QVBoxLayout(item_group)
        item_layout.addWidget(QLabel('选择量表题项 (可多选):'))
        
        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        list_widget.addItems(numeric_cols)
        # 默认选择前5个变量（如果有）
        for i in range(min(5, len(numeric_cols))):
            list_widget.item(i).setSelected(True)
        item_layout.addWidget(list_widget)
        main_layout.addWidget(item_group)
        
        # 选项
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        options_layout.addWidget(QLabel('选项:'))
        
        # 项目分析
        item_analysis_check = QCheckBox('执行项目分析')
        item_analysis_check.setChecked(False)
        options_layout.addWidget(item_analysis_check)
        
        # 删除低信度题项
        delete_items_check = QCheckBox('自动删除低信度题项')
        delete_items_check.setChecked(False)
        delete_items_check.setEnabled(False)
        options_layout.addWidget(delete_items_check)
        
        # 当选择项目分析时，启用自动删除选项
        def on_item_analysis_changed(state):
            delete_items_check.setEnabled(state == Qt.CheckState.Checked)
        item_analysis_check.stateChanged.connect(on_item_analysis_changed)
        
        main_layout.addWidget(options_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        calculate_btn = QPushButton('计算 Cronbach α')
        calculate_btn.setDefault(True)
        btn_layout.addWidget(calculate_btn)
        
        main_layout.addLayout(btn_layout)
        
        def calculate():
            selected_items = [item.text() for item in list_widget.selectedItems()]
            if len(selected_items) < 2:
                QMessageBox.warning(self, '警告', '至少选择2个题项')
                return
            
            data = self.df[selected_items].dropna()
            
            def cronbach_alpha(items):
                item_vars = items.var(axis=0, ddof=1)
                total_var = items.sum(axis=1).var(ddof=1)
                k = items.shape[1]
                if k < 2 or total_var == 0:
                    return 0
                alpha = (k / (k - 1)) * (1 - item_vars.sum() / total_var)
                return alpha
            
            alpha = cronbach_alpha(data)
            
            interpretation = ''
            if alpha >= 0.9:
                interpretation = '优秀'
            elif alpha >= 0.8:
                interpretation = '良好'
            elif alpha >= 0.7:
                interpretation = '可接受'
            elif alpha >= 0.6:
                interpretation = '一般'
            else:
                interpretation = '较差'
            
            result_html = f'''
            <h2>信度分析 - Cronbach's α</h2>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>Cronbach's α</b></td><td>{alpha:.4f}</td></tr>
            <tr><td><b>题项数</b></td><td>{len(selected_items)}</td></tr>
            <tr><td><b>有效样本量</b></td><td>{len(data)}</td></tr>
            <tr><td><b>评价</b></td><td>{interpretation}</td></tr>
            </table>
            <p><b>题项:</b> {', '.join(selected_items)}</p>
            '''
            
            # 执行项目分析
            if item_analysis_check.isChecked():
                result_html += '<h3>项目分析</h3>'
                result_html += '''<table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
                <tr><th>题项</th><th>均值</th><th>标准差</th><th>与总分相关</th><th>删除后α</th></tr>'''
                
                # 计算总分
                total_scores = data.sum(axis=1)
                
                # 计算每个题项的统计量
                item_stats = []
                for item in selected_items:
                    item_data = data[item]
                    item_mean = item_data.mean()
                    item_std = item_data.std()
                    # 计算与总分的相关
                    item_corr = np.corrcoef(item_data, total_scores)[0, 1]
                    # 计算删除该题项后的α
                    temp_items = [i for i in selected_items if i != item]
                    temp_alpha = cronbach_alpha(data[temp_items])
                    item_stats.append((item, item_mean, item_std, item_corr, temp_alpha))
                
                # 排序（按删除后α降序）
                item_stats.sort(key=lambda x: x[4], reverse=True)
                
                for item, mean, std, corr, alpha_if_deleted in item_stats:
                    result_html += f'<tr><td>{item}</td><td>{mean:.4f}</td><td>{std:.4f}</td><td>{corr:.4f}</td><td>{alpha_if_deleted:.4f}</td></tr>'
                
                result_html += '</table>'
                
                # 自动删除低信度题项
                if delete_items_check.isChecked():
                    # 找出删除后α更高的题项
                    items_to_delete = []
                    for item, _, _, _, alpha_if_deleted in item_stats:
                        if alpha_if_deleted > alpha:
                            items_to_delete.append(item)
                    
                    if items_to_delete:
                        # 计算删除后的α
                        remaining_items = [i for i in selected_items if i not in items_to_delete]
                        if len(remaining_items) >= 2:
                            new_alpha = cronbach_alpha(data[remaining_items])
                            result_html += f'<h4>删除低信度题项后</h4>'
                            result_html += f'<p><b>剩余题项:</b> {", ".join(remaining_items)}</p>'
                            result_html += f'<p><b>新的 Cronbach\'s α:</b> {new_alpha:.4f}</p>'
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            dialog.accept()
        
        calculate_btn.clicked.connect(calculate)
        dialog.exec()

    def show_histogram(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self, '警告', '没有数值型数据')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('直方图')
        dialog.resize(450, 350)
        
        main_layout = QVBoxLayout(dialog)
        
        # 变量选择
        var_group = QWidget()
        var_layout = QVBoxLayout(var_group)
        var_layout.addWidget(QLabel('选择变量:'))
        
        combo = QComboBox()
        combo.addItems(numeric_cols)
        var_layout.addWidget(combo)
        main_layout.addWidget(var_group)
        
        # 图表选项
        chart_group = QWidget()
        chart_layout = QVBoxLayout(chart_group)
        chart_layout.addWidget(QLabel('图表选项:'))
        
        #  bins数量
        bins_group = QWidget()
        bins_layout = QHBoxLayout(bins_group)
        bins_layout.addWidget(QLabel('bins数量:'))
        
        bins_combo = QComboBox()
        bins_combo.addItems(['自动', '10', '20', '30', '50', '100'])
        bins_combo.setCurrentText('自动')
        bins_layout.addWidget(bins_combo)
        chart_layout.addWidget(bins_group)
        
        # 颜色
        color_group = QWidget()
        color_layout = QHBoxLayout(color_group)
        color_layout.addWidget(QLabel('颜色:'))
        
        color_combo = QComboBox()
        color_combo.addItems(['蓝色', '绿色', '红色', '橙色', '紫色', '灰色'])
        color_combo.setCurrentText('蓝色')
        color_layout.addWidget(color_combo)
        chart_layout.addWidget(color_group)
        
        # 显示密度曲线
        density_check = QCheckBox('显示密度曲线')
        density_check.setChecked(False)
        chart_layout.addWidget(density_check)
        
        # 显示均值线
        mean_check = QCheckBox('显示均值线')
        mean_check.setChecked(True)
        chart_layout.addWidget(mean_check)
        
        main_layout.addWidget(chart_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        plot_btn = QPushButton('绘制')
        plot_btn.setDefault(True)
        btn_layout.addWidget(plot_btn)
        
        main_layout.addLayout(btn_layout)
        
        def plot():
            col = combo.currentText()
            data = self.df[col].dropna()
            
            # 获取参数
            bins = 'auto' if bins_combo.currentText() == '自动' else int(bins_combo.currentText())
            color_map = {
                '蓝色': 'skyblue',
                '绿色': 'lightgreen',
                '红色': 'lightcoral',
                '橙色': 'lightsalmon',
                '紫色': 'plum',
                '灰色': 'lightgray'
            }
            color = color_map.get(color_combo.currentText(), 'skyblue')
            
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(111)
            
            # 绘制直方图
            n, bins, patches = ax.hist(data, bins=bins, edgecolor='black', alpha=0.7, color=color)
            
            # 显示密度曲线
            if density_check.isChecked():
                sns.kdeplot(data, ax=ax, color='black', alpha=0.8)
                ax.set_ylabel('密度')
            else:
                ax.set_ylabel('频数')
            
            # 显示均值线
            if mean_check.isChecked():
                mean_val = data.mean()
                ax.axvline(x=mean_val, color='red', linestyle='--', linewidth=1.5, label=f'均值: {mean_val:.2f}')
                ax.legend()
            
            ax.set_title(f'直方图 - {col}')
            ax.set_xlabel(col)
            ax.grid(True, alpha=0.3)
            self.chart_canvas.draw()
            
            self.tab_widget.setCurrentWidget(self.chart_canvas)
            dialog.accept()
        
        plot_btn.clicked.connect(plot)
        dialog.exec()

    def show_boxplot(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = self.df.columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self, '警告', '没有数值型数据')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('箱线图')
        dialog.resize(450, 350)
        
        main_layout = QVBoxLayout(dialog)
        
        # 变量选择
        var_group = QWidget()
        var_layout = QVBoxLayout(var_group)
        var_layout.addWidget(QLabel('选择变量:'))
        
        combo = QComboBox()
        combo.addItems(numeric_cols)
        var_layout.addWidget(combo)
        main_layout.addWidget(var_group)
        
        # 分组变量（可选）
        group_group = QWidget()
        group_layout = QVBoxLayout(group_group)
        group_layout.addWidget(QLabel('分组变量 (可选):'))
        
        group_combo = QComboBox()
        group_combo.addItem('无')
        group_combo.addItems(all_cols)
        group_layout.addWidget(group_combo)
        main_layout.addWidget(group_group)
        
        # 图表选项
        chart_group = QWidget()
        chart_layout = QVBoxLayout(chart_group)
        chart_layout.addWidget(QLabel('图表选项:'))
        
        # 方向
        orient_group = QWidget()
        orient_layout = QHBoxLayout(orient_group)
        orient_layout.addWidget(QLabel('方向:'))
        
        orient_combo = QComboBox()
        orient_combo.addItems(['垂直', '水平'])
        orient_combo.setCurrentText('垂直')
        orient_layout.addWidget(orient_combo)
        chart_layout.addWidget(orient_group)
        
        # 显示均值点
        mean_check = QCheckBox('显示均值点')
        mean_check.setChecked(True)
        chart_layout.addWidget(mean_check)
        
        # 显示异常值
        outlier_check = QCheckBox('显示异常值')
        outlier_check.setChecked(True)
        chart_layout.addWidget(outlier_check)
        
        main_layout.addWidget(chart_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        plot_btn = QPushButton('绘制')
        plot_btn.setDefault(True)
        btn_layout.addWidget(plot_btn)
        
        main_layout.addLayout(btn_layout)
        
        def plot():
            col = combo.currentText()
            group_col = group_combo.currentText()
            vert = orient_combo.currentText() == '垂直'
            
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(111)
            
            if group_col == '无':
                # 单个箱线图
                data = self.df[col].dropna()
                box = ax.boxplot(data, vert=vert, showmeans=mean_check.isChecked(), showfliers=outlier_check.isChecked())
                
                if vert:
                    ax.set_ylabel(col)
                else:
                    ax.set_xlabel(col)
            else:
                # 分组箱线图
                groups = [group[col].dropna().values for _, group in self.df.groupby(group_col)]
                groups = [g for g in groups if len(g) > 0]
                
                if len(groups) == 0:
                    QMessageBox.warning(self, '警告', '分组变量没有有效数据')
                    return
                
                box = ax.boxplot(groups, vert=vert, showmeans=mean_check.isChecked(), showfliers=outlier_check.isChecked())
                
                # 设置标签
                group_names = [str(name) for name, _ in self.df.groupby(group_col)]
                if vert:
                    ax.set_ylabel(col)
                    ax.set_xticklabels(group_names)
                else:
                    ax.set_xlabel(col)
                    ax.set_yticklabels(group_names)
            
            ax.set_title(f'箱线图 - {col}' + (f' by {group_col}' if group_col != '无' else ''))
            ax.grid(True, alpha=0.3, axis='y' if vert else 'x')
            self.chart_canvas.draw()
            
            self.tab_widget.setCurrentWidget(self.chart_canvas)
            dialog.accept()
        
        plot_btn.clicked.connect(plot)
        dialog.exec()

    def show_scatterplot(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('散点图')
        layout = QFormLayout(dialog)
        
        x_combo = QComboBox()
        x_combo.addItems(numeric_cols)
        layout.addRow('X 轴:', x_combo)
        
        y_combo = QComboBox()
        y_combo.addItems(numeric_cols)
        if len(numeric_cols) > 1:
            y_combo.setCurrentIndex(1)
        layout.addRow('Y 轴:', y_combo)
        
        btn = QPushButton('绘制')
        layout.addRow(btn)
        
        def plot():
            x_col = x_combo.currentText()
            y_col = y_combo.currentText()
            
            data = self.df[[x_col, y_col]].dropna()
            
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(111)
            ax.scatter(data[x_col], data[y_col], alpha=0.6, edgecolor='black')
            ax.set_title(f'散点图 - {x_col} vs {y_col}')
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.grid(True, alpha=0.3)
            
            z = np.polyfit(data[x_col], data[y_col], 1)
            p = np.poly1d(z)
            ax.plot(data[x_col], p(data[x_col]), "r--", alpha=0.8, label='趋势线')
            ax.legend()
            
            self.chart_canvas.draw()
            
            self.tab_widget.setCurrentWidget(self.chart_canvas)
            dialog.accept()
        
        btn.clicked.connect(plot)
        dialog.exec()

    def show_barchart(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        all_cols = self.df.columns.tolist()
        
        dialog = QDialog(self)
        dialog.setWindowTitle('条形图')
        layout = QFormLayout(dialog)
        
        combo = QComboBox()
        combo.addItems(all_cols)
        layout.addRow('选择变量:', combo)
        
        btn = QPushButton('绘制')
        layout.addRow(btn)
        
        def plot():
            col = combo.currentText()
            data = self.df[col].value_counts()
            
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(111)
            bars = ax.bar(range(len(data)), data.values, edgecolor='black', alpha=0.7)
            ax.set_title(f'条形图 - {col}')
            ax.set_xlabel(col)
            ax.set_ylabel('频数')
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels(data.index, rotation=45, ha='right')
            ax.grid(True, alpha=0.3, axis='y')
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom')
            
            self.chart_canvas.figure.tight_layout()
            self.chart_canvas.draw()
            
            self.tab_widget.setCurrentWidget(self.chart_canvas)
            dialog.accept()
        
        btn.clicked.connect(plot)
        dialog.exec()

    def show_heatmap(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        corr_matrix = self.df[numeric_cols].corr()
        
        self.chart_canvas.figure.clear()
        ax = self.chart_canvas.figure.add_subplot(111)
        im = ax.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        ax.set_xticks(range(len(numeric_cols)))
        ax.set_yticks(range(len(numeric_cols)))
        ax.set_xticklabels(numeric_cols, rotation=45, ha='right')
        ax.set_yticklabels(numeric_cols)
        ax.set_title('相关系数热力图')
        
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                       ha='center', va='center', color='black', fontsize=9)
        
        self.chart_canvas.figure.colorbar(im, ax=ax)
        self.chart_canvas.figure.tight_layout()
        self.chart_canvas.draw()
        
        self.tab_widget.setCurrentWidget(self.chart_canvas)
    
    def on_nav_item_clicked(self, item):
        # 处理左侧菜单点击事件
        text = item.text()
        if text == '描述统计':
            self.show_descriptive_stats()
        elif text == 't 检验':
            # 显示t检验子菜单或默认显示单样本t检验
            self.show_ttest_one_sample()
        elif text == '方差分析':
            self.show_anova()
        elif text == '相关分析':
            self.show_correlation()
        elif text == '回归分析':
            self.show_regression()
        elif text == '信度分析':
            self.show_reliability()
        elif text == '图表绘制':
            # 显示图表子菜单或默认显示直方图
            self.show_histogram()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('AnalyX')
    app.setOrganizationName('AnalyX')
    
    window = AnalyXMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
