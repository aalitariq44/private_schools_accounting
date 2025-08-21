#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محرر قالب الهوية - واجهة لتحرير إعدادات القالب بصريا
"""

import sys
import json
import logging
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QWidget, QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
    QLineEdit, QColorDialog, QComboBox, QCheckBox, QGroupBox,
    QScrollArea, QTextEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

# إضافة مسار المشروع
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from templates.id_template import (
    TEMPLATE_ELEMENTS, save_template_as_json, load_template_from_json,
    ID_WIDTH, ID_HEIGHT, GRID_COLS, GRID_ROWS
)


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
    """محرر قالب الهوية الرئيسي"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("محرر قالب الهوية")
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
        
        # التبويبات لتحرير العناصر
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # شريط الأزرار السفلي
        self.create_bottom_buttons(layout)
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات"""
        toolbar = QHBoxLayout()
        
        # زر تحميل قالب
        load_btn = QPushButton("تحميل قالب")
        load_btn.clicked.connect(self.load_template)
        toolbar.addWidget(load_btn)
        
        # زر حفظ قالب
        save_btn = QPushButton("حفظ القالب")
        save_btn.clicked.connect(self.save_template)
        toolbar.addWidget(save_btn)
        
        # زر إعادة التعيين
        reset_btn = QPushButton("إعادة التعيين")
        reset_btn.clicked.connect(self.reset_template)
        toolbar.addWidget(reset_btn)
        
        toolbar.addStretch()
        
        # زر معاينة
        preview_btn = QPushButton("معاينة")
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
        """تحميل القالب الحالي"""
        self.tabs.clear()
        self.elements.clear()
        
        for element_name, element_config in TEMPLATE_ELEMENTS.items():
            editor = ElementEditor(element_name, element_config)
            
            # إنشاء منطقة تمرير للمحرر
            scroll = QScrollArea()
            scroll.setWidget(editor)
            scroll.setWidgetResizable(True)
            
            self.tabs.addTab(scroll, element_name)
            self.elements[element_name] = editor
    
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
        """معاينة القالب"""
        try:
            # تطبيق التغييرات أولاً
            self.apply_changes()
            
            # إنشاء معاينة
            from core.pdf.student_id_generator import generate_student_ids_pdf
            
            sample_data = [{
                'name': 'أحمد محمد علي السامرائي',
                'grade': 'الصف الثالث الابتدائي',
                'school_name': 'مدرسة النموذج الأهلية'
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
            else:
                QMessageBox.warning(self, "خطأ", "فشل في إنشاء المعاينة")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في المعاينة:\n{str(e)}")
    
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
