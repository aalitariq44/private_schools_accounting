#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار التحديثات الجديدة على صفحة الرواتب
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.pages.salaries.add_salary_dialog import AddSalaryDialog

def test_add_salary_dialog():
    """اختبار نافذة إضافة راتب جديد مع الميزات الجديدة"""
    app = QApplication(sys.argv)
    
    dialog = AddSalaryDialog()
    dialog.show()
    
    app.exec_()

if __name__ == "__main__":
    test_add_salary_dialog()
