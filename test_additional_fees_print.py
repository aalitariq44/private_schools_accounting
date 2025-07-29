#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ميزة طباعة إيصال الرسوم الإضافية
"""

import sys
import os
import logging
from pathlib import Path

# إضافة المجلد الجذر للمشروع إلى مسار Python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# تكوين السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_additional_fees_print():
    """اختبار طباعة إيصال الرسوم الإضافية"""
    try:
        from core.printing.additional_fees_print_manager import print_additional_fees_receipt
        
        # بيانات تجريبية للاختبار
        test_data = {
            'student': {
                'id': 1,
                'name': 'أحمد محمد علي',
                'grade': 'الخامس الابتدائي',
                'section': 'أ',
                'school_name': 'مدرسة النور الأهلية'
            },
            'fees': [
                {
                    'id': 1,
                    'fee_type': 'رسوم كتب',
                    'amount': 50000,
                    'paid': True,
                    'payment_date': '2025-01-15',
                    'created_at': '2025-01-10',
                    'notes': 'رسوم كتب الفصل الثاني'
                },
                {
                    'id': 2,
                    'fee_type': 'رسوم نشاطات',
                    'amount': 25000,
                    'paid': False,
                    'payment_date': None,
                    'created_at': '2025-01-12',
                    'notes': 'رسوم النشاطات اللاصفية'
                },
                {
                    'id': 3,
                    'fee_type': 'رسوم امتحانات',
                    'amount': 30000,
                    'paid': True,
                    'payment_date': '2025-01-20',
                    'created_at': '2025-01-18',
                    'notes': 'رسوم امتحانات نصف السنة'
                }
            ],
            'summary': {
                'fees_count': 3,
                'total_amount': 105000,
                'paid_amount': 80000,
                'unpaid_amount': 25000
            },
            'print_date': '2025-01-29',
            'print_time': '14:30:00',
            'receipt_number': 'AF20250129143000'
        }
        
        print("🔍 اختبار إنشاء إيصال الرسوم الإضافية...")
        
        # اختبار المعاينة
        preview_path = print_additional_fees_receipt(test_data, preview_only=True)
        
        if preview_path and os.path.exists(preview_path):
            print(f"✅ تم إنشاء معاينة الإيصال بنجاح: {preview_path}")
        else:
            print("❌ فشل في إنشاء معاينة الإيصال")
            return False
        
        # اختبار الطباعة الفعلية
        print_path = print_additional_fees_receipt(test_data, preview_only=False)
        
        if print_path and os.path.exists(print_path):
            print(f"✅ تم إنشاء إيصال الطباعة بنجاح: {print_path}")
        else:
            print("❌ فشل في إنشاء إيصال الطباعة")
            return False
        
        print("🎉 اختبار طباعة الرسوم الإضافية مكتمل بنجاح!")
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        logging.error(f"خطأ في اختبار طباعة الرسوم الإضافية: {e}")
        return False

def test_print_dialog():
    """اختبار نافذة طباعة الرسوم الإضافية"""
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.pages.students.additional_fees_print_dialog import AdditionalFeesPrintDialog
        
        # إنشاء تطبيق Qt للاختبار
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        print("🔍 اختبار نافذة طباعة الرسوم الإضافية...")
        
        # إنشاء نافذة الطباعة (مع معرف طالب وهمي)
        dialog = AdditionalFeesPrintDialog(student_id=1)
        
        print("✅ تم إنشاء نافذة طباعة الرسوم الإضافية بنجاح")
        
        # إغلاق النافذة
        dialog.close()
        
        print("🎉 اختبار نافذة الطباعة مكتمل بنجاح!")
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار النافذة: {e}")
        logging.error(f"خطأ في اختبار نافذة الطباعة: {e}")
        return False

if __name__ == "__main__":
    print("🚀 بدء اختبار ميزة طباعة إيصال الرسوم الإضافية...")
    print("=" * 60)
    
    # اختبار وحدة الطباعة
    if test_additional_fees_print():
        print("\n" + "=" * 60)
        
        # اختبار النافذة (اختياري - يتطلب Qt)
        try:
            test_print_dialog()
        except Exception as e:
            print(f"⚠️ تعذر اختبار النافذة (Qt غير متوفر): {e}")
    else:
        print("❌ فشل في اختبار وحدة الطباعة")
        sys.exit(1)
    
    print("\n🎉 جميع الاختبارات مكتملة!")
