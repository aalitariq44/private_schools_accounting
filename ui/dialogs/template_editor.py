#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محرر قالب الهوية المحسّن - واجهة لتحرير إعدادات القالب بصريا مع معاينة لحظية
"""

import sys
import json
import logging
import tempfile
import threading
import os
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QWidget, QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
    QLineEdit, QColorDialog, QComboBox, QCheckBox, QGroupBox,
    QScrollArea, QTextEdit, QFileDialog, QMessageBox, QSplitter,
    QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, QUrl
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView

# إضافة مسار المشروع
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from templates.id_template import (
    TEMPLATE_ELEMENTS, save_template_as_json, load_template_from_json,
    ID_WIDTH, ID_HEIGHT, GRID_COLS, GRID_ROWS
)


class LivePDFGenerator(QThread):
    """مولد PDF لحظي في خيط منفصل"""
    pdf_generated = pyqtSignal(str)  # إشارة عند اكتمال توليد PDF
    error_occurred = pyqtSignal(str)  # إشارة عند حدوث خطأ
    
    def __init__(self):
        super().__init__()
        self.template_data = None
        self.should_generate = False
        self.temp_dir = Path(tempfile.gettempdir()) / "id_preview"
        self.temp_dir.mkdir(exist_ok=True)
        
    def set_template_data(self, template_data):
        """تحديث بيانات القالب"""
        self.template_data = template_data.copy()
        self.should_generate = True
        
    def run(self):
        """تشغيل مولد PDF"""
        if not self.template_data or not self.should_generate:
            return
            
        try:
            self.should_generate = False
            
            # بيانات تجريبية للمعاينة
            sample_data = {
                'student_name': 'أحمد محمد علي',
                'class_name': 'الصف السادس أ',
                'student_id': '123456',
                'school_name': 'مدرسة الأمل الابتدائية',
                'school_address': 'شارع الملك فهد، الرياض',
                'phone': '011-4567890',
                'email': 'info@amal-school.edu.sa',
                'academic_year': '2024-2025'
            }
            
            # إنشاء PDF للمعاينة (نستخدم القالب الافتراضي مؤقتاً)
            from core.pdf.student_id_generator import StudentIDGenerator
            
            pdf_path = self.temp_dir / f"live_preview_{datetime.now().strftime('%H%M%S')}.pdf"
            
            # تطبيق تغييرات القالب مؤقتاً
            self.apply_template_temporarily()
            
            # توليد PDF 
            generator = StudentIDGenerator()
            success = generator.generate_student_ids(
                students_data=[sample_data],
                output_path=str(pdf_path),
                school_name=sample_data.get('school_name', ''),
                custom_title="هوية طالب - معاينة"
            )
            
            if success and pdf_path.exists():
                self.pdf_generated.emit(str(pdf_path))
            else:
                self.error_occurred.emit("فشل في توليد PDF")
                
        except Exception as e:
            logging.error(f"خطأ في توليد PDF لحظي: {e}")
            self.error_occurred.emit(f"خطأ: {str(e)}")
    
    def apply_template_temporarily(self):
        """تطبيق تغييرات القالب مؤقتاً على TEMPLATE_ELEMENTS"""
        try:
            from templates.id_template import TEMPLATE_ELEMENTS
            
            # نطبق التغييرات مؤقتاً فقط
            for element_name, element_data in self.template_data.items():
                if element_name in TEMPLATE_ELEMENTS:
                    TEMPLATE_ELEMENTS[element_name].update(element_data)
                    
        except Exception as e:
            logging.error(f"خطأ في تطبيق القالب مؤقتاً: {e}")


class ColorButton(QPushButton):
    """زر لاختيار لون مع عرض اللون المختار"""
    
    color_changed = pyqtSignal(list)
    
    def __init__(self, initial_color=[0, 0, 0]):
        super().__init__()
        self.color = initial_color
        self.update_color_display()
        self.clicked.connect(self.choose_color)
    
    def update_color_display(self):
        """تحديث عرض اللون على الزر"""
        r, g, b = [int(c * 255) if c <= 1 else int(c) for c in self.color]
        self.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid black;")
        self.setText(f"RGB({r}, {g}, {b})")
    
    def choose_color(self):
        """فتح حوار اختيار اللون"""
        r, g, b = [int(c * 255) if c <= 1 else int(c) for c in self.color]
        color = QColorDialog.getColor(QColor(r, g, b), self)
        
        if color.isValid():
            self.color = [color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0]
            self.update_color_display()
            self.color_changed.emit(self.color)
    
    def set_color(self, color_list):
        """تعيين لون جديد"""
        self.color = color_list
        self.update_color_display()


class ElementEditor(QWidget):
    """محرر عنصر واحد من عناصر الهوية"""
    
    def __init__(self, element_name, element_config):
        super().__init__()
        self.element_name = element_name
        self.element_config = element_config.copy()
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة محرر العنصر"""
        layout = QVBoxLayout(self)
        
        # عنوان العنصر
        title = QLabel(f"إعدادات {self.element_name}")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # تجميع الإعدادات في مجموعات
        self.create_position_group(layout)
        self.create_appearance_group(layout)
        self.create_text_group(layout)
        
        layout.addStretch()
    
    def create_position_group(self, layout):
        """إنشاء مجموعة إعدادات الموقع والحجم"""
        group = QGroupBox("الموقع والحجم")
        form = QFormLayout(group)
        
        # الموقع X
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(0.0, 1.0)
        self.x_spin.setSingleStep(0.01)
        self.x_spin.setDecimals(2)
        self.x_spin.setValue(self.element_config.get('x', 0.5))
        form.addRow("موقع X (0-1):", self.x_spin)
        
        # الموقع Y
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(0.0, 1.0)
        self.y_spin.setSingleStep(0.01)
        self.y_spin.setDecimals(2)
        self.y_spin.setValue(self.element_config.get('y', 0.5))
        form.addRow("موقع Y (0-1):", self.y_spin)
        
        # العرض (إذا كان موجوداً)
        if 'width' in self.element_config:
            self.width_spin = QDoubleSpinBox()
            self.width_spin.setRange(0.01, 1.0)
            self.width_spin.setSingleStep(0.01)
            self.width_spin.setDecimals(2)
            self.width_spin.setValue(self.element_config.get('width', 0.2))
            form.addRow("العرض (0-1):", self.width_spin)
        
        # الارتفاع (إذا كان موجوداً)
        if 'height' in self.element_config:
            self.height_spin = QDoubleSpinBox()
            self.height_spin.setRange(0.01, 1.0)
            self.height_spin.setSingleStep(0.01)
            self.height_spin.setDecimals(2)
            self.height_spin.setValue(self.element_config.get('height', 0.1))
            form.addRow("الارتفاع (0-1):", self.height_spin)
        
        layout.addWidget(group)
    
    def create_appearance_group(self, layout):
        """إنشاء مجموعة إعدادات المظهر"""
        group = QGroupBox("المظهر")
        form = QFormLayout(group)
        
        # حجم الخط
        if 'font_size' in self.element_config:
            self.font_size_spin = QSpinBox()
            self.font_size_spin.setRange(4, 24)
            self.font_size_spin.setValue(self.element_config.get('font_size', 8))
            form.addRow("حجم الخط:", self.font_size_spin)
        
        # نوع الخط
        if 'font_name' in self.element_config:
            self.font_combo = QComboBox()
            fonts = ["Helvetica", "Helvetica-Bold", "Cairo", "Cairo-Bold", "Amiri", "Amiri-Bold"]
            self.font_combo.addItems(fonts)
            font_name = self.element_config.get('font_name', 'Helvetica')
            if font_name in fonts:
                self.font_combo.setCurrentText(font_name)
            form.addRow("نوع الخط:", self.font_combo)
        
        # المحاذاة
        if 'alignment' in self.element_config:
            self.alignment_combo = QComboBox()
            self.alignment_combo.addItems(["left", "center", "right"])
            self.alignment_combo.setCurrentText(self.element_config.get('alignment', 'right'))
            form.addRow("المحاذاة:", self.alignment_combo)
        
        # لون النص
        if 'color' in self.element_config:
            color_value = self.element_config.get('color', [0, 0, 0])
            if not isinstance(color_value, list):
                color_value = [0, 0, 0]  # افتراضي أسود
            self.text_color_btn = ColorButton(color_value)
            form.addRow("لون النص:", self.text_color_btn)
        
        # لون الحدود
        if 'border_color' in self.element_config:
            border_color = self.element_config.get('border_color', [0, 0, 0])
            if not isinstance(border_color, list):
                border_color = [0, 0, 0]
            self.border_color_btn = ColorButton(border_color)
            form.addRow("لون الحدود:", self.border_color_btn)
        
        # لون التعبئة
        if 'fill_color' in self.element_config:
            fill_color = self.element_config.get('fill_color', [1, 1, 1])
            if not isinstance(fill_color, list):
                fill_color = [1, 1, 1]
            self.fill_color_btn = ColorButton(fill_color)
            form.addRow("لون التعبئة:", self.fill_color_btn)
        
        # سمك الحدود
        if 'border_width' in self.element_config:
            self.border_width_spin = QDoubleSpinBox()
            self.border_width_spin.setRange(0.1, 5.0)
            self.border_width_spin.setSingleStep(0.1)
            self.border_width_spin.setDecimals(1)
            self.border_width_spin.setValue(self.element_config.get('border_width', 1.0))
            form.addRow("سمك الحدود:", self.border_width_spin)
        
        layout.addWidget(group)
    
    def create_text_group(self, layout):
        """إنشاء مجموعة إعدادات النص"""
        group = QGroupBox("النص")
        form = QFormLayout(group)
        
        # النص الثابت
        if 'text' in self.element_config:
            self.text_edit = QLineEdit()
            self.text_edit.setText(self.element_config.get('text', ''))
            form.addRow("النص:", self.text_edit)
        
        # التسمية
        if 'label' in self.element_config:
            self.label_edit = QLineEdit()
            self.label_edit.setText(self.element_config.get('label', ''))
            form.addRow("التسمية:", self.label_edit)
        
        # العرض الأقصى
        if 'max_width' in self.element_config:
            self.max_width_spin = QDoubleSpinBox()
            self.max_width_spin.setRange(0.1, 1.0)
            self.max_width_spin.setSingleStep(0.05)
            self.max_width_spin.setDecimals(2)
            self.max_width_spin.setValue(self.element_config.get('max_width', 1.0))
            form.addRow("العرض الأقصى (0-1):", self.max_width_spin)
        
        layout.addWidget(group)
    
    def get_config(self):
        """الحصول على إعدادات العنصر المحدثة"""
        config = self.element_config.copy()
        
        # تحديث الموقع والحجم
        config['x'] = self.x_spin.value()
        config['y'] = self.y_spin.value()
        
        if hasattr(self, 'width_spin'):
            config['width'] = self.width_spin.value()
        if hasattr(self, 'height_spin'):
            config['height'] = self.height_spin.value()
        
        # تحديث المظهر
        if hasattr(self, 'font_size_spin'):
            config['font_size'] = self.font_size_spin.value()
        if hasattr(self, 'font_combo'):
            config['font_name'] = self.font_combo.currentText()
        if hasattr(self, 'alignment_combo'):
            config['alignment'] = self.alignment_combo.currentText()
        
        # تحديث الألوان
        if hasattr(self, 'text_color_btn'):
            config['color'] = self.text_color_btn.color
        if hasattr(self, 'border_color_btn'):
            config['border_color'] = self.border_color_btn.color
        if hasattr(self, 'fill_color_btn'):
            config['fill_color'] = self.fill_color_btn.color
        
        # تحديث سمك الحدود
        if hasattr(self, 'border_width_spin'):
            config['border_width'] = self.border_width_spin.value()
        
        # تحديث النص
        if hasattr(self, 'text_edit'):
            config['text'] = self.text_edit.text()
        if hasattr(self, 'label_edit'):
            config['label'] = self.label_edit.text()
        if hasattr(self, 'max_width_spin'):
            config['max_width'] = self.max_width_spin.value()
        
        return config


