import sys
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import seaborn as sns
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QSplitter, QListWidget,
    QTextEdit, QMenuBar, QToolBar, QStatusBar, QFileDialog,
    QMessageBox, QDialog, QFormLayout, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QProgressBar, QTabWidget, QDockWidget,
    QHeaderView, QInputDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont, QPalette, QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class AnalyXMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = pd.DataFrame()
        self.current_file = None
        self.dark_theme = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('AnalyX - 学术统计软件 v1.0')
        self.setMinimumSize(1400, 900)
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        self.create_central_widget()
        self.create_dock_widgets()
        self.load_sample_data()

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('文件(&F)')
        new_action = QAction('新建项目(&N)', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction('打开文件(&O)...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        import_menu = file_menu.addMenu('导入(&I)')
        import_csv_action = QAction('CSV 文件...', self)
        import_csv_action.triggered.connect(self.import_csv)
        import_menu.addAction(import_csv_action)
        
        import_excel_action = QAction('Excel 文件...', self)
        import_excel_action.triggered.connect(self.import_excel)
        import_menu.addAction(import_excel_action)
        
        import_spss_action = QAction('SPSS .sav 文件...', self)
        import_spss_action.triggered.connect(self.import_spss)
        import_menu.addAction(import_spss_action)
        
        file_menu.addSeparator()
        
        save_action = QAction('保存(&S)', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('另存为(&A)...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_menu = file_menu.addMenu('导出(&E)')
        export_csv_action = QAction('CSV 文件...', self)
        export_csv_action.triggered.connect(self.export_csv)
        export_menu.addAction(export_csv_action)
        
        export_pdf_action = QAction('PDF 文档...', self)
        export_pdf_action.triggered.connect(self.export_pdf)
        export_menu.addAction(export_pdf_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu('编辑(&E)')
        
        analysis_menu = menubar.addMenu('分析(&A)')
        descriptive_action = QAction('描述统计...', self)
        descriptive_action.triggered.connect(self.show_descriptive_stats)
        analysis_menu.addAction(descriptive_action)
        
        analysis_menu.addSeparator()
        
        ttest_menu = analysis_menu.addMenu('t 检验')
        ttest_one_action = QAction('单样本 t 检验...', self)
        ttest_one_action.triggered.connect(self.show_ttest_one_sample)
        ttest_menu.addAction(ttest_one_action)
        
        ttest_ind_action = QAction('独立样本 t 检验...', self)
        ttest_ind_action.triggered.connect(self.show_ttest_independent)
        ttest_menu.addAction(ttest_ind_action)
        
        ttest_paired_action = QAction('配对样本 t 检验...', self)
        ttest_paired_action.triggered.connect(self.show_ttest_paired)
        ttest_menu.addAction(ttest_paired_action)
        
        analysis_menu.addSeparator()
        
        anova_action = QAction('单因素 ANOVA...', self)
        anova_action.triggered.connect(self.show_anova)
        analysis_menu.addAction(anova_action)
        
        analysis_menu.addSeparator()
        
        corr_action = QAction('相关分析...', self)
        corr_action.triggered.connect(self.show_correlation)
        analysis_menu.addAction(corr_action)
        
        regression_action = QAction('回归分析...', self)
        regression_action.triggered.connect(self.show_regression)
        analysis_menu.addAction(regression_action)
        
        analysis_menu.addSeparator()
        
        reliability_action = QAction('信度分析 (Cronbach α)...', self)
        reliability_action.triggered.connect(self.show_reliability)
        analysis_menu.addAction(reliability_action)

        chart_menu = menubar.addMenu('图表(&C)')
        histogram_action = QAction('直方图...', self)
        histogram_action.triggered.connect(self.show_histogram)
        chart_menu.addAction(histogram_action)
        
        boxplot_action = QAction('箱线图...', self)
        boxplot_action.triggered.connect(self.show_boxplot)
        chart_menu.addAction(boxplot_action)
        
        scatter_action = QAction('散点图...', self)
        scatter_action.triggered.connect(self.show_scatterplot)
        chart_menu.addAction(scatter_action)
        
        bar_action = QAction('条形图...', self)
        bar_action.triggered.connect(self.show_barchart)
        chart_menu.addAction(bar_action)
        
        heatmap_action = QAction('热力图...', self)
        heatmap_action.triggered.connect(self.show_heatmap)
        chart_menu.addAction(heatmap_action)

        tools_menu = menubar.addMenu('工具(&T)')
        theme_action = QAction('切换主题(&D)', self)
        theme_action.triggered.connect(self.toggle_theme)
        tools_menu.addAction(theme_action)

        help_menu = menubar.addMenu('帮助(&H)')
        about_action = QAction('关于 ByteStats(&A)...', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_tool_bar(self):
        toolbar = QToolBar('主工具栏', self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        new_action = QAction('新建', self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        open_action = QAction('打开', self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction('保存', self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel('就绪')
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addWidget(self.status_label, 1)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def create_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
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
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tab_widget.addTab(self.data_table, '数据视图')
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont('Consolas', 10))
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

    def new_project(self):
        reply = QMessageBox.question(
            self, '确认', '当前项目未保存，是否继续？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.df = pd.DataFrame()
            self.current_file = None
            self.update_data_table()
            self.results_text.clear()
            self.status_label.setText('新项目已创建')

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
            self.status_label.setText(f'已加载: {os.path.basename(file_path)}')
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
            self.status_label.setText(f'已保存: {os.path.basename(file_path)}')
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
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
            QApplication.setPalette(palette)
            plt.style.use('dark_background')
        else:
            QApplication.setPalette(QApplication.style().standardPalette())
            plt.style.use('default')
        self.status_label.setText('已切换主题')

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
        layout = QFormLayout(dialog)
        
        combo = QComboBox()
        combo.addItems(numeric_cols)
        layout.addRow('选择变量:', combo)
        
        btn = QPushButton('计算')
        layout.addRow(btn)
        
        def calculate():
            col = combo.currentText()
            data = self.df[col].dropna()
            desc = stats.describe(data)
            result_html = f'''
            <h2>描述统计 - {col}</h2>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>样本数</b></td><td>{desc.nobs}</td></tr>
            <tr><td><b>均值</b></td><td>{desc.mean:.4f}</td></tr>
            <tr><td><b>中位数</b></td><td>{np.median(data):.4f}</td></tr>
            <tr><td><b>标准差</b></td><td>{np.std(data, ddof=1):.4f}</td></tr>
            <tr><td><b>方差</b></td><td>{desc.variance:.4f}</td></tr>
            <tr><td><b>最小值</b></td><td>{desc.minmax[0]:.4f}</td></tr>
            <tr><td><b>最大值</b></td><td>{desc.minmax[1]:.4f}</td></tr>
            <tr><td><b>全距</b></td><td>{desc.minmax[1] - desc.minmax[0]:.4f}</td></tr>
            <tr><td><b>偏度</b></td><td>{desc.skewness:.4f}</td></tr>
            <tr><td><b>峰度</b></td><td>{desc.kurtosis:.4f}</td></tr>
            </table>
            '''
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            dialog.accept()
        
        btn.clicked.connect(calculate)
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
        layout = QFormLayout(dialog)
        
        combo = QComboBox()
        combo.addItems(numeric_cols)
        layout.addRow('选择变量:', combo)
        
        test_value = QDoubleSpinBox()
        test_value.setRange(-1e9, 1e9)
        test_value.setValue(0)
        test_value.setDecimals(4)
        layout.addRow('检验值:', test_value)
        
        btn = QPushButton('计算')
        layout.addRow(btn)
        
        def calculate():
            col = combo.currentText()
            data = self.df[col].dropna()
            t_stat, p_val = stats.ttest_1samp(data, test_value.value())
            mean_diff = np.mean(data) - test_value.value()
            se_diff = stats.sem(data)
            ci = stats.t.interval(0.95, len(data)-1, loc=np.mean(data), scale=se_diff)
            
            result_html = f'''
            <h2>单样本 t 检验 - {col}</h2>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>t 值</b></td><td>{t_stat:.4f}</td></tr>
            <tr><td><b>自由度</b></td><td>{len(data)-1}</td></tr>
            <tr><td><b>P 值</b></td><td>{p_val:.6f}</td></tr>
            <tr><td><b>显著性</b></td><td>{'显著 (p < 0.05)' if p_val < 0.05 else '不显著'}</td></tr>
            <tr><td><b>均值差</b></td><td>{mean_diff:.4f}</td></tr>
            <tr><td><b>标准误差</b></td><td>{se_diff:.4f}</td></tr>
            <tr><td><b>95% 置信区间</b></td><td>[{ci[0]-test_value.value():.4f}, {ci[1]-test_value.value():.4f}]</td></tr>
            </table>
            '''
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            dialog.accept()
        
        btn.clicked.connect(calculate)
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
        layout = QFormLayout(dialog)
        
        dep_var_combo = QComboBox()
        dep_var_combo.addItems(numeric_cols)
        layout.addRow('因变量:', dep_var_combo)
        
        factor_combo = QComboBox()
        factor_combo.addItems(all_cols)
        layout.addRow('因子 (分组):', factor_combo)
        
        btn = QPushButton('计算')
        layout.addRow(btn)
        
        def calculate():
            dep_col = dep_var_combo.currentText()
            factor_col = factor_combo.currentText()
            
            groups = [group[dep_col].dropna().values for _, group in self.df.groupby(factor_col)]
            groups = [g for g in groups if len(g) > 0]
            
            if len(groups) < 2:
                QMessageBox.warning(self, '警告', '因子至少需要2个组别')
                return
            
            f_stat, p_val = stats.f_oneway(*groups)
            
            result_html = f'''
            <h2>单因素方差分析 (ANOVA)</h2>
            <p>因变量: {dep_col}, 因子: {factor_col}</p>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>F 值</b></td><td>{f_stat:.4f}</td></tr>
            <tr><td><b>P 值</b></td><td>{p_val:.6f}</td></tr>
            <tr><td><b>显著性</b></td><td>{'显著 (p < 0.05)' if p_val < 0.05 else '不显著'}</td></tr>
            </table>
            '''
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            dialog.accept()
        
        btn.clicked.connect(calculate)
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
        layout = QFormLayout(dialog)
        
        var1_combo = QComboBox()
        var1_combo.addItems(numeric_cols)
        layout.addRow('变量 X:', var1_combo)
        
        var2_combo = QComboBox()
        var2_combo.addItems(numeric_cols)
        if len(numeric_cols) > 1:
            var2_combo.setCurrentIndex(1)
        layout.addRow('变量 Y:', var2_combo)
        
        method_combo = QComboBox()
        method_combo.addItems(['Pearson', 'Spearman'])
        layout.addRow('方法:', method_combo)
        
        btn = QPushButton('计算')
        layout.addRow(btn)
        
        def calculate():
            col1 = var1_combo.currentText()
            col2 = var2_combo.currentText()
            method = method_combo.currentText()
            
            data = self.df[[col1, col2]].dropna()
            
            if method == 'Pearson':
                corr, p_val = stats.pearsonr(data[col1], data[col2])
            else:
                corr, p_val = stats.spearmanr(data[col1], data[col2])
            
            result_html = f'''
            <h2>相关分析 - {method}</h2>
            <p>{col1} & {col2}</p>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>相关系数 r</b></td><td>{corr:.4f}</td></tr>
            <tr><td><b>样本量 N</b></td><td>{len(data)}</td></tr>
            <tr><td><b>P 值</b></td><td>{p_val:.6f}</td></tr>
            <tr><td><b>显著性</b></td><td>{'显著 (p < 0.05)' if p_val < 0.05 else '不显著'}</td></tr>
            </table>
            '''
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            dialog.accept()
        
        btn.clicked.connect(calculate)
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
        layout = QFormLayout(dialog)
        
        x_combo = QComboBox()
        x_combo.addItems(numeric_cols)
        layout.addRow('自变量 X:', x_combo)
        
        y_combo = QComboBox()
        y_combo.addItems(numeric_cols)
        if len(numeric_cols) > 1:
            y_combo.setCurrentIndex(1)
        layout.addRow('因变量 Y:', y_combo)
        
        btn = QPushButton('计算')
        layout.addRow(btn)
        
        def calculate():
            x_col = x_combo.currentText()
            y_col = y_combo.currentText()
            
            data = self.df[[x_col, y_col]].dropna()
            x = data[x_col].values
            y = data[y_col].values
            
            slope, intercept, r_value, p_val, std_err = stats.linregress(x, y)
            r_squared = r_value ** 2
            
            result_html = f'''
            <h2>简单线性回归</h2>
            <p>Y = {y_col}, X = {x_col}</p>
            <h3>模型摘要</h3>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><td><b>R</b></td><td>{r_value:.4f}</td></tr>
            <tr><td><b>R²</b></td><td>{r_squared:.4f}</td></tr>
            <tr><td><b>调整 R²</b></td><td>{1 - (1 - r_squared) * (len(y) - 1) / (len(y) - 2):.4f}</td></tr>
            </table>
            <h3>系数</h3>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
            <tr><th></th><th>系数</th><th>标准误</th><th>t</th><th>P</th></tr>
            <tr><td><b>(截距)</b></td><td>{intercept:.4f}</td><td>-</td><td>-</td><td>-</td></tr>
            <tr><td><b>{x_col}</b></td><td>{slope:.4f}</td><td>{std_err:.4f}</td><td>{slope/std_err:.4f}</td><td>{p_val:.6f}</td></tr>
            </table>
            '''
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            dialog.accept()
        
        btn.clicked.connect(calculate)
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
        layout = QVBoxLayout(dialog)
        
        label = QLabel('选择量表题项 (按住Ctrl多选):')
        layout.addWidget(label)
        
        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        list_widget.addItems(numeric_cols)
        layout.addWidget(list_widget)
        
        btn = QPushButton('计算 Cronbach α')
        layout.addWidget(btn)
        
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
            <tr><td><b>评价</b></td><td>{interpretation}</td></tr>
            </table>
            <p><b>题项:</b> {', '.join(selected_items)}</p>
            '''
            self.results_text.setHtml(result_html)
            self.tab_widget.setCurrentWidget(self.results_text)
            dialog.accept()
        
        btn.clicked.connect(calculate)
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
        layout = QFormLayout(dialog)
        
        combo = QComboBox()
        combo.addItems(numeric_cols)
        layout.addRow('选择变量:', combo)
        
        btn = QPushButton('绘制')
        layout.addRow(btn)
        
        def plot():
            col = combo.currentText()
            data = self.df[col].dropna()
            
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(111)
            ax.hist(data, bins='auto', edgecolor='black', alpha=0.7)
            ax.set_title(f'直方图 - {col}')
            ax.set_xlabel(col)
            ax.set_ylabel('频数')
            ax.grid(True, alpha=0.3)
            self.chart_canvas.draw()
            
            self.tab_widget.setCurrentWidget(self.chart_canvas)
            dialog.accept()
        
        btn.clicked.connect(plot)
        dialog.exec()

    def show_boxplot(self):
        if self.df.empty:
            QMessageBox.warning(self, '警告', '请先加载数据')
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self, '警告', '没有数值型数据')
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('箱线图')
        layout = QFormLayout(dialog)
        
        combo = QComboBox()
        combo.addItems(numeric_cols)
        layout.addRow('选择变量:', combo)
        
        btn = QPushButton('绘制')
        layout.addRow(btn)
        
        def plot():
            col = combo.currentText()
            data = self.df[col].dropna()
            
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(111)
            ax.boxplot(data, vert=True)
            ax.set_title(f'箱线图 - {col}')
            ax.set_ylabel(col)
            ax.grid(True, alpha=0.3, axis='y')
            self.chart_canvas.draw()
            
            self.tab_widget.setCurrentWidget(self.chart_canvas)
            dialog.accept()
        
        btn.clicked.connect(plot)
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


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('AnalyX')
    app.setOrganizationName('AnalyX')
    
    window = AnalyXMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
