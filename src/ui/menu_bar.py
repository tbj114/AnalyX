from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMenu
from PyQt6.QtGui import QPalette, QColor, QFont, QAction


class ModernMenuBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 0, 20, 0)
        self.layout.setSpacing(0)
        
        # Modern background
        self.setStyleSheet('''
            QWidget {
                background-color: #f8f7f3;
                border-bottom: 1px solid #e8e6dc;
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
            menu_button = QPushButton(menu_name)
            menu_button.setFont(QFont('Poppins', 11, QFont.Weight.Medium))
            menu_button.setStyleSheet('''
                QPushButton {
                    background-color: transparent;
                    color: #141413;
                    border: none;
                    padding: 10px 20px;
                    font-size: 11px;
                    font-weight: 500;
                    border-radius: 6px;
                    margin: 4px 2px;
                }
                QPushButton:hover {
                    background-color: rgba(106, 155, 204, 0.1);
                    color: #6a9bcc;
                }
            ''')
            menu = QMenu(menu_button)
            menu.setStyleSheet('''
                QMenu {
                    background-color: white;
                    color: #141413;
                    border: 1px solid #e8e6dc;
                    border-radius: 6px;
                    padding: 4px 0;
                    font-family: Lora;
                }
                QMenu::item {
                    padding: 8px 24px;
                    border: none;
                }
                QMenu::item:selected {
                    background-color: rgba(106, 155, 204, 0.1);
                    color: #6a9bcc;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #e8e6dc;
                    margin: 4px 0;
                }
            ''')
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
                submenu.setStyleSheet('''
                    QMenu {
                        background-color: white;
                        color: #141413;
                        border: 1px solid #e8e6dc;
                        border-radius: 6px;
                        padding: 4px 0;
                        font-family: Lora;
                    }
                    QMenu::item {
                        padding: 8px 24px;
                        border: none;
                    }
                    QMenu::item:selected {
                        background-color: rgba(106, 155, 204, 0.1);
                        color: #6a9bcc;
                    }
                ''')
                self.add_menu_items(submenu, subitems)
