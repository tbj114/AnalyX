from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMenu
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt


class ModernMenuBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 8, 20, 8)
        self.layout.setSpacing(4)
        
        self.setStyleSheet('''
            ModernMenuBar {
                background-color: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
            }
        ''')
        
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
            menu_button = self.create_menu_button(menu_name)
            menu = self.create_menu()
            self.add_menu_items(menu, items)
            menu_button.setMenu(menu)
            self.layout.addWidget(menu_button)
        
        self.layout.addStretch()
    
    def create_menu_button(self, text):
        btn = QPushButton(text)
        btn.setFont(QFont('Inter', 11, QFont.Weight.Medium))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                color: #475569;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                color: #1e293b;
            }
            QPushButton:pressed {
                background-color: #cbd5e1;
            }
        ''')
        return btn
    
    def create_menu(self):
        menu = QMenu()
        menu.setCursor(Qt.CursorShape.PointingHandCursor)
        menu.setStyleSheet('''
            QMenu {
                background-color: #ffffff;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px;
                font-family: Inter;
                font-size: 11px;
            }
            QMenu::item {
                padding: 10px 16px;
                border-radius: 8px;
                margin: 2px 0;
            }
            QMenu::item:selected {
                background-color: #f1f5f9;
                color: #1e293b;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e2e8f0;
                margin: 4px 8px;
            }
            QMenu::right-arrow {
                width: 12px;
                height: 12px;
            }
        ''')
        return menu
    
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
                submenu.setCursor(Qt.CursorShape.PointingHandCursor)
                submenu.setStyleSheet('''
                    QMenu {
                        background-color: #ffffff;
                        color: #1e293b;
                        border: 1px solid #e2e8f0;
                        border-radius: 12px;
                        padding: 8px;
                        font-family: Inter;
                        font-size: 11px;
                    }
                    QMenu::item {
                        padding: 10px 16px;
                        border-radius: 8px;
                        margin: 2px 0;
                    }
                    QMenu::item:selected {
                        background-color: #f1f5f9;
                        color: #1e293b;
                    }
                ''')
                self.add_menu_items(submenu, subitems)
