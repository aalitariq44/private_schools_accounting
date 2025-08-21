#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إضافة بيانات تجريبية للطلاب لاختبار ميزة إنشاء الهويات
"""

import sqlite3
import config
from datetime import datetime

def add_test_students():
    try:
        conn = sqlite3.connect(str(config.DATABASE_PATH))
        cur = conn.cursor()
        
        # التحقق من وجود مدارس
        cur.execute("SELECT id, name_ar FROM schools LIMIT 3")
        schools = cur.fetchall()
        
        if not schools:
            print("لا توجد مدارس في قاعدة البيانات")
            conn.close()
            return
        
        print(f"تم العثور على {len(schools)} مدرسة")
        for school in schools:
            print(f"  - {school[1]} (ID: {school[0]})")
        
        # بيانات طلاب تجريبية
        test_students = [
            {
                'name': 'أحمد محمد علي',
                'school_id': schools[0][0],
                'grade': 'الأول الابتدائي',
                'section': 'أ',
                'gender': 'ذكر',
                'phone': '07801234567'
            },
            {
                'name': 'فاطمة حسن محمود',
                'school_id': schools[0][0],
                'grade': 'الثاني الابتدائي',
                'section': 'ب',
                'gender': 'أنثى',
                'phone': '07802345678'
            },
            {
                'name': 'محمد عبدالله أحمد',
                'school_id': schools[1][0] if len(schools) > 1 else schools[0][0],
                'grade': 'الثالث الابتدائي',
                'section': 'أ',
                'gender': 'ذكر',
                'phone': '07803456789'
            },
            {
                'name': 'نور الهدى صالح',
                'school_id': schools[1][0] if len(schools) > 1 else schools[0][0],
                'grade': 'الرابع الابتدائي',
                'section': 'ب',
                'gender': 'أنثى',
                'phone': '07804567890'
            },
            {
                'name': 'عمار طارق حسين',
                'school_id': schools[2][0] if len(schools) > 2 else schools[0][0],
                'grade': 'الخامس الابتدائي',
                'section': 'أ',
                'gender': 'ذكر',
                'phone': '07805678901'
            },
            {
                'name': 'زينب خالد عبدالرحمن',
                'school_id': schools[2][0] if len(schools) > 2 else schools[0][0],
                'grade': 'السادس الابتدائي',
                'section': 'ب',
                'gender': 'أنثى',
                'phone': '07806789012'
            }
        ]
        
        # التحقق من وجود طلاب مسبقاً
        cur.execute("SELECT COUNT(*) FROM students")
        student_count = cur.fetchone()[0]
        
        if student_count > 0:
            print(f"يوجد بالفعل {student_count} طالب في قاعدة البيانات")
            response = input("هل تريد إضافة طلاب جدد؟ (y/n): ")
            if response.lower() != 'y':
                conn.close()
                return
        
        # إدخال الطلاب
        current_time = datetime.now().isoformat()
        
        for student in test_students:
            try:
                cur.execute("""
                    INSERT INTO students (
                        name, school_id, grade, section, gender, phone,
                        academic_year, total_fee, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student['name'],
                    student['school_id'],
                    student['grade'],
                    student['section'],
                    student['gender'],
                    student['phone'],
                    '2025-2026',
                    1000000,  # رسوم تجريبية (مليون دينار)
                    'نشط',
                    current_time,
                    current_time
                ))
                
                print(f"تم إضافة الطالب: {student['name']}")
                
            except sqlite3.IntegrityError as e:
                print(f"تحذير: {student['name']} - {e}")
        
        conn.commit()
        
        # عرض إحصائية نهائية
        cur.execute("SELECT COUNT(*) FROM students")
        final_count = cur.fetchone()[0]
        print(f"\nتم الانتهاء. إجمالي الطلاب في قاعدة البيانات: {final_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"خطأ في إضافة البيانات التجريبية: {e}")

if __name__ == "__main__":
    add_test_students()
