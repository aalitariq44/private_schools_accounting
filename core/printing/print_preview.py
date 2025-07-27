#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة معاينة الطباعة
"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTextEdit, QLabel, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QMessageBox, QProgressDialog, QSplitter,
    QFrame, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextDocument, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

from .print_config import PrintSettings, PaperSize, PrintOrientation, PrintQuality


class PrintPreviewDialog(QDialog):
    """نافذة معاينة الطباعة"""
    
    def __init__(self, html_content: str, title: str = "معاينة الطباعة", parent=None):
        super().__init__(parent)
        self.html_content = html_content
        self.printer = QPrinter()
        self.print_settings = PrintSettings()
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(1000, 700)
        
        self.setup_ui()
        self.setup_connections()
        self.load_preview()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)
            
            # شريط الأدوات
            self.create_toolbar(layout)
            
            # منطقة المعاينة والإعدادات
            splitter = QSplitter(Qt.Horizontal)
            
            # منطقة المعاينة
            self.create_preview_area(splitter)
            
            # لوحة الإعدادات
            self.create_settings_panel(splitter)
            
            # تحديد نسب العرض
            splitter.setSizes([700, 300])
            layout.addWidget(splitter)
            
            # أزرار التحكم
            self.create_control_buttons(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة معاينة الطباعة: {e}")
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("toolbarFrame")
            
            toolbar_layout = QHBoxLayout(toolbar_frame)
            
            # عنوان النافذة
            title_label = QLabel("معاينة الطباعة")
            title_label.setObjectName("titleLabel")
            toolbar_layout.addWidget(title_label)
            
            toolbar_layout.addStretch()
            
            # أزرار سريعة
            self.zoom_in_btn = QPushButton("تكبير")
            self.zoom_in_btn.setObjectName("toolbarButton")
            toolbar_layout.addWidget(self.zoom_in_btn)
            
            self.zoom_out_btn = QPushButton("تصغير")
            self.zoom_out_btn.setObjectName("toolbarButton")
            toolbar_layout.addWidget(self.zoom_out_btn)
            
            self.fit_width_btn = QPushButton("ملء العرض")
            self.fit_width_btn.setObjectName("toolbarButton")
            toolbar_layout.addWidget(self.fit_width_btn)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
    
    def create_preview_area(self, parent):
        """إنشاء منطقة المعاينة"""
        try:
            preview_frame = QFrame()
            preview_frame.setObjectName("previewFrame")
            
            preview_layout = QVBoxLayout(preview_frame)
            preview_layout.setContentsMargins(5, 5, 5, 5)
            
            # عنوان المعاينة
            preview_label = QLabel("معاينة المستند")
            preview_label.setObjectName("sectionLabel")
            preview_layout.addWidget(preview_label)
            
            # عارض الويب للمعاينة
            self.web_view = QWebEngineView()
            self.web_view.setObjectName("webView")
            preview_layout.addWidget(self.web_view)
            
            parent.addWidget(preview_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء منطقة المعاينة: {e}")
    
    def create_settings_panel(self, parent):
        """إنشاء لوحة الإعدادات"""
        try:
            settings_frame = QFrame()
            settings_frame.setObjectName("settingsFrame")
            
            settings_layout = QVBoxLayout(settings_frame)
            settings_layout.setContentsMargins(10, 10, 10, 10)
            
            # عنوان الإعدادات
            settings_label = QLabel("إعدادات الطباعة")
            settings_label.setObjectName("sectionLabel")
            settings_layout.addWidget(settings_label)
            
            # إعدادات الورق
            self.create_paper_settings(settings_layout)
            
            # إعدادات التخطيط
            self.create_layout_settings(settings_layout)
            
            # إعدادات الجودة
            self.create_quality_settings(settings_layout)
            
            # إعدادات إضافية
            self.create_additional_settings(settings_layout)
            
            settings_layout.addStretch()
            
            parent.addWidget(settings_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء لوحة الإعدادات: {e}")
    
    def create_paper_settings(self, layout):
        """إعدادات الورق"""
        try:
            paper_group = QGroupBox("إعدادات الورق")
            paper_group.setObjectName("settingsGroup")
            
            paper_layout = QVBoxLayout(paper_group)
            
            # حجم الورق
            paper_size_layout = QHBoxLayout()
            paper_size_layout.addWidget(QLabel("حجم الورق:"))
            
            self.paper_size_combo = QComboBox()
            self.paper_size_combo.setObjectName("settingsCombo")
            for size in PaperSize:
                self.paper_size_combo.addItem(size.value, size)
            paper_size_layout.addWidget(self.paper_size_combo)
            
            paper_layout.addLayout(paper_size_layout)
            
            # اتجاه الورق
            orientation_layout = QHBoxLayout()
            orientation_layout.addWidget(QLabel("الاتجاه:"))
            
            self.orientation_combo = QComboBox()
            self.orientation_combo.setObjectName("settingsCombo")
            for orientation in PrintOrientation:
                self.orientation_combo.addItem(
                    "عمودي" if orientation == PrintOrientation.PORTRAIT else "أفقي",
                    orientation
                )
            orientation_layout.addWidget(self.orientation_combo)
            
            paper_layout.addLayout(orientation_layout)
            
            layout.addWidget(paper_group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء إعدادات الورق: {e}")
    
    def create_layout_settings(self, layout):
        """إعدادات التخطيط"""
        try:
            layout_group = QGroupBox("إعدادات التخطيط")
            layout_group.setObjectName("settingsGroup")
            
            layout_layout = QVBoxLayout(layout_group)
            
            # الهوامش
            margins_layout = QVBoxLayout()
            margins_layout.addWidget(QLabel("الهوامش (مم):"))
            
            # هامش علوي
            top_layout = QHBoxLayout()
            top_layout.addWidget(QLabel("علوي:"))
            self.top_margin_spin = QSpinBox()
            self.top_margin_spin.setRange(0, 50)
            self.top_margin_spin.setValue(20)
            self.top_margin_spin.setObjectName("settingsSpin")
            top_layout.addWidget(self.top_margin_spin)
            margins_layout.addLayout(top_layout)
            
            # هامش سفلي
            bottom_layout = QHBoxLayout()
            bottom_layout.addWidget(QLabel("سفلي:"))
            self.bottom_margin_spin = QSpinBox()
            self.bottom_margin_spin.setRange(0, 50)
            self.bottom_margin_spin.setValue(20)
            self.bottom_margin_spin.setObjectName("settingsSpin")
            bottom_layout.addWidget(self.bottom_margin_spin)
            margins_layout.addLayout(bottom_layout)
            
            # هامش أيمن
            right_layout = QHBoxLayout()
            right_layout.addWidget(QLabel("أيمن:"))
            self.right_margin_spin = QSpinBox()
            self.right_margin_spin.setRange(0, 50)
            self.right_margin_spin.setValue(20)
            self.right_margin_spin.setObjectName("settingsSpin")
            right_layout.addWidget(self.right_margin_spin)
            margins_layout.addLayout(right_layout)
            
            # هامش أيسر
            left_layout = QHBoxLayout()
            left_layout.addWidget(QLabel("أيسر:"))
            self.left_margin_spin = QSpinBox()
            self.left_margin_spin.setRange(0, 50)
            self.left_margin_spin.setValue(20)
            self.left_margin_spin.setObjectName("settingsSpin")
            left_layout.addWidget(self.left_margin_spin)
            margins_layout.addLayout(left_layout)
            
            layout_layout.addLayout(margins_layout)
            
            layout.addWidget(layout_group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء إعدادات التخطيط: {e}")
    
    def create_quality_settings(self, layout):
        """إعدادات الجودة"""
        try:
            quality_group = QGroupBox("إعدادات الجودة")
            quality_group.setObjectName("settingsGroup")
            
            quality_layout = QVBoxLayout(quality_group)
            
            # جودة الطباعة
            quality_layout.addWidget(QLabel("جودة الطباعة:"))
            
            self.quality_combo = QComboBox()
            self.quality_combo.setObjectName("settingsCombo")
            for quality in PrintQuality:
                quality_text = {
                    PrintQuality.DRAFT: "مسودة",
                    PrintQuality.NORMAL: "عادي",
                    PrintQuality.HIGH: "عالي"
                }
                self.quality_combo.addItem(quality_text[quality], quality)
            
            quality_layout.addWidget(self.quality_combo)
            
            layout.addWidget(quality_group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء إعدادات الجودة: {e}")
    
    def create_additional_settings(self, layout):
        """إعدادات إضافية"""
        try:
            additional_group = QGroupBox("إعدادات إضافية")
            additional_group.setObjectName("settingsGroup")
            
            additional_layout = QVBoxLayout(additional_group)
            
            # رأس الصفحة
            self.header_check = QCheckBox("عرض رأس الصفحة")
            self.header_check.setChecked(True)
            self.header_check.setObjectName("settingsCheck")
            additional_layout.addWidget(self.header_check)
            
            # تذييل الصفحة
            self.footer_check = QCheckBox("عرض تذييل الصفحة")
            self.footer_check.setChecked(True)
            self.footer_check.setObjectName("settingsCheck")
            additional_layout.addWidget(self.footer_check)
            
            # أرقام الصفحات
            self.page_numbers_check = QCheckBox("عرض أرقام الصفحات")
            self.page_numbers_check.setChecked(True)
            self.page_numbers_check.setObjectName("settingsCheck")
            additional_layout.addWidget(self.page_numbers_check)
            
            layout.addWidget(additional_group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الإعدادات الإضافية: {e}")
    
    def create_control_buttons(self, layout):
        """إنشاء أزرار التحكم"""
        try:
            buttons_frame = QFrame()
            buttons_frame.setObjectName("buttonsFrame")
            
            buttons_layout = QHBoxLayout(buttons_frame)
            
            # زر الطباعة
            self.print_button = QPushButton("طباعة")
            self.print_button.setObjectName("primaryButton")
            buttons_layout.addWidget(self.print_button)
            
            # زر تحديث المعاينة
            self.refresh_button = QPushButton("تحديث المعاينة")
            self.refresh_button.setObjectName("secondaryButton")
            buttons_layout.addWidget(self.refresh_button)
            
            # زر إعدادات متقدمة
            self.advanced_button = QPushButton("إعدادات متقدمة")
            self.advanced_button.setObjectName("secondaryButton")
            buttons_layout.addWidget(self.advanced_button)
            
            buttons_layout.addStretch()
            
            # زر الإلغاء
            self.cancel_button = QPushButton("إلغاء")
            self.cancel_button.setObjectName("cancelButton")
            buttons_layout.addWidget(self.cancel_button)
            
            layout.addWidget(buttons_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء أزرار التحكم: {e}")
    
    def setup_connections(self):
        """ربط الإشارات"""
        try:
            # أزرار التحكم
            self.print_button.clicked.connect(self.print_document)
            self.refresh_button.clicked.connect(self.refresh_preview)
            self.advanced_button.clicked.connect(self.show_advanced_settings)
            self.cancel_button.clicked.connect(self.reject)
            
            # أزرار التكبير والتصغير
            self.zoom_in_btn.clicked.connect(self.zoom_in)
            self.zoom_out_btn.clicked.connect(self.zoom_out)
            self.fit_width_btn.clicked.connect(self.fit_width)
            
            # إعدادات الطباعة
            self.paper_size_combo.currentTextChanged.connect(self.update_preview_delayed)
            self.orientation_combo.currentTextChanged.connect(self.update_preview_delayed)
            self.quality_combo.currentTextChanged.connect(self.update_preview_delayed)
            
            # الهوامش
            self.top_margin_spin.valueChanged.connect(self.update_preview_delayed)
            self.bottom_margin_spin.valueChanged.connect(self.update_preview_delayed)
            self.right_margin_spin.valueChanged.connect(self.update_preview_delayed)
            self.left_margin_spin.valueChanged.connect(self.update_preview_delayed)
            
            # الإعدادات الإضافية
            self.header_check.toggled.connect(self.update_preview_delayed)
            self.footer_check.toggled.connect(self.update_preview_delayed)
            self.page_numbers_check.toggled.connect(self.update_preview_delayed)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def update_preview_delayed(self):
        """تحديث المعاينة مع تأخير لتجنب التحديث المستمر"""
        try:
            if hasattr(self, 'update_timer'):
                self.update_timer.stop()
            
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.refresh_preview)
            self.update_timer.start(500)  # تأخير نصف ثانية
            
        except Exception as e:
            logging.error(f"خطأ في تحديث المعاينة المؤجل: {e}")
    
    def load_preview(self):
        """تحميل المعاينة الأولية"""
        try:
            self.web_view.setHtml(self.html_content)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المعاينة: {e}")
    
    def refresh_preview(self):
        """تحديث المعاينة"""
        try:
            # تحديث إعدادات الطباعة
            self.update_print_settings()
            
            # إعادة تحميل المحتوى مع الإعدادات الجديدة
            self.web_view.setHtml(self.html_content)
            
        except Exception as e:
            logging.error(f"خطأ في تحديث المعاينة: {e}")
    
    def update_print_settings(self):
        """تحديث إعدادات الطباعة"""
        try:
            # حجم الورق
            self.print_settings.paper_size = self.paper_size_combo.currentData()
            
            # الاتجاه
            self.print_settings.orientation = self.orientation_combo.currentData()
            
            # الجودة
            self.print_settings.quality = self.quality_combo.currentData()
            
            # الهوامش
            self.print_settings.margins = {
                "top": self.top_margin_spin.value(),
                "bottom": self.bottom_margin_spin.value(),
                "right": self.right_margin_spin.value(),
                "left": self.left_margin_spin.value()
            }
            
            # الإعدادات الإضافية
            self.print_settings.header_enabled = self.header_check.isChecked()
            self.print_settings.footer_enabled = self.footer_check.isChecked()
            self.print_settings.page_numbers = self.page_numbers_check.isChecked()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث إعدادات الطباعة: {e}")
    
    def zoom_in(self):
        """تكبير المعاينة"""
        try:
            self.web_view.setZoomFactor(self.web_view.zoomFactor() * 1.2)
        except Exception as e:
            logging.error(f"خطأ في تكبير المعاينة: {e}")
    
    def zoom_out(self):
        """تصغير المعاينة"""
        try:
            self.web_view.setZoomFactor(self.web_view.zoomFactor() / 1.2)
        except Exception as e:
            logging.error(f"خطأ في تصغير المعاينة: {e}")
    
    def fit_width(self):
        """ملء العرض"""
        try:
            self.web_view.setZoomFactor(1.0)
        except Exception as e:
            logging.error(f"خطأ في ملء العرض: {e}")
    
    def print_document(self):
        """طباعة المستند"""
        try:
            # إعداد الطابعة
            self.configure_printer()
            
            # فتح نافذة الطباعة
            print_dialog = QPrintDialog(self.printer, self)
            if print_dialog.exec_() == QPrintDialog.Accepted:
                # طباعة المحتوى
                self.web_view.page().print(self.printer, self.on_print_finished)
                
                # إظهار رسالة الانتظار
                self.show_printing_progress()
            
        except Exception as e:
            logging.error(f"خطأ في الطباعة: {e}")
            QMessageBox.critical(self, "خطأ في الطباعة", f"حدث خطأ أثناء الطباعة:\\n{str(e)}")
    
    def configure_printer(self):
        """تكوين الطابعة"""
        try:
            # حجم الورق
            if self.print_settings.paper_size == PaperSize.A4:
                self.printer.setPageSize(QPrinter.A4)
            elif self.print_settings.paper_size == PaperSize.A3:
                self.printer.setPageSize(QPrinter.A3)
            elif self.print_settings.paper_size == PaperSize.LETTER:
                self.printer.setPageSize(QPrinter.Letter)
            elif self.print_settings.paper_size == PaperSize.LEGAL:
                self.printer.setPageSize(QPrinter.Legal)
            
            # الاتجاه
            if self.print_settings.orientation == PrintOrientation.PORTRAIT:
                self.printer.setOrientation(QPrinter.Portrait)
            else:
                self.printer.setOrientation(QPrinter.Landscape)
            
            # الجودة
            if self.print_settings.quality == PrintQuality.DRAFT:
                self.printer.setResolution(150)
            elif self.print_settings.quality == PrintQuality.NORMAL:
                self.printer.setResolution(300)
            else:
                self.printer.setResolution(600)
            
            # الهوامش (تحويل من مم إلى نقاط)
            margins = self.print_settings.margins
            margin_left = margins["left"] * 2.83  # تحويل مم إلى نقاط
            margin_top = margins["top"] * 2.83
            margin_right = margins["right"] * 2.83
            margin_bottom = margins["bottom"] * 2.83
            
            self.printer.setPageMargins(margin_left, margin_top, margin_right, margin_bottom, QPrinter.Point)
            
        except Exception as e:
            logging.error(f"خطأ في تكوين الطابعة: {e}")
    
    def show_printing_progress(self):
        """إظهار تقدم الطباعة"""
        try:
            self.progress_dialog = QProgressDialog("جاري الطباعة...", "إلغاء", 0, 0, self)
            self.progress_dialog.setModal(True)
            self.progress_dialog.show()
            
        except Exception as e:
            logging.error(f"خطأ في إظهار تقدم الطباعة: {e}")
    
    def on_print_finished(self, success):
        """عند انتهاء الطباعة"""
        try:
            if hasattr(self, 'progress_dialog'):
                self.progress_dialog.close()
            
            if success:
                QMessageBox.information(self, "نجحت الطباعة", "تمت الطباعة بنجاح")
                self.accept()
            else:
                QMessageBox.warning(self, "فشلت الطباعة", "حدث خطأ أثناء الطباعة")
                
        except Exception as e:
            logging.error(f"خطأ في معالجة انتهاء الطباعة: {e}")
    
    def show_advanced_settings(self):
        """إظهار الإعدادات المتقدمة"""
        try:
            from .advanced_print_settings import AdvancedPrintSettingsDialog
            
            dialog = AdvancedPrintSettingsDialog(self.print_settings, self)
            if dialog.exec_() == QDialog.Accepted:
                self.print_settings = dialog.get_settings()
                self.refresh_preview()
                
        except Exception as e:
            logging.error(f"خطأ في إظهار الإعدادات المتقدمة: {e}")
            QMessageBox.information(self, "قريباً", "الإعدادات المتقدمة قيد التطوير")
    
    def get_print_settings(self) -> PrintSettings:
        """الحصول على إعدادات الطباعة"""
        self.update_print_settings()
        return self.print_settings
    
    def apply_styles(self):
        """تطبيق التنسيقات"""
        style = """
            QDialog {
                background-color: #F8F9FA;
                font-family: Arial, sans-serif;
            }
            
            #toolbarFrame {
                background-color: #FFFFFF;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }
            
            #titleLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
            }
            
            #toolbarButton {
                background-color: #6C757D;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 0 2px;
            }
            
            #toolbarButton:hover {
                background-color: #5A6268;
            }
            
            #previewFrame, #settingsFrame {
                background-color: #FFFFFF;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                margin: 5px;
            }
            
            #sectionLabel {
                font-size: 14px;
                font-weight: bold;
                color: #495057;
                padding: 10px;
                background-color: #F8F9FA;
                border-bottom: 1px solid #E9ECEF;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E9ECEF;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
            
            #settingsCombo, #settingsSpin {
                padding: 8px;
                border: 1px solid #CED4DA;
                border-radius: 4px;
                background-color: white;
            }
            
            #settingsCheck {
                color: #495057;
                font-weight: normal;
            }
            
            #primaryButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 120px;
            }
            
            #primaryButton:hover {
                background-color: #0056B3;
            }
            
            #secondaryButton {
                background-color: #6C757D;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                min-width: 120px;
            }
            
            #secondaryButton:hover {
                background-color: #5A6268;
            }
            
            #cancelButton {
                background-color: #DC3545;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                min-width: 120px;
            }
            
            #cancelButton:hover {
                background-color: #C82333;
            }
            
            #buttonsFrame {
                background-color: #F8F9FA;
                border-top: 1px solid #E9ECEF;
                padding: 15px;
                margin-top: 10px;
            }
        """
        
        self.setStyleSheet(style)
