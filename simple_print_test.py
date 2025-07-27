#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مبسط لنظام الطباعة
"""

import sys
import os

# إضافة المسار
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox

def test_print_system():
    """اختبار نظام الطباعة"""
    try:
        # استيراد نظام الطباعة
        from core.printing import print_manager, TemplateType, PrintHelper
        
        print("✅ تم استيراد نظام الطباعة بنجاح!")
        
        # بيانات تجريبية
        sample_student = {
            'id': 1,
            'name': 'أحمد محمد علي',
            'school_name': 'مدرسة النور الأهلية',
            'grade': 'الرابع الابتدائي',
            'section': 'أ',
            'gender': 'ذكر',
            'phone': '07901234567',
            'status': 'نشط',
            'total_fee': 500000,
            'start_date': '2024-09-01'
        }
        
        print("✅ تم إعداد البيانات التجريبية!")
        
        # اختبار تقديم القالب
        from core.printing import TemplateManager
        template_manager = TemplateManager()
        
        html_content = template_manager.render_template(
            TemplateType.STUDENT_REPORT,
            {'student': sample_student}
        )
        
        if html_content and len(html_content) > 100:
            print("✅ نظام القوالب يعمل بشكل صحيح!")
            print(f"📄 طول المحتوى: {len(html_content)} حرف")
        else:
            print("❌ مشكلة في نظام القوالب")
            return False
        
        print("🎉 جميع الاختبارات نجحت!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في النظام: {e}")
        import traceback
        traceback.print_exc()
        return False

class SimplePrintTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار نظام الطباعة المبسط")
        self.setGeometry(100, 100, 600, 400)
        
        # الويدجت المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # بيانات تجريبية
        self.sample_student = {
            'id': 1,
            'name': 'أحمد محمد علي',
            'school_name': 'مدرسة النور الأهلية',
            'grade': 'الرابع الابتدائي',
            'section': 'أ',
            'gender': 'ذكر',
            'phone': '07901234567',
            'status': 'نشط',
            'total_fee': 500000,
            'start_date': '2024-09-01'
        }
        
        # أزرار الاختبار
        btn_test_template = QPushButton("اختبار تقديم القالب")
        btn_test_template.clicked.connect(self.test_template)
        layout.addWidget(btn_test_template)
        
        btn_test_preview = QPushButton("اختبار نافذة المعاينة")
        btn_test_preview.clicked.connect(self.test_preview)
        layout.addWidget(btn_test_preview)
        
        btn_test_student_report = QPushButton("اختبار تقرير طالب")
        btn_test_student_report.clicked.connect(self.test_student_report)
        layout.addWidget(btn_test_student_report)
    
    def test_template(self):
        """اختبار تقديم القالب"""
        try:
            from core.printing import TemplateManager, TemplateType
            
            template_manager = TemplateManager()
            html_content = template_manager.render_template(
                TemplateType.STUDENT_REPORT,
                {'student': self.sample_student}
            )
            
            if html_content:
                QMessageBox.information(
                    self, "نجح!", 
                    f"تم تقديم القالب بنجاح!\\nطول المحتوى: {len(html_content)} حرف"
                )
            else:
                QMessageBox.warning(self, "فشل", "فشل في تقديم القالب")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في اختبار القالب:\\n{str(e)}")
    
    def test_preview(self):
        """اختبار نافذة المعاينة"""
        try:
            from core.printing import TemplateManager, TemplateType, PrintPreviewDialog
            
            template_manager = TemplateManager()
            html_content = template_manager.render_template(
                TemplateType.STUDENT_REPORT,
                {'student': self.sample_student}
            )
            
            if html_content:
                preview_dialog = PrintPreviewDialog(html_content, "اختبار المعاينة", self)
                preview_dialog.apply_styles()
                preview_dialog.exec_()
            else:
                QMessageBox.warning(self, "فشل", "فشل في تقديم القالب للمعاينة")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في اختبار المعاينة:\\n{str(e)}")
    
    def test_student_report(self):
        """اختبار طباعة تقرير الطالب"""
        try:
            from core.printing import print_manager
            
            print_manager.print_student_report(self.sample_student, self)
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في اختبار طباعة التقرير:\\n{str(e)}")

def main():
    print("🖨️ اختبار نظام الطباعة المبسط")
    print("=" * 40)
    
    # اختبار وحدة الاستيراد
    if test_print_system():
        print("\\n🚀 بدء تشغيل التطبيق...")
        
        app = QApplication(sys.argv)
        
        # تطبيق الخط العربي
        app.setLayoutDirection(2)  # Right to Left
        
        window = SimplePrintTestWindow()
        window.show()
        
        print("✅ التطبيق جاهز للاختبار!")
        
        sys.exit(app.exec_())
    else:
        print("❌ فشل في تهيئة النظام")

if __name__ == "__main__":
    main()
