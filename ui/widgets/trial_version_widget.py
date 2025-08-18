#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ويدجت النسخة التجريبية
"""

import logging
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
import webbrowser


class TrialVersionWidget(QWidget):
    """ويدجت النسخة التجريبية"""
    
    # إشارة عند الضغط على زر الاتصال
    contact_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # إطار الويدجت (مشابه لويدجت العام الدراسي)
            self.frame = QFrame()
            self.frame.setObjectName("trialFrame")
            self.frame.setFixedHeight(30)  # نفس ارتفاع ويدجت العام الدراسي
            self.frame.setCursor(Qt.PointingHandCursor)
            
            frame_layout = QHBoxLayout()
            frame_layout.setContentsMargins(10, 4, 10, 4)
            frame_layout.setSpacing(8)
            
            # النص الرئيسي
            main_label = QLabel("النسخة التجريبية - للحصول على النسخة الكاملة اضغط هنا")
            main_label.setObjectName("trialLabel")
            main_label.setAlignment(Qt.AlignCenter)
            frame_layout.addWidget(main_label)
            
            self.frame.setLayout(frame_layout)
            layout.addWidget(self.frame)
            
            self.setLayout(layout)
            
            # ربط الحدث للنقر على الويدجت
            self.frame.mousePressEvent = self.widget_clicked
            
        except Exception as e:
            logging.error(f"خطأ في إعداد ويدجت النسخة التجريبية: {e}")
            
    def widget_clicked(self, event):
        """معالج النقر على الويدجت"""
        self.show_contact_info()
            
    def setup_styles(self):
        """إعداد أنماط العرض"""
        try:
            # تصميم مشابه لويدجت العام الدراسي مع لون مختلف
            self.setStyleSheet("""
                #trialFrame {
                    background-color: #e74c3c; /* أحمر مثل ويدجت العام الدراسي لكن أحمر */
                    border-radius: 5px; /* نفس الشكل */
                    border: none;
                    padding: 4px;
                }
                
                #trialLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 14px; /* نفس حجم الخط */
                    padding: 0px;
                    background: transparent;
                }
            """)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد أنماط النسخة التجريبية: {e}")
    
    def show_contact_info(self):
        """عرض معلومات الاتصال"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            message = """للحصول على النسخة الكاملة اتصل على:

📞 07710995922

✨ مزايا النسخة الكاملة:
• إضافة عدد غير محدود من الطلاب
• إضافة عدد غير محدود من المعلمين والموظفين
• جميع الميزات المتقدمة
• دعم فني مستمر
• تحديثات مجانية

💰 أسعار مناسبة ومرونة في الدفع
🔒 ضمان الجودة والموثوقية"""

            QMessageBox.information(
                self,
                "النسخة الكاملة",
                message
            )
            
            self.contact_clicked.emit()
            
        except Exception as e:
            logging.error(f"خطأ في عرض معلومات الاتصال: {e}")
