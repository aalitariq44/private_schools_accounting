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
            layout.setContentsMargins(10, 5, 10, 5)
            layout.setSpacing(15)
            
            # إطار العرض
            frame = QFrame()
            frame.setObjectName("trialFrame")
            frame_layout = QHBoxLayout(frame)
            frame_layout.setContentsMargins(15, 8, 15, 8)
            frame_layout.setSpacing(10)
            
            # أيقونة التجريبية
            trial_icon = QLabel("🔒")
            trial_icon.setAlignment(Qt.AlignCenter)
            trial_icon.setObjectName("trialIcon")
            frame_layout.addWidget(trial_icon)
            
            # نص النسخة التجريبية
            trial_label = QLabel("النسخة التجريبية")
            trial_label.setObjectName("trialLabel")
            trial_label.setAlignment(Qt.AlignCenter)
            frame_layout.addWidget(trial_label)
            
            # خط فاصل
            separator = QFrame()
            separator.setFrameShape(QFrame.VLine)
            separator.setFrameShadow(QFrame.Sunken)
            separator.setObjectName("separator")
            frame_layout.addWidget(separator)
            
            # نص شراء النسخة الكاملة
            purchase_label = QLabel("لشراء النسخة الكاملة")
            purchase_label.setObjectName("purchaseLabel")
            purchase_label.setAlignment(Qt.AlignCenter)
            frame_layout.addWidget(purchase_label)
            
            # زر الاتصال
            contact_btn = QPushButton("📞 07710995922")
            contact_btn.setObjectName("contactButton")
            contact_btn.setCursor(Qt.PointingHandCursor)
            contact_btn.clicked.connect(self.show_contact_info)
            frame_layout.addWidget(contact_btn)
            
            layout.addWidget(frame)
            layout.addStretch()
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد ويدجت النسخة التجريبية: {e}")
            
    def setup_styles(self):
        """إعداد أنماط العرض"""
        try:
            self.setStyleSheet("""
                #trialFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #e74c3c, stop:0.5 #c0392b, stop:1 #e74c3c);
                    border: 2px solid #a93226;
                    border-radius: 15px;
                    color: white;
                    font-weight: bold;
                }
                
                #trialIcon {
                    font-size: 20px;
                    color: #fff;
                    background: transparent;
                }
                
                #trialLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #fff;
                    background: transparent;
                    min-width: 100px;
                }
                
                #purchaseLabel {
                    font-size: 14px;
                    color: #f8f9fa;
                    background: transparent;
                    min-width: 120px;
                }
                
                #separator {
                    color: #fff;
                    background: #fff;
                    max-width: 1px;
                }
                
                #contactButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f39c12, stop:1 #d68910);
                    color: white;
                    border: 2px solid #b7950b;
                    border-radius: 8px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 14px;
                    min-width: 120px;
                }
                
                #contactButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f7dc6f, stop:1 #f39c12);
                    border-color: #d68910;
                }
                
                #contactButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #d68910, stop:1 #b7950b);
                }
            """)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد أنماط النسخة التجريبية: {e}")
    
    def show_contact_info(self):
        """عرض معلومات الاتصال"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            message = """للحصول على النسخة الكاملة من البرنامج:

📞 اتصل بالرقم: 07710995922

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
                "النسخة الكاملة - معلومات الاتصال",
                message
            )
            
            self.contact_clicked.emit()
            
        except Exception as e:
            logging.error(f"خطأ في عرض معلومات الاتصال: {e}")
