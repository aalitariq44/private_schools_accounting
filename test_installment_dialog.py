#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إضافة قسط للطالب
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.pages.students.add_installment_dialog import AddInstallmentDialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # إنشاء نافذة إضافة قسط تجريبية
    # استخدام student_id=1 و max_amount=1000 كقيم تجريبية
    dialog = AddInstallmentDialog(1, 1000)
    dialog.show()
    
    sys.exit(app.exec_())