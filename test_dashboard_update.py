#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لتشغيل لوحة التحكم المحدثة
"""

import sys
import os

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

def test_dashboard():
    """اختبار لوحة التحكم"""
    try:
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        # تشغيل النافذة الرئيسية
        from app.main_window import MainWindow
        
        window = MainWindow()
        window.show()
        
        print("تم تشغيل التطبيق بنجاح مع التعديلات الجديدة!")
        print("الترتيب الجديد للإحصائيات:")
        print("الصف الأول: المدارس - الطلاب - المعلمين")
        print("الصف الثاني: مجموع الرسوم الدراسية - مجموع الأقساط المدفوعة - المتبقي")
        print("الصف الثالث: مجموع الرسوم الإضافية - الرسوم الإضافية المدفوعة - الرسوم الإضافية غير المدفوعة")
        
        return app.exec_()
        
    except Exception as e:
        print(f"خطأ في تشغيل التطبيق: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_dashboard())
