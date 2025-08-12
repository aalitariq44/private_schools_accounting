# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QDialogButtonBox

class ColumnSelectionDialog(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تحديد الأعمدة للطباعة")
        self.setLayout(QVBoxLayout())

        self.list_widget = QListWidget()
        for col_key, col_display in columns.items():
            item = QListWidgetItem(col_display)
            item.setData(1, col_key)  # Use a custom role to store the key
            item.setCheckState(2)  # Qt.Checked
            self.list_widget.addItem(item)
        
        self.layout().addWidget(self.list_widget)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout().addWidget(self.button_box)

    def get_selected_columns(self):
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == 2: # Qt.Checked
                selected.append(item.data(1)) # Get the key back
        return selected
