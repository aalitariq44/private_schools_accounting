#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت ملء قاعدة البيانات ببيانات تجريبية شاملة
يتضمن المدارس والطلاب والمعلمين والموظفين والأقساط والرسوم الإضافية والمصروفات والإيرادات
"""

import sqlite3
import random
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import sys
import os

# إضافة مسار المشروع (دليل المشروع الرئيسي)
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))  # Set CWD to project root for imports

import importlib.util
spec = importlib.util.spec_from_file_location("config", project_root / "config.py")
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
from core.database.connection import db_manager

class TestDataGenerator:
    """مولد البيانات التجريبية"""
    
    def __init__(self):
        """تهيئة المولد"""
        self.db_manager = db_manager
        
        # قائمة أسماء الولد (24 اسم)
        self.boy_names = [
            "أحمد", "محمد", "علي", "حسين", "عمر", "خالد", "عبدالله",
            "يوسف", "إبراهيم", "إسماعيل", "سلمان", "سعيد", "راشد", "فهد", "طلال",
            "ناصر", "صالح", "عادل", "فاروق", "جميل", "كريم", "منير", "نهاد"
        ]
        
        # قائمة أسماء البنات (24 اسم)
        self.girl_names = [
            "فاطمة", "زينب", "مريم", "عائشة", "خديجة", "آمنة", "هند", "رقية",
            "أم كلثوم", "سارة", "نور", "ليلى", "هدى", "رنا", "سلمى", "نادية",
            "إيمان", "لبنى", "غادة", "سهى", "فرح", "أسماء", "رغد", "دينا"
        ]
        
        # مجموعة لتتبع الأسماء المستخدمة لتجنب التكرار
        self.used_names = set()
        
        # أسماء الطلاب والمعلمين والموظفين (ثلاثية) - سيتم توليدها ديناميكياً
        self.names = []  # سيتم ملؤها لاحقاً إذا لزم الأمر
        
        # أنواع الوظائف للموظفين
        self.job_types = [
            "محاسب", "كاتب", "عامل نظافة", "حارس أمن", "سائق", 
            "مشرف", "أمين مكتبة", "فني كمبيوتر", "مسؤول صيانة", "مرشد تربوي"
        ]
        
        # أنواع المصروفات
        self.expense_types = [
            "رواتب المعلمين", "رواتب الموظفين", "فواتير الكهرباء", "فواتير الماء",
            "صيانة المباني", "قرطاسية", "معدات مكتبية", "وقود السيارات",
            "مواد تنظيف", "أدوات مدرسية", "صيانة الحاسوب", "الإنترنت"
        ]
        
        # فئات الإيرادات الخارجية
        # تحديث: فئات الإيرادات الخارجية طبقًا للصورة
        self.income_categories = [
            "الحانوت", "النقل", "الأنشطة", "التبرعات", "إيجارات", "أخرى"
        ]
        
        # أنواع الرسوم الإضافية
        self.additional_fee_types = [
            "رسوم التسجيل", "الزي المدرسي", "الكتب", "القرطاسية", "رسوم النشاطات"
        ]
        
        # الصفوف لكل نوع مدرسة
        self.grades = {
            "ابتدائية": ["الأول الابتدائي", "الثاني الابتدائي", "الثالث الابتدائي", 
                        "الرابع الابتدائي", "الخامس الابتدائي", "السادس الابتدائي"],
            "متوسطة": ["الأول المتوسط", "الثاني المتوسط", "الثالث المتوسط"],
            "إعدادية": ["الرابع العلمي", "الرابع الأدبي", "الخامس العلمي", 
                       "الخامس الأدبي", "السادس العلمي", "السادس الأدبي"]
        }
        # الشعب
        self.sections = ["أ", "ب"]
        
    def generate_unique_name(self, gender=None):
        """توليد اسم ثلاثي فريد بدون تكرار"""
        max_attempts = 1000  # لتجنب حلقة لا نهائية
        attempts = 0
        
        while attempts < max_attempts:
            # اختيار الاسم الأول حسب الجنس
            if gender == "ذكر":
                first_name = random.choice(self.boy_names)
            elif gender == "أنثى":
                first_name = random.choice(self.girl_names)
            else:
                # للمعلمين والموظفين بدون جنس محدد
                first_name = random.choice(self.boy_names + self.girl_names)
            
            # الاسم الثاني والثالث من قائمة الولد فقط
            second_name = random.choice(self.boy_names)
            third_name = random.choice(self.boy_names)
            
            # تجميع الاسم الكامل
            full_name = f"{first_name} {second_name} {third_name}"
            
            # التحقق من عدم التكرار
            if full_name not in self.used_names:
                self.used_names.add(full_name)
                return full_name
            
            attempts += 1
        
        # إذا فشلنا في العثور على اسم فريد، نضيف رقم
        first_name = random.choice(self.boy_names + self.girl_names)
        second_name = random.choice(self.boy_names)
        third_name = random.choice(self.boy_names)
        unique_name = f"{first_name} {second_name} {third_name} {len(self.used_names) + 1}"
        self.used_names.add(unique_name)
        return unique_name
        
    def clear_all_data(self):
        """حذف جميع البيانات الموجودة"""
        print("🗑️ حذف البيانات الموجودة...")
        
        tables = ['salaries', 'expenses', 'external_income', 'employees', 'teachers',
                 'additional_fees', 'installments', 'students', 'schools']
        
        try:
            with self.db_manager.get_cursor() as cursor:
                # تعطيل فحص المفاتيح الأجنبية مؤقتاً
                cursor.execute("PRAGMA foreign_keys = OFF")
                
                for table in tables:
                    cursor.execute(f"DELETE FROM {table}")
                    print(f"   ✅ تم حذف بيانات جدول {table}")
                
                # إعادة تفعيل فحص المفاتيح الأجنبية
                cursor.execute("PRAGMA foreign_keys = ON")
                
            print("✅ تم حذف جميع البيانات بنجاح")
            
        except Exception as e:
            print(f"❌ خطأ في حذف البيانات: {e}")
            raise
    
    def create_schools(self):
        """إنشاء المدارس الثلاث"""
        print("🏫 إنشاء المدارس...")
        
        schools_data = [
            {
                "name_ar": "مدرسة سومر الابتدائية",
                "name_en": "Sumer Elementary School",
                "school_types": ",".join(["ابتدائية"]),
                "principal_name": self.generate_unique_name("ذكر"),
                "address": "حي الجامعة - شارع الكندي - بغداد",
                "phone": "07710995922 - 07810454344"
            },
            {
                "name_ar": "ثانوية سومر للبنات",
                "name_en": "Sumer Girls High School",
                "school_types": ",".join(["متوسطة", "إعدادية"]),
                "principal_name": self.generate_unique_name("أنثى"),
                "address": "حي الجامعة - شارع الكندي - بغداد",
                "phone": "07721556789 - 07821667890"
            },
            {
                "name_ar": "ثانوية سومر للبنين",
                "name_en": "Sumer Boys High School", 
                "school_types": ",".join(["متوسطة", "إعدادية"]),
                "principal_name": self.generate_unique_name("ذكر"),
                "address": "حي الجامعة - شارع الكندي - بغداد",
                "phone": "07731778901 - 07831889012"
            }
        ]
        
        school_ids = []
        try:
            for school in schools_data:
                query = """
                    INSERT INTO schools (name_ar, name_en, school_types, principal_name, address, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                school_id = self.db_manager.execute_insert(
                    query, 
                    (school["name_ar"], school["name_en"], school["school_types"], 
                     school["principal_name"], school["address"], school["phone"])
                )
                school_ids.append(school_id)
                print(f"   ✅ تم إنشاء {school['name_ar']} (ID: {school_id})")
            
            print(f"✅ تم إنشاء {len(school_ids)} مدارس بنجاح")
            return school_ids
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء المدارس: {e}")
            raise
    
    def create_students(self, school_ids):
        """إنشاء الطلاب لكل مدرسة"""
        print("👨‍🎓 إنشاء الطلاب...")
        
        # معلومات المدارس
        schools_info = [
            {"id": school_ids[0], "name": "مدرسة سومر الابتدائية", "types": ["ابتدائية"], "students_count": 45},
            {"id": school_ids[1], "name": "ثانوية سومر للبنات", "types": ["متوسطة", "إعدادية"], "students_count": 50},
            {"id": school_ids[2], "name": "ثانوية سومر للبنين", "types": ["متوسطة", "إعدادية"], "students_count": 48}
        ]
        
        student_ids = []
        
        try:
            for school in schools_info:
                print(f"   📝 إنشاء طلاب {school['name']}...")
                
                # تحديد الصفوف المتاحة
                available_grades = []
                for school_type in school["types"]:
                    available_grades.extend(self.grades[school_type])
                
                # تحديد الجنس حسب المدرسة
                if "للبنات" in school["name"]:
                    gender = "أنثى"
                elif "للبنين" in school["name"]:
                    gender = "ذكر"
                else:  # ابتدائية مختلطة
                    gender = None  # سيتم تحديده عشوائياً
                
                for i in range(school["students_count"]):
                    # تحديد الجنس
                    if gender is None:
                        student_gender = random.choice(["ذكر", "أنثى"])
                    else:
                        student_gender = gender
                    
                    name = self.generate_unique_name(student_gender)
                    grade = random.choice(available_grades)
                    section = random.choice(self.sections)
                    
                    # تحديد الرسوم حسب الصف
                    if grade in ["الأول الابتدائي", "الثاني الابتدائي", "الثالث الابتدائي"]:
                        total_fee = 500000
                    elif grade in ["الرابع الابتدائي", "الخامس الابتدائي", "السادس الابتدائي"]:
                        total_fee = 600000
                    elif grade == "الأول المتوسط":
                        total_fee = 800000
                    elif grade == "الثاني المتوسط":
                        total_fee = 850000
                    elif grade == "الثالث المتوسط":
                        total_fee = 900000
                    elif grade in ["الرابع العلمي", "الرابع الأدبي"]:
                        total_fee = 1000000
                    elif grade in ["الخامس العلمي", "الخامس الأدبي"]:
                        total_fee = 1250000
                    elif grade in ["السادس العلمي", "السادس الأدبي"]:
                        total_fee = 1500000
                    else:
                        total_fee = 0  # قيمة افتراضية
                    
                    # تاريخ مباشرة حديث
                    start_date = date(2025, random.randint(8, 12), random.randint(1, 28))
                    
                    # رقم هاتف عراقي
                    phone = f"077{random.randint(10000000, 99999999)}"
                    
                    # إدخال بيانات الطالب
                    query = """
                        INSERT INTO students (name, school_id, grade, section, gender, phone, 
                                            total_fee, start_date, academic_year, guardian_name, guardian_phone)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    guardian_name = self.generate_unique_name("ذكر")  # الولي عادة ذكر
                    guardian_phone = f"078{random.randint(10000000, 99999999)}"
                    academic_year = "2025-2026"
                    
                    student_id = self.db_manager.execute_insert(
                        query, 
                        (name, school["id"], grade, section, student_gender, phone,
                         total_fee, start_date, academic_year, guardian_name, guardian_phone)
                    )
                    student_ids.append(student_id)
                
                print(f"   ✅ تم إنشاء {school['students_count']} طالب في {school['name']}")
            
            print(f"✅ تم إنشاء {len(student_ids)} طالب بنجاح")
            return student_ids
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء الطلاب: {e}")
            raise
    
    def create_teachers(self, school_ids):
        """إنشاء المعلمين لكل مدرسة"""
        print("👨‍🏫 إنشاء المعلمين...")
        
        teacher_ids = []
        
        try:
            for school_id in school_ids:
                # عدد المعلمين بين 10-14
                teachers_count = random.randint(10, 14)
                
                for i in range(teachers_count):
                    name = self.generate_unique_name()
                    class_hours = random.randint(10, 14)
                    # اختر راتب ثابت من مبالغ واضحة بزيادات 50,000
                    monthly_salary = random.choice([400000, 450000, 500000, 550000, 600000])
                    phone = f"075{random.randint(10000000, 99999999)}"
                    
                    query = """
                        INSERT INTO teachers (name, school_id, class_hours, monthly_salary, phone)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    
                    teacher_id = self.db_manager.execute_insert(
                        query, (name, school_id, class_hours, monthly_salary, phone)
                    )
                    teacher_ids.append(teacher_id)
                
                print(f"   ✅ تم إنشاء {teachers_count} معلم للمدرسة ID: {school_id}")
            
            print(f"✅ تم إنشاء {len(teacher_ids)} معلم بنجاح")
            return teacher_ids
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء المعلمين: {e}")
            raise
    
    def create_employees(self, school_ids):
        """إنشاء الموظفين لكل مدرسة"""
        print("👨‍💼 إنشاء الموظفين...")
        
        employee_ids = []
        
        try:
            for school_id in school_ids:
                # 10 موظفين لكل مدرسة
                for i in range(10):
                    name = self.generate_unique_name()
                    job_type = random.choice(self.job_types)
                    # اختر راتب ثابت من مبالغ واضحة بزيادات 50,000
                    monthly_salary = random.choice([300000, 350000, 400000, 450000, 500000])
                    phone = f"076{random.randint(10000000, 99999999)}"
                    
                    query = """
                        INSERT INTO employees (name, school_id, job_type, monthly_salary, phone)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    
                    employee_id = self.db_manager.execute_insert(
                        query, (name, school_id, job_type, monthly_salary, phone)
                    )
                    employee_ids.append(employee_id)
                
                print(f"   ✅ تم إنشاء 10 موظفين للمدرسة ID: {school_id}")
            
            print(f"✅ تم إنشاء {len(employee_ids)} موظف بنجاح")
            return employee_ids
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء الموظفين: {e}")
            raise
    
    def create_installments(self, student_ids):
        """إنشاء أقساط للطلاب"""
        print("💰 إنشاء الأقساط...")
        
        installment_ids = []
        
        try:
            for student_id in student_ids:
                # الحصول على معلومات الطالب
                student = self.db_manager.execute_fetch_one(
                    "SELECT total_fee, start_date FROM students WHERE id = ?", 
                    (student_id,)
                )
                
                if not student:
                    continue
                
                total_fee = student['total_fee']
                start_date = datetime.strptime(student['start_date'], '%Y-%m-%d').date()
                
                # تعديل: جعل مبالغ الأقساط أرقاماً واضحة (مضاعف 100,000)
                # تحديد عدد الأقساط (1-4 أقساط)
                installments_count = random.randint(1, 4)
                basic_amount = ((total_fee // installments_count) // 100000) * 100000
                if basic_amount == 0:
                    basic_amount = 100000
                remaining_amount = total_fee - basic_amount * (installments_count - 1)
                for i in range(installments_count):
                    if i == installments_count - 1:
                        amount = remaining_amount
                    else:
                        amount = basic_amount
                    
                    # تاريخ الدفع (بعد تاريخ المباشرة)
                    payment_date = start_date + timedelta(days=random.randint(0, 120))
                    payment_time = f"{random.randint(8, 16):02d}:{random.randint(0, 59):02d}:00"
                    
                    # ملاحظات أحياناً
                    notes = random.choice([None, "قسط نقدي", "قسط مؤجل", "دفعة كاملة"]) if random.random() < 0.3 else None
                    
                    query = """
                        INSERT INTO installments (student_id, amount, payment_date, payment_time, notes)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    
                    installment_id = self.db_manager.execute_insert(
                        query, (student_id, amount, payment_date, payment_time, notes)
                    )
                    installment_ids.append(installment_id)
            
            print(f"✅ تم إنشاء {len(installment_ids)} قسط بنجاح")
            return installment_ids
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء الأقساط: {e}")
            raise
    
    def create_additional_fees(self, student_ids):
        """إنشاء رسوم إضافية لبعض الطلاب"""
        print("📋 إنشاء الرسوم الإضافية...")
        
        additional_fee_ids = []
        
        try:
            # 60% من الطلاب سيكون لديهم رسوم إضافية
            selected_students = random.sample(student_ids, int(len(student_ids) * 0.6))
            
            for student_id in selected_students:
                # عدد الرسوم الإضافية (1-3 رسوم)
                fees_count = random.randint(1, 3)
                
                for i in range(fees_count):
                    fee_type = random.choice(self.additional_fee_types)
                    # تحديد مبلغ الرسوم الثابت بناءً على النوع
                    if fee_type == "رسوم التسجيل":
                        amount = 25000
                    elif fee_type in ["الزي المدرسي", "الكتب"]:
                        amount = 40000
                    elif fee_type == "القرطاسية":
                        amount = 25000
                    elif fee_type == "رسوم النشاطات":
                        amount = 90000
                    else:
                        amount = 0
                    paid = random.choice([True, False])  # 70% مدفوعة
                    payment_date = None
                    
                    if paid:
                        # تاريخ دفع حديث
                        payment_date = date(2025, random.randint(8, 12), random.randint(1, 28))
                    
                    notes = random.choice([None, "مدفوع نقداً", "تم التأجيل", "مستحق"]) if random.random() < 0.4 else None
                    
                    query = """
                        INSERT INTO additional_fees (student_id, fee_type, amount, paid, payment_date, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    
                    fee_id = self.db_manager.execute_insert(
                        query, (student_id, fee_type, amount, paid, payment_date, notes)
                    )
                    additional_fee_ids.append(fee_id)
            
            print(f"✅ تم إنشاء {len(additional_fee_ids)} رسم إضافي بنجاح")
            return additional_fee_ids
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء الرسوم الإضافية: {e}")
            raise
    
    def create_expenses(self, school_ids):
        """إنشاء المصروفات للمدارس"""
        print("📉 إنشاء المصروفات...")
        
        expense_ids = []
        
        try:
            for school_id in school_ids:
                # 15-25 مصروف لكل مدرسة
                expenses_count = random.randint(15, 25)
                
                for i in range(expenses_count):
                    expense_type = random.choice(self.expense_types)
                    # مبلغ المصروف ثابت من خيارات محددة
                    amount = random.choice([50000, 100000, 250000])
                    expense_date = date(2025, random.randint(8, 12), random.randint(1, 28))
                    description = f"مصروف {expense_type} للمدرسة"
                    notes = random.choice([None, "مصروف ضروري", "مصروف عاجل", "مصروف شهري"]) if random.random() < 0.3 else None
                    
                    query = """
                        INSERT INTO expenses (school_id, expense_type, amount, expense_date, description, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    
                    expense_id = self.db_manager.execute_insert(
                        query, (school_id, expense_type, amount, expense_date, description, notes)
                    )
                    expense_ids.append(expense_id)
                
                print(f"   ✅ تم إنشاء {expenses_count} مصروف للمدرسة ID: {school_id}")
            
            print(f"✅ تم إنشاء {len(expense_ids)} مصروف بنجاح")
            return expense_ids
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء المصروفات: {e}")
            raise
    
    def create_external_income(self, school_ids):
        """إنشاء الإيرادات الخارجية للمدارس"""
        print("📈 إنشاء الإيرادات الخارجية...")
        
        income_ids = []
        
        try:
            for school_id in school_ids:
                # 8-15 إيراد خارجي لكل مدرسة
                income_count = random.randint(8, 15)
                
                for i in range(income_count):
                    # اختيار فئة الإيراد من الفئات المحدّثة
                    category = random.choice(self.income_categories)
                    # توليد وصف نوع الإيراد بناءً على الفئة المختارة
                    if category == "الحانوت":
                        income_type = f"أموال {category}"
                    elif category == "النقل":
                        income_type = f"عائدات {category}"
                    elif category == "الأنشطة":
                        income_type = f"عائدات {category}"
                    elif category == "التبرعات":
                        income_type = "تبرعات من مؤسسة"
                    elif category == "إيجارات":
                        income_type = "إيجارات من جهات خارجية"
                    else:
                        income_type = "دخل متفرقة"
                    
                    # مبلغ الإيراد الخارجي ثابت من خيارات محددة
                    amount = random.choice([50000, 100000, 250000])
                    income_date = date(2025, random.randint(8, 12), random.randint(1, 28))
                    title = f"إيراد من {category}"
                    description = f"إيراد خارجي من {category} للمدرسة"
                    notes = random.choice([None, "إيراد إضافي", "إيراد استثنائي", "إيراد شهري"]) if random.random() < 0.3 else None
                    
                    query = """
                        INSERT INTO external_income (school_id, title, amount, category, income_type, 
                                                   description, income_date, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    income_id = self.db_manager.execute_insert(
                        query, (school_id, title, amount, category, income_type, 
                               description, income_date, notes)
                    )
                    income_ids.append(income_id)
                
                print(f"   ✅ تم إنشاء {income_count} إيراد خارجي للمدرسة ID: {school_id}")
            
            print(f"✅ تم إنشاء {len(income_ids)} إيراد خارجي بنجاح")
            return income_ids
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء الإيرادات الخارجية: {e}")
            raise
    
    def create_salary_payments(self, teacher_ids, employee_ids):
        """إنشاء دفعات رواتب للمعلمين والموظفين"""
        print("💳 إنشاء دفعات الرواتب...")
        
        salary_ids = []
        
        try:
            # رواتب المعلمين
            for teacher_id in teacher_ids:
                # الحصول على معلومات المعلم مع المدرسة
                teacher = self.db_manager.execute_fetch_one(
                    "SELECT name, monthly_salary, school_id FROM teachers WHERE id = ?", 
                    (teacher_id,)
                )
                
                if not teacher:
                    continue
                
                # 1-3 دفعات راتب
                payments_count = random.randint(1, 3)
                
                for i in range(payments_count):
                    base_salary = teacher['monthly_salary']
                    paid_amount = random.randint(int(base_salary * 0.5), base_salary)
                    
                    # فترة الراتب
                    from_date = date(2025, random.randint(8, 11), 1)
                    to_date = date(from_date.year, from_date.month, 30)
                    days_count = (to_date - from_date).days + 1
                    
                    # تاريخ الدفع
                    payment_date = to_date + timedelta(days=random.randint(1, 10))
                    payment_time = f"{random.randint(8, 16):02d}:{random.randint(0, 59):02d}:00"
                    
                    notes = random.choice([None, "راتب كامل", "راتب جزئي", "راتب مع مكافأة"]) if random.random() < 0.3 else None
                    
                    query = """
                        INSERT INTO salaries (staff_type, staff_id, base_salary, paid_amount,
                                               from_date, to_date, days_count, payment_date, payment_time, notes, school_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    salary_id = self.db_manager.execute_insert(
                        query, ('teacher', teacher_id, base_salary, paid_amount,
                               from_date, to_date, days_count, payment_date, payment_time, notes, teacher['school_id'])
                    )
                    salary_ids.append(salary_id)
            
            # رواتب الموظفين
            for employee_id in employee_ids:
                # الحصول على معلومات الموظف مع المدرسة
                employee = self.db_manager.execute_fetch_one(
                    "SELECT name, monthly_salary, school_id FROM employees WHERE id = ?", 
                    (employee_id,)
                )
                
                if not employee:
                    continue
                
                # 1-3 دفعات راتب
                payments_count = random.randint(1, 3)
                
                for i in range(payments_count):
                    base_salary = employee['monthly_salary']
                    paid_amount = random.randint(int(base_salary * 0.5), base_salary)
                    
                    # فترة الراتب
                    from_date = date(2025, random.randint(8, 11), 1)
                    to_date = date(from_date.year, from_date.month, 30)
                    days_count = (to_date - from_date).days + 1
                    
                    # تاريخ الدفع
                    payment_date = to_date + timedelta(days=random.randint(1, 10))
                    payment_time = f"{random.randint(8, 16):02d}:{random.randint(0, 59):02d}:00"
                    
                    notes = random.choice([None, "راتب كامل", "راتب جزئي", "راتب مع علاوة"]) if random.random() < 0.3 else None
                    
                    query = """
                        INSERT INTO salaries (staff_type, staff_id, base_salary, paid_amount,
                                            from_date, to_date, days_count, payment_date, payment_time, notes, school_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    salary_id = self.db_manager.execute_insert(
                        query, ('employee', employee_id, base_salary, paid_amount,
                               from_date, to_date, days_count, payment_date, payment_time, notes, employee['school_id'])
                    )
                    salary_ids.append(salary_id)
            
            print(f"✅ تم إنشاء {len(salary_ids)} دفعة راتب بنجاح")
            return salary_ids
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء دفعات الرواتب: {e}")
            raise
    
    def print_summary(self):
        """طباعة ملخص البيانات المُدخلة"""
        print("\n" + "="*50)
        print("📊 ملخص البيانات التجريبية المُدخلة")
        print("="*50)
        
        try:
            # إحصائيات المدارس
            schools_count = self.db_manager.execute_fetch_one("SELECT COUNT(*) as count FROM schools")['count']
            print(f"🏫 المدارس: {schools_count}")
            
            # إحصائيات الطلاب
            students_count = self.db_manager.execute_fetch_one("SELECT COUNT(*) as count FROM students")['count']
            total_fees = self.db_manager.execute_fetch_one("SELECT SUM(total_fee) as total FROM students")['total'] or 0
            print(f"👨‍🎓 الطلاب: {students_count}")
            print(f"💰 إجمالي الرسوم الدراسية: {total_fees:,} دينار")
            
            # إحصائيات المعلمين
            teachers_count = self.db_manager.execute_fetch_one("SELECT COUNT(*) as count FROM teachers")['count']
            teachers_salaries = self.db_manager.execute_fetch_one("SELECT SUM(monthly_salary) as total FROM teachers")['total'] or 0
            print(f"👨‍🏫 المعلمين: {teachers_count}")
            print(f"💵 رواتب المعلمين الشهرية: {teachers_salaries:,} دينار")
            
            # إحصائيات الموظفين
            employees_count = self.db_manager.execute_fetch_one("SELECT COUNT(*) as count FROM employees")['count']
            employees_salaries = self.db_manager.execute_fetch_one("SELECT SUM(monthly_salary) as total FROM employees")['total'] or 0
            print(f"👨‍💼 الموظفين: {employees_count}")
            print(f"💵 رواتب الموظفين الشهرية: {employees_salaries:,} دينار")
            
            # إحصائيات الأقساط
            installments_count = self.db_manager.execute_fetch_one("SELECT COUNT(*) as count FROM installments")['count']
            paid_amount = self.db_manager.execute_fetch_one("SELECT SUM(amount) as total FROM installments")['total'] or 0
            print(f"📋 الأقساط المدفوعة: {installments_count}")
            print(f"💳 المبالغ المدفوعة: {paid_amount:,} دينار")
            
            # إحصائيات الرسوم الإضافية
            additional_fees_count = self.db_manager.execute_fetch_one("SELECT COUNT(*) as count FROM additional_fees")['count']
            additional_fees_amount = self.db_manager.execute_fetch_one("SELECT SUM(amount) as total FROM additional_fees")['total'] or 0
            print(f"📄 الرسوم الإضافية: {additional_fees_count}")
            print(f"💰 مبلغ الرسوم الإضافية: {additional_fees_amount:,} دينار")
            
            # إحصائيات المصروفات
            expenses_count = self.db_manager.execute_fetch_one("SELECT COUNT(*) as count FROM expenses")['count']
            expenses_amount = self.db_manager.execute_fetch_one("SELECT SUM(amount) as total FROM expenses")['total'] or 0
            print(f"📉 المصروفات: {expenses_count}")
            print(f"💸 إجمالي المصروفات: {expenses_amount:,} دينار")
            
            # إحصائيات الإيرادات الخارجية
            income_count = self.db_manager.execute_fetch_one("SELECT COUNT(*) as count FROM external_income")['count']
            income_amount = self.db_manager.execute_fetch_one("SELECT SUM(amount) as total FROM external_income")['total'] or 0
            print(f"📈 الإيرادات الخارجية: {income_count}")
            print(f"💹 إجمالي الإيرادات الخارجية: {income_amount:,} دينار")
            
            # إحصائيات الرواتب
            salaries_count = self.db_manager.execute_fetch_one("SELECT COUNT(*) as count FROM salaries")['count']
            salaries_amount = self.db_manager.execute_fetch_one("SELECT SUM(paid_amount) as total FROM salaries")['total'] or 0
            print(f"💳 دفعات الرواتب: {salaries_count}")
            print(f"💰 إجمالي الرواتب المدفوعة: {salaries_amount:,} دينار")
            
            print("\n✅ تم إنشاء جميع البيانات التجريبية بنجاح!")
            print("📱 يمكنك الآن تشغيل التطبيق واستكشاف البيانات")
            
        except Exception as e:
            print(f"❌ خطأ في عرض الملخص: {e}")
    
    def generate_all_data(self):
        """تشغيل جميع عمليات إنشاء البيانات"""
        print("🚀 بدء إنشاء البيانات التجريبية الشاملة...")
        print("⏱️ قد يستغرق هذا بضع دقائق...")
        
        try:
            # تهيئة قاعدة البيانات
            self.db_manager.initialize_database()
            
            # حذف البيانات الموجودة
            self.clear_all_data()
            
            # إنشاء المدارس
            school_ids = self.create_schools()
            
            # إنشاء الطلاب
            student_ids = self.create_students(school_ids)
            
            # إنشاء المعلمين
            teacher_ids = self.create_teachers(school_ids)
            
            # إنشاء الموظفين
            employee_ids = self.create_employees(school_ids)
            
            # إنشاء الأقساط (تم التعطيل حسب طلب المستخدم)
            # self.create_installments(student_ids)
            
            # إنشاء الرسوم الإضافية
            self.create_additional_fees(student_ids)
            
            # إنشاء المصروفات
            self.create_expenses(school_ids)
            
            # إنشاء الإيرادات الخارجية
            self.create_external_income(school_ids)
            
            # إنشاء دفعات الرواتب
            self.create_salary_payments(teacher_ids, employee_ids)
            
            # طباعة الملخص
            self.print_summary()
            
        except Exception as e:
            print(f"❌ خطأ عام في إنشاء البيانات: {e}")
            raise


def main():
    """الدالة الرئيسية"""
    print("="*60)
    print("🎯 مولد البيانات التجريبية لنظام حسابات المدارس الأهلية")
    print("="*60)
    
    try:
        generator = TestDataGenerator()
        generator.generate_all_data()
        
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف العملية من قبل المستخدم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل المولد: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