class TemplateEditor(QDialog):
    """محرر قالب الهوية الرئيسي مع معاينة لحظية"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("محرر قالب الهوية - مع معاينة لحظية")
        self.setModal(True)
        self.resize(1200, 800)  # حجم أكبر للمعاينة
        
        self.elements = {}
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)
        
        self.setup_ui()
        self.load_current_template()
        
        # تأخير بسيط ثم معاينة أولية
        QTimer.singleShot(1000, self.initial_preview)
    
    def setup_ui(self):
        """إعداد واجهة المحرر مع المعاينة"""
        layout = QVBoxLayout(self)
        
        # شريط الأزرار العلوي
        self.create_toolbar(layout)
        
        # التقسيم الرئيسي: محرر + معاينة
        main_splitter = QSplitter(Qt.Horizontal)
        
        # الجانب الأيسر: محرر العناصر
        self.create_editor_panel(main_splitter)
        
        # الجانب الأيمن: معاينة لحظية
        self.create_preview_panel(main_splitter)
        
        # تحديد نسب العرض (40% محرر، 60% معاينة)
        main_splitter.setSizes([480, 720])
        layout.addWidget(main_splitter)
        
        # شريط الأزرار السفلي
        self.create_bottom_buttons(layout)
        
        # تطبيق الأنماط
        self.apply_modern_styles()
    
    def create_editor_panel(self, parent):
        """إنشاء لوحة المحرر"""
        editor_frame = QFrame()
        editor_frame.setObjectName("editorFrame")
        
        editor_layout = QVBoxLayout(editor_frame)
        
        # عنوان
        title_label = QLabel("إعدادات عناصر الهوية")
        title_label.setObjectName("panelTitle")
        editor_layout.addWidget(title_label)
        
        # التبويبات لتحرير العناصر
        self.tabs = QTabWidget()
        self.tabs.setObjectName("elementTabs")
        editor_layout.addWidget(self.tabs)
        
        parent.addWidget(editor_frame)
    
    def create_preview_panel(self, parent):
        """إنشاء لوحة المعاينة اللحظية للـ PDF"""
        preview_frame = QFrame()
        preview_frame.setObjectName("previewFrame")
        
        preview_layout = QVBoxLayout(preview_frame)
        
        # عنوان المعاينة
        preview_title = QLabel("📄 معاينة PDF لحظية")
        preview_title.setObjectName("panelTitle")
        preview_layout.addWidget(preview_title)
        
        # أزرار تحكم المعاينة
        controls_layout = QHBoxLayout()
        
        # مؤشر الحالة
        self.preview_status = QLabel("جاري التحضير...")
        self.preview_status.setObjectName("statusLabel")
        controls_layout.addWidget(self.preview_status)
        
        controls_layout.addStretch()
        
        self.auto_update_checkbox = QCheckBox("تحديث تلقائي")
        self.auto_update_checkbox.setObjectName("autoUpdateCheck")
        self.auto_update_checkbox.setChecked(True)
        self.auto_update_checkbox.stateChanged.connect(self.toggle_auto_update)
        controls_layout.addWidget(self.auto_update_checkbox)
        
        self.manual_refresh_btn = QPushButton("🔄 تحديث يدوي")
        self.manual_refresh_btn.setObjectName("refreshButton")
        self.manual_refresh_btn.clicked.connect(self.force_pdf_update)
        controls_layout.addWidget(self.manual_refresh_btn)
        
        preview_layout.addLayout(controls_layout)
        
        # شريط التقدم
        self.pdf_progress = QProgressBar()
        self.pdf_progress.setObjectName("pdfProgress")
        self.pdf_progress.setVisible(False)
        self.pdf_progress.setRange(0, 0)  # للدوران اللانهائي
        preview_layout.addWidget(self.pdf_progress)
        
        # عارض PDF الحقيقي
        self.pdf_preview_widget = QWebEngineView()
        self.pdf_preview_widget.setObjectName("pdfPreviewWidget")
        preview_layout.addWidget(self.pdf_preview_widget)
        
        parent.addWidget(preview_frame)
        
        # إعداد مولد PDF اللحظي
        self.setup_live_pdf_generator()
    
    def setup_live_pdf_generator(self):
        """إعداد مولد PDF اللحظي"""
        self.pdf_generator = LivePDFGenerator()
        self.pdf_generator.pdf_generated.connect(self.on_pdf_ready)
        self.pdf_generator.error_occurred.connect(self.on_pdf_error)
        
        # تايمر للتحديث المؤجل
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.trigger_pdf_generation)
        
        # متغيرات التحكم
        self.auto_update_enabled = True
        self.current_pdf_path = None
        
    def on_pdf_ready(self, pdf_path):
        """عند اكتمال توليد PDF"""
        try:
            self.current_pdf_path = pdf_path
            self.pdf_progress.setVisible(False)
            self.preview_status.setText("✅ PDF جاهز")
            
            # تحميل PDF في العارض
            import urllib.parse
            file_path = pdf_path.replace("\\", "/")
            if not file_path.startswith("/"):
                file_path = "/" + file_path
            file_url = f"file://{file_path}"
            
            self.pdf_preview_widget.load(QUrl(file_url))
            
        except Exception as e:
            logging.error(f"خطأ في عرض PDF: {e}")
            self.preview_status.setText(f"❌ خطأ في العرض: {str(e)[:30]}...")
    
    def on_pdf_error(self, error_msg):
        """عند حدوث خطأ في توليد PDF"""
        self.pdf_progress.setVisible(False)
        self.preview_status.setText(f"❌ {error_msg}")
        logging.error(f"خطأ في توليد PDF: {error_msg}")
    
    def toggle_auto_update(self, state):
        """تبديل التحديث التلقائي"""
        self.auto_update_enabled = bool(state)
        if self.auto_update_enabled:
            self.schedule_pdf_update()
    
    def force_pdf_update(self):
        """فرض تحديث PDF يدوياً"""
        self.schedule_pdf_update()
    
    def schedule_pdf_update(self):
        """جدولة تحديث PDF مع تأخير"""
        if not self.auto_update_enabled:
            return
            
        self.update_timer.stop()
        self.update_timer.start(1000)  # تأخير ثانية واحدة
        
        self.pdf_progress.setVisible(True)
        self.preview_status.setText("⏳ جاري التحديث...")
    
    def trigger_pdf_generation(self):
        """تشغيل توليد PDF"""
        try:
            template_data = self.get_current_template_data()
            
            if not self.pdf_generator.isRunning():
                self.pdf_generator.set_template_data(template_data)
                if not self.pdf_generator.isRunning():
                    self.pdf_generator.start()
            else:
                # إذا كان يعمل، قم بتحديث البيانات فقط
                self.pdf_generator.set_template_data(template_data)
                
        except Exception as e:
            logging.error(f"خطأ في تشغيل توليد PDF: {e}")
            self.on_pdf_error(f"خطأ في التشغيل: {str(e)}")
    
    def get_current_template_data(self):
        """الحصول على بيانات القالب الحالية"""
        template_data = {}
        
        # جمع البيانات من جميع محررات العناصر
        for element_name, editor in self.elements.items():
            try:
                element_data = editor.get_config()
                template_data[element_name] = element_data
            except Exception as e:
                logging.error(f"خطأ في الحصول على بيانات العنصر {element_name}: {e}")
                continue
        
        return template_data
    
    def initial_preview(self):
        """معاينة أولية بعد تحميل القالب"""
        try:
            self.preview_status.setText("⏳ إنشاء معاينة أولية...")
            self.force_pdf_update()
        except Exception as e:
            logging.error(f"خطأ في المعاينة الأولية: {e}")
            self.preview_status.setText("❌ فشل في المعاينة الأولية")
    
    def apply_modern_styles(self):
        """تطبيق أنماط عصرية"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            #panelTitle {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-bottom: 2px solid #3498db;
                margin-bottom: 10px;
            }
            
            #editorFrame, #previewFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin: 5px;
            }
            
            #elementTabs::pane {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
            }
            
            #elementTabs::tab-bar {
                alignment: center;
            }
            
            #elementTabs QTabBar::tab {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            
            #elementTabs QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
                border-bottom: none;
            }
            
            #elementTabs QTabBar::tab:hover {
                background-color: #5dade2;
                color: white;
            }
            
            #controlButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            
            #controlButton:hover {
                background-color: #7f8c8d;
            }
            
            #primaryButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 120px;
            }
            
            #primaryButton:hover {
                background-color: #2980b9;
            }
            
            #previewWebView {
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                background-color: white;
            }
            
            #pdfPreviewWidget {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: white;
            }
            
            #statusLabel {
                color: #7f8c8d;
                font-size: 12px;
                font-weight: normal;
                padding: 5px;
            }
            
            #autoUpdateCheck {
                font-size: 12px;
                color: #2c3e50;
            }
            
            #autoUpdateCheck::indicator:checked {
                background-color: #27ae60;
                border: 2px solid #27ae60;
            }
            
            #refreshButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            
            #refreshButton:hover {
                background-color: #e67e22;
            }
            
            #pdfProgress {
                border: 1px solid #3498db;
                border-radius: 4px;
                text-align: center;
                background-color: #ecf0f1;
            }
            
            #pdfProgress::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ecf0f1;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #fdfdfd;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
                font-size: 14px;
            }
            
            QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            
            QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
        """)
    
    def connect_element_changes(self, editor):
        """ربط تغييرات العنصر بالمعاينة اللحظية"""
        # ربط جميع العناصر القابلة للتغيير
        if hasattr(editor, 'x_spin'):
            editor.x_spin.valueChanged.connect(self.schedule_preview_update)
        if hasattr(editor, 'y_spin'):
            editor.y_spin.valueChanged.connect(self.schedule_preview_update)
        if hasattr(editor, 'width_spin'):
            editor.width_spin.valueChanged.connect(self.schedule_preview_update)
        if hasattr(editor, 'height_spin'):
            editor.height_spin.valueChanged.connect(self.schedule_preview_update)
        if hasattr(editor, 'font_size_spin'):
            editor.font_size_spin.valueChanged.connect(self.schedule_preview_update)
        if hasattr(editor, 'font_combo'):
            editor.font_combo.currentTextChanged.connect(self.schedule_preview_update)
        if hasattr(editor, 'alignment_combo'):
            editor.alignment_combo.currentTextChanged.connect(self.schedule_preview_update)
        if hasattr(editor, 'text_edit'):
            editor.text_edit.textChanged.connect(self.schedule_preview_update)
        if hasattr(editor, 'label_edit'):
            editor.label_edit.textChanged.connect(self.schedule_preview_update)
        if hasattr(editor, 'text_color_btn'):
            editor.text_color_btn.color_changed.connect(lambda: self.schedule_preview_update())
        if hasattr(editor, 'border_color_btn'):
            editor.border_color_btn.color_changed.connect(lambda: self.schedule_preview_update())
        if hasattr(editor, 'fill_color_btn'):
            editor.fill_color_btn.color_changed.connect(lambda: self.schedule_preview_update())
    
    def schedule_preview_update(self):
        """جدولة تحديث المعاينة PDF (مع تأخير لتجنب التحديث المستمر)"""
        if hasattr(self, 'auto_update_enabled') and self.auto_update_enabled:
            self.schedule_pdf_update()
        # إذا كان التحديث التلقائي مُعطلاً، لا نفعل شيئاً
    
    def update_preview(self):
        """تحديث المعاينة PDF اللحظية"""
        try:
            # إذا كان التحديث التلقائي مفعل، استخدم الجدولة
            if hasattr(self, 'auto_update_enabled') and self.auto_update_enabled:
                self.schedule_pdf_update()
            else:
                # تحديث فوري للتحديث اليدوي
                self.trigger_pdf_generation()
                
        except Exception as e:
            logging.error(f"خطأ في تحديث المعاينة: {e}")
            if hasattr(self, 'preview_status'):
                self.preview_status.setText(f"❌ خطأ: {str(e)[:30]}...")
    
    def apply_changes_to_preview(self):
        """تطبيق التغييرات على القالب للمعاينة فقط"""
        try:
            from templates.id_template import TEMPLATE_ELEMENTS
            
            # تطبيق التغييرات مؤقتاً للمعاينة
            for element_name, editor in self.elements.items():
                if element_name in TEMPLATE_ELEMENTS:
                    TEMPLATE_ELEMENTS[element_name].update(editor.get_config())
            
        except Exception as e:
            logging.error(f"خطأ في تطبيق التغييرات للمعاينة: {e}")
    
    def generate_preview_html(self):
        """إنشاء HTML للمعاينة"""
        try:
            # بيانات نموذجية للمعاينة
            sample_data = {
                'name': 'أحمد محمد علي السامرائي',
                'grade': 'الصف الثالث الابتدائي',
                'school_name': 'مدرسة النموذج الأهلية',
                'birthdate': '15/03/2010',
                'id': 'ST2025001'
            }
            
            from templates.id_template import TEMPLATE_ELEMENTS
            
            # إنشاء HTML يحاكي تصميم الهوية
            html = f"""
            <!DOCTYPE html>
            <html dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>معاينة هوية الطالب</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        background-color: #f5f5f5;
                        direction: rtl;
                    }}
                    .id-card {{
                        width: 300px;
                        height: 189px;
                        background-color: white;
                        border: 2px solid #333;
                        position: relative;
                        margin: 20px auto;
                        border-radius: 12px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .preview-info {{
                        text-align: center;
                        color: #666;
                        font-size: 14px;
                        margin-bottom: 20px;
                        background-color: white;
                        padding: 10px;
                        border-radius: 6px;
                        border: 1px solid #ddd;
                    }}
                    .element {{
                        position: absolute;
                        font-family: Arial, sans-serif;
                    }}
                    .photo-box {{
                        background-color: #f8f8f8;
                        border: 2px solid #ddd;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #999;
                        font-size: 12px;
                        border-radius: 4px;
                    }}
                    .qr-box {{
                        background-color: white;
                        border: 1px solid #ccc;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #999;
                        font-size: 10px;
                        border-radius: 4px;
                    }}
                    .birth-date-box {{
                        background-color: #fafafa;
                        border: 1px solid #ddd;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #999;
                        font-size: 12px;
                        border-radius: 4px;
                    }}
                    .line {{
                        background-color: #3498db;
                        height: 2px;
                    }}
                </style>
            </head>
            <body>
                <div class="preview-info">
                    معاينة لحظية لهوية الطالب - يتم التحديث تلقائياً عند التعديل
                </div>
                <div class="id-card">
            """
            
            # إضافة العناصر
            for element_name, config in TEMPLATE_ELEMENTS.items():
                x_percent = config.get('x', 0) * 100
                y_percent = (1 - config.get('y', 0)) * 100  # عكس Y للHTML
                
                if element_name == "photo_box":
                    width = config.get('width', 0.3) * 300
                    height = config.get('height', 0.5) * 189
                    html += f"""
                    <div class="element photo-box" style="
                        right: {x_percent}%; 
                        top: {y_percent - (height/189*100)}%; 
                        width: {width}px; 
                        height: {height}px;
                    ">
                        {config.get('label', 'صورة الطالب')}
                    </div>
                    """
                
                elif element_name == "qr_box":
                    width = config.get('width', 0.2) * 300
                    height = config.get('height', 0.25) * 189
                    html += f"""
                    <div class="element qr-box" style="
                        right: {x_percent}%; 
                        top: {y_percent - (height/189*100)}%; 
                        width: {width}px; 
                        height: {height}px;
                    ">
                        {config.get('label', 'QR Code')}
                    </div>
                    """
                
                elif element_name == "birth_date_box":
                    width = config.get('width', 0.6) * 300
                    height = config.get('height', 0.25) * 189
                    birthdate = sample_data.get('birthdate', '_____ / _____ / _________')
                    html += f"""
                    <div class="element birth-date-box" style="
                        right: {x_percent}%; 
                        top: {y_percent - (height/189*100)}%; 
                        width: {width}px; 
                        height: {height}px;
                    ">
                        {birthdate}
                    </div>
                    """
                
                elif config.get('type') == 'line' or element_name.endswith('_line'):
                    width = config.get('width', 0.9) * 300
                    html += f"""
                    <div class="element line" style="
                        right: {x_percent}%; 
                        top: {y_percent}%; 
                        width: {width}px;
                    "></div>
                    """
                
                elif 'text' in config and config.get('text'):
                    text = config['text']
                    font_size = config.get('font_size', 12)
                    color = config.get('color', [0, 0, 0])
                    color_rgb = f"rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)})"
                    font_weight = 'bold' if 'Bold' in config.get('font_name', '') else 'normal'
                    
                    html += f"""
                    <div class="element" style="
                        right: {x_percent}%; 
                        top: {y_percent}%; 
                        font-size: {font_size}px;
                        color: {color_rgb};
                        font-weight: {font_weight};
                        text-align: right;
                    ">
                        {text}
                    </div>
                    """
                
                elif element_name in ['student_name', 'student_grade', 'id_number']:
                    # عرض البيانات الفعلية
                    text = ""
                    if element_name == 'student_name':
                        text = sample_data['name']
                    elif element_name == 'student_grade':
                        text = sample_data['grade']
                    elif element_name == 'id_number':
                        text = f"رقم الطالب: {sample_data['id']}"
                    
                    font_size = config.get('font_size', 12)
                    color = config.get('color', [0, 0, 0])
                    color_rgb = f"rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)})"
                    font_weight = 'bold' if 'Bold' in config.get('font_name', '') else 'normal'
                    
                    html += f"""
                    <div class="element" style="
                        right: {x_percent}%; 
                        top: {y_percent}%; 
                        font-size: {font_size}px;
                        color: {color_rgb};
                        font-weight: {font_weight};
                        text-align: right;
                    ">
                        {text}
                    </div>
                    """
                
                elif element_name == 'school_name':
                    text = sample_data['school_name']
                    font_size = config.get('font_size', 12)
                    color = config.get('color', [0, 0, 0])
                    color_rgb = f"rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)})"
                    font_weight = 'bold' if 'Bold' in config.get('font_name', '') else 'normal'
                    
                    html += f"""
                    <div class="element" style="
                        right: {x_percent}%; 
                        top: {y_percent}%; 
                        font-size: {font_size}px;
                        color: {color_rgb};
                        font-weight: {font_weight};
                        text-align: right;
                    ">
                        {text}
                    </div>
                    """
            
            html += """
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء HTML للمعاينة: {e}")
            return f"<html><body><h2>خطأ في المعاينة: {str(e)}</h2></body></html>"
    
    def zoom_in_preview(self):
        """تكبير المعاينة"""
        current_zoom = self.preview_web_view.zoomFactor()
        self.preview_web_view.setZoomFactor(current_zoom * 1.2)
    
    def zoom_out_preview(self):
        """تصغير المعاينة"""
        current_zoom = self.preview_web_view.zoomFactor()
        self.preview_web_view.setZoomFactor(current_zoom / 1.2)
    
    def fit_preview(self):
        """ملء الشاشة"""
        self.preview_web_view.setZoomFactor(1.0)
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات"""
        toolbar = QHBoxLayout()
        
        # زر تحميل قالب
        load_btn = QPushButton("📁 تحميل قالب")
        load_btn.setObjectName("controlButton")
        load_btn.clicked.connect(self.load_template)
        toolbar.addWidget(load_btn)
        
        # زر حفظ قالب
        save_btn = QPushButton("💾 حفظ القالب")
        save_btn.setObjectName("controlButton")
        save_btn.clicked.connect(self.save_template)
        toolbar.addWidget(save_btn)
        
        # زر تصدير PDF
        export_pdf_btn = QPushButton("📄 تصدير PDF")
        export_pdf_btn.setObjectName("controlButton")
        export_pdf_btn.clicked.connect(self.export_pdf_template)
        toolbar.addWidget(export_pdf_btn)
        
        # زر إعادة التعيين
        reset_btn = QPushButton("🔄 إعادة التعيين")
        reset_btn.setObjectName("controlButton")
        reset_btn.clicked.connect(self.reset_template)
        toolbar.addWidget(reset_btn)
        
        toolbar.addStretch()
        
        # زر معاينة PDF
        preview_btn = QPushButton("👁️ معاينة PDF")
        preview_btn.setObjectName("primaryButton")
        preview_btn.clicked.connect(self.preview_template)
        toolbar.addWidget(preview_btn)
        
        layout.addLayout(toolbar)
    
    def create_bottom_buttons(self, layout):
        """إنشاء أزرار أسفل النافذة"""
        buttons = QHBoxLayout()
        
        buttons.addStretch()
        
        # زر تطبيق
        apply_btn = QPushButton("تطبيق")
        apply_btn.clicked.connect(self.apply_changes)
        buttons.addWidget(apply_btn)
        
        # زر إلغاء
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        # زر موافق
        ok_btn = QPushButton("موافق")
        ok_btn.clicked.connect(self.accept_changes)
        buttons.addWidget(ok_btn)
        
        layout.addLayout(buttons)
    
    def load_current_template(self):
        """تحميل القالب الحالي مع ربط التغييرات"""
        self.tabs.clear()
        self.elements.clear()
        
        for element_name, element_config in TEMPLATE_ELEMENTS.items():
            editor = ElementEditor(element_name, element_config)
            
            # ربط التغييرات بالمعاينة اللحظية
            self.connect_element_changes(editor)
            
            # إنشاء منطقة تمرير للمحرر
            scroll = QScrollArea()
            scroll.setWidget(editor)
            scroll.setWidgetResizable(True)
            
            # ترجمة أسماء العناصر للعربية
            tab_name = self.get_element_display_name(element_name)
            self.tabs.addTab(scroll, tab_name)
            self.elements[element_name] = editor
    
    def get_element_display_name(self, element_name):
        """الحصول على الاسم المعروض للعنصر بالعربية"""
        display_names = {
            'id_title': 'عنوان الهوية',
            'school_name': 'اسم المدرسة',
            'student_name': 'اسم الطالب',
            'student_name_label': 'تسمية اسم الطالب',
            'student_grade': 'الصف الدراسي',
            'student_grade_label': 'تسمية الصف',
            'academic_year': 'العام الدراسي',
            'academic_year_label': 'تسمية العام الدراسي',
            'photo_box': 'مربع الصورة',
            'qr_box': 'مربع QR',
            'birth_date_box': 'تاريخ الميلاد',
            'birth_date_label': 'تسمية تاريخ الميلاد',
            'id_number': 'رقم الطالب',
            'header_line': 'الخط العلوي',
            'footer_line': 'الخط السفلي'
        }
        return display_names.get(element_name, element_name)
    
    def load_template(self):
        """تحميل قالب من ملف"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "تحميل قالب",
            "",
            "ملفات JSON (*.json)"
        )
        
        if file_path:
            try:
                success = load_template_from_json(file_path)
                if success:
                    self.load_current_template()
                    QMessageBox.information(self, "نجح", "تم تحميل القالب بنجاح")
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في تحميل القالب")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"خطأ في تحميل القالب:\n{str(e)}")
    
    def save_template(self):
        """حفظ القالب إلى ملف"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "حفظ القالب",
            f"id_template_custom.json",
            "ملفات JSON (*.json)"
        )
        
        if file_path:
            try:
                # تطبيق التغييرات أولاً
                self.apply_changes()
                
                # حفظ القالب
                save_template_as_json(file_path)
                QMessageBox.information(self, "نجح", f"تم حفظ القالب في:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"خطأ في حفظ القالب:\n{str(e)}")
    
    def reset_template(self):
        """إعادة تعيين القالب للإعدادات الافتراضية"""
        reply = QMessageBox.question(
            self,
            "تأكيد",
            "هل أنت متأكد من إعادة تعيين القالب للإعدادات الافتراضية؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                from templates.id_template import ensure_default_template
                ensure_default_template()
                self.load_current_template()
                QMessageBox.information(self, "نجح", "تم إعادة تعيين القالب")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"خطأ في إعادة التعيين:\n{str(e)}")
    
    def preview_template(self):
        """معاينة القالب في PDF"""
        try:
            # تطبيق التغييرات أولاً
            self.apply_changes()
            
            # إنشاء معاينة PDF
            from core.pdf.student_id_generator import generate_student_ids_pdf
            
            sample_data = [{
                'name': 'أحمد محمد علي السامرائي',
                'grade': 'الصف الثالث الابتدائي',
                'school_name': 'مدرسة النموذج الأهلية',
                'birthdate': '15/03/2010',
                'id': 'ST2025001'
            }]
            
            temp_dir = Path.home() / "Documents"
            preview_path = temp_dir / "preview_template.pdf"
            
            success = generate_student_ids_pdf(
                sample_data,
                str(preview_path),
                "مدرسة النموذج الأهلية",
                "هوية طالب"
            )
            
            if success and preview_path.exists():
                import subprocess
                subprocess.Popen([str(preview_path)], shell=True)
                QMessageBox.information(self, "معاينة", "تم إنشاء معاينة PDF وسيتم فتحها الآن")
            else:
                QMessageBox.warning(self, "خطأ", "فشل في إنشاء المعاينة")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في المعاينة:\n{str(e)}")
    
    def export_pdf_template(self):
        """تصدير القالب كـ PDF للطباعة"""
        try:
            # تطبيق التغييرات أولاً
            self.apply_changes()
            
            # اختيار مسار الحفظ
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "تصدير القالب كـ PDF",
                f"student_id_template.pdf",
                "ملفات PDF (*.pdf)"
            )
            
            if file_path:
                from core.pdf.student_id_generator import generate_student_ids_pdf
                
                # إنشاء عدة هويات نموذجية
                sample_data = [
                    {
                        'name': 'أحمد محمد علي',
                        'grade': 'الصف الثالث الابتدائي',
                        'school_name': 'مدرسة النموذج الأهلية',
                        'birthdate': '15/03/2010',
                        'id': 'ST2025001'
                    },
                    {
                        'name': 'فاطمة أحمد حسن',
                        'grade': 'الصف الرابع الابتدائي',
                        'school_name': 'مدرسة النموذج الأهلية',
                        'birthdate': '22/07/2009',
                        'id': 'ST2025002'
                    },
                    {
                        'name': 'محمد عبدالله سالم',
                        'grade': 'الصف الخامس الابتدائي',
                        'school_name': 'مدرسة النموذج الأهلية',
                        'birthdate': '10/11/2008',
                        'id': 'ST2025003'
                    }
                ]
                
                success = generate_student_ids_pdf(
                    sample_data,
                    file_path,
                    "مدرسة النموذج الأهلية",
                    "هوية طالب"
                )
                
                if success:
                    QMessageBox.information(self, "نجح", f"تم تصدير القالب بنجاح:\n{file_path}")
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في تصدير القالب")
                    
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في تصدير القالب:\n{str(e)}")
    
    def apply_changes(self):
        """تطبيق التغييرات على القالب"""
        try:
            global TEMPLATE_ELEMENTS
            
            new_elements = {}
            for element_name, editor in self.elements.items():
                new_elements[element_name] = editor.get_config()
            
            TEMPLATE_ELEMENTS.clear()
            TEMPLATE_ELEMENTS.update(new_elements)
            
        except Exception as e:
            logging.error(f"خطأ في تطبيق التغييرات: {e}")
            raise e
    
    def accept_changes(self):
        """قبول التغييرات وإغلاق النافذة"""
        try:
            self.apply_changes()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في تطبيق التغييرات:\n{str(e)}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # تطبيق نمط عربي
    app.setLayoutDirection(Qt.RightToLeft)
    
    editor = TemplateEditor()
    editor.show()
    
    sys.exit(app.exec_())
