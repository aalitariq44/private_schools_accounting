#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح ترتيب المعرف في جدول الطلاب
"""

import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt

class NumericTableWidgetItem(QTableWidgetItem):
    """عنصر جدول مخصص للترتيب الرقمي"""
    
    def __init__(self, text, numeric_value=None):
        super().__init__(text)
        if numeric_value is not None:
            self.setData(Qt.UserRole, numeric_value)
        else:
            # محاولة استخراج القيمة الرقمية من النص
            try:
                # إزالة الفواصل والعملة
                clean_text = text.replace(',', '').replace('د.ع', '').strip()
                numeric_value = float(clean_text) if clean_text else 0
                self.setData(Qt.UserRole, numeric_value)
            except:
                self.setData(Qt.UserRole, 0)
    
    def __lt__(self, other):
        """مقارنة مخصصة للترتيب الرقمي"""
        try:
            self_data = self.data(Qt.UserRole)
            other_data = other.data(Qt.UserRole)
            
            # إذا كان كلاهما رقمي
            if self_data is not None and other_data is not None:
                if isinstance(self_data, (int, float)) and isinstance(other_data, (int, float)):
                    return float(self_data) < float(other_data)
            
            # في حالة عدم وجود بيانات رقمية، استخدم الترتيب النصي
            return super().__lt__(other)
        except:
            return super().__lt__(other)

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # إنشاء الجدول
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["المعرف", "الاسم"])
        self.table.setSortingEnabled(True)
        
        # إضافة البيانات التجريبية
        test_data = [
            (1, "زيد محمد علي"),
            (10, "عائل أحمد محمد"),
            (100, "أحمد علي محمد"),
            (2, "ياسر عبدالله أحمد"),
            (21, "سارة أحمد محمد"),
            (101, "نادية علي محمد"),
            (3, "مريم أحمد محمد"),
            (30, "خالد محمد أحمد"),
            (102, "سهام محمد أحمد"),
            (4, "فاطمة علي محمد"),
            (40, "سلمى محمد علي")
        ]
        
        self.table.setRowCount(len(test_data))
        
        for row, (id_val, name) in enumerate(test_data):
            # عمود المعرف بالفئة المخصصة
            id_item = NumericTableWidgetItem(str(id_val), id_val)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, id_item)
            
            # عمود الاسم
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, name_item)
        
        layout.addWidget(self.table)
        
        # زر للاختبار
        test_btn = QPushButton("اختبار الترتيب")
        test_btn.clicked.connect(self.test_sorting)
        layout.addWidget(test_btn)
        
        self.setLayout(layout)
        self.setWindowTitle("اختبار ترتيب المعرف")
        self.resize(600, 400)
    
    def test_sorting(self):
        print("اختبار الترتيب...")
        # ترتيب عمود المعرف تصاعدياً
        self.table.sortItems(0, Qt.AscendingOrder)
        
        # طباعة النتائج
        print("النتائج بعد الترتيب:")
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)
            print(f"الصف {row + 1}: المعرف = {id_item.text()}, الاسم = {name_item.text()}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
