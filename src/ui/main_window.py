import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem, 
    QComboBox, QLineEdit, QTextEdit, QDialog, QFormLayout, QSpinBox,
    QRadioButton, QGroupBox, QScrollArea, QSplitter, QStatusBar,
    QCheckBox, QTabWidget, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QPixmap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy import stats

class AnalyXMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.df = pd.DataFrame()
        self.current_file = None
        self.dark_theme = False
        self.init_ui()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("AnalyX - 数据分析工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create main content area
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self.create_sidebar()
        content_layout.addWidget(sidebar)
        
        # Create workspace
        workspace = self.create_workspace()
        content_layout.addWidget(workspace, 1)
        
        main_layout.addWidget(content_area, 1)
        
        # Create status bar
        status_bar = self.create_status_bar()
        self.setStatusBar(status_bar)
        
        # Apply initial theme
        self.apply_theme()
    
    def create_header(self):
        header = QWidget()
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(20)
        
        # Logo and title
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(10)
        
        logo_label = QLabel()
        logo_label.setText("AX")
        logo_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        logo_label.setFixedSize(36, 36)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("""
            background-color: #3b82f6;
            color: white;
            border-radius: 18px;
        """)
        
        title_label = QLabel("AnalyX")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Medium))
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        
        # Navigation
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(20)
        
        nav_items = ["数据", "分析", "可视化", "导出"]
        for item in nav_items:
            nav_button = QPushButton(item)
            nav_button.setFlat(True)
            nav_button.setFont(QFont("Arial", 12))
            nav_button.setStyleSheet("""
                QPushButton {
                    color: #64748b;
                    padding: 8px 12px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #f1f5f9;
                    color: #3b82f6;
                }
                QPushButton:pressed {
                    background-color: #e2e8f0;
                }
            """)
            nav_layout.addWidget(nav_button)
        
        # Actions
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)
        
        theme_toggle = QPushButton("🌙")
        theme_toggle.setFixedSize(36, 36)
        theme_toggle.setFlat(True)
        theme_toggle.setStyleSheet("""
            QPushButton {
                border-radius: 18px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)
        theme_toggle.clicked.connect(self.toggle_theme)
        
        min_button = QPushButton("-")
        min_button.setFixedSize(36, 36)
        min_button.setFlat(True)
        min_button.setStyleSheet("""
            QPushButton {
                border-radius: 18px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)
        min_button.clicked.connect(self.showMinimized)
        
        close_button = QPushButton("✕")
        close_button.setFixedSize(36, 36)
        close_button.setFlat(True)
        close_button.setStyleSheet("""
            QPushButton {
                border-radius: 18px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #fee2e2;
                color: #dc2626;
            }
        """)
        close_button.clicked.connect(self.close)
        
        actions_layout.addWidget(theme_toggle)
        actions_layout.addWidget(min_button)
        actions_layout.addWidget(close_button)
        
        header_layout.addWidget(logo_container)
        header_layout.addWidget(nav_container, 1)
        header_layout.addWidget(actions_container)
        
        header.setStyleSheet("""
            background-color: white;
            border-bottom: 1px solid #e2e8f0;
        """)
        
        return header
    
    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(20)
        
        # Section: 数据操作
        data_section = QWidget()
        data_layout = QVBoxLayout(data_section)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(10)
        
        data_title = QLabel("数据操作")
        data_title.setFont(QFont("Arial", 12, QFont.Weight.Medium))
        data_title.setStyleSheet("color: #64748b;")
        
        import_button = QPushButton("导入数据")
        import_button.setFont(QFont("Arial", 11))
        import_button.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
        """)
        import_button.clicked.connect(self.import_data)
        
        export_button = QPushButton("导出数据")
        export_button.setFont(QFont("Arial", 11))
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
        """)
        export_button.clicked.connect(self.export_data)
        
        data_layout.addWidget(data_title)
        data_layout.addWidget(import_button)
        data_layout.addWidget(export_button)
        
        # Section: 分析工具
        analysis_section = QWidget()
        analysis_layout = QVBoxLayout(analysis_section)
        analysis_layout.setContentsMargins(0, 0, 0, 0)
        analysis_layout.setSpacing(10)
        
        analysis_title = QLabel("分析工具")
        analysis_title.setFont(QFont("Arial", 12, QFont.Weight.Medium))
        analysis_title.setStyleSheet("color: #64748b;")
        
        descriptive_button = QPushButton("描述性统计")
        descriptive_button.setFont(QFont("Arial", 11))
        descriptive_button.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
        """)
        descriptive_button.clicked.connect(self.descriptive_stats)
        
        ttest_button = QPushButton("t检验")
        ttest_button.setFont(QFont("Arial", 11))
        ttest_button.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
        """)
        ttest_button.clicked.connect(self.ttest)
        
        anova_button = QPushButton("方差分析")
        anova_button.setFont(QFont("Arial", 11))
        anova_button.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
        """)
        anova_button.clicked.connect(self.anova)
        
        correlation_button = QPushButton("相关性分析")
        correlation_button.setFont(QFont("Arial", 11))
        correlation_button.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
        """)
        correlation_button.clicked.connect(self.correlation)
        
        regression_button = QPushButton("回归分析")
        regression_button.setFont(QFont("Arial", 11))
        regression_button.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
        """)
        regression_button.clicked.connect(self.regression)
        
        reliability_button = QPushButton("信度分析")
        reliability_button.setFont(QFont("Arial", 11))
        reliability_button.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
        """)
        reliability_button.clicked.connect(self.reliability)
        
        analysis_layout.addWidget(analysis_title)
        analysis_layout.addWidget(descriptive_button)
        analysis_layout.addWidget(ttest_button)
        analysis_layout.addWidget(anova_button)
        analysis_layout.addWidget(correlation_button)
        analysis_layout.addWidget(regression_button)
        analysis_layout.addWidget(reliability_button)
        
        # Section: 数据信息
        info_section = QWidget()
        info_layout = QVBoxLayout(info_section)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(10)
        
        info_title = QLabel("数据信息")
        info_title.setFont(QFont("Arial", 12, QFont.Weight.Medium))
        info_title.setStyleSheet("color: #64748b;")
        
        self.info_label = QLabel("未导入数据")
        self.info_label.setFont(QFont("Arial", 10))
        self.info_label.setStyleSheet("color: #94a3b8;")
        self.info_label.setWordWrap(True)
        
        info_layout.addWidget(info_title)
        info_layout.addWidget(self.info_label)
        
        sidebar_layout.addWidget(data_section)
        sidebar_layout.addWidget(analysis_section)
        sidebar_layout.addWidget(info_section)
        sidebar_layout.addStretch(1)
        
        sidebar.setStyleSheet("""
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
        """)
        
        return sidebar
    
    def create_workspace(self):
        workspace = QWidget()
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)
        
        # Workspace header
        workspace_header = QWidget()
        workspace_header.setFixedHeight(50)
        workspace_header_layout = QHBoxLayout(workspace_header)
        workspace_header_layout.setContentsMargins(20, 0, 20, 0)
        workspace_header_layout.setSpacing(20)
        
        workspace_title = QLabel("工作区")
        workspace_title.setFont(QFont("Arial", 14, QFont.Weight.Medium))
        
        workspace_header_layout.addWidget(workspace_title)
        workspace_header_layout.addStretch(1)
        
        workspace_header.setStyleSheet("""
            background-color: white;
            border-bottom: 1px solid #e2e8f0;
        """)
        
        # Workspace content
        workspace_content = QWidget()
        workspace_content_layout = QVBoxLayout(workspace_content)
        workspace_content_layout.setContentsMargins(0, 0, 0, 0)
        workspace_content_layout.setSpacing(0)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #f8fafc;
            }
            QTabBar {
                background-color: white;
                border-bottom: 1px solid #e2e8f0;
            }
            QTabBar::tab {
                background-color: white;
                color: #64748b;
                padding: 12px 24px;
                border: none;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:hover {
                color: #3b82f6;
            }
            QTabBar::tab:selected {
                color: #3b82f6;
                border-bottom: 2px solid #3b82f6;
            }
        """)
        
        # Data tab
        data_tab = QWidget()
        data_tab_layout = QVBoxLayout(data_tab)
        data_tab_layout.setContentsMargins(20, 20, 20, 20)
        
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                gridline-color: #e2e8f0;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #64748b;
                padding: 8px;
                border: 1px solid #e2e8f0;
            }
            QTableWidgetItem {
                padding: 8px;
            }
        """)
        
        data_tab_layout.addWidget(self.data_table)
        
        # Results tab
        results_tab = QWidget()
        results_tab_layout = QVBoxLayout(results_tab)
        results_tab_layout.setContentsMargins(20, 20, 20, 20)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 12px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        
        results_tab_layout.addWidget(self.results_text)
        
        # Chart tab
        chart_tab = QWidget()
        chart_tab_layout = QVBoxLayout(chart_tab)
        chart_tab_layout.setContentsMargins(20, 20, 20, 20)
        
        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("""
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
        """)
        
        chart_tab_layout.addWidget(self.canvas)
        
        self.tabs.addTab(data_tab, "数据")
        self.tabs.addTab(results_tab, "结果")
        self.tabs.addTab(chart_tab, "图表")
        
        workspace_content_layout.addWidget(self.tabs)
        
        workspace_layout.addWidget(workspace_header)
        workspace_layout.addWidget(workspace_content, 1)
        
        return workspace
    
    def create_status_bar(self):
        status_bar = QStatusBar()
        status_bar.setFixedHeight(30)
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f8fafc;
                border-top: 1px solid #e2e8f0;
                color: #64748b;
                font-size: 10px;
            }
        """)
        
        status_label = QLabel("就绪")
        status_bar.addWidget(status_label)
        
        return status_bar
    
    def apply_theme(self):
        if self.dark_theme:
            # Dark theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e293b;
                    color: #e2e8f0;
                }
                QHeaderView::section {
                    background-color: #334155;
                    color: #e2e8f0;
                    border: 1px solid #475569;
                }
                QTableWidget {
                    background-color: #334155;
                    border: 1px solid #475569;
                    gridline-color: #475569;
                }
                QTextEdit {
                    background-color: #334155;
                    border: 1px solid #475569;
                    color: #e2e8f0;
                }
                QPushButton {
                    background-color: #334155;
                    color: #e2e8f0;
                    border: 1px solid #475569;
                }
                QPushButton:hover {
                    background-color: #475569;
                    border-color: #64748b;
                }
                QTabWidget::pane {
                    background-color: #334155;
                }
                QTabBar {
                    background-color: #1e293b;
                    border-bottom: 1px solid #475569;
                }
                QTabBar::tab {
                    background-color: #1e293b;
                    color: #94a3b8;
                }
                QTabBar::tab:hover {
                    color: #e2e8f0;
                }
                QTabBar::tab:selected {
                    color: #e2e8f0;
                    border-bottom: 2px solid #3b82f6;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("")
    
    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.apply_theme()
    
    def import_data(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "导入数据", "", "CSV Files (*.csv);;Excel Files (*.xlsx;*.xls)")
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                else:
                    self.df = pd.read_excel(file_path)
                
                self.current_file = file_path
                self.update_data_table()
                self.update_info_label()
                self.statusBar().showMessage(f"成功导入数据: {os.path.basename(file_path)}")
            except Exception as e:
                self.statusBar().showMessage(f"导入失败: {str(e)}")
    
    def export_data(self):
        if self.df.empty:
            self.statusBar().showMessage("无数据可导出")
            return
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "导出数据", "", "CSV Files (*.csv);;Excel Files (*.xlsx)")
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df.to_csv(file_path, index=False)
                else:
                    self.df.to_excel(file_path, index=False)
                
                self.statusBar().showMessage(f"成功导出数据: {os.path.basename(file_path)}")
            except Exception as e:
                self.statusBar().showMessage(f"导出失败: {str(e)}")
    
    def update_data_table(self):
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(len(self.df.columns))
        self.data_table.setHorizontalHeaderLabels(self.df.columns)
        
        for i, row in self.df.iterrows():
            self.data_table.insertRow(i)
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, item)
        
        self.data_table.resizeColumnsToContents()
    
    def update_info_label(self):
        info = f"行数: {len(self.df)}\n列数: {len(self.df.columns)}\n列名: {', '.join(self.df.columns[:5])}{'...' if len(self.df.columns) > 5 else ''}"
        self.info_label.setText(info)
    
    def descriptive_stats(self):
        if self.df.empty:
            self.statusBar().showMessage("请先导入数据")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("描述性统计")
        dialog.setGeometry(300, 300, 600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Variable selection
        var_group = QGroupBox("选择变量")
        var_layout = QVBoxLayout(var_group)
        
        self.var_checkboxes = []
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                checkbox = QCheckBox(col)
                checkbox.setChecked(True)
                self.var_checkboxes.append(checkbox)
                var_layout.addWidget(checkbox)
        
        layout.addWidget(var_group)
        
        # Options
        options_group = QGroupBox("选项")
        options_layout = QVBoxLayout(options_group)
        
        mean_checkbox = QCheckBox("均值")
        mean_checkbox.setChecked(True)
        options_layout.addWidget(mean_checkbox)
        
        std_checkbox = QCheckBox("标准差")
        std_checkbox.setChecked(True)
        options_layout.addWidget(std_checkbox)
        
        min_checkbox = QCheckBox("最小值")
        min_checkbox.setChecked(True)
        options_layout.addWidget(min_checkbox)
        
        max_checkbox = QCheckBox("最大值")
        max_checkbox.setChecked(True)
        options_layout.addWidget(max_checkbox)
        
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        run_button = QPushButton("运行")
        run_button.clicked.connect(lambda: self.run_descriptive_stats(dialog))
        button_layout.addWidget(run_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def run_descriptive_stats(self, dialog):
        selected_vars = [cb.text() for cb in self.var_checkboxes if cb.isChecked()]
        
        if not selected_vars:
            self.statusBar().showMessage("请至少选择一个变量")
            return
        
        stats_df = self.df[selected_vars].describe()
        result = stats_df.to_string()
        
        self.results_text.setText(result)
        self.tabs.setCurrentIndex(1)
        
        dialog.close()
        self.statusBar().showMessage("描述性统计分析完成")
    
    def ttest(self):
        if self.df.empty:
            self.statusBar().showMessage("请先导入数据")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("t检验")
        dialog.setGeometry(300, 300, 500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Test type
        test_type_group = QGroupBox("检验类型")
        test_type_layout = QVBoxLayout(test_type_group)
        
        self.ttest_type = QComboBox()
        self.ttest_type.addItems(["独立样本t检验", "配对样本t检验"])
        test_type_layout.addWidget(self.ttest_type)
        
        layout.addWidget(test_type_group)
        
        # Variable selection
        var_group = QGroupBox("选择变量")
        var_layout = QVBoxLayout(var_group)
        
        self.ttest_var1 = QComboBox()
        self.ttest_var1.addItems([col for col in self.df.columns if pd.api.types.is_numeric_dtype(self.df[col])])
        var_layout.addWidget(QLabel("变量1"))
        var_layout.addWidget(self.ttest_var1)
        
        self.ttest_var2 = QComboBox()
        self.ttest_var2.addItems([col for col in self.df.columns if pd.api.types.is_numeric_dtype(self.df[col])])
        var_layout.addWidget(QLabel("变量2"))
        var_layout.addWidget(self.ttest_var2)
        
        layout.addWidget(var_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        run_button = QPushButton("运行")
        run_button.clicked.connect(lambda: self.run_ttest(dialog))
        button_layout.addWidget(run_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def run_ttest(self, dialog):
        var1 = self.ttest_var1.currentText()
        var2 = self.ttest_var2.currentText()
        test_type = self.ttest_type.currentText()
        
        try:
            if test_type == "独立样本t检验":
                stat, p = stats.ttest_ind(self.df[var1], self.df[var2], nan_policy='omit')
            else:
                stat, p = stats.ttest_rel(self.df[var1], self.df[var2], nan_policy='omit')
            
            result = f"t检验结果:\n"\
                     f"检验类型: {test_type}\n"\
                     f"变量1: {var1}\n"\
                     f"变量2: {var2}\n"\
                     f"t统计量: {stat:.4f}\n"\
                     f"p值: {p:.4f}\n"\
                     f"结论: {'显著' if p < 0.05 else '不显著'}"
            
            self.results_text.setText(result)
            self.tabs.setCurrentIndex(1)
            
            dialog.close()
            self.statusBar().showMessage("t检验分析完成")
        except Exception as e:
            self.statusBar().showMessage(f"分析失败: {str(e)}")
    
    def anova(self):
        if self.df.empty:
            self.statusBar().showMessage("请先导入数据")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("方差分析")
        dialog.setGeometry(300, 300, 500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Variable selection
        var_group = QGroupBox("选择变量")
        var_layout = QVBoxLayout(var_group)
        
        self.anova_dependent = QComboBox()
        self.anova_dependent.addItems([col for col in self.df.columns if pd.api.types.is_numeric_dtype(self.df[col])])
        var_layout.addWidget(QLabel("因变量"))
        var_layout.addWidget(self.anova_dependent)
        
        self.anova_independent = QComboBox()
        self.anova_independent.addItems([col for col in self.df.columns if not pd.api.types.is_numeric_dtype(self.df[col])])
        var_layout.addWidget(QLabel("自变量"))
        var_layout.addWidget(self.anova_independent)
        
        layout.addWidget(var_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        run_button = QPushButton("运行")
        run_button.clicked.connect(lambda: self.run_anova(dialog))
        button_layout.addWidget(run_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def run_anova(self, dialog):
        dependent = self.anova_dependent.currentText()
        independent = self.anova_independent.currentText()
        
        try:
            groups = [group[1][dependent].dropna() for group in self.df.groupby(independent)]
            stat, p = stats.f_oneway(*groups)
            
            result = f"方差分析结果:\n"\
                     f"因变量: {dependent}\n"\
                     f"自变量: {independent}\n"\
                     f"F统计量: {stat:.4f}\n"\
                     f"p值: {p:.4f}\n"\
                     f"结论: {'显著' if p < 0.05 else '不显著'}"
            
            self.results_text.setText(result)
            self.tabs.setCurrentIndex(1)
            
            dialog.close()
            self.statusBar().showMessage("方差分析完成")
        except Exception as e:
            self.statusBar().showMessage(f"分析失败: {str(e)}")
    
    def correlation(self):
        if self.df.empty:
            self.statusBar().showMessage("请先导入数据")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("相关性分析")
        dialog.setGeometry(300, 300, 500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Variable selection
        var_group = QGroupBox("选择变量")
        var_layout = QVBoxLayout(var_group)
        
        self.corr_vars = []
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                checkbox = QCheckBox(col)
                checkbox.setChecked(True)
                self.corr_vars.append(checkbox)
                var_layout.addWidget(checkbox)
        
        layout.addWidget(var_group)
        
        # Correlation method
        method_group = QGroupBox("相关系数方法")
        method_layout = QVBoxLayout(method_group)
        
        self.corr_method = QComboBox()
        self.corr_method.addItems(["Pearson", "Spearman", "Kendall"])
        method_layout.addWidget(self.corr_method)
        
        layout.addWidget(method_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        run_button = QPushButton("运行")
        run_button.clicked.connect(lambda: self.run_correlation(dialog))
        button_layout.addWidget(run_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def run_correlation(self, dialog):
        selected_vars = [cb.text() for cb in self.corr_vars if cb.isChecked()]
        method = self.corr_method.currentText().lower()
        
        if len(selected_vars) < 2:
            self.statusBar().showMessage("请至少选择两个变量")
            return
        
        try:
            corr_matrix = self.df[selected_vars].corr(method=method)
            result = corr_matrix.to_string()
            
            self.results_text.setText(result)
            self.tabs.setCurrentIndex(1)
            
            # Plot correlation heatmap
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            cax = ax.matshow(corr_matrix, cmap='coolwarm')
            self.figure.colorbar(cax)
            ax.set_xticks(range(len(selected_vars)))
            ax.set_yticks(range(len(selected_vars)))
            ax.set_xticklabels(selected_vars, rotation=45, ha='right')
            ax.set_yticklabels(selected_vars)
            self.canvas.draw()
            
            dialog.close()
            self.statusBar().showMessage("相关性分析完成")
        except Exception as e:
            self.statusBar().showMessage(f"分析失败: {str(e)}")
    
    def regression(self):
        if self.df.empty:
            self.statusBar().showMessage("请先导入数据")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("回归分析")
        dialog.setGeometry(300, 300, 500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Variable selection
        var_group = QGroupBox("选择变量")
        var_layout = QVBoxLayout(var_group)
        
        self.regression_dependent = QComboBox()
        self.regression_dependent.addItems([col for col in self.df.columns if pd.api.types.is_numeric_dtype(self.df[col])])
        var_layout.addWidget(QLabel("因变量"))
        var_layout.addWidget(self.regression_dependent)
        
        var_layout.addWidget(QLabel("自变量"))
        self.regression_independents = []
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]) and col != self.regression_dependent.currentText():
                checkbox = QCheckBox(col)
                checkbox.setChecked(True)
                self.regression_independents.append(checkbox)
                var_layout.addWidget(checkbox)
        
        layout.addWidget(var_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        run_button = QPushButton("运行")
        run_button.clicked.connect(lambda: self.run_regression(dialog))
        button_layout.addWidget(run_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def run_regression(self, dialog):
        dependent = self.regression_dependent.currentText()
        independents = [cb.text() for cb in self.regression_independents if cb.isChecked()]
        
        if not independents:
            self.statusBar().showMessage("请至少选择一个自变量")
            return
        
        try:
            import statsmodels.api as sm
            
            X = self.df[independents]
            X = sm.add_constant(X)
            y = self.df[dependent]
            
            model = sm.OLS(y, X).fit()
            result = model.summary().as_text()
            
            self.results_text.setText(result)
            self.tabs.setCurrentIndex(1)
            
            # Plot regression
            if len(independents) == 1:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.scatter(self.df[independents[0]], self.df[dependent], alpha=0.5)
                ax.plot(self.df[independents[0]], model.predict(X), color='red')
                ax.set_xlabel(independents[0])
                ax.set_ylabel(dependent)
                ax.set_title('回归分析')
                self.canvas.draw()
            
            dialog.close()
            self.statusBar().showMessage("回归分析完成")
        except Exception as e:
            self.statusBar().showMessage(f"分析失败: {str(e)}")
    
    def reliability(self):
        if self.df.empty:
            self.statusBar().showMessage("请先导入数据")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("信度分析")
        dialog.setGeometry(300, 300, 500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Variable selection
        var_group = QGroupBox("选择变量")
        var_layout = QVBoxLayout(var_group)
        
        self.reliability_vars = []
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                checkbox = QCheckBox(col)
                checkbox.setChecked(True)
                self.reliability_vars.append(checkbox)
                var_layout.addWidget(checkbox)
        
        layout.addWidget(var_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        run_button = QPushButton("运行")
        run_button.clicked.connect(lambda: self.run_reliability(dialog))
        button_layout.addWidget(run_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def run_reliability(self, dialog):
        selected_vars = [cb.text() for cb in self.reliability_vars if cb.isChecked()]
        
        if len(selected_vars) < 2:
            self.statusBar().showMessage("请至少选择两个变量")
            return
        
        try:
            # Calculate Cronbach's alpha
            def cronbach_alpha(items):
                items = np.asarray(items)
                itemvars = items.var(axis=0, ddof=1)
                tvar = items.sum(axis=1).var(ddof=1)
                return (len(items) / (len(items) - 1)) * (1 - itemvars.sum() / tvar)
            
            alpha = cronbach_alpha(self.df[selected_vars].dropna())
            
            result = f"信度分析结果:\n"\
                     f"Cronbach's Alpha: {alpha:.4f}\n"\
                     f"变量数: {len(selected_vars)}\n"\
                     f"结论: {'信度良好' if alpha >= 0.7 else '信度一般' if alpha >= 0.6 else '信度较差'}"
            
            self.results_text.setText(result)
            self.tabs.setCurrentIndex(1)
            
            dialog.close()
            self.statusBar().showMessage("信度分析完成")
        except Exception as e:
            self.statusBar().showMessage(f"分析失败: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalyXMainWindow()
    window.show()
    sys.exit(app.exec())