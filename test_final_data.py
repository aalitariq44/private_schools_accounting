# -*- coding: utf-8 -*-
"""
اختبار نهائي للطباعة مع بيانات المدرسة
"""

import sqlite3
import os
import config

def test_final_data():
    """اختبار البيانات النهائية للطلاب ومدارسهم"""
    
    # اختبار طلاب من مدارس مختلفة
    db_path = os.path.join(config.DATA_DIR, 'database', 'schools.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print('📊 اختبار البيانات المحدثة:')
    print('=' * 50)

    # الطلاب مع بيانات المدرسة المحدثة
    query = '''
        SELECT s.name as student_name, 
               sc.name_ar as school_name,
               sc.address as school_address,
               sc.phone as school_phone,
               s.grade, s.section
        FROM students s
        LEFT JOIN schools sc ON s.school_id = sc.id
        LIMIT 5
    '''

    cursor.execute(query)
    students = cursor.fetchall()

    for i, student in enumerate(students, 1):
        student_name, school_name, school_address, school_phone, grade, section = student
        print(f'👤 الطالب {i}: {student_name}')
        print(f'   🏫 المدرسة: {school_name}')
        print(f'   📍 العنوان: {school_address or "عنوان المدرسة: (افتراضي)"}')
        print(f'   📞 الهاتف: {school_phone or "للتواصل (افتراضي)"}')
        print(f'   📚 الصف: {grade} - الشعبة: {section}')
        print()

    conn.close()
    print('✅ تم الاختبار بنجاح!')

if __name__ == "__main__":
    test_final_data()
