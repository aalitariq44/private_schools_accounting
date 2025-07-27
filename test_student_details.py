#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط لصفحة تفاصيل الطالب
"""

import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # اختبار الاستيراد
    from ui.pages.students.student_details_page import StudentDetailsPage
    from ui.pages.students.add_installment_dialog import AddInstallmentDialog
    from ui.pages.students.add_additional_fee_dialog import AddAdditionalFeeDialog
    
    print("✓ تم استيراد جميع الملفات بنجاح")
    
    # اختبار إنشاء الكائنات بدون واجهة مستخدم
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    
    app = QApplication(sys.argv)
    
    # إنشاء الصفحات مع منع رسائل الخطأ
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)
    
    # اختبار إنشاء صفحة التفاصيل مع طالب غير موجود
    details_page = StudentDetailsPage(99999)  # طالب غير موجود
    print("✓ تم إنشاء صفحة التفاصيل بنجاح")
    
    # اختبار إنشاء نافذة إضافة القسط
    installment_dialog = AddInstallmentDialog(1, 100000)
    print("✓ تم إنشاء نافذة إضافة القسط بنجاح")
    
    # اختبار إنشاء نافذة إضافة الرسم الإضافي
    fee_dialog = AddAdditionalFeeDialog(1)
    print("✓ تم إنشاء نافذة إضافة الرسم الإضافي بنجاح")
    
    print("\n✅ جميع الاختبارات نجحت!")
    print("\n📝 ملاحظة: إذا ظهرت رسائل خطأ أعلاه، فهي طبيعية لأننا نختبر بطالب غير موجود.")
    print("🚀 يمكنك الآن تشغيل التطبيق واختبار ميزة تفاصيل الطالب!")
    
except ImportError as e:
    print(f"❌ خطأ في الاستيراد: {e}")
except Exception as e:
    print(f"❌ خطأ عام: {e}")
    import traceback
    traceback.print_exc()
