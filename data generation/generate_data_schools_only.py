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
        
        # أسماء الطلاب والمعلمين والموظفين (ثلاثية)
        self.names = [
            "علي محمد محمد", "محمد أحمد علي", "رضا حسين صالح", "زينب عباس محمد",
            "فاطمة علي رضا", "محمد محمد علي", "مريم أحمد محمد", "أحمد علي محمد",
            "نور محمد أحمد", "سارة محمد علي", "يوسف محمد رضا", "ليلى أحمد حسين",
            "كريم علي أحمد", "هدى محمد محمد", "عمر أحمد علي", "آية محمد محمد",
            "حسام محمد أحمد", "نسرين علي محمد", "طارق أحمد محمد", "شيماء محمد علي",
            "باسم محمد أحمد", "نورا علي محمد", "سعد محمد محمد", "رنا أحمد علي",
            "ماجد علي محمد", "سلمى محمد أحمد", "وسام أحمد محمد", "دينا محمد علي",
            "خالد محمد أحمد", "منى علي محمد", "عادل أحمد محمد", "رغد محمد علي",
            "صلاح محمد أحمد", "هبة علي محمد", "جعفر محمد محمد", "رباب أحمد علي",
            "حيدر علي أحمد", "نجلاء محمد محمد", "قاسم أحمد محمد", "إيمان محمد علي",
            "مصطفى محمد أحمد", "سميرة علي محمد", "عبدالله أحمد محمد", "لبنى محمد علي",
            "فراس محمد أحمد", "غادة علي محمد", "نبيل محمد محمد", "سهى أحمد علي",
            "كاظم علي أحمد", "فرح محمد محمد", "منير أحمد محمد", "زهراء محمد علي",
            "عدنان محمد أحمد", "وداد علي محمد", "شاكر أحمد محمد", "أسماء محمد علي",
            "رائد محمد أحمد", "نادية علي محمد", "فؤاد محمد محمد", "عبير أحمد علي"
        ]
        
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
                "principal_name": "أحمد محمد علي",
                "address": "حي الجامعة - شارع الكندي - بغداد",
                "phone": "07710995922 - 07810454344"
            },
            {
                "name_ar": "ثانوية سومر للبنات",
                "name_en": "Sumer Girls High School",
                "school_types": ",".join(["متوسطة", "إعدادية"]),
                "principal_name": "فاطمة رضا أحمد",
                "address": "حي الجامعة - شارع الكندي - بغداد",
                "phone": "07721556789 - 07821667890"
            },
            {
                "name_ar": "ثانوية سومر للبنين",
                "name_en": "Sumer Boys High School", 
                "school_types": ",".join(["متوسطة", "إعدادية"]),
                "principal_name": "محمد علي يوسف",
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

            # حذف البيانات الحالية وتوليد المدارس فقط
            self.clear_all_data()
            self.create_schools()
            # طباعة ملخص البيانات
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
