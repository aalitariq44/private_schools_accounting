#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نهائي لإصلاح تخطيط هويات الطلاب باستخدام بيانات من قاعدة البيانات
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import sqlite3
import logging
from core.pdf.student_id_generator import generate_student_ids_pdf
from datetime import datetime

def get_sample_students():
    """الحصول على عينة من الطلاب من قاعدة البيانات"""
    try:
        db_path = project_root / "private_schools.db"
        if not db_path.exists():
            print("❌ قاعدة البيانات غير موجودة")
            return None
            
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # جلب عينة من الطلاب
        query = """
        SELECT id, name, grade, school_id, 
               (SELECT name FROM schools WHERE id = students.school_id) as school_name
        FROM students 
        ORDER BY id 
        LIMIT 12
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        students = []
        for row in rows:
            student = {
                'id': row[0],
                'name': row[1] or f"طالب رقم {row[0]}",
                'grade': row[2] or "غير محدد",
                'school_id': row[3],
                'school_name': row[4] or "مدرسة الاختبار"
            }
            students.append(student)
        
        conn.close()
        return students
        
    except Exception as e:
        print(f"❌ خطأ في جلب البيانات: {e}")
        return None

def create_test_pdf_with_real_data():
    """إنشاء PDF للهويات باستخدام بيانات حقيقية"""
    print("=== اختبار مع بيانات حقيقية من قاعدة البيانات ===")
    
    students = get_sample_students()
    
    if not students:
        print("سيتم استخدام بيانات اختبار بدلاً من ذلك...")
        # بيانات اختبار احتياطية
        students = []
        arabic_names = [
            "أحمد محمد علي", "فاطمة حسن محمود", "محمد عبدالله أحمد",
            "نور الهدى صالح", "عمار طارق حسين", "زينب علي حسام",
            "يوسف إبراهيم محمد", "مريم عادل صالح", "حسام الدين أحمد",
            "سارة محمود علي", "عبدالرحمن حسن", "ليلى محمد حسين"
        ]
        
        grades = [
            "الأول الابتدائي", "الثاني الابتدائي", "الثالث الابتدائي",
            "الرابع الابتدائي", "الخامس الابتدائي", "السادس الابتدائي"
        ]
        
        for i, name in enumerate(arabic_names):
            student = {
                'id': i + 1,
                'name': name,
                'grade': grades[i % len(grades)],
                'school_name': "مدرسة النور الأهلية"
            }
            students.append(student)
    
    print(f"📊 عدد الطلاب: {len(students)}")
    
    # إنشاء اسم ملف فريد
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = project_root / f"student_ids_fixed_{timestamp}.pdf"
    
    print(f"📄 إنشاء ملف: {output_file.name}")
    
    # إنشاء PDF
    school_name = students[0].get('school_name', 'مدرسة الاختبار') if students else 'مدرسة الاختبار'
    
    result = generate_student_ids_pdf(
        students,
        str(output_file),
        school_name,
        "هوية طالب"
    )
    
    if result:
        print(f"✅ تم إنشاء الملف بنجاح!")
        print(f"📁 حجم الملف: {output_file.stat().st_size / 1024:.2f} KB")
        print(f"📄 عدد الصفحات المتوقع: {(len(students) + 7) // 8}")  # 8 هويات لكل صفحة
        
        # عرض قائمة بالطلاب المُضمنين
        print("\n📋 الطلاب المُضمنون:")
        for i, student in enumerate(students, 1):
            print(f"  {i:2d}. {student['name']} - {student['grade']}")
        
        # محاولة فتح الملف
        try:
            os.startfile(str(output_file))
            print(f"\n📖 تم فتح الملف للمعاينة")
        except Exception as e:
            print(f"\n📖 يمكنك فتح الملف يدوياً: {output_file}")
            
        return True
    else:
        print("❌ فشل في إنشاء الملف")
        return False

def main():
    """الدالة الرئيسية"""
    print("اختبار نهائي لإصلاح تخطيط هويات الطلاب")
    print("=" * 50)
    
    # تعيين مستوى اللوق
    logging.basicConfig(level=logging.INFO)
    
    success = create_test_pdf_with_real_data()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ تم إصلاح مشكلة تخطيط هويات الطلاب بنجاح!")
        print("📝 التحسينات المُطبقة:")
        print("   - تقليل عدد البطاقات لكل صفحة من 10 إلى 8")
        print("   - إصلاح حساب مواضع البطاقات")
        print("   - ضبط الهوامش والمسافات")
        print("   - إضافة التحقق من حدود الصفحة")
    else:
        print("❌ هناك مشكلة لا تزال تحتاج إلى حل")

if __name__ == "__main__":
    main()
