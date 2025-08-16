#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت للتحقق من البيانات التجريبية وعرض تفاصيلها
"""

import sys
from pathlib import Path
import json

# إضافة مسار المشروع
sys.path.insert(0, str(Path(__file__).parent))

from core.database.connection import db_manager

def check_schools_data():
    """فحص بيانات المدارس"""
    print("🏫 فحص بيانات المدارس:")
    print("-" * 40)
    
    schools = db_manager.execute_query("SELECT * FROM schools ORDER BY id")
    
    for school in schools:
        school_types = json.loads(school['school_types'])
        print(f"🏢 ID: {school['id']}")
        print(f"📝 الاسم العربي: {school['name_ar']}")
        print(f"📝 الاسم الإنجليزي: {school['name_en']}")
        print(f"👨‍💼 مدير المدرسة: {school['principal_name']}")
        print(f"📍 العنوان: {school['address']}")
        print(f"📞 الهاتف: {school['phone']}")
        print(f"🎓 أنواع المدرسة: {', '.join(school_types)}")
        
        # إحصائيات الطلاب في هذه المدرسة
        students_count = db_manager.execute_fetch_one(
            "SELECT COUNT(*) as count FROM students WHERE school_id = ?", 
            (school['id'],)
        )['count']
        
        # إحصائيات المعلمين
        teachers_count = db_manager.execute_fetch_one(
            "SELECT COUNT(*) as count FROM teachers WHERE school_id = ?", 
            (school['id'],)
        )['count']
        
        # إحصائيات الموظفين
        employees_count = db_manager.execute_fetch_one(
            "SELECT COUNT(*) as count FROM employees WHERE school_id = ?", 
            (school['id'],)
        )['count']
        
        print(f"👨‍🎓 عدد الطلاب: {students_count}")
        print(f"👨‍🏫 عدد المعلمين: {teachers_count}")
        print(f"👨‍💼 عدد الموظفين: {employees_count}")
        print("")

def check_students_sample():
    """فحص عينة من بيانات الطلاب"""
    print("👨‍🎓 عينة من بيانات الطلاب:")
    print("-" * 40)
    
    # عرض 5 طلاب من كل مدرسة
    schools = db_manager.execute_query("SELECT id, name_ar FROM schools ORDER BY id")
    
    for school in schools:
        print(f"\n🏫 طلاب {school['name_ar']}:")
        students = db_manager.execute_query("""
            SELECT name, grade, section, gender, total_fee, start_date 
            FROM students 
            WHERE school_id = ? 
            ORDER BY grade, section, name 
            LIMIT 5
        """, (school['id'],))
        
        for student in students:
            print(f"   📝 {student['name']} - {student['grade']} {student['section']}")
            print(f"      👤 الجنس: {student['gender']} | 💰 الرسوم: {student['total_fee']:,} دينار")
            print(f"      📅 تاريخ المباشرة: {student['start_date']}")

def check_financial_summary():
    """فحص الملخص المالي"""
    print("\n💰 الملخص المالي التفصيلي:")
    print("-" * 50)
    
    # الإيرادات
    print("📈 الإيرادات:")
    total_student_fees = db_manager.execute_fetch_one(
        "SELECT SUM(total_fee) as total FROM students"
    )['total'] or 0
    
    paid_installments = db_manager.execute_fetch_one(
        "SELECT SUM(amount) as total FROM installments"
    )['total'] or 0
    
    paid_additional_fees = db_manager.execute_fetch_one(
        "SELECT SUM(amount) as total FROM additional_fees WHERE paid = 1"
    )['total'] or 0
    
    external_income = db_manager.execute_fetch_one(
        "SELECT SUM(amount) as total FROM external_income"
    )['total'] or 0
    
    print(f"   💰 إجمالي الرسوم الدراسية: {total_student_fees:,} دينار")
    print(f"   💳 الأقساط المدفوعة: {paid_installments:,} دينار")
    print(f"   📄 الرسوم الإضافية المدفوعة: {paid_additional_fees:,} دينار")
    print(f"   📈 الإيرادات الخارجية: {external_income:,} دينار")
    
    total_income = paid_installments + paid_additional_fees + external_income
    print(f"   🔢 إجمالي الإيرادات الفعلية: {total_income:,} دينار")
    
    # المصروفات
    print("\n📉 المصروفات:")
    total_expenses = db_manager.execute_fetch_one(
        "SELECT SUM(amount) as total FROM expenses"
    )['total'] or 0
    
    paid_salaries = db_manager.execute_fetch_one(
        "SELECT SUM(paid_amount) as total FROM salaries"
    )['total'] or 0
    
    print(f"   💸 المصروفات العامة: {total_expenses:,} دينار")
    print(f"   💵 الرواتب المدفوعة: {paid_salaries:,} دينار")
    
    total_expenses_all = total_expenses + paid_salaries
    print(f"   🔢 إجمالي المصروفات: {total_expenses_all:,} دينار")
    
    # الصافي
    net_income = total_income - total_expenses_all
    print(f"\n💹 صافي الربح/الخسارة: {net_income:,} دينار")
    
    if net_income > 0:
        print("   ✅ المدارس تحقق أرباح")
    else:
        print("   ⚠️ المدارس تواجه خسائر")

def check_grades_distribution():
    """فحص توزيع الطلاب على الصفوف"""
    print("\n📊 توزيع الطلاب على الصفوف:")
    print("-" * 40)
    
    grades_stats = db_manager.execute_query("""
        SELECT grade, COUNT(*) as students_count
        FROM students 
        GROUP BY grade 
        ORDER BY students_count DESC
    """)
    
    for grade in grades_stats:
        print(f"   📚 {grade['grade']}: {grade['students_count']} طالب")

def check_additional_fees_status():
    """فحص حالة الرسوم الإضافية"""
    print("\n📄 حالة الرسوم الإضافية:")
    print("-" * 40)
    
    # الرسوم حسب النوع
    fees_by_type = db_manager.execute_query("""
        SELECT fee_type, COUNT(*) as count, SUM(amount) as total_amount,
               SUM(CASE WHEN paid = 1 THEN amount ELSE 0 END) as paid_amount
        FROM additional_fees 
        GROUP BY fee_type 
        ORDER BY total_amount DESC
    """)
    
    for fee in fees_by_type:
        paid_percentage = (fee['paid_amount'] / fee['total_amount'] * 100) if fee['total_amount'] > 0 else 0
        print(f"   📋 {fee['fee_type']}:")
        print(f"      📊 العدد: {fee['count']} | المبلغ: {fee['total_amount']:,} دينار")
        print(f"      💰 المدفوع: {fee['paid_amount']:,} دينار ({paid_percentage:.1f}%)")

def check_teachers_and_employees():
    """فحص بيانات المعلمين والموظفين"""
    print("\n👥 المعلمين والموظفين:")
    print("-" * 40)
    
    # إحصائيات المعلمين
    teachers_stats = db_manager.execute_query("""
        SELECT s.name_ar as school_name, COUNT(t.id) as teachers_count,
               AVG(t.class_hours) as avg_hours, AVG(t.monthly_salary) as avg_salary
        FROM schools s
        LEFT JOIN teachers t ON s.id = t.school_id
        GROUP BY s.id, s.name_ar
        ORDER BY s.id
    """)
    
    print("👨‍🏫 المعلمين:")
    for school in teachers_stats:
        print(f"   🏫 {school['school_name']}:")
        print(f"      👥 العدد: {school['teachers_count']}")
        print(f"      ⏰ متوسط الحصص: {school['avg_hours']:.1f}")
        print(f"      💰 متوسط الراتب: {school['avg_salary']:,.0f} دينار")
    
    # إحصائيات الموظفين
    employees_stats = db_manager.execute_query("""
        SELECT s.name_ar as school_name, COUNT(e.id) as employees_count,
               AVG(e.monthly_salary) as avg_salary
        FROM schools s
        LEFT JOIN employees e ON s.id = e.school_id
        GROUP BY s.id, s.name_ar
        ORDER BY s.id
    """)
    
    print("\n👨‍💼 الموظفين:")
    for school in employees_stats:
        print(f"   🏫 {school['school_name']}:")
        print(f"      👥 العدد: {school['employees_count']}")
        print(f"      💰 متوسط الراتب: {school['avg_salary']:,.0f} دينار")
    
    # أنواع الوظائف
    job_types = db_manager.execute_query("""
        SELECT job_type, COUNT(*) as count, AVG(monthly_salary) as avg_salary
        FROM employees
        GROUP BY job_type
        ORDER BY count DESC
    """)
    
    print("\n💼 أنواع الوظائف:")
    for job in job_types:
        print(f"   🔧 {job['job_type']}: {job['count']} موظف | متوسط الراتب: {job['avg_salary']:,.0f} دينار")

def main():
    """الدالة الرئيسية"""
    print("="*60)
    print("🔍 فحص البيانات التجريبية لنظام حسابات المدارس الأهلية")
    print("="*60)
    
    try:
        check_schools_data()
        check_students_sample()
        check_financial_summary()
        check_grades_distribution()
        check_additional_fees_status()
        check_teachers_and_employees()
        
        print("\n" + "="*60)
        print("✅ تم فحص جميع البيانات بنجاح!")
        print("🚀 يمكنك الآن تشغيل التطبيق الرئيسي: python main.py")
        print("="*60)
        
    except Exception as e:
        print(f"❌ خطأ في فحص البيانات: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
