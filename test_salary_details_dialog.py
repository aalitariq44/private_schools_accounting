#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نافذة تفاصيل الرواتب
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

# إضافة مسار المشروع
sys.path.append('c:\\Users\\pc\\Desktop\\private_schools_accounting')

from ui.pages.shared.salary_details_dialog import SalaryDetailsDialog

class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار نافذة تفاصيل الرواتب")
        self.setGeometry(100, 100, 400, 200)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # أزرار الاختبار
        teacher_button = QPushButton("اختبار معلم")
        teacher_button.clicked.connect(self.test_teacher)
        layout.addWidget(teacher_button)
        
        employee_button = QPushButton("اختبار موظف")
        employee_button.clicked.connect(self.test_employee)
        layout.addWidget(employee_button)
    
    def test_teacher(self):
        """اختبار نافذة معلم"""
        dialog = SalaryDetailsDialog("teacher", 1, "محمد أحمد", self)
        dialog.exec_()
    
    def test_employee(self):
        """اختبار نافذة موظف"""
        dialog = SalaryDetailsDialog("employee", 1, "علي حسن", self)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    sys.exit(app.exec_())
