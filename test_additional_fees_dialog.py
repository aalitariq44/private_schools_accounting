# -*- coding: utf-8 -*-
"""
اختبار نافذة طباعة الرسوم الإضافية
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

def test_additional_fees_dialog():
    """اختبار نافذة طباعة الرسوم الإضافية"""
    try:
        from ui.pages.students.additional_fees_print_dialog import AdditionalFeesPrintDialog
        
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, True)
        
        # فتح النافذة مع معرف طالب تجريبي
        dialog = AdditionalFeesPrintDialog(1)
        
        def handle_print_request(print_data):
            """معالجة طلب الطباعة للاختبار"""
            print("✅ تم استلام طلب الطباعة:")
            print(f"   - الطالب: {print_data.get('student', {}).get('name', 'غير محدد')}")
            print(f"   - عدد الرسوم: {len(print_data.get('fees', []))}")
            print(f"   - المجموع: {print_data.get('summary', {}).get('total_amount', 0)}")
            print(f"   - معاينة فقط: {print_data.get('preview_only', True)}")
            
            QMessageBox.information(None, "نجح", "تم استلام طلب الطباعة بنجاح!")
        
        dialog.print_requested.connect(handle_print_request)
        
        print("🪟 فتح نافذة طباعة الرسوم الإضافية...")
        dialog.show()
        
        return app.exec_()
        
    except Exception as e:
        print(f"❌ خطأ في اختبار النافذة: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("🧪 اختبار نافذة طباعة الرسوم الإضافية")
    print("=" * 50)
    
    result = test_additional_fees_dialog()
    
    if result == 0:
        print("\n✅ الاختبار اكتمل!")
    else:
        print("\n❌ حدث خطأ في الاختبار!")
