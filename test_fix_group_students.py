#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لإضافة مجموعة الطلاب
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.pages.students.add_group_students_dialog import AddGroupStudentsDialog

def test_add_group_students():
    """اختبار نافذة إضافة مجموعة الطلاب"""
    app = QApplication(sys.argv)
    
    dialog = AddGroupStudentsDialog()
    dialog.show()
    
    app.exec_()

if __name__ == "__main__":
    test_add_group_students()
