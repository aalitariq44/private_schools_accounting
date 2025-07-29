#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار النافذة المحسنة لطباعة الرسوم الإضافية
"""

import sys
from pathlib import Path

# إضافة المجلد الجذر للمشروع
sys.path.insert(0, str(Path(__file__).parent))

def test_fixed_dialog():
    """اختبار النافذة المحسنة"""
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.pages.students.additional_fees_print_dialog_fixed import AdditionalFeesPrintDialogFixed
        
        print("🔍 اختبار النافذة المحسنة...")
        
        # إنشاء تطبيق Qt
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # استخدام معرف طالب تجريبي (يمكن تغييره)
        student_id = 1  # يجب أن يكون هناك طالب بهذا المعرف في قاعدة البيانات
        
        # إنشاء وعرض النافذة المحسنة
        dialog = AdditionalFeesPrintDialogFixed(student_id)
        print("✅ تم إنشاء النافذة المحسنة بنجاح")
        
        # عرض النافذة
        dialog.show()
        
        print("📱 النافذة المحسنة معروضة الآن.")
        print("💡 راجع منطقة التشخيص في أعلى النافذة لمعرفة سبب المشكلة.")
        print("🔍 استخدم زر 'إعادة تحميل' لإعادة تحميل البيانات.")
        
        # تشغيل حلقة الأحداث
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار النافذة المحسنة: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 اختبار النافذة المحسنة لطباعة الرسوم الإضافية")
    print("=" * 60)
    
    success = test_fixed_dialog()
    
    if success:
        print("\n✅ تم تشغيل النافذة المحسنة بنجاح!")
    else:
        print("\n❌ فشل في تشغيل النافذة المحسنة!")
    
    print("=" * 60)
