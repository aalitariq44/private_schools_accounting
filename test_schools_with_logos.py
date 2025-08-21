#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار صفحة المدارس مع الشعارات
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع لاستيراد الوحدات
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# استيراد صفحة المدارس
from ui.pages.schools.schools_page import SchoolsPage

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار صفحة المدارس مع الشعارات")
        self.setGeometry(100, 100, 1200, 800)
        
        # إعداد الويدجت المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # إعداد التخطيط
        layout = QVBoxLayout(central_widget)
        
        # إضافة صفحة المدارس
        self.schools_page = SchoolsPage()
        layout.addWidget(self.schools_page)
        
        # تحميل البيانات
        self.schools_page.load_schools()

def main():
    # إنشاء تطبيق PyQt5
    app = QApplication(sys.argv)
    
    # تعيين اتجاه النص للعربية
    app.setLayoutDirection(Qt.RightToLeft)
    
    # تحديد خط عربي للتطبيق
    font = QFont("Arial", 10)
    app.setFont(font)
    
    # إنشاء النافذة الرئيسية
    window = TestWindow()
    window.show()
    
    # تشغيل التطبيق
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
