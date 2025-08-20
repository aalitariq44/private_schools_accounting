#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح ترتيب جميع الأعمدة في جدول الطلاب
"""

import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout
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


class ArabicTableWidgetItem(QTableWidgetItem):
    """عنصر جدول مخصص للترتيب الأبجدي العربي"""
    
    def __init__(self, text):
        super().__init__(text)
        # تحويل النص للترتيب الأبجدي العربي
        self.setData(Qt.UserRole, self.normalize_arabic_text(text))
    
    def normalize_arabic_text(self, text):
        """تطبيع النص العربي للترتيب الصحيح"""
        if not text:
            return ""
        
        # إزالة التشكيل والرموز الإضافية
        arabic_text = text.strip()
        
        # استبدال الأحرف المتشابهة للترتيب الموحد
        replacements = {
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
            'ة': 'ه',
            'ى': 'ي',
            'ؤ': 'و',
            'ئ': 'ي'
        }
        
        for old, new in replacements.items():
            arabic_text = arabic_text.replace(old, new)
        
        return arabic_text.lower()
    
    def __lt__(self, other):
        """مقارنة مخصصة للترتيب الأبجدي العربي"""
        try:
            self_data = self.data(Qt.UserRole)
            other_data = other.data(Qt.UserRole)
            
            if self_data is not None and other_data is not None:
                return str(self_data) < str(other_data)
            
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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["المعرف", "الاسم", "الشعبة", "الرسوم", "المدفوع"])
        self.table.setSortingEnabled(True)
        
        # إضافة البيانات التجريبية
        test_data = [
            (1, "زيد محمد علي", "أ", 600000, 0),
            (10, "عائل أحمد محمد", "ب", 500000, 0),
            (100, "أحمد علي محمد", "ج", 1250000, 0),
            (2, "ياسر عبدالله أحمد", "أ", 1500000, 0),
            (21, "آمال أحمد محمد", "ب", 800000, 0),
            (101, "إبراهيم علي محمد", "أ", 1250000, 0),
            (3, "أسماء أحمد علي", "ج", 850000, 0),
            (30, "خالد محمد أحمد", "ب", 1250000, 0),
            (102, "سهام محمد أحمد", "أ", 1500000, 0),
            (4, "فاطمة علي محمد", "ج", 1500000, 0),
        ]
        
        self.table.setRowCount(len(test_data))
        
        for row, (id_val, name, section, fee, paid) in enumerate(test_data):
            # عمود المعرف بالفئة المخصصة الرقمية
            id_item = NumericTableWidgetItem(str(id_val), id_val)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, id_item)
            
            # عمود الاسم بالفئة المخصصة العربية
            name_item = ArabicTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, name_item)
            
            # عمود الشعبة بالفئة المخصصة العربية
            section_item = ArabicTableWidgetItem(section)
            section_item.setFlags(section_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, section_item)
            
            # عمود الرسوم بالفئة المخصصة الرقمية
            fee_text = f"{fee:,.0f} د.ع"
            fee_item = NumericTableWidgetItem(fee_text, fee)
            fee_item.setFlags(fee_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, fee_item)
            
            # عمود المدفوع بالفئة المخصصة الرقمية
            paid_text = f"{paid:,.0f} د.ع"
            paid_item = NumericTableWidgetItem(paid_text, paid)
            paid_item.setFlags(paid_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 4, paid_item)
        
        layout.addWidget(self.table)
        
        # أزرار الاختبار
        buttons_layout = QHBoxLayout()
        
        test_id_btn = QPushButton("ترتيب المعرف")
        test_id_btn.clicked.connect(lambda: self.test_sort_column(0, "المعرف"))
        buttons_layout.addWidget(test_id_btn)
        
        test_name_btn = QPushButton("ترتيب الاسم")
        test_name_btn.clicked.connect(lambda: self.test_sort_column(1, "الاسم"))
        buttons_layout.addWidget(test_name_btn)
        
        test_section_btn = QPushButton("ترتيب الشعبة")
        test_section_btn.clicked.connect(lambda: self.test_sort_column(2, "الشعبة"))
        buttons_layout.addWidget(test_section_btn)
        
        test_fee_btn = QPushButton("ترتيب الرسوم")
        test_fee_btn.clicked.connect(lambda: self.test_sort_column(3, "الرسوم"))
        buttons_layout.addWidget(test_fee_btn)
        
        layout.addLayout(buttons_layout)
        
        # تسمية النتائج
        self.result_label = QLabel("النتائج ستظهر هنا")
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)
        self.setWindowTitle("اختبار ترتيب جميع الأعمدة")
        self.resize(800, 500)
    
    def test_sort_column(self, column, column_name):
        print(f"\n--- اختبار ترتيب عمود {column_name} ---")
        
        # ترتيب العمود تصاعدياً
        self.table.sortItems(column, Qt.AscendingOrder)
        
        # طباعة النتائج
        print("النتائج بعد الترتيب التصاعدي:")
        results = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, column)
            results.append(item.text())
            print(f"  {row + 1}: {item.text()}")
        
        # عرض النتائج في الواجهة
        self.result_label.setText(f"ترتيب {column_name}: " + " -> ".join(results[:5]) + ("..." if len(results) > 5 else ""))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
