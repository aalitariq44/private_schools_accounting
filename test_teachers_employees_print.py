#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار وظائف الطباعة للمعلمين والموظفين
"""

import sys
import os

# إضافة مسار الجذر للمشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from core.printing.print_manager import print_teachers_list, print_employees_list
from core.printing.print_config import TemplateType


class TestPrintWindow(QMainWindow):
    """نافذة اختبار الطباعة"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("اختبار طباعة المعلمين والموظفين")
        self.setGeometry(100, 100, 400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # زر اختبار طباعة المعلمين
        teachers_btn = QPushButton("اختبار طباعة قائمة المعلمين")
        teachers_btn.clicked.connect(self.test_teachers_print)
        layout.addWidget(teachers_btn)
        
        # زر اختبار طباعة الموظفين
        employees_btn = QPushButton("اختبار طباعة قائمة الموظفين")
        employees_btn.clicked.connect(self.test_employees_print)
        layout.addWidget(employees_btn)
    
    def test_teachers_print(self):
        """اختبار طباعة المعلمين"""
        try:
            # بيانات تجريبية للمعلمين
            test_teachers = [
                {
                    'id': 1,
                    'name': 'أحمد محمد علي',
                    'school_name': 'مدرسة النور',
                    'class_hours': 20,
                    'monthly_salary': 500.0,
                    'phone': '0123456789',
                    'notes': 'معلم رياضيات'
                },
                {
                    'id': 2,
                    'name': 'فاطمة سالم',
                    'school_name': 'مدرسة الأمل',
                    'class_hours': 18,
                    'monthly_salary': 450.0,
                    'phone': '0987654321',
                    'notes': 'معلمة لغة عربية'
                },
                {
                    'id': 3,
                    'name': 'محمد سعد',
                    'school_name': 'مدرسة النور',
                    'class_hours': 22,
                    'monthly_salary': 550.0,
                    'phone': '0111222333',
                    'notes': 'معلم فيزياء'
                }
            ]
            
            filter_info = "اختبار: عرض جميع المعلمين"
            print_teachers_list(test_teachers, filter_info, parent=self)
            
        except Exception as e:
            print(f"خطأ في اختبار طباعة المعلمين: {e}")
    
    def test_employees_print(self):
        """اختبار طباعة الموظفين"""
        try:
            # بيانات تجريبية للموظفين
            test_employees = [
                {
                    'id': 1,
                    'name': 'علي حسن',
                    'school_name': 'مدرسة النور',
                    'job_type': 'محاسب',
                    'monthly_salary': 400.0,
                    'phone': '0123456789',
                    'notes': 'مسؤول الحسابات'
                },
                {
                    'id': 2,
                    'name': 'مريم أحمد',
                    'school_name': 'مدرسة الأمل',
                    'job_type': 'سكرتيرة',
                    'monthly_salary': 350.0,
                    'phone': '0987654321',
                    'notes': 'إدارية'
                },
                {
                    'id': 3,
                    'name': 'خالد سليم',
                    'school_name': 'مدرسة النور',
                    'job_type': 'عامل نظافة',
                    'monthly_salary': 250.0,
                    'phone': '0111222333',
                    'notes': 'صيانة ونظافة'
                }
            ]
            
            filter_info = "اختبار: عرض جميع الموظفين"
            print_employees_list(test_employees, filter_info, parent=self)
            
        except Exception as e:
            print(f"خطأ في اختبار طباعة الموظفين: {e}")


def main():
    """دالة التشغيل الرئيسية"""
    app = QApplication(sys.argv)
    
    window = TestPrintWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
