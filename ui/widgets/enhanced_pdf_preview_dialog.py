#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة معاينة PDF محسنة مع دعم أفضل للعرض والطباعة
"""

import logging
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QMessageBox, QWidget, QScrollArea, QTextEdit
)
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

# محاولة استيراد QWebEngineView
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
    WEB_ENGINE_AVAILABLE = True
    logging.info("تم تحميل محرك الويب بنجاح")
except ImportError:
    WEB_ENGINE_AVAILABLE = False
    logging.warning("QWebEngineView غير متوفر، سيتم استخدام العرض البديل")

from core.utils.logger import log_user_action


class EnhancedPDFPreviewDialog(QDialog):
    """نافذة معاينة PDF محسنة مع دعم أفضل للعرض والطباعة"""
    
    print_requested = pyqtSignal()
    
    def __init__(self, pdf_path, title="معاينة الإيصال", parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.pdf_title = title
        self.load_attempts = 0
        self.max_attempts = 3
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        
        # تأخير بسيط قبل تحميل PDF
        QTimer.singleShot(500, self.load_pdf)
        
        log_user_action(f"فتح معاينة PDF محسنة: {pdf_path}")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            self.setWindowTitle(self.pdf_title)
            self.setModal(True)
            self.resize(900, 700)
            
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
            
            # معلومات الحالة
            self.engine_status = QLabel()
            self.engine_status.setObjectName("engineStatus")
            if WEB_ENGINE_AVAILABLE:
                self.engine_status.setText("🌐 محرك ويب متقدم")
                self.engine_status.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.engine_status.setText("📄 وضع احتياطي")
                self.engine_status.setStyleSheet("color: orange; font-weight: bold;")
            header_layout.addWidget(self.engine_status)
            
            header_layout.addStretch()
            
            # زر إعادة التحميل
            self.reload_button = QPushButton("🔄 إعادة تحميل")
            self.reload_button.setObjectName("reloadButton")
            self.reload_button.setFixedSize(120, 35)
            header_layout.addWidget(self.reload_button)
            
            # زر الطباعة الحقيقية
            self.print_button = QPushButton("🖨️ طباعة")
            self.print_button.setObjectName("printButton")
            self.print_button.setFixedSize(120, 35)
            header_layout.addWidget(self.print_button)
            
            # زر فتح خارجي
            self.external_button = QPushButton("📂 فتح خارجي")
            self.external_button.setObjectName("externalButton")
            self.external_button.setFixedSize(120, 35)
            header_layout.addWidget(self.external_button)
            
            # زر إغلاق
            self.close_button = QPushButton("✖️ إغلاق")
            self.close_button.setObjectName("closeButton")
            self.close_button.setFixedSize(120, 35)
            header_layout.addWidget(self.close_button)
            
            main_layout.addLayout(header_layout)
            
            # منطقة عرض PDF
            # PDF display area should take most space
            if WEB_ENGINE_AVAILABLE:
                self.setup_web_viewer(main_layout)
                main_layout.setStretchFactor(self.pdf_viewer, 10)
            else:
                self.setup_fallback_viewer(main_layout)
                main_layout.setStretchFactor(self.pdf_viewer, 10)
            
            # شريط الحالة
            status_layout = QHBoxLayout()
            self.status_label = QLabel("جاري التحضير...")
            self.status_label.setObjectName("statusLabel")
            status_layout.addWidget(self.status_label)
            status_layout.addStretch()
            
            # معلومات الملف
            file_info = f"📄 {os.path.basename(self.pdf_path)}"
            if os.path.exists(self.pdf_path):
                size_mb = os.path.getsize(self.pdf_path) / 1024 / 1024
                file_info += f" ({size_mb:.1f} MB)"
            
            self.file_info_label = QLabel(file_info)
            self.file_info_label.setObjectName("fileInfo")
            status_layout.addWidget(self.file_info_label)
            
            # add status bar with minimal stretch
            # status bar layout minimal stretch
            main_layout.addLayout(status_layout)
            main_layout.setStretchFactor(status_layout, 0)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة معاينة PDF المحسنة: {e}")
            raise
    
    def setup_web_viewer(self, main_layout):
        """إعداد عارض الويب"""
        self.pdf_viewer = QWebEngineView()
        self.pdf_viewer.setObjectName("pdfViewer")
        
        # إعدادات المحرك
        settings = self.pdf_viewer.settings()
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        
        main_layout.addWidget(self.pdf_viewer)
    
    def setup_fallback_viewer(self, main_layout):
        """إعداد عارض بديل مع معلومات PDF"""
        fallback_widget = QWidget()
        fallback_layout = QVBoxLayout(fallback_widget)
        
        # رسالة توضيحية
        info_label = QLabel(
            "📋 معاينة ملف PDF\n\n"
            "لا يمكن عرض PDF داخل التطبيق لأن محرك الويب غير متوفر.\n"
            "يمكنك فتح الملف خارجياً أو طباعته مباشرة.\n\n"
            "لتحسين التجربة، قم بتثبيت PyQtWebEngine:\n"
            "pip install PyQtWebEngine"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setObjectName("fallbackInfo")
        fallback_layout.addWidget(info_label)
        
        # عرض معلومات الملف
        if os.path.exists(self.pdf_path):
            file_details = QTextEdit()
            file_details.setReadOnly(True)
            file_details.setMaximumHeight(150)
            
            stats = os.stat(self.pdf_path)
            import time
            details_text = f"""
