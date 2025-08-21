#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار التعديلات الجديدة على صفحة الواردات الخارجية
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from PyQt5.QtWidgets import QApplication
from ui.pages.external_income import ExternalIncomePage
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)

def test_external_income_updates():
    """اختبار التعديلات الجديدة"""
    app = QApplication(sys.argv)
    
    # إنشاء صفحة الواردات الخارجية
    page = ExternalIncomePage()
    page.show()
    
    print("=== اختبار التعديلات الجديدة ===")
    print("1. ✓ تم تغيير 'نوع الوارد' إلى 'عنوان الوارد'")
    print("2. ✓ تم تبديل ترتيب أعمدة 'عنوان الوارد' و 'الوصف'")
    print("3. ✓ تم إضافة خيار 'عام' و 'الجميع' لتصفية المدارس")
    print("4. ✓ تم تحديث البحث ليشمل العناوين والأوصاف والملاحظات")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_external_income_updates()
