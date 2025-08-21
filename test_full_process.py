#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from core.printing.template_manager import TemplateManager
from core.printing.print_config import TemplateType
from core.database.connection import db_manager
from ui.widgets.column_selection_dialog import ColumnSelectionDialog
import logging

logging.basicConfig(level=logging.DEBUG)

# إنشاء QApplication لـ ColumnSelectionDialog
app = QApplication(sys.argv)

try:
    print("=== اختبار عملية الطباعة الكاملة ===")
    
    # جلب بيانات طالب واحد
    students_raw = db_manager.execute_query("""
        SELECT s.id, s.name, sc.name_ar as school_name,
               s.grade, s.section, s.gender,
               s.phone, s.status, s.start_date, s.total_fee,
               COALESCE(SUM(i.amount), 0) as total_paid
        FROM students s
        LEFT JOIN schools sc ON s.school_id = sc.id
        LEFT JOIN installments i ON s.id = i.student_id
        GROUP BY s.id, s.name, sc.name_ar, s.grade, s.section, s.gender, s.phone, s.status, s.start_date, s.total_fee
        LIMIT 3
    """)
    
    if not students_raw:
        print("لم يتم العثور على طلاب")
        sys.exit(1)
    
    # تحضير البيانات كما يتم في الكود الأصلي
    students_for_print = []
    for student in students_raw:
        total_fee = student['total_fee'] if student['total_fee'] else 0
        total_paid = student['total_paid'] if student['total_paid'] else 0
        remaining = total_fee - total_paid
        
        student_data = {
            'id': student['id'],
            'name': student['name'] or "",  
            'school_name': student['school_name'] or "",
            'grade': student['grade'] or "",
            'section': student['section'] or "",
            'gender': student['gender'] or "",
            'phone': student['phone'] or "",
            'status': student['status'] or "",
            'total_fee': f"{total_fee:,.0f} د.ع",
            'total_paid': f"{total_paid:,.0f} د.ع",
            'remaining': f"{remaining:,.0f} د.ع"
        }
        students_for_print.append(student_data)
    
    print(f"تم تحضير {len(students_for_print)} طلاب")
    
    # محاكاة ColumnSelectionDialog
    columns = {
        'id': 'المعرف',
        'name': 'الاسم',
        'school_name': 'المدرسة',
        'grade': 'الصف',
        'section': 'الشعبة',
        'gender': 'الجنس',
        'status': 'الحالة',
        'total_fee': 'الرسوم الدراسية',
        'total_paid': 'المدفوع',
        'remaining': 'المتبقي'
    }

    dialog = ColumnSelectionDialog(columns, parent=None)
    
    # تحديد جميع الأعمدة (كما يحدث افتراضياً)
    selected_columns = dialog.get_selected_columns()
    
    print(f"الأعمدة المحددة: {selected_columns}")
    
    # التحقق من وجود عمود name
    if 'name' in selected_columns:
        print("✅ عمود الاسم محدد")
    else:
        print("❌ عمود الاسم غير محدد!")
    
    # إنشاء مدير القوالب
    tm = TemplateManager()
    
    # البيانات المطلوبة للقالب
    data = {
        'students': students_for_print,
        'selected_columns': selected_columns,
        'all_columns': columns,
        'filter_info': 'اختبار تلقائي',
        'company_name': 'شركة تكنولوجيا الحلول',
        'system_version': '1.0.0',
        'print_date': '2025-08-21'
    }
    
    print("=== البيانات النهائية للقالب ===")
    print(f"students count: {len(data['students'])}")
    print(f"selected_columns: {data['selected_columns']}")
    
    # تقديم القالب
    html_content = tm.render_template(TemplateType.STUDENTS_LIST, data)
    
    # البحث عن محتوى الأسماء
    found_names = []
    for student in students_for_print:
        if student['name'] in html_content:
            found_names.append(student['name'])
    
    print(f"الأسماء الموجودة في HTML: {found_names}")
    
    # البحث عن خلايا فارغة
    empty_cells = html_content.count('<td></td>')
    print(f"عدد الخلايا الفارغة: {empty_cells}")
    
    # حفظ HTML للفحص
    with open('test_full_process.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("تم حفظ HTML في test_full_process.html")

except Exception as e:
    print(f"خطأ: {e}")
    import traceback
    traceback.print_exc()

app.quit()
