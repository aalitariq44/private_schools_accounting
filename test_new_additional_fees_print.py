# -*- coding: utf-8 -*-
"""
اختبار نظام طباعة الرسوم الإضافية المحدث
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

def test_print_behavior():
    """اختبار سلوك الطباعة الجديد"""
    try:
        from core.printing.additional_fees_print_manager import print_additional_fees_receipt
        from core.printing.simple_print_direct import print_pdf_direct
        
        # إنشاء ملف اختبار
        test_data = {
            'student': {
                'id': 1,
                'name': 'طالب تجريبي',
                'grade': 'الأول',
                'section': 'أ',
                'school_name': 'مدرسة الاختبار'
            },
            'fees': [
                {
                    'id': 1,
                    'fee_type': 'رسوم النشاطات',
                    'amount': 50000,
                    'paid': True,
                    'payment_date': '2025-08-15',
                    'created_at': '2025-08-01',
                    'notes': 'رسوم الأنشطة الرياضية'
                }
            ],
            'summary': {
                'fees_count': 1,
                'total_amount': 50000,
                'paid_amount': 50000,
                'unpaid_amount': 0
            }
        }
        
        print("🧪 اختبار إنشاء PDF...")
        pdf_path = print_additional_fees_receipt(test_data, preview_only=True)
        
        if pdf_path and os.path.exists(pdf_path):
            print(f"✅ تم إنشاء PDF: {pdf_path}")
            
            # اختبار الفتح الخارجي (المعاينة)
            print("\n🔍 اختبار المعاينة (فتح خارجي)...")
            try:
                if os.name == 'nt':
                    os.startfile(pdf_path)
                print("✅ تم فتح المعاينة خارجياً")
            except Exception as e:
                print(f"❌ فشل في فتح المعاينة: {e}")
            
            return pdf_path
        else:
            print("❌ فشل في إنشاء PDF")
            return None
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return None

class TestPrintWindow(QMainWindow):
    """نافذة اختبار الطباعة"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار طباعة الرسوم الإضافية المحدث")
        self.setGeometry(300, 300, 400, 200)
        
        # إعداد واجهة المستخدم
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # زر اختبار المعاينة
        preview_btn = QPushButton("اختبار المعاينة (فتح خارجي)")
        preview_btn.clicked.connect(self.test_preview)
        layout.addWidget(preview_btn)
        
        # زر اختبار الطباعة
        print_btn = QPushButton("اختبار الطباعة (نافذة النظام)")
        print_btn.clicked.connect(self.test_print)
        layout.addWidget(print_btn)
        
        # إنشاء ملف اختبار
        self.pdf_path = test_print_behavior()
        
    def test_preview(self):
        """اختبار المعاينة"""
        try:
            if self.pdf_path:
                if os.name == 'nt':
                    os.startfile(self.pdf_path)
                QMessageBox.information(self, "معاينة", "تم فتح المعاينة في البرنامج الافتراضي")
            else:
                QMessageBox.warning(self, "خطأ", "لا يوجد ملف للمعاينة")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في المعاينة: {str(e)}")
    
    def test_print(self):
        """اختبار الطباعة"""
        try:
            if self.pdf_path:
                from core.printing.simple_print_direct import print_pdf_direct
                success = print_pdf_direct(self.pdf_path, self)
                if not success:
                    QMessageBox.information(self, "معلومات", "تم إلغاء الطباعة أو حدث خطأ")
            else:
                QMessageBox.warning(self, "خطأ", "لا يوجد ملف للطباعة")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في الطباعة: {str(e)}")

def main():
    """دالة الاختبار الرئيسية"""
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, True)
    
    window = TestPrintWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    print("🧪 اختبار نظام طباعة الرسوم الإضافية المحدث")
    print("=" * 50)
    print("سيتم:")
    print("1. إنشاء ملف PDF تجريبي")
    print("2. فتح نافذة اختبار مع خيارات:")
    print("   - المعاينة: فتح خارجي")  
    print("   - الطباعة: نافذة النظام")
    print("=" * 50)
    
    main()
