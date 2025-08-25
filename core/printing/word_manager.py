# -*- coding: utf-8 -*-
"""
مدير إنشاء ملفات Word للطباعة
"""

import logging
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional
import subprocess

try:
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("مكتبة python-docx غير متوفرة، لن تتمكن من إنشاء ملفات Word")

from PyQt5.QtWidgets import QMessageBox, QFileDialog
import config


class WordManager:
    """مدير إنشاء ملفات Word"""
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if not DOCX_AVAILABLE:
            raise ImportError("مكتبة python-docx غير متوفرة")
    
    def create_students_list_word(self, students: List[Dict], selected_columns: Dict, filter_info: Optional[str] = None):
        """إنشاء قائمة الطلاب في ملف Word"""
        try:
            # إنشاء مستند Word جديد
            doc = Document()
            # اجعل اتجاه الكتابة من اليمين لليسار بشكل افتراضي
            from docx.oxml import OxmlElement
            normal_style = doc.styles['Normal']
            # ضبط فقرة RTL
            pPr = normal_style.element.get_or_add_pPr()
            bidi = OxmlElement('w:bidi')
            pPr.append(bidi)
            # ضبط النص RTL
            rPr = normal_style.element.get_or_add_rPr()
            rtl = OxmlElement('w:rtl')
            rPr.append(rtl)
            
            # إعداد اتجاه الصفحة واللغة
            section = doc.sections[0]
            section.page_height = Inches(11.69)  # A4
            section.page_width = Inches(8.27)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            
            # ضبط اتجاه النص من اليمين لليسار
            doc.styles['Normal'].font.name = 'Arial'
            doc.styles['Normal'].font.size = Pt(11)
            
            # إضافة عنوان رئيسي
            title_paragraph = doc.add_paragraph()
            title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_run = title_paragraph.add_run('قائمة الطلاب')
            title_run.font.size = Pt(18)
            title_run.bold = True
            title_run.font.name = 'Arial'
            
            # إضافة تاريخ الطباعة
            date_paragraph = doc.add_paragraph()
            date_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            date_run = date_paragraph.add_run(f'تاريخ الطباعة: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
            date_run.font.size = Pt(12)
            date_run.font.name = 'Arial'
            
            # إضافة فراغ
            doc.add_paragraph()
            
            # عرض الفلاتر المطبقة وإجمالي العدد في جدول صغير بمحاذاة اليمين
            if filter_info:
                info_tbl = doc.add_table(rows=2, cols=1)
            else:
                info_tbl = doc.add_table(rows=1, cols=1)
            info_tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
            # الصف الأول: الفلاتر
            if filter_info:
                cell0 = info_tbl.cell(0, 0)
                p0 = cell0.paragraphs[0]
                p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run0 = p0.add_run(f'الفلاتر المطبقة: {filter_info}')
                run0.font.size = Pt(10)
                run0.italic = True
                run0.font.name = 'Arial'
            # الصف الثاني أو الوحيد: الملخص
            idx = 1 if filter_info else 0
            cell1 = info_tbl.cell(idx, 0)
            p1 = cell1.paragraphs[0]
            p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run1 = p1.add_run(f'إجمالي عدد الطلاب: {len(students)}')
            run1.font.size = Pt(12)
            run1.bold = True
            run1.font.name = 'Arial'
            # مسافة بعد الجدول الصغير
            doc.add_paragraph()
            
            # إنشاء الجدول
            if students:
                # تحديد عدد الأعمدة (ت + الأعمدة المحددة)
                num_cols = len(selected_columns) + 1
                table = doc.add_table(rows=1, cols=num_cols)
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                table.style = 'Table Grid'
                
                # جعل صف العنوان يتكرر في كل صفحة
                hdr_row = table.rows[0]
                # إضافة وسم tblHeader لعنصر الصف
                hdr_tr = hdr_row._tr
                trPr = hdr_tr.get_or_add_trPr()
                tblHeader = OxmlElement('w:tblHeader')
                trPr.append(tblHeader)
                
                # إضافة عناوين الأعمدة (RTL: العنوان الأخير على اليمين)
                header_row = table.rows[0]
                # ضع عمود الترقيم في الخلية الأخيرة
                header_row.cells[num_cols-1].text = 'ت'
                
                # ترتيب الأعمدة كما في المتطلبات
                column_order = ['id', 'name', 'school_name', 'grade', 'section', 'gender', 'phone', 'status', 'total_fee', 'total_paid', 'remaining']
                ordered_columns = []
                
                for col_key in column_order:
                    if col_key in selected_columns:
                        ordered_columns.append((col_key, selected_columns[col_key]))
                
                # إضافة أي أعمدة أخرى لم تكن في الترتيب الأساسي
                for col_key, col_name in selected_columns.items():
                    if col_key not in [item[0] for item in ordered_columns]:
                        ordered_columns.append((col_key, col_name))
                
                # ملء عناوين الأعمدة بالعكس (من اليمين لليسار)
                for i, (col_key, col_name) in enumerate(ordered_columns):
                    # تبدأ الأعمدة المحددة قبل عمود الترقيم، من الخلية قبل الأخيرة إلى الأولى
                    header_row.cells[num_cols - 2 - i].text = col_name
                
                # تنسيق عناوين الأعمدة
                for cell in header_row.cells:
                    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = cell.paragraphs[0].runs[0]
                    run.font.bold = True
                    run.font.size = Pt(11)
                    run.font.name = 'Arial'
                
                # إضافة بيانات الطلاب (RTL: الترقيم في اليمين وبقية الأعمدة تتجه نحو اليسار)
                for index, student in enumerate(students, 1):
                    row = table.add_row()
                    # ضع الترقيم في الخلية الأخيرة
                    row.cells[num_cols-1].text = str(index)
                    for i, (col_key, col_name) in enumerate(ordered_columns):
                        cell_value = student.get(col_key, '')
                        if cell_value is None:
                            cell_value = ''
                        # املأ الأعمدة المحددة بالعكس من قبل عمود الترقيم
                        row.cells[num_cols - 2 - i].text = str(cell_value)
                    
                    # تنسيق صف البيانات
                    for cell in row.cells:
                        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                        for run in cell.paragraphs[0].runs:
                            run.font.size = Pt(10)
                            run.font.name = 'Arial'
                
                # ضبط عرض الأعمدة
                for column in table.columns:
                    for cell in column.cells:
                        cell.width = Inches(1.2)
            
            else:
                # في حالة عدم وجود طلاب
                no_data_paragraph = doc.add_paragraph()
                no_data_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                no_data_run = no_data_paragraph.add_run('لا توجد بيانات طلاب للعرض')
                no_data_run.font.size = Pt(14)
                no_data_run.font.name = 'Arial'
            
            # إضافة تذييل
            doc.add_paragraph()
            footer_paragraph = doc.add_paragraph()
            footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            footer_run = footer_paragraph.add_run('نظام إدارة المدارس الخاصة')
            footer_run.font.size = Pt(10)
            footer_run.italic = True
            footer_run.font.name = 'Arial'
            
            # حفظ الملف
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"قائمة_الطلاب_{timestamp}.docx"
            filepath = os.path.join(temp_dir, filename)
            
            doc.save(filepath)
            
            # فتح الملف
            self.open_word_file(filepath)
            
            logging.info(f"تم إنشاء ملف Word بنجاح: {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء ملف Word: {e}")
            if self.parent:
                QMessageBox.critical(self.parent, "خطأ", f"فشل في إنشاء ملف Word:\n{str(e)}")
            return None
    
    def open_word_file(self, filepath: str):
        """فتح ملف Word بالتطبيق الافتراضي"""
        try:
            if os.path.exists(filepath):
                if os.name == 'nt':  # Windows
                    os.startfile(filepath)
                elif os.name == 'posix':  # Linux/Mac
                    subprocess.run(['xdg-open', filepath])
                
                logging.info(f"تم فتح ملف Word: {filepath}")
                
                # إظهار رسالة للمستخدم
                if self.parent:
                    QMessageBox.information(
                        self.parent, 
                        "تم إنشاء الملف", 
                        f"تم إنشاء ملف Word بنجاح وفتحه في التطبيق الافتراضي.\n\nمسار الملف:\n{filepath}"
                    )
            else:
                logging.error(f"ملف Word غير موجود: {filepath}")
                if self.parent:
                    QMessageBox.warning(self.parent, "خطأ", "لم يتم العثور على الملف المُنشأ")
                    
        except Exception as e:
            logging.error(f"خطأ في فتح ملف Word: {e}")
            if self.parent:
                QMessageBox.warning(
                    self.parent, 
                    "تعذر فتح الملف", 
                    f"تم إنشاء الملف بنجاح ولكن تعذر فتحه تلقائياً.\n\nيمكنك العثور على الملف في:\n{filepath}"
                )
    
    def save_word_file_as(self, filepath: str):
        """حفظ ملف Word في موقع يختاره المستخدم"""
        try:
            if not os.path.exists(filepath):
                if self.parent:
                    QMessageBox.warning(self.parent, "خطأ", "الملف المصدر غير موجود")
                return None
            
            # فتح نافذة اختيار موقع الحفظ
            save_path, _ = QFileDialog.getSaveFileName(
                self.parent,
                "حفظ ملف قائمة الطلاب",
                "قائمة_الطلاب.docx",
                "ملفات Word (*.docx);;جميع الملفات (*)"
            )
            
            if save_path:
                # نسخ الملف إلى الموقع المختار
                import shutil
                shutil.copy2(filepath, save_path)
                
                if self.parent:
                    QMessageBox.information(
                        self.parent,
                        "تم الحفظ",
                        f"تم حفظ الملف بنجاح في:\n{save_path}"
                    )
                
                logging.info(f"تم حفظ ملف Word في: {save_path}")
                return save_path
            
            return None
            
        except Exception as e:
            logging.error(f"خطأ في حفظ ملف Word: {e}")
            if self.parent:
                QMessageBox.critical(self.parent, "خطأ", f"فشل في حفظ الملف:\n{str(e)}")
            return None


def create_students_word_document(students: List[Dict], selected_columns: Dict, filter_info: Optional[str] = None, parent=None):
    """دالة مساعدة لإنشاء مستند Word لقائمة الطلاب"""
    try:
        if not DOCX_AVAILABLE:
            if parent:
                QMessageBox.critical(
                    parent, 
                    "مكتبة مفقودة", 
                    "مكتبة python-docx غير مثبتة.\nيرجى تثبيتها لإنشاء ملفات Word."
                )
            return None
        
        word_manager = WordManager(parent)
        return word_manager.create_students_list_word(students, selected_columns, filter_info)
        
    except Exception as e:
        logging.error(f"خطأ في إنشاء مستند Word: {e}")
        if parent:
            QMessageBox.critical(parent, "خطأ", f"فشل في إنشاء مستند Word:\n{str(e)}")
        return None
