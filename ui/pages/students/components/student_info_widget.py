#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مكونات معلومات الطالب - عرض المعلومات الأساسية والملخص المالي والملاحظات
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, 
    QTextEdit, QPushButton, QMessageBox, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFontDatabase, QFont
from core.database.connection import db_manager
import config


class StudentInfoWidget(QWidget):
    """مكون عرض معلومات الطالب"""
    
    # إشارة لتحديث الملاحظات
    notes_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.student_data = None
        self.installments_data = []
        self.student_id = None
        
        # الحصول على الخط من الصفحة الأم
        self.cairo_family = self.get_cairo_family_from_parent()
        
        self.setup_ui()
    
    def get_cairo_family_from_parent(self):
        """الحصول على عائلة الخط من الصفحة الأم"""
        try:
            # البحث عن الصفحة الأم للحصول على الخط
            parent = self.parent()
            while parent:
                if hasattr(parent, 'cairo_family'):
                    return parent.cairo_family
                parent = parent.parent()
            
            # إذا لم يتم العثور، تحميل الخط محلياً
            self.setup_cairo_font()
            return self.cairo_family
            
        except Exception as e:
            logging.warning(f"فشل في الحصول على عائلة الخط من الأم: {e}")
            self.setup_cairo_font()
            return self.cairo_family
    
    def setup_cairo_font(self):
        """تحميل وتطبيق خط Cairo (احتياطي)"""
        try:
            from PyQt5.QtGui import QFontDatabase
            import config
            
            font_db = QFontDatabase()
            font_dir = config.RESOURCES_DIR / "fonts"
            
            # تحميل خطوط Cairo
            id_medium = font_db.addApplicationFont(str(font_dir / "Cairo-Medium.ttf"))
            id_bold = font_db.addApplicationFont(str(font_dir / "Cairo-Bold.ttf"))
            
            # الحصول على اسم عائلة الخط
            families = font_db.applicationFontFamilies(id_medium)
            self.cairo_family = families[0] if families else "Arial"
            
            logging.info(f"تم تحميل خط Cairo بنجاح في StudentInfoWidget: {self.cairo_family}")
            
        except Exception as e:
            logging.warning(f"فشل في تحميل خط Cairo في StudentInfoWidget، استخدام الخط الافتراضي: {e}")
            self.cairo_family = "Arial"
    
    def apply_font_to_widgets(self):
        """تطبيق خط Cairo على جميع عناصر الواجهة"""
        try:
            from PyQt5.QtGui import QFont
            
            # إنشاء كائن الخط
            cairo_font = QFont(self.cairo_family, 10)
            
            # تطبيق الخط على العناصر الرئيسية
            if hasattr(self, 'name_label') and self.name_label:
                self.name_label.setFont(cairo_font)
            if hasattr(self, 'school_label') and self.school_label:
                self.school_label.setFont(cairo_font)
            if hasattr(self, 'grade_label') and self.grade_label:
                self.grade_label.setFont(cairo_font)
            if hasattr(self, 'section_label') and self.section_label:
                self.section_label.setFont(cairo_font)
            if hasattr(self, 'gender_label') and self.gender_label:
                self.gender_label.setFont(cairo_font)
            if hasattr(self, 'phone_label') and self.phone_label:
                self.phone_label.setFont(cairo_font)
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setFont(cairo_font)
            if hasattr(self, 'start_date_label') and self.start_date_label:
                self.start_date_label.setFont(cairo_font)
            if hasattr(self, 'notes_display') and self.notes_display:
                self.notes_display.setFont(cairo_font)
            if hasattr(self, 'notes_display') and self.notes_display:
                self.notes_display.setFont(cairo_font)
            if hasattr(self, 'total_fee_label') and self.total_fee_label:
                self.total_fee_label.setFont(cairo_font)
            if hasattr(self, 'paid_amount_label') and self.paid_amount_label:
                self.paid_amount_label.setFont(cairo_font)
            if hasattr(self, 'remaining_amount_label') and self.remaining_amount_label:
                self.remaining_amount_label.setFont(cairo_font)
            if hasattr(self, 'installments_count_label') and self.installments_count_label:
                self.installments_count_label.setFont(cairo_font)
            
            logging.info(f"تم تطبيق خط Cairo على عناصر StudentInfoWidget: {self.cairo_family}")
            
        except Exception as e:
            logging.warning(f"فشل في تطبيق خط Cairo على العناصر: {e}")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            layout = QVBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(15)
            
            # معلومات الطالب الأساسية
            self.create_basic_info_section(layout)
            
            # الملخص المالي
            self.create_financial_summary(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة معلومات الطالب: {e}")
            raise
    
    def create_basic_info_section(self, layout):
        """إنشاء قسم المعلومات الأساسية"""
        try:
            info_frame = QFrame()
            info_frame.setObjectName("studentInfoFrame")
            
            info_layout = QVBoxLayout(info_frame)
            info_layout.setContentsMargins(20, 15, 20, 15)
            
            # عنوان القسم
            title_label = QLabel("معلومات الطالب")
            title_label.setObjectName("sectionTitle")
            title_label.setFont(QFont(self.cairo_family, 14, QFont.Bold))
            info_layout.addWidget(title_label)
            
            # شبكة المعلومات
            grid_layout = QGridLayout()
            grid_layout.setSpacing(15)
            
            # إنشاء التسميات
            self.name_label = QLabel("--")
            self.name_label.setObjectName("studentName")
            self.name_label.setFont(QFont(self.cairo_family, 10))
            
            self.school_label = QLabel("--")
            self.school_label.setObjectName("infoValue")
            self.school_label.setFont(QFont(self.cairo_family, 10))
            
            self.grade_label = QLabel("--")
            self.grade_label.setObjectName("infoValue")
            self.grade_label.setFont(QFont(self.cairo_family, 10))
            
            self.section_label = QLabel("--")
            self.section_label.setObjectName("infoValue")
            self.section_label.setFont(QFont(self.cairo_family, 10))
            
            self.gender_label = QLabel("--")
            self.gender_label.setObjectName("infoValue")
            self.gender_label.setFont(QFont(self.cairo_family, 10))
            
            self.phone_label = QLabel("--")
            self.phone_label.setObjectName("infoValue")
            self.phone_label.setFont(QFont(self.cairo_family, 10))
            
            self.status_label = QLabel("--")
            self.status_label.setObjectName("infoValue")
            self.status_label.setFont(QFont(self.cairo_family, 10))
            
            self.start_date_label = QLabel("--")
            self.start_date_label.setObjectName("infoValue")
            self.start_date_label.setFont(QFont(self.cairo_family, 10))
            
            # إنشاء حقل الملاحظات المصغر
            self.notes_display = QLabel("--")
            self.notes_display.setObjectName("infoValue")
            self.notes_display.setWordWrap(True)
            self.notes_display.setMaximumWidth(150)
            self.notes_display.setMaximumHeight(40)
            self.notes_display.setFont(QFont(self.cairo_family, 10))
            
            # إضافة إمكانية تعديل الملاحظات بالنقر المزدوج
            self.notes_display.mouseDoubleClickEvent = self.edit_notes_dialog
            
            # إضافة المعلومات للشبكة
            # الصف الأول
            name_label = QLabel("الاسم:")
            name_label.setFont(QFont(self.cairo_family, 10))
            grid_layout.addWidget(name_label, 0, 0)
            grid_layout.addWidget(self.name_label, 0, 1)
            
            school_label = QLabel("المدرسة:")
            school_label.setFont(QFont(self.cairo_family, 10))
            grid_layout.addWidget(school_label, 0, 2)
            grid_layout.addWidget(self.school_label, 0, 3)
            
            gender_label = QLabel("الجنس:")
            gender_label.setFont(QFont(self.cairo_family, 10))
            grid_layout.addWidget(gender_label, 0, 4)
            grid_layout.addWidget(self.gender_label, 0, 5)
            
            # الصف الثاني
            grade_label = QLabel("الصف:")
            grade_label.setFont(QFont(self.cairo_family, 10))
            grid_layout.addWidget(grade_label, 1, 0)
            grid_layout.addWidget(self.grade_label, 1, 1)
            
            section_label = QLabel("الشعبة:")
            section_label.setFont(QFont(self.cairo_family, 10))
            grid_layout.addWidget(section_label, 1, 2)
            grid_layout.addWidget(self.section_label, 1, 3)
            
            phone_label = QLabel("الهاتف:")
            phone_label.setFont(QFont(self.cairo_family, 10))
            grid_layout.addWidget(phone_label, 1, 4)
            grid_layout.addWidget(self.phone_label, 1, 5)
            
            # الصف الثالث
            status_label = QLabel("الحالة:")
            status_label.setFont(QFont(self.cairo_family, 10))
            grid_layout.addWidget(status_label, 2, 0)
            grid_layout.addWidget(self.status_label, 2, 1)

            start_date_label = QLabel("تاريخ المباشرة:")
            start_date_label.setFont(QFont(self.cairo_family, 10))
            grid_layout.addWidget(start_date_label, 2, 2)
            grid_layout.addWidget(self.start_date_label, 2, 3)

            # الملاحظات في نفس الصف
            notes_label = QLabel("ملاحظات:")
            notes_label.setFont(QFont(self.cairo_family, 10))
            grid_layout.addWidget(notes_label, 2, 4)
            grid_layout.addWidget(self.notes_display, 2, 5)
            
            info_layout.addLayout(grid_layout)
            layout.addWidget(info_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم المعلومات الأساسية: {e}")
            raise
    
    def create_financial_summary(self, layout):
        """إنشاء الملخص المالي"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("financialSummary")
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(15, 10, 15, 10)
            
            # القسط الكلي
            self.total_fee_label = QLabel("القسط الكلي: 0 د.ع")
            self.total_fee_label.setObjectName("totalFee")
            self.total_fee_label.setFont(QFont(self.cairo_family, 10))
            summary_layout.addWidget(self.total_fee_label)
            
            # المدفوع
            self.paid_amount_label = QLabel("المدفوع: 0 د.ع")
            self.paid_amount_label.setObjectName("paidAmount")
            self.paid_amount_label.setFont(QFont(self.cairo_family, 10))
            summary_layout.addWidget(self.paid_amount_label)
            
            # المتبقي
            self.remaining_amount_label = QLabel("المتبقي: 0 د.ع")
            self.remaining_amount_label.setObjectName("remainingAmount")
            self.remaining_amount_label.setFont(QFont(self.cairo_family, 10))
            summary_layout.addWidget(self.remaining_amount_label)
            
            # عدد الدفعات
            self.installments_count_label = QLabel("عدد الدفعات: 0")
            self.installments_count_label.setObjectName("installmentsCount")
            self.installments_count_label.setFont(QFont(self.cairo_family, 10))
            summary_layout.addWidget(self.installments_count_label)
            
            layout.addWidget(summary_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الملخص المالي: {e}")
            raise
    
    def update_student_info(self, student_data):
        """تحديث معلومات الطالب"""
        try:
            self.student_data = student_data
            
            if not student_data:
                # قيم افتراضية في حالة عدم وجود بيانات
                self.name_label.setText("--")
                self.school_label.setText("--")
                self.grade_label.setText("--")
                self.section_label.setText("--")
                self.gender_label.setText("--")
                self.phone_label.setText("--")
                self.status_label.setText("--")
                self.start_date_label.setText("--")
                self.total_fee_label.setText("القسط الكلي: 0 د.ع")
                self.update_notes_display("")
                return
            
            # التحقق من طول البيانات
            if len(student_data) < 16:
                logging.warning(f"بيانات الطالب غير مكتملة: {len(student_data)} حقل")
                return
            
            # تحديث المعلومات بناءً على البنية الصحيحة لجدول students
            # فهارس الأعمدة الصحيحة (من PRAGMA table_info):
            # 1: name, 4: grade, 5: section, 7: gender, 9: phone
            # 12: total_fee, 13: start_date, 14: status, 15: notes
            # مع JOIN: 18: school_name, 19: school_name_en, 20: school_address, 21: school_phone, 22: school_logo_path
            
            # الاسم - الفهرس 1
            self.name_label.setText(str(student_data[1] or "--"))
            
            # اسم المدرسة - من JOIN - الفهرس 18
            if len(student_data) > 18 and student_data[18]:
                self.school_label.setText(str(student_data[18]))
            else:
                self.school_label.setText("--")
            
            # الصف - الفهرس 4
            self.grade_label.setText(str(student_data[4] or "--"))
            
            # الشعبة - الفهرس 5
            self.section_label.setText(str(student_data[5] or "--"))
            
            # الجنس - الفهرس 7
            self.gender_label.setText(str(student_data[7] or "--"))
            
            # الهاتف - الفهرس 9
            self.phone_label.setText(str(student_data[9] or "--"))
            
            # الحالة - الفهرس 14
            status_text = str(student_data[14] or "نشط")
            self.status_label.setText(status_text)
            
            # تغيير لون خلفية حقل الحالة بناءً على النص
            if status_text == "منتقل":
                self.status_label.setStyleSheet("background-color: #FF0000; color: white; padding: 2px; border-radius: 3px;")
            elif status_text == "منقطع":
                self.status_label.setStyleSheet("background-color: #8B0000; color: white; padding: 2px; border-radius: 3px;")
            elif status_text == "متخرج":
                self.status_label.setStyleSheet("background-color: #FFFF00; color: black; padding: 2px; border-radius: 3px;")
            else:
                self.status_label.setStyleSheet("")
            
            # تاريخ المباشرة - الفهرس 13
            self.start_date_label.setText(str(student_data[13] or "--"))
            
            # الملاحظات - الفهرس 15
            notes = ""
            if len(student_data) > 15 and student_data[15]:
                notes = str(student_data[15])
            self.update_notes_display(notes)
            
            # القسط الكلي - الفهرس 12
            try:
                total_fee = float(student_data[12] or 0)
                self.total_fee_label.setText(f"القسط الكلي: {total_fee:,.0f} د.ع")
            except (ValueError, TypeError):
                logging.error(f"خطأ في تحويل القسط الكلي: {student_data[12]}")
                self.total_fee_label.setText("القسط الكلي: 0 د.ع")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث معلومات الطالب: {e}")
    
    def update_financial_summary(self, installments_data):
        """تحديث الملخص المالي"""
        try:
            self.installments_data = installments_data
            
            if not self.student_data or len(self.student_data) < 13:
                # قيم افتراضية في حالة عدم وجود بيانات
                self.total_fee_label.setText("القسط الكلي: 0 د.ع")
                self.paid_amount_label.setText("المدفوع: 0 د.ع")
                self.remaining_amount_label.setText("المتبقي: 0 د.ع")
                self.installments_count_label.setText("عدد الدفعات: 0")
                return
            
            # حساب المبلغ المدفوع من الأقساط
            total_paid = 0
            for installment in installments_data:
                try:
                    # المبلغ في العمود الثاني (index 1)
                    paid_amount = float(installment[1]) if installment[1] else 0
                    total_paid += paid_amount
                except (ValueError, TypeError, IndexError):
                    continue
            
            # القسط الكلي - الفهرس 12
            try:
                total_fee = float(self.student_data[12] or 0)
            except (ValueError, TypeError):
                logging.error(f"خطأ في تحويل القسط الكلي: {self.student_data[12]}")
                total_fee = 0
            
            # المتبقي
            remaining = total_fee - total_paid
            
            # عدد الدفعات
            installments_count = len(installments_data)
            
            # تحديث التسميات
            self.total_fee_label.setText(f"القسط الكلي: {total_fee:,.0f} د.ع")
            self.paid_amount_label.setText(f"المدفوع: {total_paid:,.0f} د.ع")
            self.remaining_amount_label.setText(f"المتبقي: {remaining:,.0f} د.ع")
            self.installments_count_label.setText(f"عدد الدفعات: {installments_count}")
            
            # تلوين المتبقي
            if remaining > 0:
                self.remaining_amount_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
            else:
                self.remaining_amount_label.setStyleSheet("color: #27AE60; font-weight: bold;")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الملخص المالي: {e}")
    
    def get_student_name(self):
        """الحصول على اسم الطالب"""
        return self.name_label.text() if self.name_label.text() != "--" else ""
    
    def get_school_info(self):
        """الحصول على معلومات المدرسة"""
        if not self.student_data or len(self.student_data) < 23:
            return {"name": "", "address": "", "phone": ""}
        
        # معلومات المدرسة تأتي من JOIN
        # 18: school_name, 19: school_name_en, 20: school_address, 21: school_phone, 22: school_logo_path
        try:
            return {
                "name": str(self.student_data[18] or "") if len(self.student_data) > 18 else "",
                "address": str(self.student_data[20] or "") if len(self.student_data) > 20 else "",
                "phone": str(self.student_data[21] or "") if len(self.student_data) > 21 else ""
            }
        except (IndexError, TypeError):
            return {"name": "", "address": "", "phone": ""}
    
    def get_basic_info(self):
        """الحصول على المعلومات الأساسية"""
        return {
            "name": self.name_label.text(),
            "school": self.school_label.text(),
            "grade": self.grade_label.text(),
            "section": self.section_label.text(),
            "gender": self.gender_label.text(),
            "phone": self.phone_label.text(),
            "status": self.status_label.text(),
            "start_date": self.start_date_label.text()
        }
    
    def set_student_id(self, student_id):
        """تعيين معرف الطالب"""
        self.student_id = student_id
    
    def edit_notes_dialog(self, event):
        """فتح نافذة حوار لتعديل الملاحظات"""
        try:
            if not self.student_id:
                QMessageBox.warning(self, "خطأ", "لا يوجد طالب محدد")
                return
            
            # إنشاء نافذة الحوار
            dialog = QDialog(self)
            dialog.setWindowTitle("تعديل ملاحظات الطالب")
            dialog.setModal(True)
            dialog.resize(400, 300)
            
            # تخطيط النافذة
            layout = QVBoxLayout()
            
            # عنوان
            title_label = QLabel("ملاحظات الطالب:")
            title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
            layout.addWidget(title_label)
            
            # مربع النص
            notes_edit = QTextEdit()
            notes_edit.setPlaceholderText("اكتب ملاحظات حول الطالب هنا...")
            
            # تحميل الملاحظات الحالية مباشرة من بيانات الطالب
            current_notes = ""
            if self.student_data and len(self.student_data) > 15:
                current_notes = str(self.student_data[15] or "")
            notes_edit.setPlainText(current_notes)
            
            layout.addWidget(notes_edit)
            
            # أزرار التحكم
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.button(QDialogButtonBox.Ok).setText("حفظ")
            button_box.button(QDialogButtonBox.Cancel).setText("إلغاء")
            layout.addWidget(button_box)
            
            dialog.setLayout(layout)
            
            # ربط الأزرار
            def save_notes():
                try:
                    notes_text = notes_edit.toPlainText().strip()
                    
                    # تحديث البيانات في قاعدة البيانات
                    success = db_manager.execute_query(
                        "UPDATE students SET notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (notes_text, self.student_id)
                    )
                    
                    if success is not False:
                        # تحديث البيانات المحلية
                        if self.student_data:
                            student_data_list = list(self.student_data)
                            # الملاحظات في الفهرس 15
                            if len(student_data_list) > 15:
                                student_data_list[15] = notes_text
                            else:
                                while len(student_data_list) < 16:
                                    student_data_list.append("")
                                student_data_list[15] = notes_text
                            self.student_data = tuple(student_data_list)
                        
                        # تحديث العرض
                        self.update_notes_display(notes_text)
                        
                        # إرسال إشارة التحديث
                        self.notes_updated.emit()
                        
                        dialog.accept()
                        QMessageBox.information(self, "نجح", "تم حفظ الملاحظات بنجاح")
                    else:
                        QMessageBox.critical(self, "خطأ", "فشل في حفظ الملاحظات")
                        
                except Exception as e:
                    logging.error(f"خطأ في حفظ الملاحظات: {e}")
                    QMessageBox.critical(self, "خطأ", f"خطأ في حفظ الملاحظات: {str(e)}")
            
            button_box.accepted.connect(save_notes)
            button_box.rejected.connect(dialog.reject)
            
            # عرض النافذة
            dialog.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في فتح نافذة تعديل الملاحظات: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في فتح نافذة التعديل: {str(e)}")
    
    def update_notes_display(self, notes_text):
        """تحديث عرض الملاحظات المصغر"""
        try:
            if notes_text and notes_text.strip():
                # قطع النص إذا كان طويلاً
                display_notes = notes_text[:50] + "..." if len(notes_text) > 50 else notes_text
                self.notes_display.setText(display_notes)
                self.notes_display.setToolTip(notes_text)  # إظهار النص الكامل عند التمرير
            else:
                self.notes_display.setText("لا توجد ملاحظات")
                self.notes_display.setToolTip("")
                
        except Exception as e:
            logging.error(f"خطأ في تحديث عرض الملاحظات: {e}")
    
    def get_notes(self):
        """الحصول على الملاحظات الحالية"""
        if self.student_data and len(self.student_data) > 15:
            return str(self.student_data[15] or "")
        return ""
