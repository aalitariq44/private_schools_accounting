#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ميزة حذف المعلمين/الموظفين مع رواتبهم
"""

from core.database.connection import db_manager
import logging

def test_teacher_salary_count():
    """اختبار عدد الرواتب للمعلمين"""
    print("=== اختبار عدد الرواتب للمعلمين ===")
    
    # البحث عن معلم له رواتب
    query = """
        SELECT t.id, t.name, COUNT(s.id) as salary_count
        FROM teachers t
        LEFT JOIN salaries s ON s.staff_type = 'teacher' AND s.staff_id = t.id
        GROUP BY t.id, t.name
        HAVING salary_count > 0
        LIMIT 3
    """
    
    teachers_with_salaries = db_manager.execute_query(query)
    
    if teachers_with_salaries:
        print("المعلمون الذين لديهم رواتب:")
        for teacher in teachers_with_salaries:
            print(f"- ID: {teacher['id']}, الاسم: {teacher['name']}, عدد الرواتب: {teacher['salary_count']}")
    else:
        print("لا يوجد معلمون لديهم رواتب")
    
    print()

def test_employee_salary_count():
    """اختبار عدد الرواتب للموظفين"""
    print("=== اختبار عدد الرواتب للموظفين ===")
    
    # البحث عن موظف له رواتب
    query = """
        SELECT e.id, e.name, COUNT(s.id) as salary_count
        FROM employees e
        LEFT JOIN salaries s ON s.staff_type = 'employee' AND s.staff_id = e.id
        GROUP BY e.id, e.name
        HAVING salary_count > 0
        LIMIT 3
    """
    
    employees_with_salaries = db_manager.execute_query(query)
    
    if employees_with_salaries:
        print("الموظفون الذين لديهم رواتب:")
        for employee in employees_with_salaries:
            print(f"- ID: {employee['id']}, الاسم: {employee['name']}, عدد الرواتب: {employee['salary_count']}")
    else:
        print("لا يوجد موظفون لديهم رواتب")
    
    print()

def test_salary_deletion_check():
    """اختبار منطق فحص الرواتب قبل الحذف"""
    print("=== اختبار منطق فحص الرواتب ===")
    
    # اختبار المعلم
    teacher_query = "SELECT COUNT(*) as count FROM salaries WHERE staff_type = 'teacher' AND staff_id = ?"
    
    # جرب معلم موجود
    teachers = db_manager.execute_query("SELECT id FROM teachers LIMIT 1")
    if teachers:
        teacher_id = teachers[0]['id']
        salary_result = db_manager.execute_query(teacher_query, (teacher_id,))
        salary_count = salary_result[0]['count'] if salary_result else 0
        print(f"المعلم ID {teacher_id} لديه {salary_count} راتب")
    
    # اختبار الموظف
    employee_query = "SELECT COUNT(*) as count FROM salaries WHERE staff_type = 'employee' AND staff_id = ?"
    
    # جرب موظف موجود
    employees = db_manager.execute_query("SELECT id FROM employees LIMIT 1")
    if employees:
        employee_id = employees[0]['id']
        salary_result = db_manager.execute_query(employee_query, (employee_id,))
        salary_count = salary_result[0]['count'] if salary_result else 0
        print(f"الموظف ID {employee_id} لديه {salary_count} راتب")

def main():
    """تشغيل كافة الاختبارات"""
    print("🧪 بدء اختبار ميزة حذف المعلمين/الموظفين مع رواتبهم")
    print("=" * 60)
    
    try:
        test_teacher_salary_count()
        test_employee_salary_count()
        test_salary_deletion_check()
        
        print("✅ تم الانتهاء من كافة الاختبارات بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبارات: {e}")
        logging.error(f"خطأ في اختبار ميزة الحذف: {e}")

if __name__ == "__main__":
    main()
