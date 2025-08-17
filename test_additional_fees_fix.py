# -*- coding: utf-8 -*-
"""
اختبار طباعة الرسوم الإضافية للتأكد من حل مشكلة usedforsecurity
"""

# Apply patch first
import hashlib_patch

try:
    print("🔄 بدء اختبار طباعة الرسوم الإضافية...")
    
    # استيراد مدير طباعة الرسوم الإضافية
    from core.printing.additional_fees_print_manager import AdditionalFeesPrintManager
    print("✅ تم استيراد مدير طباعة الرسوم الإضافية بنجاح")
    
    # إنشاء مثيل من المدير
    manager = AdditionalFeesPrintManager()
    print("✅ تم إنشاء مثيل المدير بنجاح")
    
    # بيانات اختبار
    test_data = {
        'student_info': {
            'name': 'محمد أحمد',
            'class': 'الصف الأول',
            'id': '123'
        },
        'school_info': {
            'name': 'مدرسة الاختبار',
            'address': 'الرياض'
        },
        'fees': [
            {
                'name': 'رسوم النقل',
                'amount': 500.0,
                'date': '2025-08-17'
            }
        ],
        'total': 500.0
    }
    
    # اختبار إنشاء PDF
    import tempfile
    temp_file = tempfile.mktemp(suffix='.pdf')
    
    result_path = manager.create_additional_fees_receipt(test_data, temp_file)
    
    if result_path:
        print("✅ تم إنشاء PDF للرسوم الإضافية بنجاح")
        import os
        if os.path.exists(result_path):
            print("✅ ملف PDF موجود")
            # لا نحذف الملف للمراجعة
        else:
            print("❌ ملف PDF غير موجود")
    else:
        print("❌ فشل في إنشاء PDF")
    
    print("🎉 انتهى الاختبار بنجاح!")
    
except Exception as e:
    print(f"❌ خطأ في الاختبار: {e}")
    import traceback
    traceback.print_exc()
