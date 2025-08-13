#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة معاينة PDF داخلية
"""

import logging
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QMessageBox, QWidget, QScrollArea
)
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QIcon

# محاولة استيراد QWebEngineView
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False
    logging.warning("QWebEngineView غير متوفر، سيتم استخدام العرض البديل")

from core.utils.logger import log_user_action


class PDFPreviewDialog(QDialog):
    """نافذة معاينة PDF داخلية مع إمكانية الطباعة"""
    
    print_requested = pyqtSignal()
    
    def __init__(self, pdf_path, title="معاينة الإيصال", parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.pdf_title = title
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_pdf()
        
        log_user_action(f"فتح معاينة PDF: {pdf_path}")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            self.setWindowTitle(self.pdf_title)
            self.setModal(True)
            self.resize(800, 900)
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(10)
            
            # شريط العنوان والأزرار
            header_layout = QHBoxLayout()
            
            # عنوان النافذة
            title_label = QLabel(self.pdf_title)
            title_label.setObjectName("dialogTitle")
            header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            
            # زر الطباعة الحقيقية
            self.print_button = QPushButton("🖨️ طباعة")
            self.print_button.setObjectName("printButton")
            self.print_button.setFixedSize(120, 35)
            header_layout.addWidget(self.print_button)
            
            # زر إغلاق
            self.close_button = QPushButton("✖️ إغلاق")
            self.close_button.setObjectName("closeButton")
            self.close_button.setFixedSize(120, 35)
            header_layout.addWidget(self.close_button)
            
            main_layout.addLayout(header_layout)
            
            # منطقة عرض PDF
            if WEB_ENGINE_AVAILABLE:
                self.pdf_viewer = QWebEngineView()
                self.pdf_viewer.setObjectName("pdfViewer")
                main_layout.addWidget(self.pdf_viewer)
            else:
                # عرض بديل عندما لا يكون محرك الويب متوفراً
                self.setup_fallback_viewer(main_layout)
            
            # شريط الحالة
            status_layout = QHBoxLayout()
            self.status_label = QLabel("جاري تحميل المعاينة...")
            self.status_label.setObjectName("statusLabel")
            status_layout.addWidget(self.status_label)
            status_layout.addStretch()
            
            main_layout.addLayout(status_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة معاينة PDF: {e}")
            raise
    
    def setup_fallback_viewer(self, main_layout):
        """إعداد عارض بديل عندما لا يكون محرك الويب متوفراً"""
        fallback_widget = QWidget()
        fallback_layout = QVBoxLayout(fallback_widget)
        
        # رسالة توضيحية
        info_label = QLabel(
            "🔍 معاينة PDF\n\n"
            "لا يمكن عرض PDF داخل التطبيق.\n"
            "يمكنك فتح الملف خارجياً أو طباعته مباشرة."
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setObjectName("fallbackInfo")
        fallback_layout.addWidget(info_label)
        
        # أزرار الإجراءات
        buttons_layout = QHBoxLayout()
        
        open_external_btn = QPushButton("📂 فتح خارجياً")
        open_external_btn.setObjectName("primaryButton")
        open_external_btn.clicked.connect(self.open_external)
        buttons_layout.addWidget(open_external_btn)
        
        buttons_layout.addStretch()
        
        fallback_layout.addLayout(buttons_layout)
        fallback_layout.addStretch()
        
        main_layout.addWidget(fallback_widget)
        
        self.pdf_viewer = fallback_widget
    
    def setup_styles(self):
        """إعداد الأنماط"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            
            QLabel#dialogTitle {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
            }
            
            QLabel#statusLabel {
                color: #7f8c8d;
                font-size: 12px;
                padding: 5px;
            }
            
            QLabel#fallbackInfo {
                font-size: 16px;
                color: #34495e;
                background-color: white;
                border: 2px dashed #bdc3c7;
                border-radius: 10px;
                padding: 30px;
                margin: 20px;
            }
            
            QPushButton#printButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton#printButton:hover {
                background-color: #229954;
            }
            
            QPushButton#printButton:pressed {
                background-color: #1e8449;
            }
            
            QPushButton#closeButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton#closeButton:hover {
                background-color: #c0392b;
            }
            
            QPushButton#closeButton:pressed {
                background-color: #a93226;
            }
            
            QPushButton#primaryButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #2980b9;
            }
            
            QWebEngineView#pdfViewer {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
        """)
    
    def setup_connections(self):
        """إعداد الاتصالات"""
        self.print_button.clicked.connect(self.print_pdf)
        self.close_button.clicked.connect(self.accept)
    
    def load_pdf(self):
        """تحميل وعرض PDF"""
        try:
            if not os.path.exists(self.pdf_path):
                self.status_label.setText("❌ الملف غير موجود")
                QMessageBox.warning(self, "خطأ", "ملف PDF غير موجود")
                return
            
            if WEB_ENGINE_AVAILABLE:
                # تحويل المسار إلى URL مع التأكد من صحة التشفير
                import urllib.parse
                file_url = "file:///" + self.pdf_path.replace("\\", "/")
                pdf_url = QUrl(file_url)
                
                # تسجيل معلومات التحميل
                logging.info(f"تحميل PDF من URL: {file_url}")
                self.status_label.setText("🔄 جاري تحميل PDF...")
                
                self.pdf_viewer.load(pdf_url)
                self.pdf_viewer.loadFinished.connect(self.on_load_finished)
                
                # إعداد الصفحة للطباعة
                try:
                    self.pdf_viewer.page().profile().setPersistentCookiesPolicy(
                        self.pdf_viewer.page().profile().NoPersistentCookies
                    )
                except Exception as e:
                    logging.warning(f"لا يمكن تعديل إعدادات الملفات الشخصية: {e}")
            else:
                # في الوضع الاحتياطي، الملف جاهز للعرض
                self.status_label.setText("✅ الملف جاهز (وضع احتياطي)")
                logging.info("استخدام الوضع الاحتياطي للعرض")
                
        except Exception as e:
            logging.error(f"خطأ في تحميل PDF: {e}")
            self.status_label.setText("⚠️ مشكلة في التحميل، لكن الملف متاح")
            # لا نعرض رسالة خطأ منبثقة، فقط نسجل الخطأ
    
    def on_load_finished(self, success):
        """معالج انتهاء تحميل PDF"""
        try:
            if success:
                self.status_label.setText("✅ تم تحميل المعاينة بنجاح")
                logging.info("تم تحميل PDF بنجاح")
                # تفعيل زر الطباعة عند نجاح التحميل
                self.print_button.setEnabled(True)
            else:
                self.status_label.setText("⚠️ استخدام العرض الاحتياطي")
                logging.warning("فشل في تحميل PDF، استخدام العرض الاحتياطي")
                # لا نعرض رسالة خطأ إذا كان العرض الاحتياطي يعمل
                # وتبقى إمكانية الطباعة متاحة
                self.print_button.setEnabled(True)
        except Exception as e:
            logging.error(f"خطأ في معالج انتهاء التحميل: {e}")
            self.status_label.setText("✅ العرض متاح")
    
    def print_pdf(self):
        """طباعة PDF حقيقية"""
        try:
            log_user_action(f"طلب طباعة PDF: {self.pdf_path}")
            
            # تحقق من وجود الملف أولاً
            if not os.path.exists(self.pdf_path):
                QMessageBox.warning(self, "خطأ", "ملف PDF غير موجود")
                return
            
            if WEB_ENGINE_AVAILABLE and hasattr(self.pdf_viewer, 'page') and hasattr(self.pdf_viewer.page(), 'print'):
                # طباعة عبر محرك الويب
                try:
                    from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
                    
                    printer = QPrinter(QPrinter.HighResolution)
                    printer.setPageSize(QPrinter.A4)
                    printer.setOrientation(QPrinter.Portrait)
                    
                    # إعداد خصائص الطباعة
                    printer.setDocName("إيصال دفع")
                    printer.setCreator("نظام حسابات المدارس")
                    
                    dialog = QPrintDialog(printer, self)
                    dialog.setWindowTitle("طباعة الإيصال")
                    
                    if dialog.exec_() == QPrintDialog.Accepted:
                        self.status_label.setText("🖨️ جاري الطباعة...")
                        
                        def print_finished(success):
                            try:
                                if success:
                                    self.status_label.setText("✅ تم إرسال الطباعة بنجاح")
                                    QMessageBox.information(self, "نجح", "تم إرسال الطباعة بنجاح")
                                else:
                                    self.status_label.setText("❌ فشل في الطباعة")
                                    self.open_system_print()  # محاولة بديلة
                            except Exception as e:
                                logging.error(f"خطأ في callback الطباعة: {e}")
                                self.open_system_print()
                        
                        try:
                            self.pdf_viewer.page().print(printer, print_finished)
                        except Exception as e:
                            logging.error(f"خطأ في طباعة الصفحة: {e}")
                            self.open_system_print()
                    else:
                        self.status_label.setText("❌ تم إلغاء الطباعة")
                        
                except Exception as e:
                    logging.error(f"خطأ في إعداد الطباعة: {e}")
                    self.open_system_print()
            else:
                # استخدام طباعة النظام مباشرة
                self.open_system_print()
                
        except Exception as e:
            logging.error(f"خطأ شامل في طباعة PDF: {e}")
            # تجنب توقف التطبيق
            try:
                self.open_system_print()
            except:
                QMessageBox.critical(self, "خطأ", "فشل في الطباعة. تأكد من إعدادات النظام.")
    
    def open_system_print(self):
        """فتح طباعة النظام مع خيارات متعددة"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            success = False
            
            if system == "Windows":
                methods = [
                    # الطريقة الأولى - فتح عادي للطباعة اليدوية
                    lambda: os.startfile(self.pdf_path),
                    # الطريقة الثانية - PowerShell
                    lambda: subprocess.run([
                        "powershell", "-Command", 
                        f"Start-Process -FilePath '{self.pdf_path}' -Verb Print"
                    ], check=False, timeout=5, capture_output=True),
                ]
                
                for i, method in enumerate(methods):
                    try:
                        logging.info(f"محاولة طريقة الطباعة {i+1}")
                        method()
                        success = True
                        logging.info(f"نجحت طريقة الطباعة {i+1}")
                        break
                    except Exception as e:
                        logging.error(f"فشل في الطريقة {i+1}: {e}")
                        continue
                        
            elif system == "Darwin":  # macOS
                try:
                    subprocess.run(["open", "-a", "Preview", self.pdf_path], timeout=5)
                    success = True
                except Exception as e:
                    logging.error(f"فشل في فتح macOS: {e}")
            else:  # Linux
                try:
                    subprocess.run(["lp", self.pdf_path], timeout=5)
                    success = True
                except:
                    try:
                        subprocess.run(["xdg-open", self.pdf_path], timeout=5)
                        success = True
                    except Exception as e:
                        logging.error(f"فشل في فتح Linux: {e}")
            
            if success:
                self.status_label.setText("✅ تم فتح الملف للطباعة")
                QMessageBox.information(
                    self, "تم فتح الملف", 
                    "تم فتح الملف بنجاح.\n\n"
                    "للطباعة:\n"
                    "• اضغط Ctrl+P\n"
                    "• أو اذهب إلى File → Print\n"
                    "• اختر الطابعة واضغط Print"
                )
            else:
                raise Exception("فشل في جميع طرق الطباعة")
            
        except Exception as e:
            logging.error(f"خطأ في طباعة النظام: {e}")
            self.status_label.setText("❌ مشكلة في الطباعة")
            
            # رسالة مفيدة للمستخدم
            QMessageBox.warning(
                self, "مشكلة في الطباعة", 
                f"لم تنجح الطباعة التلقائية.\n\n"
                "يمكنك:\n"
                "1. الضغط على 'فتح خارجي' ثم الطباعة يدوياً\n"
                "2. التأكد من تثبيت قارئ PDF\n"
                "3. التأكد من إعدادات الطابعة\n\n"
                f"مسار الملف: {os.path.basename(self.pdf_path)}"
            )
    
    def open_external(self):
        """فتح PDF في تطبيق خارجي"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                os.startfile(self.pdf_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", self.pdf_path])
            else:  # Linux
                subprocess.run(["xdg-open", self.pdf_path])
                
            log_user_action(f"فتح PDF خارجياً: {self.pdf_path}")
            
        except Exception as e:
            logging.error(f"خطأ في فتح PDF خارجياً: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في فتح الملف: {str(e)}")
    
    def closeEvent(self, event):
        """معالج إغلاق النافذة"""
        # تنظيف الملفات المؤقتة إذا لزم الأمر
        try:
            if self.pdf_path and "temp" in self.pdf_path and os.path.exists(self.pdf_path):
                # لا نحذف الملف فوراً، قد يحتاجه المستخدم للطباعة
                pass
        except Exception as e:
            logging.error(f"خطأ في تنظيف الملفات: {e}")
        
        event.accept()
