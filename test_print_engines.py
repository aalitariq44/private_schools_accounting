# -*- coding: utf-8 -*-
"""
اختبار نظام الطباعة الجديد
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox

# إضافة مسار المشروع للـ PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.printing import (
    WEB_ENGINE_AVAILABLE, 
    web_print_payment_receipt, 
    print_payment_receipt
)


class PrintTestWindow(QWidget):
    """نافذة اختبار نظام الطباعة"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("اختبار نظام الطباعة الجديد")
        self.setGeometry(300, 300, 400, 300)
        
        layout = QVBoxLayout()
        
        # معلومات المحرك
        status_label = QLabel()
        if WEB_ENGINE_AVAILABLE:
            status_label.setText("✅ محرك الويب الحديث: متوفر")
            status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            status_label.setText("❌ محرك الويب الحديث: غير متوفر")
            status_label.setStyleSheet("color: red; font-weight: bold;")
        
        layout.addWidget(status_label)
        
        # أزرار الاختبار
        if WEB_ENGINE_AVAILABLE:
            btn_web = QPushButton("اختبار المحرك الحديث")
            btn_web.clicked.connect(self.test_web_engine)
            layout.addWidget(btn_web)
        
        btn_legacy = QPushButton("اختبار المحرك التقليدي")
        btn_legacy.clicked.connect(self.test_legacy_engine)
        layout.addWidget(btn_legacy)
        
        # زر المقارنة
        if WEB_ENGINE_AVAILABLE:
            btn_compare = QPushButton("مقارنة المحركين")
            btn_compare.clicked.connect(self.compare_engines)
            layout.addWidget(btn_compare)
        
        self.setLayout(layout)
    
    def get_sample_data(self):
        """إنشاء بيانات تجريبية للاختبار"""
        return {
            'id': 1,
            'student_name': 'علي أحمد محمد',
            'grade': 'الرابع العلمي',
            'section': 'أ',
            'amount': 100000,
            'payment_date': datetime.now(),
            'total_paid': 100000,
            'total_fee': 400000,
            'remaining': 300000
        }
    
    def test_web_engine(self):
        """اختبار المحرك الحديث"""
        try:
            data = self.get_sample_data()
            web_print_payment_receipt(data, parent=self)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في اختبار المحرك الحديث:\n{e}")
    
    def test_legacy_engine(self):
        """اختبار المحرك التقليدي"""
        try:
            data = self.get_sample_data()
            print_payment_receipt(data, parent=self, use_web_engine=False)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في اختبار المحرك التقليدي:\n{e}")
    
    def compare_engines(self):
        """مقارنة المحركين"""
        QMessageBox.information(
            self, 
            "مقارنة المحركين",
            "سيتم فتح نافذتي معاينة:\n"
            "1. المحرك الحديث (جودة عالية)\n"
            "2. المحرك التقليدي (للمقارنة)\n\n"
            "لاحظ الفرق في جودة العرض والتنسيق"
        )
        
        data = self.get_sample_data()
        
        # المحرك الحديث
        try:
            web_print_payment_receipt(data, parent=self)
        except Exception as e:
            QMessageBox.warning(self, "تحذير", f"فشل المحرك الحديث: {e}")
        
        # المحرك التقليدي
        try:
            print_payment_receipt(data, parent=self, use_web_engine=False)
        except Exception as e:
            QMessageBox.warning(self, "تحذير", f"فشل المحرك التقليدي: {e}")


def main():
    """الدالة الرئيسية"""
    app = QApplication(sys.argv)
    app.setLayoutDirection(2)  # RTL
    
    window = PrintTestWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
