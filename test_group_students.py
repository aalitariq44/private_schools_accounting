#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نافذة إضافة مجموعة الطلاب
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# إعداد المسار لاستيراد الوحدات
sys.path.insert(0, '.')

from ui.pages.students.add_group_students_dialog import AddGroupStudentsDialog

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار نافذة إضافة مجموعة الطلاب")
        self.setGeometry(100, 100, 500, 300)
        
        # إعداد الواجهة
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # عنوان
        title = QLabel("اختبار ميزة إضافة مجموعة الطلاب")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 20px;")
        layout.addWidget(title)
        
        # زر لفتح النافذة
        test_btn = QPushButton("فتح نافذة إضافة مجموعة الطلاب")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2ECC71;
            }
        """)
        test_btn.clicked.connect(self.open_dialog)
        layout.addWidget(test_btn)
        
        # معلومات الاختبار
        info = QLabel("""
الميزات المتاحة في الاختبار:
• إدخال المعلومات المشتركة (مدرسة، صف، شعبة، إلخ)
• إضافة عدة طلاب بأسمائهم وأرقام هواتفهم
• حذف الطلاب من القائمة
• عداد الطلاب التلقائي
• التحقق من صحة البيانات قبل الحفظ
        """)
        info.setStyleSheet("color: #7f8c8d; font-size: 14px; margin: 20px;")
        layout.addWidget(info)
        
    def open_dialog(self):
        """فتح نافذة إضافة مجموعة الطلاب"""
        try:
            dialog = AddGroupStudentsDialog(self)
            result = dialog.exec_()
            
            if result == dialog.Accepted:
                print("تم حفظ المجموعة بنجاح!")
            else:
                print("تم إلغاء العملية")
                
        except Exception as e:
            print(f"خطأ في فتح النافذة: {e}")
            logging.error(f"خطأ في فتح النافذة: {e}")

def main():
    # إعداد التسجيل
    logging.basicConfig(level=logging.DEBUG)
    
    app = QApplication(sys.argv)
    
    # تعيين الخط لدعم العربية
    app.setLayoutDirection(Qt.RightToLeft)
    
    # تعيين خط مناسب للعربية
    font = QFont("Arial", 12)
    app.setFont(font)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
