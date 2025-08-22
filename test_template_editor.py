#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار محرر قالب الهوية المحسّن
"""

import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# استيراد المحرر المحسّن
from ui.dialogs.template_editor import TemplateEditor

def main():
    """الدالة الرئيسية"""
    try:
        app = QApplication(sys.argv)
        
        # تطبيق نمط عربي
        app.setLayoutDirection(Qt.RightToLeft)
        
        # إنشاء وعرض المحرر
        editor = TemplateEditor()
        editor.show()
        
        # تشغيل التطبيق
        sys.exit(app.exec_())
        
    except Exception as e:
        logging.error(f"خطأ في تشغيل المحرر: {e}")
        print(f"خطأ: {e}")

if __name__ == "__main__":
    main()
