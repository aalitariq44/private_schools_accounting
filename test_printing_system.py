#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام الطباعة
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from core.printing import print_manager, TemplateType

class PrintTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار نظام الطباعة")
        self.setGeometry(100, 100, 800, 600)
        
        # الويدجت المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # بيانات تجريبية
        self.sample_student = {
            'id': 1,
            'name': 'أحمد محمد علي',
            'school_name': 'مدرسة النور الأهلية',
            'grade': 'الرابع الابتدائي',
            'section': 'أ',
            'gender': 'ذكر',
            'phone': '07901234567',
            'status': 'نشط',
            'total_fee': 500000,
            'start_date': '2024-09-01'
        }
        
        self.sample_students = [
            self.sample_student,
            {
                'id': 2,
                'name': 'فاطمة أحمد حسن',
                'school_name': 'مدرسة النور الأهلية',
                'grade': 'الخامس الابتدائي',
                'section': 'ب',
                'gender': 'أنثى',
                'phone': '07901234568',
                'status': 'نشط',
                'total_fee': 550000,
                'start_date': '2024-09-01'
            },
            {
                'id': 3,
                'name': 'محمد صالح حمود',
                'school_name': 'مدرسة النور الأهلية',
                'grade': 'السادس الابتدائي',
                'section': 'أ',
                'gender': 'ذكر',
                'phone': '07901234569',
                'status': 'نشط',
                'total_fee': 600000,
                'start_date': '2024-09-01'
            }
        ]
        
        # أزرار الاختبار
        btn_student_report = QPushButton("اختبار تقرير طالب")
        btn_student_report.clicked.connect(self.test_student_report)
        layout.addWidget(btn_student_report)
        
        btn_students_list = QPushButton("اختبار قائمة الطلاب")
        btn_students_list.clicked.connect(self.test_students_list)
        layout.addWidget(btn_students_list)
        
        btn_receipt = QPushButton("اختبار إيصال دفع")
        btn_receipt.clicked.connect(self.test_payment_receipt)
        layout.addWidget(btn_receipt)
        
        btn_financial = QPushButton("اختبار التقرير المالي")
        btn_financial.clicked.connect(self.test_financial_report)
        layout.addWidget(btn_financial)
    
    def test_student_report(self):
        """اختبار تقرير الطالب"""
        print_manager.print_student_report(self.sample_student, self)
    
    def test_students_list(self):
        """اختبار قائمة الطلاب"""
        print_manager.print_students_list(
            self.sample_students, 
            "المدرسة: مدرسة النور الأهلية | الصف: جميع الصفوف", 
            self
        )
    
    def test_payment_receipt(self):
        """اختبار إيصال الدفع"""
        receipt_data = {
            'id': 'REC-001',
            'student_name': 'أحمد محمد علي',
            'school_name': 'مدرسة النور الأهلية',
            'payment_date': '2024-01-15',
            'payment_method': 'نقداً',
            'description': 'رسوم دراسية - شهر كانون الثاني',
            'amount': 100000
        }
        print_manager.print_payment_receipt(receipt_data, self)
    
    def test_financial_report(self):
        """اختبار التقرير المالي"""
        financial_data = {
            'total_income': 5000000,
            'total_expenses': 3000000
        }
        print_manager.print_financial_report(
            financial_data, 
            "كانون الثاني 2024", 
            self
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # تطبيق الخط العربي
    app.setLayoutDirection(2)  # Right to Left
    
    window = PrintTestWindow()
    window.show()
    
    sys.exit(app.exec_())
