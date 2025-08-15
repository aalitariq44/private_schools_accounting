#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ويدجت عرض العام الدراسي الحالي
"""

import logging
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from core.utils.settings_manager import get_academic_year


class AcademicYearWidget(QWidget):
    """ويدجت عرض العام الدراسي الحالي"""
    
    # إشارة عند تغيير العام الدراسي
    academic_year_changed = pyqtSignal(str)
    
    def __init__(self, parent=None, show_label=True, auto_refresh=True):
        super().__init__(parent)
        self.show_label = show_label
        self.auto_refresh = auto_refresh
        self.current_year = None
        
        self.setup_ui()
        self.setup_styles()
        self.load_academic_year()
        
        if auto_refresh:
            self.setup_auto_refresh()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # إطار الويدجت
            self.frame = QFrame()
            self.frame.setObjectName("academicYearFrame")
            # ضبط ارتفاع الويدجت
            self.frame.setFixedHeight(30)
            frame_layout = QHBoxLayout()
            frame_layout.setContentsMargins(0, 0, 0, 0)
            frame_layout.setSpacing(0)
            
            if self.show_label:
                # تسمية
                self.label = QLabel("العام الدراسي:")
                self.label.setObjectName("academicYearLabel")
                frame_layout.addWidget(self.label)
            
            # العام الدراسي
            self.year_label = QLabel("تحميل...")
            self.year_label.setObjectName("academicYearValue")
            self.year_label.setAlignment(Qt.AlignCenter)
            
            frame_layout.addWidget(self.year_label)
            
            self.frame.setLayout(frame_layout)
            layout.addWidget(self.frame)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد ويدجت العام الدراسي: {e}")
    
    def setup_styles(self):
        """إعداد أنماط الويدجت"""
        try:
            # ضبط خصائص الخط والحشوة لعرض العام الدراسي
            self.setStyleSheet("""
                #academicYearFrame {
                    background-color: #3498db; /* Blue color */
                    border-radius: 5px; /* Same rounding as the button */
                    border: none;
                    padding: 4px;
                }
                
                #academicYearLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding-right: 0px;
                }
                
                #academicYearValue {
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 0px;
                }
            """)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد أنماط ويدجت العام الدراسي: {e}")
    
    def setup_auto_refresh(self):
        """إعداد التحديث التلقائي"""
        try:
            # تحديث كل 30 ثانية
            self.refresh_timer = QTimer()
            self.refresh_timer.timeout.connect(self.refresh_academic_year)
            self.refresh_timer.start(30000)  # 30 ثانية
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التحديث التلقائي: {e}")
    
    def load_academic_year(self):
        """تحميل العام الدراسي الحالي"""
        try:
            year = get_academic_year()
            self.set_academic_year(year)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل العام الدراسي: {e}")
            self.year_label.setText("خطأ في التحميل")
    
    def set_academic_year(self, year: str):
        """تعيين العام الدراسي"""
        try:
            if year != self.current_year:
                self.current_year = year
                self.year_label.setText(year)
                self.academic_year_changed.emit(year)
                
        except Exception as e:
            logging.error(f"خطأ في تعيين العام الدراسي: {e}")
    
    def refresh_academic_year(self):
        """تحديث العام الدراسي"""
        try:
            year = get_academic_year()
            if year != self.current_year:
                self.set_academic_year(year)
                logging.info(f"تم تحديث العام الدراسي في الويدجت: {year}")
                
        except Exception as e:
            logging.error(f"خطأ في تحديث العام الدراسي: {e}")
    
    def get_academic_year(self) -> str:
        """الحصول على العام الدراسي الحالي"""
        return self.current_year or ""
    
    def set_style_variant(self, variant: str):
        """تغيير نمط الويدجت"""
        try:
            variants = {
                "primary": {
                    "bg": "#3498db",
                    "border": "#2980b9",
                    "value_bg": "#2980b9"
                },
                "success": {
                    "bg": "#27ae60",
                    "border": "#219a52",
                    "value_bg": "#1e8449"
                },
                "warning": {
                    "bg": "#f39c12",
                    "border": "#e67e22",
                    "value_bg": "#d68910"
                },
                "danger": {
                    "bg": "#e74c3c",
                    "border": "#c0392b",
                    "value_bg": "#a93226"
                }
            }
            
            if variant in variants:
                colors = variants[variant]
                style = f"""
                    #academicYearFrame {{
                        background-color: {colors['bg']};
                        border: 2px solid {colors['border']};
                        border-radius: 8px;
                        min-height: 30px;
                        padding: 0px;
                    }}
                    
                    #academicYearLabel {{
                        color: white;
                        font-weight: bold;
                        font-size: 4px;
                        padding-right: 0px;
                    }}
                    
                    #academicYearValue {{
                        color: white;
                        font-weight: bold;
                        font-size: 4px;
                        background-color: {colors['value_bg']};
                        border-radius: 4px;
                        padding: 0px;
                        min-width: 100px;
                    }}
                """
                self.setStyleSheet(style)
                
        except Exception as e:
            logging.error(f"خطأ في تغيير نمط الويدجت: {e}")


if __name__ == "__main__":
    """اختبار الويدجت"""
    import sys
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow
    from PyQt5.QtCore import Qt
    
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    
    # إنشاء نافذة اختبار
    window = QMainWindow()
    window.setWindowTitle("اختبار ويدجت العام الدراسي")
    window.resize(400, 200)
    
    central_widget = QWidget()
    layout = QVBoxLayout()
    
    # إنشاء ويدجت العام الدراسي
    year_widget1 = AcademicYearWidget(show_label=True)
    year_widget2 = AcademicYearWidget(show_label=False)
    year_widget2.set_style_variant("success")
    
    layout.addWidget(year_widget1)
    layout.addWidget(year_widget2)
    layout.addStretch()
    
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    
    window.show()
    sys.exit(app.exec_())
