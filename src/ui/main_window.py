import sys
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
matplotlib.rc('font', family='sans-serif')

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QListWidget,
    QTextEdit, QFileDialog, QMessageBox, QDialog, QComboBox,
    QDoubleSpinBox, QPushButton, QLabel, QTabWidget,
    QHeaderView, QCheckBox, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush, QPainter, QPen, QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .title_bar import ModernTitleBar
from .menu_bar import ModernMenuBar
from .tool_bar import ModernToolBar
from .status_bar import ModernStatusBar
from .editable_header import EditableHeaderView
from utils import DataHandler, FileHandler


class AnalyXMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.df = pd.DataFrame()
        self.current_file = None
        self.dark_theme = False  # Changed to light theme by default
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('AnalyX - 学术统计软件')
        self.setMinimumSize(1400, 900)
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a gradient background widget
        self.background_widget = QWidget()
        self.background_layout = QVBoxLayout(self.background_widget)
        self.background_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_bar = ModernTitleBar(self)
        self.background_layout.addWidget(self.title_bar)
        
        self.menu_bar = ModernMenuBar(self)
        self.background_layout.addWidget(self.menu_bar)
        
        self.tool_bar = ModernToolBar(self)
        self.background_layout.addWidget(self.tool_bar)
        
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)
        
        # Sidebar with artistic design
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)
        
        # Sidebar header with gradient
        sidebar_header = QWidget()
        sidebar_header.setFixedHeight(60)
        sidebar_header.setStyleSheet('''
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6a9bcc, stop:1 #788c5d);
                border-radius: 8px 8px 0 0;
            }
        ''')
        sidebar_header_layout = QVBoxLayout(sidebar_header)
        sidebar_header_layout.setContentsMargins(20, 0, 20, 0)
        
        sidebar_title = QLabel('分析工具')
        sidebar_title.setFont(QFont('Poppins', 14, QFont.Weight.Bold))
        sidebar_title.setStyleSheet('color: #faf9f5;')
        sidebar_header_layout.addWidget(sidebar_title, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        
        self.sidebar_layout.addWidget(sidebar_header)
        
        # Navigation list with modern styling
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
                background-color: #faf9f5;
                color: #141413;
                border: none;
                padding: 10px 0;
                border-radius: 0 0 8px 8px;
            }
            QListWidget::item {
                padding: 12px 20px;
                border-left: 3px solid transparent;
                font-size: 12px;
                font-family: 'Lora';
            }
            QListWidget::item:hover {
                background-color: rgba(106, 155, 204, 0.1);
                color: #6a9bcc;
            }
            QListWidget::item:selected {
                background-color: rgba(106, 155, 204, 0.2);
                color: #6a9bcc;
                border-left: 3px solid #6a9bcc;
            }
        ''')
        self.nav_list.itemClicked.connect(self.on_nav_item_clicked)
        self.sidebar_layout.addWidget(self.nav_list)
        
        # Sidebar footer
        sidebar_footer = QWidget()
        sidebar_footer.setFixedHeight(60)
        sidebar_footer.setStyleSheet('''
            QWidget {
                background-color: #faf9f5;
                border-radius: 0 0 8px 8px;
            }
        ''')
        sidebar_footer_layout = QVBoxLayout(sidebar_footer)
        sidebar_footer_layout.setContentsMargins(20, 0, 20, 0)
        
        version_label = QLabel('版本 1.0')
        version_label.setStyleSheet('color: #777777; font-size: 10px; font-family: Lora;')
        sidebar_footer_layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        
        self.sidebar_layout.addWidget(sidebar_footer)
        
        # Workspace with card-like design
        self.workspace = QWidget()
        self.workspace.setStyleSheet('''
            QWidget {
                background-color: #faf9f5;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
        ''')
        self.workspace_layout = QVBoxLayout(self.workspace)
        self.workspace_layout.setContentsMargins(20, 20, 20, 20)
        self.workspace_layout.setSpacing(15)
        
        # Tab widget with modern styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet('''
            QTabWidget {
                background-color: transparent;
                color: #141413;
            }
            QTabBar {
                background-color: transparent;
                height: 50px;
                padding-left: 10px;
            }
            QTabBar::tab {
                background-color: transparent;
                color: #b0aea5;
                padding: 0 30px;
                font-size: 13px;
                font-weight: 500;
                font-family: Poppins;
                border-bottom: 3px solid transparent;
                margin-right: 10px;
            }
            QTabBar::tab:hover {
                color: #6a9bcc;
            }
            QTabBar::tab:selected {
                color: #6a9bcc;
                border-bottom: 3px solid #6a9bcc;
            }
        ''')
        
        # Data table with modern styling
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.header_view = EditableHeaderView(Qt.Orientation.Horizontal, self)
        self.data_table.setHorizontalHeader(self.header_view)
        self.data_table.setStyleSheet('''
            QTableWidget {
                background-color: white;
                color: #141413;
                border: 1px solid #e8e6dc;
                border-radius: 6px;
                gridline-color: #e8e6dc;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #e8e6dc;
                font-family: Lora;
            }
            QTableWidget::item:selected {
                background-color: rgba(106, 155, 204, 0.1);
                color: #6a9bcc;
            }
            QHeaderView::section {
                background-color: #f8f7f3;
                color: #141413;
                padding: 12px;
                border: none;
                border-bottom: 1px solid #e8e6dc;
                font-size: 12px;
                font-weight: 500;
                font-family: Poppins;
            }
            QHeaderView::section:horizontal {
                border-right: 1px solid #e8e6dc;
            }
        ''')
        self.data_table.cellChanged.connect(self.on_cell_changed)
        self.tab_widget.addTab(self.data_table, '数据视图')
        
        # Results text with modern styling
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont('Consolas', 11))
        self.results_text.setStyleSheet('''
            QTextEdit {
                background-color: white;
                color: #141413;
                border: 1px solid #e8e6dc;
                border-radius: 6px;
                padding: 20px;
                font-family: Lora;
            }
        ''')
        self.tab_widget.addTab(self.results_text, '分析结果')
        
        # Chart canvas with modern styling
        self.chart_canvas = FigureCanvas(Figure(figsize=(10, 7)))
        chart_container = QWidget()
        chart_container.setStyleSheet('''
            QWidget {
                background-color: white;
                border: 1px solid #e8e6dc;
                border-radius: 6px;
            }
        ''')
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.setContentsMargins(10, 10, 10, 10)
        chart_layout.addWidget(self.chart_canvas)
        self.tab_widget.addTab(chart_container, '图表')
        
        self.workspace_layout.addWidget(self.tab_widget)
        
        self.content_layout.addWidget(self.sidebar)
        self.content_layout.addWidget(self.workspace)
        
        self.status_bar = ModernStatusBar(self)
        
        self.background_layout.addWidget(self.content_widget)
        self.background_layout.addWidget(self.status_bar)
        
        self.main_layout.addWidget(self.background_widget)
        
        self.apply_theme()
        self.load_sample_data()
    
    def apply_theme(self):
        if self.dark_theme:
            # Dark theme
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 35))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 30))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 40, 45))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(50, 50, 55))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
            palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
            palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 50))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 70, 70))
            palette.setColor(QPalette.ColorRole.Link, QColor(70, 140, 255))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(70, 140, 255))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(20, 20, 25))
            QApplication.setPalette(palette)
            plt.style.use('seaborn-v0_8-dark')
            
            # Update styles for dark theme
            self.background_widget.setStyleSheet('''
                QWidget {
                    background-color: #1a1a1a;
                }
            ''')
            
            self.sidebar.setStyleSheet('''
                QWidget {
                    background-color: #222227;
                    border-radius: 8px;
                }
            ''')
            
            self.nav_list.setStyleSheet('''
                QListWidget {
                    background-color: #222227;
                    color: #b0aea5;
                    border: none;
                    padding: 10px 0;
                    border-radius: 0 0 8px 8px;
                }
                QListWidget::item {
                    padding: 12px 20px;
                    border-left: 3px solid transparent;
                    font-size: 12px;
                    font-family: 'Lora';
                }
                QListWidget::item:hover {
                    background-color: rgba(106, 155, 204, 0.1);
                    color: #6a9bcc;
                }
                QListWidget::item:selected {
                    background-color: rgba(106, 155, 204, 0.2);
                    color: #6a9bcc;
                    border-left: 3px solid #6a9bcc;
                }
            ''')
            
            self.workspace.setStyleSheet('''
                QWidget {
                    background-color: #222227;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                }
            ''')
            
            self.data_table.setStyleSheet('''
                QTableWidget {
                    background-color: #1a1a20;
                    color: #faf9f5;
                    border: 1px solid #333333;
                    border-radius: 6px;
                    gridline-color: #333333;
                }
                QTableWidget::item {
                    padding: 10px;
                    border-bottom: 1px solid #333333;
                    font-family: Lora;
                }
                QTableWidget::item:selected {
                    background-color: rgba(106, 155, 204, 0.2);
                    color: #6a9bcc;
                }
                QHeaderView::section {
                    background-color: #222227;
                    color: #b0aea5;
                    padding: 12px;
                    border: none;
                    border-bottom: 1px solid #333333;
                    font-size: 12px;
                    font-weight: 500;
                    font-family: Poppins;
                }
                QHeaderView::section:horizontal {
                    border-right: 1px solid #333333;
                }
            ''')
            
            self.results_text.setStyleSheet('''
                QTextEdit {
                    background-color: #1a1a20;
                    color: #faf9f5;
                    border: 1px solid #333333;
                    border-radius: 6px;
                    padding: 20px;
                    font-family: Lora;
                }
            ''')
            
            if self.tab_widget.count() > 2:
                chart_container = self.tab_widget.widget(2)
                chart_container.setStyleSheet('''
                    QWidget {
                        background-color: #1a1a20;
                        border: 1px solid #333333;
                        border-radius: 6px;
                    }
                ''')
        else:
            # Light theme
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(250, 249, 245))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(20, 20, 19))
            palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(248, 247, 243))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(20, 20, 19))
            palette.setColor(QPalette.ColorRole.Text, QColor(20, 20, 19))
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 238, 232))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(20, 20, 19))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(217, 119, 87))
            palette.setColor(QPalette.ColorRole.Link, QColor(106, 155, 204))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(106, 155, 204))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            QApplication.setPalette(palette)
            plt.style.use('seaborn-v0_8-whitegrid')
            
            # Update styles for light theme
            self.background_widget.setStyleSheet('''
                QWidget {
                    background-color: #faf9f5;
                }
            ''')
            
            self.sidebar.setStyleSheet('''
                QWidget {
                    background-color: #faf9f5;
                    border-radius: 8px;
                }
            ''')
            
            self.nav_list.setStyleSheet('''
                QListWidget {
                    background-color: #faf9f5;
                    color: #141413;
                    border: none;
                    padding: 10px 0;
                    border-radius: 0 0 8px 8px;
                }
                QListWidget::item {
                    padding: 12px 20px;
                    border-left: 3px solid transparent;
                    font-size: 12px;
                    font-family: 'Lora';
                }
                QListWidget::item:hover {
                    background-color: rgba(106, 155, 204, 0.1);
                    color: #6a9bcc;
                }
                QListWidget::item:selected {
                    background-color: rgba(106, 155, 204, 0.2);
                    color: #6a9bcc;
                    border-left: 3px solid #6a9bcc;
                }
            ''')
            
            self.workspace.setStyleSheet('''
                QWidget {
                    background-color: #faf9f5;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                }
            ''')
            
            self.data_table.setStyleSheet('''
                QTableWidget {
                    background-color: white;
                    color: #141413;
                    border: 1px solid #e8e6dc;
                    border-radius: 6px;
                    gridline-color: #e8e6dc;
                }
                QTableWidget::item {
                    padding: 10px;
                    border-bottom: 1px solid #e8e6dc;
                    font-family: Lora;
                }
                QTableWidget::item:selected {
                    background-color: rgba(106, 155, 204, 0.1);
                    color: #6a9bcc;
                }
                QHeaderView::section {
                    background-color: #f8f7f3;
                    color: #141413;
                    padding: 12px;
                    border: none;
                    border-bottom: 1px solid #e8e6dc;
                    font-size: 12px;
                    font-weight: 500;
                    font-family: Poppins;
                }
                QHeaderView::section:horizontal {
                    border-right: 1px solid #e8e6dc;
                }
            ''')
            
            self.results_text.setStyleSheet('''
                QTextEdit {
                    background-color: white;
                    color: #141413;
                    border: 1px solid #e8e6dc;
                    border-radius: 6px;
                    padding: 20px;
                    font-family: Lora;
                }
            ''')
            
            if self.tab_widget.count() > 2:
                chart_container = self.tab_widget.widget(2)
                chart_container.setStyleSheet('''
                    QWidget {
                        background-color: white;
                        border: 1px solid #e8e6dc;
                        border-radius: 6px;
                    }
                ''')
    
    def load_sample_data(self):
        self.df = DataHandler.load_sample_data()
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
        item = self.data_table.item(row, col)
        if item:
            value = item.text()
            try:
                if value == '':
                    self.df.iloc[row, col] = pd.NA
                else:
                    try:
                        self.df.iloc[row, col] = float(value)
                    except ValueError:
                        self.df.iloc[row, col] = value
            except Exception as e:
                pass
    
    def on_header_changed(self, col, new_name):
        if 0 <= col < len(self.df.columns):
            old_name = self.df.columns[col]
            if old_name != new_name:
                new_columns = list(self.df.columns)
                new_columns[col] = new_name
                self.df.columns = new_columns
    
    def on_nav_item_clicked(self, item):
        text = item.text()
        if text == '描述统计':
            self.show_descriptive_stats()
        elif text == 't 检验':
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
            self.show_histogram()
    
    def new_project(self):
        reply = QMessageBox.question(
            self, '确认', '当前项目未保存，是否继续？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.df = DataHandler.create_empty_table(100, 100)
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
            self.df = FileHandler.load_file(file_path)
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
            FileHandler.save_to_file(self.df, file_path)
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
            QApplication.setPalette(QApplication.style().standardPalette())
            plt.style.use('seaborn-v0_8-whitegrid')
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
        
        main_layout = QVBoxLayout(dialog)
        
        var_group = QWidget()
        var_layout = QVBoxLayout(var_group)
        var_layout.addWidget(QLabel('选择变量 (可多选):'))
        
        var_list = QListWidget()
        var_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        var_list.addItems(numeric_cols)
        if numeric_cols:
            var_list.setCurrentRow(0)
        var_layout.addWidget(var_list)
        main_layout.addWidget(var_group)
        
        stats_group = QWidget()
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.addWidget(QLabel('选择统计量:'))
        
        stats_grid = QWidget()
        grid_layout = QGridLayout(stats_grid)
        
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
        
        ci_group = QWidget()
        ci_layout = QHBoxLayout(ci_group)
        ci_check = QCheckBox('计算95%置信区间')
        ci_check.setChecked(False)
        ci_layout.addWidget(ci_check)
        main_layout.addWidget(ci_group)
        
        chart_group = QWidget()
        chart_layout = QHBoxLayout(chart_group)
        chart_check = QCheckBox('生成直方图')
        chart_check.setChecked(False)
        chart_layout.addWidget(chart_check)
        main_layout.addWidget(chart_group)
        
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
        
        var_group = QWidget()
        var_layout = QVBoxLayout(var_group)
        var_layout.addWidget(QLabel('选择变量:'))
        
        combo = QComboBox()
        combo.addItems(numeric_cols)
        var_layout.addWidget(combo)
        main_layout.addWidget(var_group)
        
        test_value_group = QWidget()
        test_value_layout = QHBoxLayout(test_value_group)
        test_value_layout.addWidget(QLabel('检验值:'))
        
        test_value = QDoubleSpinBox()
        test_value.setRange(-1e9, 1e9)
        test_value.setValue(0)
        test_value.setDecimals(4)
        test_value_layout.addWidget(test_value)
        main_layout.addWidget(test_value_group)
        
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        options_layout.addWidget(QLabel('选项:'))
        
        ci_group = QWidget()
        ci_layout = QHBoxLayout(ci_group)
        ci_layout.addWidget(QLabel('置信水平:'))
        
        ci_combo = QComboBox()
        ci_combo.addItems(['90%', '95%', '99%'])
        ci_combo.setCurrentText('95%')
        ci_layout.addWidget(ci_combo)
        options_layout.addWidget(ci_group)
        
        chart_check = QCheckBox('生成箱线图')
        chart_check.setChecked(False)
        options_layout.addWidget(chart_check)
        
        effect_size_check = QCheckBox('计算效应量 (Cohen\'s d)')
        effect_size_check.setChecked(True)
        options_layout.addWidget(effect_size_check)
        
        main_layout.addWidget(options_group)
        
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
            
            ci_level = float(ci_combo.currentText().strip('%')) / 100
            
            t_stat, p_val = stats.ttest_1samp(data, test_value.value())
            mean_diff = np.mean(data) - test_value.value()
            se_diff = stats.sem(data)
            ci = stats.t.interval(ci_level, len(data)-1, loc=np.mean(data), scale=se_diff)
            
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
        
        dep_var_group = QWidget()
        dep_var_layout = QVBoxLayout(dep_var_group)
        dep_var_layout.addWidget(QLabel('因变量:'))
        
        dep_var_combo = QComboBox()
        dep_var_combo.addItems(numeric_cols)
        dep_var_layout.addWidget(dep_var_combo)
        main_layout.addWidget(dep_var_group)
        
        factor_group = QWidget()
        factor_layout = QVBoxLayout(factor_group)
        factor_layout.addWidget(QLabel('因子 (分组):'))
        
        factor_combo = QComboBox()
        factor_combo.addItems(all_cols)
        factor_layout.addWidget(factor_combo)
        main_layout.addWidget(factor_group)
        
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        options_layout.addWidget(QLabel('选项:'))
        
        post_hoc_check = QCheckBox('执行事后检验 (Tukey HSD)')
        post_hoc_check.setChecked(False)
        options_layout.addWidget(post_hoc_check)
        
        chart_check = QCheckBox('生成箱线图')
        chart_check.setChecked(False)
        options_layout.addWidget(chart_check)
        
        effect_size_check = QCheckBox('计算效应量 (η²)')
        effect_size_check.setChecked(True)
        options_layout.addWidget(effect_size_check)
        
        main_layout.addWidget(options_group)
        
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
            
            f_stat, p_val = stats.f_oneway(*groups)
            
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
            
            if post_hoc_check.isChecked() and p_val < 0.05:
                from statsmodels.stats.multicomp import pairwise_tukeyhsd
                
                data = []
                labels = []
                for i, group in enumerate(groups):
                    data.extend(group)
                    labels.extend([f'组{i+1}'] * len(group))
                
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
        
        var_group = QWidget()
        var_layout = QVBoxLayout(var_group)
        var_layout.addWidget(QLabel('变量选择:'))
        
        var1_layout = QHBoxLayout()
        var1_layout.addWidget(QLabel('变量 X:'))
        var1_combo = QComboBox()
        var1_combo.addItems(numeric_cols)
        var1_layout.addWidget(var1_combo)
        var_layout.addLayout(var1_layout)
        
        var2_layout = QHBoxLayout()
        var2_layout.addWidget(QLabel('变量 Y:'))
        var2_combo = QComboBox()
        var2_combo.addItems(numeric_cols)
        if len(numeric_cols) > 1:
            var2_combo.setCurrentIndex(1)
        var2_layout.addWidget(var2_combo)
        var_layout.addLayout(var2_layout)
        
        main_layout.addWidget(var_group)
        
        method_group = QWidget()
        method_layout = QVBoxLayout(method_group)
        method_layout.addWidget(QLabel('相关方法:'))
        
        method_combo = QComboBox()
        method_combo.addItems(['Pearson', 'Spearman', 'Kendall'])
        method_layout.addWidget(method_combo)
        main_layout.addWidget(method_group)
        
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        options_layout.addWidget(QLabel('选项:'))
        
        ci_group = QWidget()
        ci_layout = QHBoxLayout(ci_group)
        ci_layout.addWidget(QLabel('置信水平:'))
        
        ci_combo = QComboBox()
        ci_combo.addItems(['90%', '95%', '99%'])
        ci_combo.setCurrentText('95%')
        ci_layout.addWidget(ci_combo)
        options_layout.addWidget(ci_group)
        
        chart_check = QCheckBox('生成散点图')
        chart_check.setChecked(False)
        options_layout.addWidget(chart_check)
        
        regression_check = QCheckBox('添加回归直线')
        regression_check.setChecked(False)
        regression_check.setEnabled(False)
        options_layout.addWidget(regression_check)
        
        def on_chart_check_changed(state):
            regression_check.setEnabled(state == Qt.CheckState.Checked)
        chart_check.stateChanged.connect(on_chart_check_changed)
        
        main_layout.addWidget(options_group)
        
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
            
            if method == 'Pearson':
                corr, p_val = stats.pearsonr(data[col1], data[col2])
            elif method == 'Spearman':
                corr, p_val = stats.spearmanr(data[col1], data[col2])
            else:
                corr, p_val = stats.kendalltau(data[col1], data[col2])
            
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
            
            if method == 'Pearson' and len(data) > 3:
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
            
            if chart_check.isChecked():
                self.chart_canvas.figure.clear()
                ax = self.chart_canvas.figure.add_subplot(111)
                ax.scatter(data[col1], data[col2], alpha=0.6, edgecolor='black')
                ax.set_title(f'散点图 - {col1} vs {col2}')
                ax.set_xlabel(col1)
                ax.set_ylabel(col2)
                ax.grid(True, alpha=0.3)
                
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
        
        var_group = QWidget()
        var_layout = QVBoxLayout(var_group)
        var_layout.addWidget(QLabel('变量选择:'))
        
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel('自变量 X:'))
        x_combo = QComboBox()
        x_combo.addItems(numeric_cols)
        x_layout.addWidget(x_combo)
        var_layout.addLayout(x_layout)
        
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel('因变量 Y:'))
        y_combo = QComboBox()
        y_combo.addItems(numeric_cols)
        if len(numeric_cols) > 1:
            y_combo.setCurrentIndex(1)
        y_layout.addWidget(y_combo)
        var_layout.addLayout(y_layout)
        
        main_layout.addWidget(var_group)
        
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        options_layout.addWidget(QLabel('选项:'))
        
        ci_group = QWidget()
        ci_layout = QHBoxLayout(ci_group)
        ci_layout.addWidget(QLabel('置信水平:'))
        
        ci_combo = QComboBox()
        ci_combo.addItems(['90%', '95%', '99%'])
        ci_combo.setCurrentText('95%')
        ci_layout.addWidget(ci_combo)
        options_layout.addWidget(ci_group)
        
        chart_check = QCheckBox('生成散点图和回归直线')
        chart_check.setChecked(False)
        options_layout.addWidget(chart_check)
        
        residual_check = QCheckBox('执行残差分析')
        residual_check.setChecked(False)
        options_layout.addWidget(residual_check)
        
        main_layout.addWidget(options_group)
        
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
            
            slope, intercept, r_value, p_val, std_err = stats.linregress(x, y)
            r_squared = r_value ** 2
            adjusted_r_squared = 1 - (1 - r_squared) * (len(y) - 1) / (len(y) - 2)
            
            ci_level = float(ci_combo.currentText().strip('%')) / 100
            
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
            
            if chart_check.isChecked():
                self.chart_canvas.figure.clear()
                ax = self.chart_canvas.figure.add_subplot(111)
                ax.scatter(x, y, alpha=0.6, edgecolor='black', label='数据点')
                y_pred = intercept + slope * x
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
        
        item_group = QWidget()
        item_layout = QVBoxLayout(item_group)
        item_layout.addWidget(QLabel('选择量表题项 (可多选):'))
        
        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        list_widget.addItems(numeric_cols)
        for i in range(min(5, len(numeric_cols))):
            list_widget.item(i).setSelected(True)
        item_layout.addWidget(list_widget)
        main_layout.addWidget(item_group)
        
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        options_layout.addWidget(QLabel('选项:'))
        
        item_analysis_check = QCheckBox('执行项目分析')
        item_analysis_check.setChecked(False)
        options_layout.addWidget(item_analysis_check)
        
        delete_items_check = QCheckBox('自动删除低信度题项')
        delete_items_check.setChecked(False)
        delete_items_check.setEnabled(False)
        options_layout.addWidget(delete_items_check)
        
        def on_item_analysis_changed(state):
            delete_items_check.setEnabled(state == Qt.CheckState.Checked)
        item_analysis_check.stateChanged.connect(on_item_analysis_changed)
        
        main_layout.addWidget(options_group)
        
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
            
            if item_analysis_check.isChecked():
                result_html += '<h3>项目分析</h3>'
                result_html += '''<table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
                <tr><th>题项</th><th>均值</th><th>标准差</th><th>与总分相关</th><th>删除后α</th></tr>'''
                
                total_scores = data.sum(axis=1)
                
                item_stats = []
                for item in selected_items:
                    item_data = data[item]
                    item_mean = item_data.mean()
                    item_std = item_data.std()
                    item_corr = np.corrcoef(item_data, total_scores)[0, 1]
                    temp_items = [i for i in selected_items if i != item]
                    temp_alpha = cronbach_alpha(data[temp_items])
                    item_stats.append((item, item_mean, item_std, item_corr, temp_alpha))
                
                item_stats.sort(key=lambda x: x[4], reverse=True)
                
                for item, mean, std, corr, alpha_if_deleted in item_stats:
                    result_html += f'<tr><td>{item}</td><td>{mean:.4f}</td><td>{std:.4f}</td><td>{corr:.4f}</td><td>{alpha_if_deleted:.4f}</td></tr>'
                
                result_html += '</table>'
                
                if delete_items_check.isChecked():
                    items_to_delete = []
                    for item, _, _, _, alpha_if_deleted in item_stats:
                        if alpha_if_deleted > alpha:
                            items_to_delete.append(item)
                    
                    if items_to_delete:
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
        
        var_group = QWidget()
        var_layout = QVBoxLayout(var_group)
        var_layout.addWidget(QLabel('选择变量:'))
        
        combo = QComboBox()
        combo.addItems(numeric_cols)
        var_layout.addWidget(combo)
        main_layout.addWidget(var_group)
        
        chart_group = QWidget()
        chart_layout = QVBoxLayout(chart_group)
        chart_layout.addWidget(QLabel('图表选项:'))
        
        bins_group = QWidget()
        bins_layout = QHBoxLayout(bins_group)
        bins_layout.addWidget(QLabel('bins数量:'))
        
        bins_combo = QComboBox()
        bins_combo.addItems(['自动', '10', '20', '30', '50', '100'])
        bins_combo.setCurrentText('自动')
        bins_layout.addWidget(bins_combo)
        chart_layout.addWidget(bins_group)
        
        color_group = QWidget()
        color_layout = QHBoxLayout(color_group)
        color_layout.addWidget(QLabel('颜色:'))
        
        color_combo = QComboBox()
        color_combo.addItems(['蓝色', '绿色', '红色', '橙色', '紫色', '灰色'])
        color_combo.setCurrentText('蓝色')
        color_layout.addWidget(color_combo)
        chart_layout.addWidget(color_group)
        
        density_check = QCheckBox('显示密度曲线')
        density_check.setChecked(False)
        chart_layout.addWidget(density_check)
        
        mean_check = QCheckBox('显示均值线')
        mean_check.setChecked(True)
        chart_layout.addWidget(mean_check)
        
        main_layout.addWidget(chart_group)
        
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
            
            n, bins, patches = ax.hist(data, bins=bins, edgecolor='black', alpha=0.7, color=color)
            
            if density_check.isChecked():
                sns.kdeplot(data, ax=ax, color='black', alpha=0.8)
                ax.set_ylabel('密度')
            else:
                ax.set_ylabel('频数')
            
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
        pass
    
    def show_scatterplot(self):
        pass
    
    def show_barchart(self):
        pass
    
    def show_heatmap(self):
        pass
