#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('.')

from PyQt5.QtWidgets import QApplication
from ui.pages.shared.salary_details_dialog import SalaryDetailsDialog

def test_salary_dialog():
    """اختبار نافذة تفاصيل الرواتب"""
    app = QApplication(sys.argv)
    
    # اختبار مع معلم (ID=1, Name=زهراء محمد علي)
    dialog = SalaryDetailsDialog(
        person_type="teacher",
        person_id=1,
        person_name="زهراء محمد علي"
    )
    
    dialog.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_salary_dialog()
