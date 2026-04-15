from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMenu, QAction
from PyQt6.QtGui import QPalette, QColor


class ModernMenuBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(0)
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(25, 25, 30))
        self.setPalette(palette)
        
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
