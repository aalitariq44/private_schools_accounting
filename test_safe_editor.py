#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار محرر القالب مع معاينة PDF آمنة (تدعم البدائل)
"""

import sys
import logging
from pathlib import Path
from PyQt5.QtCore import QCoreApplication, Qt

# إعداد Qt قبل أي شيء آخر
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)

# محاولة استيراد QWebEngine مبكراً
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
    print("✅ QWebEngine متوفر - سيتم استخدام معاينة PDF متقدمة")
except ImportError:
    WEB_ENGINE_AVAILABLE = False
    print("⚠️ QWebEngine غير متوفر - سيتم استخدام معاينة بديلة")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# إعداد المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_template_editor_safe():
    """اختبار آمن لمحرر القالب"""
    
    try:
        # إنشاء التطبيق
        app = QApplication(sys.argv)
        app.setLayoutDirection(Qt.RightToLeft)
        
        if WEB_ENGINE_AVAILABLE:
            # استخدام المحرر الكامل
            from ui.dialogs.template_editor import TemplateEditor
            
            logging.info("إنشاء محرر القالب مع معاينة PDF...")
            editor = TemplateEditor()
        else:
            # محرر مبسط بدون معاينة PDF
            from ui.dialogs.template_editor_simple import SimpleTemplateEditor
            
            logging.info("إنشاء محرر القالب المبسط...")
            editor = SimpleTemplateEditor()
        
        logging.info("عرض المحرر...")
        editor.show()
        
        # تشغيل التطبيق
        return app.exec_()
        
    except Exception as e:
        logging.error(f"خطأ في اختبار المحرر: {e}")
        print(f"خطأ: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_template_editor_safe())
