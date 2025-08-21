#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لميزة حذف المعلمين/الموظفين مع رواتبهم
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt

# إضافة المسار للنظام
sys.path.append('.')

from core.database.connection import db_manager
from ui.pages.teachers.teachers_page import TeachersPage
from ui.pages.employees.employees_page import EmployeesPage

class TestMainWindow(QMainWindow):
    """نافذة اختبار الميزة"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار ميزة حذف المعلمين/الموظفين مع رواتبهم")
        self.setGeometry(100, 100, 1200, 800)
        
        # الودجت المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # التخطيط
        layout = QVBoxLayout(central_widget)
        
        # تسمية
        title_label = QLabel("اختبار ميزة حذف المعلمين/الموظفين مع رواتبهم")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # أزرار الاختبار
        test_teachers_btn = QPushButton("اختبار صفحة المعلمين")
        test_teachers_btn.clicked.connect(self.test_teachers_page)
        layout.addWidget(test_teachers_btn)
        
        test_employees_btn = QPushButton("اختبار صفحة الموظفين")
        test_employees_btn.clicked.connect(self.test_employees_page)
        layout.addWidget(test_employees_btn)
        
        # صفحات الاختبار
        self.teachers_page = None
        self.employees_page = None
        
        # إعداد الستايل
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
            QPushButton {
                background-color: #2980B9;
                color: white;
                border: none;
                padding: 10px 20px;
                margin: 5px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
        """)
    
    def test_teachers_page(self):
        """اختبار صفحة المعلمين"""
        try:
            if self.teachers_page is None:
                self.teachers_page = TeachersPage()
            
            self.teachers_page.show()
            self.teachers_page.raise_()
            self.teachers_page.activateWindow()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح صفحة المعلمين:\n{e}")
            logging.error(f"خطأ في اختبار صفحة المعلمين: {e}")
    
    def test_employees_page(self):
        """اختبار صفحة الموظفين"""
        try:
            if self.employees_page is None:
                self.employees_page = EmployeesPage()
            
            self.employees_page.show()
            self.employees_page.raise_()
            self.employees_page.activateWindow()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح صفحة الموظفين:\n{e}")
            logging.error(f"خطأ في اختبار صفحة الموظفين: {e}")

def main():
    """تشغيل التطبيق"""
    app = QApplication(sys.argv)
    
    # إعداد الخط العربي
    app.setLayoutDirection(Qt.RightToLeft)
    
    # إنشاء النافذة الرئيسية
    window = TestMainWindow()
    window.show()
    
    # تشغيل التطبيق
    sys.exit(app.exec_())

if __name__ == "__main__":
    # إعداد اللوغ
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/test_deletion.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    print("🧪 بدء اختبار ميزة حذف المعلمين/الموظفين مع رواتبهم")
    print("=" * 60)
    print("تعليمات الاختبار:")
    print("1. انقر على زر 'اختبار صفحة المعلمين' لفتح صفحة المعلمين")
    print("2. انقر على زر 'اختبار صفحة الموظفين' لفتح صفحة الموظفين")
    print("3. في كل صفحة، انقر بالزر الأيمن على أي معلم/موظف")
    print("4. اختر 'حذف' من القائمة لاختبار الميزة")
    print("5. لاحظ رسالة التحذير التي تظهر مع عدد الرواتب")
    print("6. يمكنك اختيار 'No' لإلغاء الحذف والحفاظ على البيانات")
    print("=" * 60)
    
    main()
