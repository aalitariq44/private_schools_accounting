#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار التحسينات على صفحة تفاصيل الطالب
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# إضافة مسار المشروع للـ PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.pages.students.student_details_page import StudentDetailsPage


class TestWindow(QMainWindow):
    """نافذة اختبار صفحة تفاصيل الطالب"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار صفحة تفاصيل الطالب المحدثة")
        self.setGeometry(100, 100, 1400, 900)
        
        # تعيين اتجاه النص من اليمين إلى اليسار
        self.setLayoutDirection(Qt.RightToLeft)
        
        # إنشاء صفحة تفاصيل الطالب (معرف وهمي للاختبار)
        student_details = StudentDetailsPage(1)
        
        # تعيين كأداة مركزية
        self.setCentralWidget(student_details)
        
        # ربط إشارة الرجوع
        student_details.back_requested.connect(self.close)
        
        print("تم إنشاء صفحة تفاصيل الطالب بالتحسينات الجديدة:")
        print("✓ خط Cairo بحجم 18 بكسل")
        print("✓ تخطيط عمودي للجداول")
        print("✓ ملخص تفصيلي للرسوم الإضافية")
        print("✓ تصميم محسن ومتوافق مع باقي التطبيق")


def main():
    """الدالة الرئيسية"""
    app = QApplication(sys.argv)
    
    # تعيين اتجاه التطبيق من اليمين إلى اليسار
    app.setLayoutDirection(Qt.RightToLeft)
    
    # إنشاء النافذة الرئيسية
    window = TestWindow()
    window.show()
    
    # بدء التطبيق
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
