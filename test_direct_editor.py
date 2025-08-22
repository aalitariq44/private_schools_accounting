#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مباشر لمحرر القالب مع معاينة PDF
"""

import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# إعداد المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_template_editor():
    """اختبار محرر القالب مع معاينة PDF"""
    
    try:
        # إعداد خصائص Qt قبل إنشاء التطبيق
        from PyQt5.QtCore import QCoreApplication, Qt
        from PyQt5.QtWebEngineWidgets import QWebEngineView  # استيراد مبكر
        
        # تفعيل مشاركة سياق OpenGL
        QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
        
        # إنشاء التطبيق
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        app.setLayoutDirection(Qt.RightToLeft)
        
        # استيراد وإنشاء المحرر
        from ui.dialogs.template_editor import TemplateEditor
        
        logging.info("إنشاء محرر القالب...")
        editor = TemplateEditor()
        
        logging.info("عرض المحرر...")
        editor.show()
        
        # تشغيل التطبيق
        return app.exec_()
        
    except Exception as e:
        logging.error(f"خطأ في اختبار المحرر: {e}")
        print(f"خطأ: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_template_editor())
