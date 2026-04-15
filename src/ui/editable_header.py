from PyQt6.QtWidgets import QHeaderView, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


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
        self.editor.setText(self.model().headerData(index, self.orientation))
        self.editor.setGeometry(rect)
        self.editor.setFont(QFont('Lora', 12))
        self.editor.setStyleSheet('''
            QLineEdit {
                background-color: white;
                color: #141413;
                border: 2px solid #6a9bcc;
                border-radius: 4px;
                padding: 8px;
                font-family: Lora;
                font-size: 12px;
            }
            QLineEdit:focus {
                outline: none;
                box-shadow: 0 0 0 2px rgba(106, 155, 204, 0.2);
            }
        ''')
        self.editor.selectAll()
        self.editor.setFocus()
        
        self.editor.editingFinished.connect(self.finish_editing)
        self.editor.show()
    
    def finish_editing(self):
        if self.editing_index != -1 and self.editor:
            new_text = self.editor.text()
            if new_text:
                old_text = self.model().headerData(self.editing_index, self.orientation)
                if old_text != new_text:
                    self.model().setHeaderData(self.editing_index, self.orientation, new_text)
                    self.parent().on_header_changed(self.editing_index, new_text)
            
            self.editor.deleteLater()
            self.editor = None
            self.editing_index = -1
