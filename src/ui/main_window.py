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
    QHeaderView, QCheckBox, QGridLayout, QSpacerItem, QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QCursor

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
        self.dark_theme = False
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('AnalyX - 专业统计分析平台')
        self.setMinimumSize(1400, 900)
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.title_bar = ModernTitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        self.menu_bar = ModernMenuBar(self)
        self.main_layout.addWidget(self.menu_bar)
        
        self.tool_bar = ModernToolBar(self)
        self.main_layout.addWidget(self.tool_bar)
        
        self.content_area = QWidget()
        self.content_area.setStyleSheet('background-color: #f1f5f9;')
        content_layout = QHBoxLayout(self.content_area)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(24)
        
        self.sidebar = self.create_sidebar()
        content_layout.addWidget(self.sidebar)
        
        self.workspace = self.create_workspace()
        content_layout.addWidget(self.workspace, 1)
        
        self.main_layout.addWidget(self.content_area)
        
        self.status_bar = ModernStatusBar(self)
        self.main_layout.addWidget(self.status_bar)
        
        self.apply_theme()
        self.load_sample_data()
    
    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet('''
            QWidget {
                background-color: #ffffff;
                border-radius: 16px;
            }
        ''')
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        sidebar_header = QWidget()
        sidebar_header.setFixedHeight(72)
        sidebar_header.setStyleSheet('''
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 16px 16px 0 0;
            }
        ''')
        
        header_layout = QVBoxLayout(sidebar_header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        header_title = QLabel('分析工具')
        header_title.setFont(QFont('Inter', 16, QFont.Weight.Bold))
        header_title.setStyleSheet('color: white;')
        
        header_subtitle = QLabel('选择分析类型')
        header_subtitle.setFont(QFont('Inter', 11))
        header_subtitle.setStyleSheet('color: rgba(255, 255, 255, 0.8);')
        
        header_layout.addWidget(header_title)
        header_layout.addWidget(header_subtitle)
        
        sidebar_layout.addWidget(sidebar_header)
        
        self.nav_list = QListWidget()
        nav_items = [
            ('📊', '描述统计'),
            ('📈', 't 检验'),
            ('📉', '方差分析'),
            ('🔗', '相关分析'),
            ('📐', '回归分析'),
            ('✅', '信度分析'),
            ('🎨', '图表绘制')
        ]
        
        for icon, text in nav_items:
            self.nav_list.addItem(f'{icon}  {text}')
        
        self.nav_list.setStyleSheet('''
            QListWidget {
                background-color: transparent;
                color: #475569;
                border: none;
                padding: 12px 8px;
                font-family: Inter;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 14px 16px;
                border-radius: 10px;
                margin: 2px 8px;
                font-weight: 500;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
                color: #1e293b;
            }
            QListWidget::item:selected {
                background-color: #6366f1;
                color: white;
            }
        ''')
        self.nav_list.itemClicked.connect(self.on_nav_item_clicked)
        sidebar_layout.addWidget(self.nav_list, 1)
        
        sidebar_footer = QWidget()
        sidebar_footer.setFixedHeight(72)
        sidebar_footer.setStyleSheet('''
            QWidget {
                background-color: #f8fafc;
                border-radius: 0 0 16px 16px;
                border-top: 1px solid #e2e8f0;
            }
        ''')
        
        footer_layout = QVBoxLayout(sidebar_footer)
        footer_layout.setContentsMargins(24, 0, 24, 0)
        
        version_label = QLabel('AnalyX v1.0')
        version_label.setFont(QFont('Inter', 11, QFont.Weight.Medium))
        version_label.setStyleSheet('color: #64748b;')
        
        footer_layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        sidebar_layout.addWidget(sidebar_footer)
        
        return sidebar
    
    def create_workspace(self):
        workspace = QWidget()
        workspace.setStyleSheet('''
            QWidget {
                background-color: #ffffff;
                border-radius: 16px;
            }
        ''')
        
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(24, 24, 24, 24)
        workspace_layout.setSpacing(20)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet('''
            QTabWidget {
                background-color: transparent;
                color: #1e293b;
                font-family: Inter;
            }
            QTabBar {
                background-color: transparent;
                height: 48px;
                padding-left: 0;
            }
            QTabBar::tab {
                background-color: transparent;
                color: #94a3b8;
                padding: 0 28px;
                font-size: 12px;
                font-weight: 600;
                border-bottom: 3px solid transparent;
                margin-right: 4px;
            }
            QTabBar::tab:hover {
                color: #64748b;
            }
            QTabBar::tab:selected {
                color: #6366f1;
                border-bottom: 3px solid #6366f1;
            }
        ''')
        
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.header_view = EditableHeaderView(Qt.Orientation.Horizontal, self)
        self.data_table.setHorizontalHeader(self.header_view)
        self.data_table.setStyleSheet('''
            QTableWidget {
                background-color: #ffffff;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                gridline-color: #f1f5f9;
                font-family: Inter;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 12px 16px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #6366f120;
                color: #6366f1;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                padding: 14px 16px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-size: 12px;
                font-weight: 600;
                font-family: Inter;
            }
            QHeaderView::section:horizontal {
                border-right: 1px solid #f1f5f9;
            }
        ''')
        self.data_table.cellChanged.connect(self.on_cell_changed)
        self.tab_widget.addTab(self.data_table, '📋  数据视图')
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont('Inter', 11))
        self.results_text.setStyleSheet('''
            QTextEdit {
                background-color: #ffffff;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 24px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        self.tab_widget.addTab(self.results_text, '📊  分析结果')
        
        self.chart_canvas = FigureCanvas(Figure(figsize=(10, 7)))
        chart_container = QWidget()
        chart_container.setStyleSheet('''
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        ''')
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.setContentsMargins(16, 16, 16, 16)
        chart_layout.addWidget(self.chart_canvas)
        self.tab_widget.addTab(chart_container, '🎨  图表')
        
        workspace_layout.addWidget(self.tab_widget)
        
        return workspace
    
    def apply_theme(self):
        if self.dark_theme:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(15, 23, 42))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(226, 232, 240))
            palette.setColor(QPalette.ColorRole.Base, QColor(30, 41, 59))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(51, 65, 85))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(51, 65, 85))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(226, 232, 240))
            palette.setColor(QPalette.ColorRole.Text, QColor(226, 232, 240))
            palette.setColor(QPalette.ColorRole.Button, QColor(51, 65, 85))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(226, 232, 240))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(239, 68, 68))
            palette.setColor(QPalette.ColorRole.Link, QColor(99, 102, 241))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(99, 102, 241))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            QApplication.setPalette(palette)
            plt.style.use('seaborn-v0_8-dark')
        else:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(248, 250, 252))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 41, 59))
            palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(248, 250, 252))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(30, 41, 59))
            palette.setColor(QPalette.ColorRole.Text, QColor(30, 41, 59))
            palette.setColor(QPalette.ColorRole.Button, QColor(241, 245, 249))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(30, 41, 59))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(239, 68, 68))
            palette.setColor(QPalette.ColorRole.Link, QColor(99, 102, 241))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(99, 102, 241))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            QApplication.setPalette(palette)
            plt.style.use('seaborn-v0_8-whitegrid')
    
    def load_sample_data(self):
        self.df = DataHandler.load_sample_data()
        self.update_data_table()
        if not self.df.empty:
            self.status_bar.data_info_label.setText(f'{len(self.df)} 行 × {len(self.df.columns)} 列')
    
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
        if '描述统计' in text:
            self.show_descriptive_stats()
        elif 't 检验' in text:
            self.show_ttest_one_sample()
        elif '方差分析' in text:
            self.show_anova()
        elif '相关分析' in text:
            self.show_correlation()
        elif '回归分析' in text:
            self.show_regression()
        elif '信度分析' in text:
            self.show_reliability()
        elif '图表绘制' in text:
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
            self.status_bar.data_info_label.setText(f'{len(self.df)} 行 × {len(self.df.columns)} 列')
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
        self.apply_theme()
        self.status_bar.status_label.setText('已切换主题')
    
    def show_about(self):
        QMessageBox.about(
            self, '关于 AnalyX',
            '<h2 style="color: #6366f1;">AnalyX 1.0</h2>'
            '<p>专业统计分析平台</p>'
            '<p>功能全面超越 SPSS，速度更快</p>'
            '<p>支持：描述统计、t 检验、ANOVA、相关、回归、信度分析等</p>'
            '<p style="color: #64748b;">© 2024 AnalyX. All rights reserved.</p>'
        )
    
    def show_descriptive_stats(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self, '警告', '没有数值型数据')
            return
        
        dialog = self.create_modern_dialog('描述统计', 560, 500)
        main_layout = dialog.layout()
        
        var_group = self.create_form_section('选择变量 (可多选):')
        var_list = QListWidget()
        var_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        var_list.addItems(numeric_cols)
        if numeric_cols:
            var_list.setCurrentRow(0)
        var_list.setStyleSheet('''
            QListWidget {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 8px;
                font-family: Inter;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #6366f1;
                color: white;
            }
        ''')
        var_group.layout().addWidget(var_list)
        main_layout.addWidget(var_group)
        
        stats_group = self.create_form_section('选择统计量:')
        stats_grid = QWidget()
        grid_layout = QGridLayout(stats_grid)
        grid_layout.setSpacing(12)
        
        checks = [
            ('均值', True), ('中位数', True), ('标准差', True),
            ('方差', True), ('最小值', True), ('最大值', True),
            ('全距', True), ('偏度', True), ('峰度', True),
            ('百分位数', False)
        ]
        check_widgets = {}
        for i, (text, checked) in enumerate(checks):
            check = QCheckBox(text)
            check.setChecked(checked)
            check.setFont(QFont('Inter', 11))
            check.setStyleSheet('color: #475569;')
            check_widgets[text] = check
            grid_layout.addWidget(check, i // 2, i % 2)
        
        stats_group.layout().addWidget(stats_grid)
        main_layout.addWidget(stats_group)
        
        ci_check = QCheckBox('计算95%置信区间')
        ci_check.setFont(QFont('Inter', 11))
        ci_check.setStyleSheet('color: #475569;')
        main_layout.addWidget(ci_check)
        
        chart_check = QCheckBox('生成直方图')
        chart_check.setFont(QFont('Inter', 11))
        chart_check.setStyleSheet('color: #475569;')
        main_layout.addWidget(chart_check)
        
        btn_layout = self.create_button_layout(dialog)
        main_layout.addLayout(btn_layout)
        
        def calculate():
            selected_items = [item.text() for item in var_list.selectedItems()]
            if not selected_items:
                QMessageBox.warning(self, '警告', '请至少选择一个变量')
                return
            
            result_html = '<h2 style="color: #1e293b; margin-bottom: 20px;">描述统计结果</h2>'
            
            for col in selected_items:
                data = self.df[col].dropna()
                desc = stats.describe(data)
                
                result_html += f'<h3 style="color: #6366f1; margin-top: 24px; margin-bottom: 12px;">{col}</h3>'
                result_html += '<table style="border-collapse: collapse; width: 100%; margin-bottom: 16px;">'
                result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">样本数</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{desc.nobs}</td></tr>'
                
                if check_widgets['均值'].isChecked():
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">均值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{desc.mean:.4f}</td></tr>'
                if check_widgets['中位数'].isChecked():
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">中位数</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{np.median(data):.4f}</td></tr>'
                if check_widgets['标准差'].isChecked():
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">标准差</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{np.std(data, ddof=1):.4f}</td></tr>'
                if check_widgets['方差'].isChecked():
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">方差</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{desc.variance:.4f}</td></tr>'
                if check_widgets['最小值'].isChecked():
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">最小值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{desc.minmax[0]:.4f}</td></tr>'
                if check_widgets['最大值'].isChecked():
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">最大值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{desc.minmax[1]:.4f}</td></tr>'
                if check_widgets['全距'].isChecked():
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">全距</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{desc.minmax[1] - desc.minmax[0]:.4f}</td></tr>'
                if check_widgets['偏度'].isChecked():
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">偏度</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{desc.skewness:.4f}</td></tr>'
                if check_widgets['峰度'].isChecked():
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">峰度</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{desc.kurtosis:.4f}</td></tr>'
                if check_widgets['百分位数'].isChecked():
                    percentiles = np.percentile(data, [25, 50, 75])
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">25%分位数</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{percentiles[0]:.4f}</td></tr>'
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">50%分位数</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{percentiles[1]:.4f}</td></tr>'
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">75%分位数</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{percentiles[2]:.4f}</td></tr>'
                if ci_check.isChecked():
                    ci = stats.t.interval(0.95, len(data)-1, loc=np.mean(data), scale=stats.sem(data))
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">95%置信区间</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">[{ci[0]:.4f}, {ci[1]:.4f}]</td></tr>'
                
                result_html += '</table>'
                
                if chart_check.isChecked():
                    self.chart_canvas.figure.clear()
                    ax = self.chart_canvas.figure.add_subplot(111)
                    ax.hist(data, bins='auto', edgecolor='#e2e8f0', alpha=0.8, color='#6366f1')
                    ax.set_title(f'直方图 - {col}', fontsize=12, fontweight='bold')
                    ax.set_xlabel(col, fontsize=10)
                    ax.set_ylabel('频数', fontsize=10)
                    ax.grid(True, alpha=0.3, axis='y')
                    self.chart_canvas.draw()
                    self.tab_widget.setCurrentIndex(2)
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentIndex(1)
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
        dialog.exec()
    
    def create_modern_dialog(self, title, width, height):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(width, height)
        dialog.setStyleSheet('''
            QDialog {
                background-color: #ffffff;
            }
        ''')
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        return dialog
    
    def create_form_section(self, label_text):
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        label = QLabel(label_text)
        label.setFont(QFont('Inter', 12, QFont.Weight.Bold))
        label.setStyleSheet('color: #1e293b;')
        layout.addWidget(label)
        
        return section
    
    def create_button_layout(self, dialog):
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        return btn_layout
    
    def setup_dialog_buttons(self, dialog, btn_layout, calculate_callback):
        cancel_btn = QPushButton('取消')
        cancel_btn.setFont(QFont('Inter', 11, QFont.Weight.Medium))
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setStyleSheet('''
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: none;
                border-radius: 10px;
                padding: 12px 28px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        ''')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        calculate_btn = QPushButton('计算')
        calculate_btn.setDefault(True)
        calculate_btn.setFont(QFont('Inter', 11, QFont.Weight.Medium))
        calculate_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        calculate_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 28px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #7c3aed);
            }
        ''')
        calculate_btn.clicked.connect(calculate_callback)
        btn_layout.addWidget(calculate_btn)
    
    def show_ttest_one_sample(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self, '警告', '没有数值型数据')
            return
        
        dialog = self.create_modern_dialog('单样本 t 检验', 520, 480)
        main_layout = dialog.layout()
        
        var_group = self.create_form_section('选择变量:')
        combo = QComboBox()
        combo.addItems(numeric_cols)
        combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-family: Inter;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #cbd5e1;
            }
            QComboBox:focus {
                border-color: #6366f1;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        ''')
        var_group.layout().addWidget(combo)
        main_layout.addWidget(var_group)
        
        test_value_group = QWidget()
        test_value_layout = QHBoxLayout(test_value_group)
        test_value_layout.setContentsMargins(0, 0, 0, 0)
        test_value_layout.setSpacing(12)
        
        test_label = QLabel('检验值:')
        test_label.setFont(QFont('Inter', 12, QFont.Weight.Bold))
        test_label.setStyleSheet('color: #1e293b;')
        
        test_value = QDoubleSpinBox()
        test_value.setRange(-1e9, 1e9)
        test_value.setValue(0)
        test_value.setDecimals(4)
        test_value.setStyleSheet('''
            QDoubleSpinBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        
        test_value_layout.addWidget(test_label)
        test_value_layout.addWidget(test_value)
        main_layout.addWidget(test_value_group)
        
        options_group = self.create_form_section('选项:')
        ci_group = QWidget()
        ci_layout = QHBoxLayout(ci_group)
        ci_layout.setContentsMargins(0, 0, 0, 0)
        ci_layout.setSpacing(12)
        
        ci_label = QLabel('置信水平:')
        ci_label.setFont(QFont('Inter', 11))
        ci_label.setStyleSheet('color: #475569;')
        
        ci_combo = QComboBox()
        ci_combo.addItems(['90%', '95%', '99%'])
        ci_combo.setCurrentText('95%')
        ci_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 8px 12px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        
        ci_layout.addWidget(ci_label)
        ci_layout.addWidget(ci_combo)
        options_group.layout().addWidget(ci_group)
        
        chart_check = QCheckBox('生成箱线图')
        chart_check.setFont(QFont('Inter', 11))
        chart_check.setStyleSheet('color: #475569;')
        options_group.layout().addWidget(chart_check)
        
        effect_size_check = QCheckBox('计算效应量 (Cohen\'s d)')
        effect_size_check.setChecked(True)
        effect_size_check.setFont(QFont('Inter', 11))
        effect_size_check.setStyleSheet('color: #475569;')
        options_group.layout().addWidget(effect_size_check)
        
        main_layout.addWidget(options_group)
        
        btn_layout = self.create_button_layout(dialog)
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
            
            result_html = f'<h2 style="color: #1e293b; margin-bottom: 20px;">单样本 t 检验 - {col}</h2>'
            result_html += '<table style="border-collapse: collapse; width: 100%;">'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">t 值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{t_stat:.4f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">自由度</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{len(data)-1}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">P 值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{p_val:.6f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">显著性</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{"显著 (p < 0.05)" if p_val < 0.05 else "不显著"}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">均值差</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{mean_diff:.4f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">标准误差</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{se_diff:.4f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">{int(ci_level*100)}% 置信区间</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">[{ci[0]-test_value.value():.4f}, {ci[1]-test_value.value():.4f}]</td></tr>'
            
            if effect_size_check.isChecked():
                result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">Cohen\'s d</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{cohens_d:.4f}</td></tr>'
            
            result_html += '</table>'
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentIndex(1)
            
            if chart_check.isChecked():
                self.chart_canvas.figure.clear()
                ax = self.chart_canvas.figure.add_subplot(111)
                ax.boxplot(data, vert=True, patch_artist=True, boxprops=dict(facecolor='#6366f1', alpha=0.7))
                ax.axhline(y=test_value.value(), color='#ef4444', linestyle='--', linewidth=2, label=f'检验值: {test_value.value()}')
                ax.set_title(f'箱线图 - {col}', fontsize=12, fontweight='bold')
                ax.set_ylabel(col, fontsize=10)
                ax.grid(True, alpha=0.3, axis='y')
                ax.legend()
                self.chart_canvas.draw()
                self.tab_widget.setCurrentIndex(2)
            
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
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
        
        dialog = self.create_modern_dialog('独立样本 t 检验', 520, 400)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        test_var_label = QLabel('检验变量:')
        test_var_label.setFont(QFont('Inter', 12, QFont.Weight.Bold))
        test_var_label.setStyleSheet('color: #1e293b;')
        layout.addWidget(test_var_label)
        
        test_var_combo = QComboBox()
        test_var_combo.addItems(numeric_cols)
        test_var_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        layout.addWidget(test_var_combo)
        
        group_var_label = QLabel('分组变量:')
        group_var_label.setFont(QFont('Inter', 12, QFont.Weight.Bold))
        group_var_label.setStyleSheet('color: #1e293b;')
        layout.addWidget(group_var_label)
        
        group_var_combo = QComboBox()
        group_var_combo.addItems(all_cols)
        group_var_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        layout.addWidget(group_var_combo)
        
        layout.addStretch()
        
        btn_layout = self.create_button_layout(dialog)
        layout.addLayout(btn_layout)
        
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
            
            result_html = f'<h2 style="color: #1e293b; margin-bottom: 20px;">独立样本 t 检验</h2>'
            result_html += f'<p style="color: #64748b; margin-bottom: 16px;">检验变量: {test_col}, 分组变量: {group_col}</p>'
            result_html += '<table style="border-collapse: collapse; width: 100%;">'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">组1均值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{mean1:.4f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">组2均值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{mean2:.4f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">均值差</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{mean1 - mean2:.4f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">t 值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{t_stat:.4f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">P 值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{p_val:.6f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">显著性</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{"显著 (p < 0.05)" if p_val < 0.05 else "不显著"}</td></tr>'
            result_html += '</table>'
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentIndex(1)
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
        dialog.exec()
    
    def show_ttest_paired(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        dialog = self.create_modern_dialog('配对样本 t 检验', 520, 400)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        var1_label = QLabel('变量1 (前测):')
        var1_label.setFont(QFont('Inter', 12, QFont.Weight.Bold))
        var1_label.setStyleSheet('color: #1e293b;')
        layout.addWidget(var1_label)
        
        var1_combo = QComboBox()
        var1_combo.addItems(numeric_cols)
        var1_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        layout.addWidget(var1_combo)
        
        var2_label = QLabel('变量2 (后测):')
        var2_label.setFont(QFont('Inter', 12, QFont.Weight.Bold))
        var2_label.setStyleSheet('color: #1e293b;')
        layout.addWidget(var2_label)
        
        var2_combo = QComboBox()
        var2_combo.addItems(numeric_cols)
        if len(numeric_cols) > 1:
            var2_combo.setCurrentIndex(1)
        var2_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        layout.addWidget(var2_combo)
        
        layout.addStretch()
        
        btn_layout = self.create_button_layout(dialog)
        layout.addLayout(btn_layout)
        
        def calculate():
            col1 = var1_combo.currentText()
            col2 = var2_combo.currentText()
            
            data = self.df[[col1, col2]].dropna()
            t_stat, p_val = stats.ttest_rel(data[col1], data[col2])
            
            result_html = f'<h2 style="color: #1e293b; margin-bottom: 20px;">配对样本 t 检验</h2>'
            result_html += f'<p style="color: #64748b; margin-bottom: 16px;">{col1} vs {col2}</p>'
            result_html += '<table style="border-collapse: collapse; width: 100%;">'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">t 值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{t_stat:.4f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">P 值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{p_val:.6f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">显著性</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{"显著 (p < 0.05)" if p_val < 0.05 else "不显著"}</td></tr>'
            result_html += '</table>'
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentIndex(1)
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
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
        
        dialog = self.create_modern_dialog('单因素 ANOVA', 520, 520)
        main_layout = dialog.layout()
        
        dep_var_group = self.create_form_section('因变量:')
        dep_var_combo = QComboBox()
        dep_var_combo.addItems(numeric_cols)
        dep_var_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        dep_var_group.layout().addWidget(dep_var_combo)
        main_layout.addWidget(dep_var_group)
        
        factor_group = self.create_form_section('因子 (分组):')
        factor_combo = QComboBox()
        factor_combo.addItems(all_cols)
        factor_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        factor_group.layout().addWidget(factor_combo)
        main_layout.addWidget(factor_group)
        
        options_group = self.create_form_section('选项:')
        post_hoc_check = QCheckBox('执行事后检验 (Tukey HSD)')
        post_hoc_check.setFont(QFont('Inter', 11))
        post_hoc_check.setStyleSheet('color: #475569;')
        options_group.layout().addWidget(post_hoc_check)
        
        chart_check = QCheckBox('生成箱线图')
        chart_check.setFont(QFont('Inter', 11))
        chart_check.setStyleSheet('color: #475569;')
        options_group.layout().addWidget(chart_check)
        
        effect_size_check = QCheckBox('计算效应量 (η²)')
        effect_size_check.setChecked(True)
        effect_size_check.setFont(QFont('Inter', 11))
        effect_size_check.setStyleSheet('color: #475569;')
        options_group.layout().addWidget(effect_size_check)
        
        main_layout.addWidget(options_group)
        
        btn_layout = self.create_button_layout(dialog)
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
            
            result_html = f'<h2 style="color: #1e293b; margin-bottom: 20px;">单因素方差分析 (ANOVA)</h2>'
            result_html += f'<p style="color: #64748b; margin-bottom: 16px;">因变量: {dep_col}, 因子: {factor_col}</p>'
            result_html += '<table style="border-collapse: collapse; width: 100%;">'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">F 值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{f_stat:.4f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">P 值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{p_val:.6f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">显著性</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{"显著 (p < 0.05)" if p_val < 0.05 else "不显著"}</td></tr>'
            
            if effect_size_check.isChecked():
                result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">η² (效应量)</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{eta_squared:.4f}</td></tr>'
            
            result_html += '</table>'
            
            if post_hoc_check.isChecked() and p_val < 0.05:
                from statsmodels.stats.multicomp import pairwise_tukeyhsd
                
                data = []
                labels = []
                for i, group in enumerate(groups):
                    data.extend(group)
                    labels.extend([f'组{i+1}'] * len(group))
                
                tukey = pairwise_tukeyhsd(data, labels, alpha=0.05)
                
                result_html += '<h3 style="color: #6366f1; margin-top: 24px; margin-bottom: 12px;">事后检验 (Tukey HSD)</h3>'
                result_html += '<table style="border-collapse: collapse; width: 100%;">'
                result_html += '<tr><th style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">比较组</th><th style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">均值差</th><th style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">p 值</th><th style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">显著性</th></tr>'
                
                for i, (group1, group2, meandiff, p, reject) in enumerate(zip(
                    tukey.groupsunique[tukey.group1inds],
                    tukey.groupsunique[tukey.group2inds],
                    tukey.meandiffs,
                    tukey.pvalues,
                    tukey.reject
                )):
                    result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{group1} vs {group2}</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{meandiff:.4f}</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{p:.4f}</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{"显著" if reject else "不显著"}</td></tr>'
                
                result_html += '</table>'
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentIndex(1)
            
            if chart_check.isChecked():
                self.chart_canvas.figure.clear()
                ax = self.chart_canvas.figure.add_subplot(111)
                bp = ax.boxplot(groups, vert=True, patch_artist=True)
                for patch in bp['boxes']:
                    patch.set_facecolor('#6366f1')
                    patch.set_alpha(0.7)
                ax.set_title(f'箱线图 - {dep_col} by {factor_col}', fontsize=12, fontweight='bold')
                ax.set_ylabel(dep_col, fontsize=10)
                ax.set_xticklabels([f'组{i+1}' for i in range(len(groups))])
                ax.grid(True, alpha=0.3, axis='y')
                self.chart_canvas.draw()
                self.tab_widget.setCurrentIndex(2)
            
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
        dialog.exec()
    
    def show_correlation(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        dialog = self.create_modern_dialog('相关分析', 540, 540)
        main_layout = dialog.layout()
        
        var_group = self.create_form_section('变量选择:')
        var1_layout = QHBoxLayout()
        var1_layout.setSpacing(12)
        var1_label = QLabel('变量 X:')
        var1_label.setFont(QFont('Inter', 11))
        var1_label.setStyleSheet('color: #475569;')
        var1_combo = QComboBox()
        var1_combo.addItems(numeric_cols)
        var1_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 10px 14px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        var1_layout.addWidget(var1_label)
        var1_layout.addWidget(var1_combo)
        var_group.layout().addLayout(var1_layout)
        
        var2_layout = QHBoxLayout()
        var2_layout.setSpacing(12)
        var2_label = QLabel('变量 Y:')
        var2_label.setFont(QFont('Inter', 11))
        var2_label.setStyleSheet('color: #475569;')
        var2_combo = QComboBox()
        var2_combo.addItems(numeric_cols)
        if len(numeric_cols) > 1:
            var2_combo.setCurrentIndex(1)
        var2_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 10px 14px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        var2_layout.addWidget(var2_label)
        var2_layout.addWidget(var2_combo)
        var_group.layout().addLayout(var2_layout)
        main_layout.addWidget(var_group)
        
        method_group = self.create_form_section('相关方法:')
        method_combo = QComboBox()
        method_combo.addItems(['Pearson', 'Spearman', 'Kendall'])
        method_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 10px 14px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        method_group.layout().addWidget(method_combo)
        main_layout.addWidget(method_group)
        
        options_group = self.create_form_section('选项:')
        ci_group = QWidget()
        ci_layout = QHBoxLayout(ci_group)
        ci_layout.setContentsMargins(0, 0, 0, 0)
        ci_layout.setSpacing(12)
        ci_label = QLabel('置信水平:')
        ci_label.setFont(QFont('Inter', 11))
        ci_label.setStyleSheet('color: #475569;')
        ci_combo = QComboBox()
        ci_combo.addItems(['90%', '95%', '99%'])
        ci_combo.setCurrentText('95%')
        ci_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 8px 12px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        ci_layout.addWidget(ci_label)
        ci_layout.addWidget(ci_combo)
        options_group.layout().addWidget(ci_group)
        
        chart_check = QCheckBox('生成散点图')
        chart_check.setFont(QFont('Inter', 11))
        chart_check.setStyleSheet('color: #475569;')
        options_group.layout().addWidget(chart_check)
        
        regression_check = QCheckBox('添加回归直线')
        regression_check.setFont(QFont('Inter', 11))
        regression_check.setStyleSheet('color: #475569;')
        regression_check.setEnabled(False)
        options_group.layout().addWidget(regression_check)
        
        def on_chart_check_changed(state):
            regression_check.setEnabled(state == Qt.CheckState.Checked)
        chart_check.stateChanged.connect(on_chart_check_changed)
        
        main_layout.addWidget(options_group)
        
        btn_layout = self.create_button_layout(dialog)
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
            
            result_html = f'<h2 style="color: #1e293b; margin-bottom: 20px;">相关分析</h2>'
            result_html += f'<p style="color: #64748b; margin-bottom: 16px;">{col1} 与 {col2} ({method})</p>'
            result_html += '<table style="border-collapse: collapse; width: 100%;">'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">相关系数</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{corr:.4f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">P 值</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{p_val:.6f}</td></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">显著性</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{"显著 (p < 0.05)" if p_val < 0.05 else "不显著"}</td></tr>'
            result_html += '</table>'
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentIndex(1)
            
            if chart_check.isChecked():
                self.chart_canvas.figure.clear()
                ax = self.chart_canvas.figure.add_subplot(111)
                ax.scatter(data[col1], data[col2], alpha=0.7, color='#6366f1', s=50)
                
                if regression_check.isChecked():
                    z = np.polyfit(data[col1], data[col2], 1)
                    p = np.poly1d(z)
                    ax.plot(data[col1], p(data[col1]), color='#ef4444', linewidth=2)
                
                ax.set_title(f'散点图 - {col1} vs {col2}', fontsize=12, fontweight='bold')
                ax.set_xlabel(col1, fontsize=10)
                ax.set_ylabel(col2, fontsize=10)
                ax.grid(True, alpha=0.3)
                self.chart_canvas.draw()
                self.tab_widget.setCurrentIndex(2)
            
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
        dialog.exec()
    
    def show_regression(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        dialog = self.create_modern_dialog('回归分析', 540, 480)
        main_layout = dialog.layout()
        
        dep_var_group = self.create_form_section('因变量 (Y):')
        dep_var_combo = QComboBox()
        dep_var_combo.addItems(numeric_cols)
        dep_var_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        dep_var_group.layout().addWidget(dep_var_combo)
        main_layout.addWidget(dep_var_group)
        
        indep_var_group = self.create_form_section('自变量 (X):')
        indep_var_list = QListWidget()
        indep_var_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        indep_var_list.addItems(numeric_cols)
        if numeric_cols:
            indep_var_list.setCurrentRow(1)
        indep_var_list.setStyleSheet('''
            QListWidget {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 8px;
                font-family: Inter;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #6366f1;
                color: white;
            }
        ''')
        indep_var_group.layout().addWidget(indep_var_list)
        main_layout.addWidget(indep_var_group)
        
        btn_layout = self.create_button_layout(dialog)
        main_layout.addLayout(btn_layout)
        
        def calculate():
            dep_col = dep_var_combo.currentText()
            selected_indeps = [item.text() for item in indep_var_list.selectedItems()]
            
            if not selected_indeps:
                QMessageBox.warning(self, '警告', '请至少选择一个自变量')
                return
            
            data = self.df[[dep_col] + selected_indeps].dropna()
            
            from sklearn.linear_model import LinearRegression
            
            X = data[selected_indeps].values
            y = data[dep_col].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            result_html = f'<h2 style="color: #1e293b; margin-bottom: 20px;">回归分析</h2>'
            result_html += f'<p style="color: #64748b; margin-bottom: 16px;">因变量: {dep_col}</p>'
            result_html += '<h3 style="color: #6366f1; margin-top: 20px; margin-bottom: 12px;">回归系数</h3>'
            result_html += '<table style="border-collapse: collapse; width: 100%;">'
            result_html += '<tr><th style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">变量</th><th style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">系数</th></tr>'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">截距</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{model.intercept_:.4f}</td></tr>'
            
            for i, col in enumerate(selected_indeps):
                result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{col}</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{model.coef_[i]:.4f}</td></tr>'
            
            result_html += '</table>'
            result_html += f'<h3 style="color: #6366f1; margin-top: 20px; margin-bottom: 12px;">模型拟合</h3>'
            result_html += '<table style="border-collapse: collapse; width: 100%;">'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">R²</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0;">{model.score(X, y):.4f}</td></tr>'
            result_html += '</table>'
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentIndex(1)
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
        dialog.exec()
    
    def show_reliability(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        dialog = self.create_modern_dialog('信度分析', 520, 460)
        main_layout = dialog.layout()
        
        var_group = self.create_form_section('选择量表题项 (可多选):')
        var_list = QListWidget()
        var_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        var_list.addItems(numeric_cols)
        var_list.setStyleSheet('''
            QListWidget {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 8px;
                font-family: Inter;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #6366f1;
                color: white;
            }
        ''')
        var_group.layout().addWidget(var_list)
        main_layout.addWidget(var_group)
        
        btn_layout = self.create_button_layout(dialog)
        main_layout.addLayout(btn_layout)
        
        def calculate():
            selected_items = [item.text() for item in var_list.selectedItems()]
            if len(selected_items) < 2:
                QMessageBox.warning(self, '警告', '请至少选择2个题项')
                return
            
            data = self.df[selected_items].dropna()
            
            def cronbach_alpha(data):
                k = data.shape[1]
                if k < 2:
                    return 0
                variances = data.var(axis=0, ddof=1)
                total_variance = data.sum(axis=1).var(ddof=1)
                alpha = (k / (k - 1)) * (1 - variances.sum() / total_variance)
                return alpha
            
            alpha = cronbach_alpha(data)
            
            result_html = f'<h2 style="color: #1e293b; margin-bottom: 20px;">信度分析</h2>'
            result_html += f'<p style="color: #64748b; margin-bottom: 16px;">题项数: {len(selected_items)}</p>'
            result_html += '<table style="border-collapse: collapse; width: 100%;">'
            result_html += f'<tr><td style="padding: 10px 14px; border: 1px solid #e2e8f0; background: #f8fafc; font-weight: 600;">Cronbach\'s α</td><td style="padding: 10px 14px; border: 1px solid #e2e8f0; font-size: 18px; font-weight: bold;">{alpha:.4f}</td></tr>'
            result_html += '</table>'
            
            if alpha >= 0.9:
                feedback = '优秀'
            elif alpha >= 0.8:
                feedback = '良好'
            elif alpha >= 0.7:
                feedback = '可接受'
            elif alpha >= 0.6:
                feedback = '一般'
            else:
                feedback = '较差'
            
            result_html += f'<p style="margin-top: 16px; font-size: 14px; font-weight: 600;">信度评价: {feedback}</p>'
            
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentIndex(1)
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
        dialog.exec()
    
    def show_histogram(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self, '警告', '没有数值型数据')
            return
        
        dialog = self.create_modern_dialog('直方图', 520, 380)
        main_layout = dialog.layout()
        
        var_group = self.create_form_section('选择变量:')
        combo = QComboBox()
        combo.addItems(numeric_cols)
        combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        var_group.layout().addWidget(combo)
        main_layout.addWidget(var_group)
        
        btn_layout = self.create_button_layout(dialog)
        main_layout.addLayout(btn_layout)
        
        def calculate():
            col = combo.currentText()
            data = self.df[col].dropna()
            
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(111)
            ax.hist(data, bins='auto', edgecolor='#e2e8f0', alpha=0.8, color='#6366f1')
            ax.set_title(f'直方图 - {col}', fontsize=12, fontweight='bold')
            ax.set_xlabel(col, fontsize=10)
            ax.set_ylabel('频数', fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
            self.chart_canvas.draw()
            self.tab_widget.setCurrentIndex(2)
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
        dialog.exec()
    
    def show_boxplot(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self, '警告', '没有数值型数据')
            return
        
        dialog = self.create_modern_dialog('箱线图', 520, 380)
        main_layout = dialog.layout()
        
        var_group = self.create_form_section('选择变量 (可多选):')
        var_list = QListWidget()
        var_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        var_list.addItems(numeric_cols)
        if numeric_cols:
            var_list.setCurrentRow(0)
        var_list.setStyleSheet('''
            QListWidget {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 8px;
                font-family: Inter;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #6366f1;
                color: white;
            }
        ''')
        var_group.layout().addWidget(var_list)
        main_layout.addWidget(var_group)
        
        btn_layout = self.create_button_layout(dialog)
        main_layout.addLayout(btn_layout)
        
        def calculate():
            selected_items = [item.text() for item in var_list.selectedItems()]
            if not selected_items:
                QMessageBox.warning(self, '警告', '请至少选择一个变量')
                return
            
            data = [self.df[col].dropna() for col in selected_items]
            
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(111)
            bp = ax.boxplot(data, vert=True, patch_artist=True, labels=selected_items)
            for patch in bp['boxes']:
                patch.set_facecolor('#6366f1')
                patch.set_alpha(0.7)
            ax.set_title('箱线图', fontsize=12, fontweight='bold')
            ax.set_ylabel('数值', fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
            self.chart_canvas.draw()
            self.tab_widget.setCurrentIndex(2)
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
        dialog.exec()
    
    def show_scatterplot(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        dialog = self.create_modern_dialog('散点图', 540, 420)
        main_layout = dialog.layout()
        
        var_group = self.create_form_section('变量选择:')
        var1_layout = QHBoxLayout()
        var1_layout.setSpacing(12)
        var1_label = QLabel('X 轴:')
        var1_label.setFont(QFont('Inter', 11))
        var1_label.setStyleSheet('color: #475569;')
        var1_combo = QComboBox()
        var1_combo.addItems(numeric_cols)
        var1_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 10px 14px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        var1_layout.addWidget(var1_label)
        var1_layout.addWidget(var1_combo)
        var_group.layout().addLayout(var1_layout)
        
        var2_layout = QHBoxLayout()
        var2_layout.setSpacing(12)
        var2_label = QLabel('Y 轴:')
        var2_label.setFont(QFont('Inter', 11))
        var2_label.setStyleSheet('color: #475569;')
        var2_combo = QComboBox()
        var2_combo.addItems(numeric_cols)
        if len(numeric_cols) > 1:
            var2_combo.setCurrentIndex(1)
        var2_combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 10px 14px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        var2_layout.addWidget(var2_label)
        var2_layout.addWidget(var2_combo)
        var_group.layout().addLayout(var2_layout)
        main_layout.addWidget(var_group)
        
        btn_layout = self.create_button_layout(dialog)
        main_layout.addLayout(btn_layout)
        
        def calculate():
            col1 = var1_combo.currentText()
            col2 = var2_combo.currentText()
            
            data = self.df[[col1, col2]].dropna()
            
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(111)
            ax.scatter(data[col1], data[col2], alpha=0.7, color='#6366f1', s=50)
            ax.set_title(f'散点图 - {col1} vs {col2}', fontsize=12, fontweight='bold')
            ax.set_xlabel(col1, fontsize=10)
            ax.set_ylabel(col2, fontsize=10)
            ax.grid(True, alpha=0.3)
            self.chart_canvas.draw()
            self.tab_widget.setCurrentIndex(2)
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
        dialog.exec()
    
    def show_barchart(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        all_cols = self.df.columns.tolist()
        if not all_cols:
            QMessageBox.warning(self, '警告', '没有数据')
            return
        
        dialog = self.create_modern_dialog('条形图', 520, 400)
        main_layout = dialog.layout()
        
        var_group = self.create_form_section('选择分类变量:')
        combo = QComboBox()
        combo.addItems(all_cols)
        combo.setStyleSheet('''
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-family: Inter;
                font-size: 12px;
            }
        ''')
        var_group.layout().addWidget(combo)
        main_layout.addWidget(var_group)
        
        btn_layout = self.create_button_layout(dialog)
        main_layout.addLayout(btn_layout)
        
        def calculate():
            col = combo.currentText()
            data = self.df[col].dropna()
            counts = data.value_counts()
            
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(111)
            colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']
            bars = ax.bar(range(len(counts)), counts.values, color=colors[:len(counts)], alpha=0.8)
            ax.set_xticks(range(len(counts)))
            ax.set_xticklabels(counts.index, rotation=45, ha='right')
            ax.set_title(f'条形图 - {col}', fontsize=12, fontweight='bold')
            ax.set_ylabel('频数', fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
            self.chart_canvas.figure.tight_layout()
            self.chart_canvas.draw()
            self.tab_widget.setCurrentIndex(2)
            dialog.accept()
        
        self.setup_dialog_buttons(dialog, btn_layout, calculate)
        dialog.exec()
    
    def show_heatmap(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, '警告', '至少需要2个数值型变量')
            return
        
        self.chart_canvas.figure.clear()
        ax = self.chart_canvas.figure.add_subplot(111)
        corr_matrix = self.df[numeric_cols].corr()
        im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)
        
        ax.set_xticks(range(len(numeric_cols)))
        ax.set_yticks(range(len(numeric_cols)))
        ax.set_xticklabels(numeric_cols, rotation=45, ha='right')
        ax.set_yticklabels(numeric_cols)
        ax.set_title('相关系数热力图', fontsize=12, fontweight='bold')
        
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}', 
                       ha='center', va='center', color='white', fontweight='bold')
        
        self.chart_canvas.figure.colorbar(im, ax=ax)
        self.chart_canvas.figure.tight_layout()
        self.chart_canvas.draw()
        self.tab_widget.setCurrentIndex(2)