#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.printing.template_manager import TemplateManager
from core.printing.print_config import TemplateType
from core.database.connection import db_manager
import logging

logging.basicConfig(level=logging.DEBUG)

# تجربة تقديم القالب مباشرة
try:
    print("=== اختبار تقديم قالب الطلاب ===")
    
    # إنشاء مدير القوالب
    tm = TemplateManager()
    
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
        LIMIT 1
    """)
    
    if not students_raw:
        print("لم يتم العثور على طلاب")
        sys.exit(1)
    
    student = students_raw[0]
    print(f"الطالب: {student['name']}")
    
    # تحضير البيانات
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
    
    # البيانات المطلوبة للقالب
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
    
    selected_columns = ['id', 'name', 'school_name', 'grade', 'section', 'gender', 'status']
    
    data = {
        'students': [student_data],
        'selected_columns': selected_columns,
        'all_columns': columns,
        'filter_info': 'اختبار',
        'company_name': 'شركة تكنولوجيا الحلول',
        'system_version': '1.0.0',
        'print_date': '2025-08-21'
    }
    
    print("البيانات المُمررة للقالب:")
    print(f"  students: {data['students']}")
    print(f"  selected_columns: {data['selected_columns']}")
    print(f"  all_columns: {data['all_columns']}")
    print()
    
    # تقديم القالب
    html_content = tm.render_template(TemplateType.STUDENTS_LIST, data)
    
    print("=== محتوى HTML المُولد ===")
    print(html_content[:2000])  # أول 2000 حرف
    
    # البحث عن محتوى عمود الاسم
    if 'آية محمد محمد' in html_content or student['name'] in html_content:
        print("✅ تم العثور على اسم الطالب في HTML")
    else:
        print("❌ لم يتم العثور على اسم الطالب في HTML")
        
    # البحث عن خلايا فارغة
    if '<td></td>' in html_content:
        print("⚠️  توجد خلايا فارغة في الجدول")
        count = html_content.count('<td></td>')
        print(f"   عدد الخلايا الفارغة: {count}")
    else:
        print("✅ لا توجد خلايا فارغة في الجدول")
    
    # حفظ HTML لفحص يدوي
    with open('test_output.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("تم حفظ HTML في test_output.html")

except Exception as e:
    print(f"خطأ: {e}")
    import traceback
    traceback.print_exc()
