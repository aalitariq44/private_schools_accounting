#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تعديل المدرسة في نافذة الإعدادات المتقدمة
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.pages.settings.advanced_settings_dialog import show_advanced_settings

def test_advanced_edit():
    """اختبار تعديل المدرسة في الإعدادات المتقدمة"""
    app = QApplication(sys.argv)
    
    # إعداد النافذة الرئيسية للاختبار
    try:
        result = show_advanced_settings()
        print(f"نتيجة النافذة: {result}")
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
    
    app.quit()

if __name__ == "__main__":
    test_advanced_edit()