معلومات الملف:
📄 الاسم: {os.path.basename(self.pdf_path)}
📂 المسار: {self.pdf_path}
📏 الحجم: {stats.st_size / 1024:.1f} KB
📅 تاريخ الإنشاء: {time.ctime(stats.st_ctime)}
🕒 آخر تعديل: {time.ctime(stats.st_mtime)}
            """
            file_details.setPlainText(details_text)
            fallback_layout.addWidget(file_details)
        
        fallback_layout.addStretch()
        main_layout.addWidget(fallback_widget)
        self.pdf_viewer = fallback_widget
    
    def setup_styles(self):
        """إعداد الأنماط"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            
            QLabel#dialogTitle {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
            }
            
            QLabel#engineStatus {
                font-size: 12px;
                padding: 5px;
            }
            
            QLabel#statusLabel {
                color: #6c757d;
                font-size: 12px;
                padding: 5px;
            }
            
            QLabel#fileInfo {
                color: #495057;
                font-size: 11px;
                padding: 5px;
            }
            
            QLabel#fallbackInfo {
                font-size: 14px;
                color: #495057;
                background-color: white;
                border: 2px dashed #dee2e6;
                border-radius: 10px;
                padding: 30px;
                margin: 20px;
                line-height: 1.6;
            }
            
            QPushButton#printButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#printButton:hover {
                background-color: #218838;
            }
            
            QPushButton#externalButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#externalButton:hover {
                background-color: #138496;
            }
            
            QPushButton#reloadButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#reloadButton:hover {
                background-color: #e0a800;
            }
            
            QPushButton#closeButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#closeButton:hover {
                background-color: #c82333;
            }
            
            QWebEngineView#pdfViewer {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #f8f9fa;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
    
    def setup_connections(self):
        """إعداد الاتصالات"""
        self.print_button.clicked.connect(self.print_pdf)
        self.external_button.clicked.connect(self.open_external)
        self.reload_button.clicked.connect(self.load_pdf)
        self.close_button.clicked.connect(self.accept)
    
    def load_pdf(self):
        """تحميل وعرض PDF"""
        try:
            self.load_attempts += 1
            
            if not os.path.exists(self.pdf_path):
                self.status_label.setText("❌ الملف غير موجود")
                QMessageBox.warning(self, "خطأ", "ملف PDF غير موجود")
                return
            
            if WEB_ENGINE_AVAILABLE and hasattr(self, 'pdf_viewer') and hasattr(self.pdf_viewer, 'load'):
                self.status_label.setText(f"🔄 جاري التحميل (المحاولة {self.load_attempts})...")
                
                # تحويل المسار إلى URL صحيح
                import urllib.parse
                file_path = self.pdf_path.replace("\\", "/")
                if not file_path.startswith("/"):
                    file_path = "/" + file_path
                file_url = f"file://{file_path}"
                
                logging.info(f"تحميل PDF من: {file_url}")
                
                # تحميل الملف
                pdf_url = QUrl(file_url)
                self.pdf_viewer.load(pdf_url)
                self.pdf_viewer.loadFinished.connect(self.on_load_finished)
                
            else:
                self.status_label.setText("📄 جاهز للعرض (وضع احتياطي)")
                logging.info("استخدام الوضع الاحتياطي للعرض")
                
        except Exception as e:
            logging.error(f"خطأ في تحميل PDF: {e}")
            self.status_label.setText(f"❌ فشل في التحميل: {str(e)[:50]}...")
            
            if self.load_attempts < self.max_attempts:
                QTimer.singleShot(2000, self.load_pdf)  # إعادة المحاولة بعد ثانيتين
    
    def on_load_finished(self, success):
        """معالج انتهاء تحميل PDF"""
        try:
            if success:
                self.status_label.setText("✅ تم تحميل PDF بنجاح")
                logging.info("تم تحميل PDF بنجاح")
            else:
                self.status_label.setText("✅ العرض متاح (وضع احتياطي)")
                logging.info("فشل في تحميل PDF مباشرة، الوضع الاحتياطي متاح")
                
                # لا نعرض رسالة خطأ إذا كان الملف موجود والوضع الاحتياطي يعمل
                if not os.path.exists(self.pdf_path):
                    reply = QMessageBox.question(
                        self, "مشكلة في الملف", 
                        "الملف غير متاح للعرض المباشر. هل تريد فتحه خارجياً؟",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        self.open_external()
        except Exception as e:
            logging.error(f"خطأ في معالج انتهاء التحميل: {e}")
            self.status_label.setText("✅ الملف متاح للاستخدام")
    
    def print_pdf(self):
        """طباعة PDF حقيقية"""
        try:
            log_user_action(f"طلب طباعة PDF محسنة: {self.pdf_path}")
            
            # تحقق من وجود الملف
            if not os.path.exists(self.pdf_path):
                QMessageBox.warning(self, "خطأ", "ملف PDF غير موجود")
                return
            
            if WEB_ENGINE_AVAILABLE and hasattr(self.pdf_viewer, 'page') and hasattr(self.pdf_viewer.page(), 'print'):
                # طباعة عبر محرك الويب مع الحماية من الإغلاق
                try:
                    from core.printing.safe_print_manager import SafePrintManager
                    
                    safe_manager = SafePrintManager(self)
                    
                    def handle_print_success():
                        """معالجة نجاح الطباعة"""
                        self.status_label.setText("✅ تم إرسال الطباعة بنجاح")
                        QMessageBox.information(self, "نجح", "تم إرسال الطباعة بنجاح!")
                    
                    def handle_print_failure():
                        """معالجة فشل الطباعة"""
                        self.status_label.setText("❌ فشل في الطباعة")
                        self.open_system_print()  # محاولة بديلة
                    
                    # استخدام الطباعة الآمنة
                    success = safe_manager.safe_print_with_dialog(self.pdf_viewer)
                    if success:
                        handle_print_success()
                    else:
                        handle_print_failure()
                        
                except Exception as e:
                    logging.error(f"خطأ في إعداد الطباعة الآمنة: {e}")
                    self.open_system_print()  # العودة للطريقة التقليدية
            else:
                # استخدام طباعة النظام
                self.open_system_print()
                
        except Exception as e:
            logging.error(f"خطأ شامل في طباعة PDF محسنة: {e}")
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
                    # الطريقة الثانية - محاولة الطباعة المباشرة
                    lambda: subprocess.run([
                        "powershell", "-Command", 
                        f"Start-Process '{self.pdf_path}' -Verb Print"
                    ], check=True, timeout=10),
                ]
                
                for i, method in enumerate(methods):
                    try:
                        method()
                        success = True
                        break
                    except Exception as e:
                        logging.error(f"فشل في الطريقة {i+1}: {e}")
                        continue
                        
            elif system == "Darwin":  # macOS
                subprocess.run(["open", "-a", "Preview", self.pdf_path])
                success = True
            else:  # Linux
                try:
                    subprocess.run(["lp", self.pdf_path])
                    success = True
                except:
                    subprocess.run(["xdg-open", self.pdf_path])
                    success = True
            
            if success:
                QMessageBox.information(
                    self, "تم فتح الملف", 
                    "تم فتح الملف بنجاح.\n\n"
                    "للطباعة:\n"
                    "• اضغط Ctrl+P\n"
                    "• أو اذهب إلى File → Print\n"
                    "• اختر الطابعة واضغط Print"
                )
                self.status_label.setText("✅ تم فتح الملف للطباعة")
            else:
                raise Exception("فشل في جميع طرق الطباعة")
            
        except Exception as e:
            logging.error(f"خطأ في طباعة النظام: {e}")
            QMessageBox.critical(
                self, "خطأ في الطباعة", 
                f"فشل في فتح الطباعة: {str(e)}\n\n"
                "تأكد من:\n"
                "• وجود طابعة مثبتة في النظام\n"
                "• تثبيت قارئ PDF (Adobe Reader أو غيره)\n"
                "• صحة مسار الملف"
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
            self.status_label.setText("✅ تم فتح الملف خارجياً")
            
        except Exception as e:
            logging.error(f"خطأ في فتح PDF خارجياً: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في فتح الملف: {str(e)}")
    
    def closeEvent(self, event):
        """معالج إغلاق النافذة"""
        try:
            # لا نحذف الملفات المؤقتة فوراً، قد يحتاجها المستخدم
            logging.info(f"إغلاق نافذة معاينة PDF: {self.pdf_path}")
        except Exception as e:
            logging.error(f"خطأ في إغلاق النافذة: {e}")
        
        event.accept()
