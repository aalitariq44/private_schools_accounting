#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار محرر القالب مع معاينة PDF لحظية
"""

import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('template_editor_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

from ui.dialogs.template_editor import TemplateEditor

class TestMainWindow(QMainWindow):
    """نافذة اختبار محرر القالب"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار محرر القالب مع معاينة PDF لحظية")
        self.setGeometry(100, 100, 400, 200)
        
        # واجهة بسيطة
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # زر فتح المحرر
        open_editor_btn = QPushButton("🎨 فتح محرر القالب مع معاينة PDF")
        open_editor_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        open_editor_btn.clicked.connect(self.open_template_editor)
        layout.addWidget(open_editor_btn)
        
        # تعليمات
        instructions = """
📋 تعليمات الاستخدام:

1. اضغط على الزر أعلاه لفتح محرر القالب
2. ستظهر نافذة جديدة مع:
   • محرر العناصر على اليسار
   • معاينة PDF لحظية على اليمين
3. عند تعديل أي إعداد، ستتحدث المعاينة تلقائياً
4. يمكن إيقاف/تشغيل التحديث التلقائي
5. استخدم "تحديث يدوي" لفرض تحديث المعاينة

🔧 الميزات الجديدة:
• معاينة PDF حقيقية (ليس HTML)
• تحديث لحظي عند التعديل
• تحكم في التحديث التلقائي
• إشارات حالة واضحة
• أداء محسّن مع المعالجة المتوازية
        """
        
        from PyQt5.QtWidgets import QTextEdit
        instructions_text = QTextEdit()
        instructions_text.setPlainText(instructions)
        instructions_text.setReadOnly(True)
        instructions_text.setMaximumHeight(250)
        layout.addWidget(instructions_text)
    
    def open_template_editor(self):
        """فتح محرر القالب"""
        try:
            logging.info("فتح محرر القالب مع معاينة PDF...")
            
            # إنشاء المحرر
            editor = TemplateEditor(self)
            
            # فتح النافذة
            result = editor.exec_()
            
            if result == editor.Accepted:
                logging.info("تم حفظ تغييرات القالب")
            else:
                logging.info("تم إلغاء تحرير القالب")
                
        except Exception as e:
            logging.error(f"خطأ في فتح محرر القالب: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, "خطأ", 
                f"فشل في فتح محرر القالب:\n{str(e)}"
            )

def main():
    """الدالة الرئيسية"""
    try:
        # إنشاء التطبيق
        app = QApplication(sys.argv)
        app.setLayoutDirection(Qt.RightToLeft)  # دعم العربية
        
        # إنشاء النافذة الرئيسية
        window = TestMainWindow()
        window.show()
        
        logging.info("تم تشغيل اختبار محرر القالب بنجاح")
        
        # تشغيل التطبيق
        sys.exit(app.exec_())
        
    except Exception as e:
        logging.error(f"خطأ في تشغيل التطبيق: {e}")
        print(f"خطأ: {e}")

if __name__ == "__main__":
    main()
