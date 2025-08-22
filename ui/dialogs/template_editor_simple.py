#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محرر قالب الهوية المبسط - بدون معاينة PDF
"""

import sys
import json
import logging
import tempfile
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QWidget, QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
    QLineEdit, QColorDialog, QComboBox, QCheckBox, QGroupBox,
    QScrollArea, QTextEdit, QFileDialog, QMessageBox, QSplitter,
    QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont

# إضافة مسار المشروع
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from templates.id_template import (
    TEMPLATE_ELEMENTS, save_template_as_json, load_template_from_json,
    ID_WIDTH, ID_HEIGHT, GRID_COLS, GRID_ROWS
)

class ColorButton(QPushButton):
    """زر اختيار اللون"""
    
    def __init__(self, initial_color="#000000"):
        super().__init__()
        self.current_color = initial_color
        self.update_button_color()
        self.clicked.connect(self.choose_color)
    
    def update_button_color(self):
        """تحديث لون الزر"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                border: 2px solid #333;
                border-radius: 6px;
                min-width: 60px;
                min-height: 30px;
            }}
        """)
        self.setText(self.current_color)
    
    def choose_color(self):
        """فتح نافذة اختيار اللون"""
        color = QColorDialog.getColor(QColor(self.current_color), self)
        if color.isValid():
            self.current_color = color.name()
            self.update_button_color()
    
    def get_color(self):
        """الحصول على اللون الحالي"""
        return self.current_color
    
    def set_color(self, color):
        """تعيين لون جديد"""
        self.current_color = color
        self.update_button_color()

class ElementEditor(QWidget):
    """محرر عنصر من عناصر الهوية"""
    
    def __init__(self, element_name, element_config):
        super().__init__()
        self.element_name = element_name
        self.element_config = element_config.copy()
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """إعداد واجهة المحرر"""
        layout = QFormLayout(self)
        
        # الموقع
        position_group = QGroupBox("الموقع والحجم")
        position_layout = QFormLayout(position_group)
        
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 300)
        self.x_spin.setSuffix(" مم")
        position_layout.addRow("الموقع الأفقي (X):", self.x_spin)
        
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 200)
        self.y_spin.setSuffix(" مم")
        position_layout.addRow("الموقع العمودي (Y):", self.y_spin)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 200)
        self.width_spin.setSuffix(" مم")
        position_layout.addRow("العرض:", self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 100)
        self.height_spin.setSuffix(" مم")
        position_layout.addRow("الارتفاع:", self.height_spin)
        
        layout.addRow(position_group)
        
        # النص (إذا كان العنصر نصي)
        if self.element_config.get('type') == 'text':
            text_group = QGroupBox("إعدادات النص")
            text_layout = QFormLayout(text_group)
            
            self.font_size_spin = QSpinBox()
            self.font_size_spin.setRange(6, 72)
            self.font_size_spin.setSuffix(" نقطة")
            text_layout.addRow("حجم الخط:", self.font_size_spin)
            
            self.font_combo = QComboBox()
            self.font_combo.addItems([
                "Arial", "Times New Roman", "Calibri", "Tahoma",
                "Amiri", "Cairo", "Tajawal"
            ])
            text_layout.addRow("نوع الخط:", self.font_combo)
            
            self.color_button = ColorButton()
            text_layout.addRow("لون النص:", self.color_button)
            
            self.alignment_combo = QComboBox()
            self.alignment_combo.addItems(["يسار", "وسط", "يمين"])
            text_layout.addRow("المحاذاة:", self.alignment_combo)
            
            layout.addRow(text_group)
        
        # الحدود والتأثيرات
        border_group = QGroupBox("الحدود والخلفية")
        border_layout = QFormLayout(border_group)
        
        self.border_width_spin = QDoubleSpinBox()
        self.border_width_spin.setRange(0, 10)
        self.border_width_spin.setSingleStep(0.5)
        self.border_width_spin.setSuffix(" نقطة")
        border_layout.addRow("سمك الحدود:", self.border_width_spin)
        
        self.border_color_button = ColorButton("#000000")
        border_layout.addRow("لون الحدود:", self.border_color_button)
        
        self.background_color_button = ColorButton("#FFFFFF")
        border_layout.addRow("لون الخلفية:", self.background_color_button)
        
        layout.addRow(border_group)
        
        # إعدادات خاصة حسب نوع العنصر
        if self.element_name == 'photo_box':
            photo_group = QGroupBox("إعدادات الصورة")
            photo_layout = QFormLayout(photo_group)
            
            self.photo_border_radius_spin = QSpinBox()
            self.photo_border_radius_spin.setRange(0, 50)
            self.photo_border_radius_spin.setSuffix(" نقطة")
            photo_layout.addRow("انحناء الزوايا:", self.photo_border_radius_spin)
            
            layout.addRow(photo_group)
    
    def load_config(self):
        """تحميل الإعدادات الحالية"""
        self.x_spin.setValue(self.element_config.get('x', 0))
        self.y_spin.setValue(self.element_config.get('y', 0))
        self.width_spin.setValue(self.element_config.get('width', 20))
        self.height_spin.setValue(self.element_config.get('height', 10))
        
        if hasattr(self, 'font_size_spin'):
            self.font_size_spin.setValue(self.element_config.get('font_size', 12))
        
        if hasattr(self, 'font_combo'):
            font = self.element_config.get('font', 'Arial')
            index = self.font_combo.findText(font)
            if index >= 0:
                self.font_combo.setCurrentIndex(index)
        
        if hasattr(self, 'color_button'):
            self.color_button.set_color(self.element_config.get('color', '#000000'))
        
        if hasattr(self, 'alignment_combo'):
            alignment = self.element_config.get('alignment', 'center')
            alignment_map = {'left': 0, 'center': 1, 'right': 2}
            self.alignment_combo.setCurrentIndex(alignment_map.get(alignment, 1))
        
        self.border_width_spin.setValue(self.element_config.get('border_width', 1))
        self.border_color_button.set_color(self.element_config.get('border_color', '#000000'))
        self.background_color_button.set_color(self.element_config.get('background_color', '#FFFFFF'))
        
        if hasattr(self, 'photo_border_radius_spin'):
            self.photo_border_radius_spin.setValue(self.element_config.get('border_radius', 5))
    
    def get_config(self):
        """الحصول على الإعدادات الحالية"""
        config = {
            'x': self.x_spin.value(),
            'y': self.y_spin.value(),
            'width': self.width_spin.value(),
            'height': self.height_spin.value(),
            'border_width': self.border_width_spin.value(),
            'border_color': self.border_color_button.get_color(),
            'background_color': self.background_color_button.get_color(),
        }
        
        if hasattr(self, 'font_size_spin'):
            config['font_size'] = self.font_size_spin.value()
        
        if hasattr(self, 'font_combo'):
            config['font'] = self.font_combo.currentText()
        
        if hasattr(self, 'color_button'):
            config['color'] = self.color_button.get_color()
        
        if hasattr(self, 'alignment_combo'):
            alignment_map = {0: 'left', 1: 'center', 2: 'right'}
            config['alignment'] = alignment_map[self.alignment_combo.currentIndex()]
        
        if hasattr(self, 'photo_border_radius_spin'):
            config['border_radius'] = self.photo_border_radius_spin.value()
        
        return config

class SimpleTemplateEditor(QDialog):
    """محرر قالب الهوية المبسط - بدون معاينة PDF"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("محرر قالب الهوية - إصدار مبسط")
        self.setModal(True)
        self.resize(800, 600)
        
        self.elements = {}
        self.setup_ui()
        self.load_current_template()
    
    def setup_ui(self):
        """إعداد واجهة المحرر"""
        layout = QVBoxLayout(self)
        
        # شريط الأزرار العلوي
        self.create_toolbar(layout)
        
        # محرر العناصر
        self.create_editor_panel(layout)
        
        # شريط الأزرار السفلي
        self.create_bottom_buttons(layout)
        
        # تطبيق الأنماط
        self.apply_styles()
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات"""
        toolbar_layout = QHBoxLayout()
        
        info_label = QLabel("📝 محرر قالب الهوية (إصدار مبسط)")
        info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        toolbar_layout.addWidget(info_label)
        
        toolbar_layout.addStretch()
        
        # زر معاينة PDF
        preview_btn = QPushButton("👁️ معاينة PDF")
        preview_btn.setObjectName("previewButton")
        preview_btn.clicked.connect(self.generate_preview_pdf)
        toolbar_layout.addWidget(preview_btn)
        
        layout.addLayout(toolbar_layout)
    
    def create_editor_panel(self, layout):
        """إنشاء لوحة المحرر"""
        # التبويبات لتحرير العناصر
        self.tabs = QTabWidget()
        self.tabs.setObjectName("elementTabs")
        layout.addWidget(self.tabs)
    
    def create_bottom_buttons(self, layout):
        """إنشاء الأزرار السفلية"""
        buttons_layout = QHBoxLayout()
        
        # زر حفظ
        save_btn = QPushButton("💾 حفظ القالب")
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(self.save_template)
        buttons_layout.addWidget(save_btn)
        
        # زر استعادة افتراضي
        reset_btn = QPushButton("🔄 استعادة افتراضي")
        reset_btn.setObjectName("resetButton")
        reset_btn.clicked.connect(self.reset_template)
        buttons_layout.addWidget(reset_btn)
        
        buttons_layout.addStretch()
        
        # زر إلغاء
        cancel_btn = QPushButton("❌ إلغاء")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        # زر موافق
        ok_btn = QPushButton("✅ موافق")
        ok_btn.setObjectName("okButton")
        ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_btn)
        
        layout.addLayout(buttons_layout)
    
    def apply_styles(self):
        """تطبيق الأنماط"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            #elementTabs::pane {
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                background-color: white;
                margin-top: 10px;
            }
            
            #elementTabs::tab-bar {
                alignment: right;
            }
            
            #elementTabs QTabBar::tab {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
                color: #2c3e50;
            }
            
            #elementTabs QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            
            #previewButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 120px;
            }
            
            #previewButton:hover {
                background-color: #8e44ad;
            }
            
            #saveButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 120px;
            }
            
            #saveButton:hover {
                background-color: #229954;
            }
            
            #resetButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 120px;
            }
            
            #resetButton:hover {
                background-color: #e67e22;
            }
            
            #cancelButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 120px;
            }
            
            #cancelButton:hover {
                background-color: #c0392b;
            }
            
            #okButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 120px;
            }
            
            #okButton:hover {
                background-color: #2980b9;
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
    
    def load_current_template(self):
        """تحميل القالب الحالي"""
        self.tabs.clear()
        self.elements.clear()
        
        for element_name, element_config in TEMPLATE_ELEMENTS.items():
            editor = ElementEditor(element_name, element_config)
            
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
            'header_line': 'خط الرأس',
            'photo_box': 'مربع الصورة',
            'student_name': 'اسم الطالب',
            'student_grade': 'الصف الدراسي',
            'academic_year': 'العام الدراسي',
            'birth_date_box': 'تاريخ الميلاد',
            'qr_box': 'رمز QR',
            'id_number': 'رقم الهوية',
        }
        return display_names.get(element_name, element_name)
    
    def save_template(self):
        """حفظ القالب"""
        try:
            # جمع الإعدادات من جميع المحررات
            for element_name, editor in self.elements.items():
                new_config = editor.get_config()
                TEMPLATE_ELEMENTS[element_name].update(new_config)
            
            # حفظ إلى ملف
            save_template_as_json(TEMPLATE_ELEMENTS, 'templates/id_template_updated.json')
            
            QMessageBox.information(self, "تم الحفظ", "تم حفظ القالب بنجاح!")
            logging.info("تم حفظ قالب الهوية المحدث")
            
        except Exception as e:
            logging.error(f"خطأ في حفظ القالب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ القالب:\n{str(e)}")
    
    def reset_template(self):
        """إعادة تعيين القالب للإعدادات الافتراضية"""
        reply = QMessageBox.question(
            self, "إعادة تعيين", 
            "هل أنت متأكد من إعادة تعيين جميع الإعدادات إلى القيم الافتراضية؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # إعادة تحميل القالب الافتراضي
            self.load_current_template()
            QMessageBox.information(self, "تم الإعادة", "تم إعادة تعيين القالب للإعدادات الافتراضية")
    
    def generate_preview_pdf(self):
        """إنشاء معاينة PDF"""
        try:
            # تطبيق التغييرات الحالية
            for element_name, editor in self.elements.items():
                new_config = editor.get_config()
                TEMPLATE_ELEMENTS[element_name].update(new_config)
            
            # بيانات تجريبية
            sample_data = {
                'student_name': 'أحمد محمد علي',
                'class_name': 'الصف السادس أ',
                'student_id': '123456',
                'school_name': 'مدرسة الأمل الابتدائية'
            }
            
            # إنشاء PDF
            from core.pdf.student_id_generator import StudentIDGenerator
            
            preview_path = Path(tempfile.gettempdir()) / "template_preview.pdf"
            
            generator = StudentIDGenerator()
            success = generator.generate_student_ids(
                students_data=[sample_data],
                output_path=str(preview_path),
                school_name=sample_data['school_name'],
                custom_title="معاينة القالب"
            )
            
            if success and preview_path.exists():
                # فتح PDF خارجياً
                import os
                os.startfile(str(preview_path))
                QMessageBox.information(self, "معاينة", "تم إنشاء معاينة PDF وفتحها خارجياً")
            else:
                QMessageBox.warning(self, "خطأ", "فشل في إنشاء معاينة PDF")
                
        except Exception as e:
            logging.error(f"خطأ في إنشاء معاينة PDF: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في إنشاء المعاينة:\n{str(e)}")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    
    editor = SimpleTemplateEditor()
    editor.show()
    
    sys.exit(app.exec_())
