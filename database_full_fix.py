#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح شامل لقاعدة البيانات والتطبيق
هذا السكريبت يقوم بتنظيف وإصلاح جميع مشاكل قاعدة البيانات
"""

import sqlite3
import os
import shutil
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseFixer:
    """مدير إصلاح قاعدة البيانات"""
    
    def __init__(self):
        self.db_path = 'data/database/schools.db'
        self.backup_dir = 'data/backups/manual'
        
    def create_backup(self):
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        try:
            if not os.path.exists(self.db_path):
                logging.warning("ملف قاعدة البيانات غير موجود، سيتم إنشاء قاعدة بيانات جديدة")
                return True
                
            # إنشاء مجلد النسخ الاحتياطية
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # اسم النسخة الاحتياطية
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"database_backup_before_fix_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # نسخ قاعدة البيانات
            shutil.copy2(self.db_path, backup_path)
            logging.info(f"تم إنشاء نسخة احتياطية: {backup_path}")
            return True
            
        except Exception as e:
            logging.error(f"فشل في إنشاء النسخة الاحتياطية: {e}")
            return False
    
    def fix_database_schema(self):
        """إصلاح بنية قاعدة البيانات بالكامل"""
        try:
            # التأكد من وجود مجلد قاعدة البيانات
            os.makedirs('data/database', exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            logging.info("بدء إصلاح بنية قاعدة البيانات...")
            
            # 1. إصلاح جدول external_income
            self._fix_external_income_table(cursor)
            
            # 2. إصلاح جدول expenses
            self._fix_expenses_table(cursor)
            
            # 3. إصلاح جدول salaries
            self._fix_salaries_table(cursor)
            
            # 4. إصلاح جدول schools
            self._fix_schools_table(cursor)
            
            # 5. إصلاح جدول students
            self._fix_students_table(cursor)
            
            # 6. إصلاح جدول teachers
            self._fix_teachers_table(cursor)
            
            # 7. إصلاح جدول employees
            self._fix_employees_table(cursor)
            
            # 8. إنشاء الفهارس المطلوبة
            self._create_indexes(cursor)
            
            # 9. تنظيف البيانات
            self._clean_data(cursor)
            
            conn.commit()
            conn.close()
            
            logging.info("تم إصلاح بنية قاعدة البيانات بنجاح!")
            return True
            
        except Exception as e:
            logging.error(f"فشل في إصلاح قاعدة البيانات: {e}")
            return False
    
    def _fix_external_income_table(self, cursor):
        """إصلاح جدول الإيرادات الخارجية"""
        logging.info("إصلاح جدول external_income...")
        
        # إنشاء الجدول إذا لم يكن موجوداً
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS external_income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER NOT NULL,
                title TEXT,
                amount DECIMAL(10,2) NOT NULL,
                category TEXT NOT NULL DEFAULT 'أخرى',
                income_type TEXT NOT NULL,
                description TEXT,
                income_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
            )
        """)
        
        # التحقق من الأعمدة المطلوبة وإضافتها إذا لم تكن موجودة
        cursor.execute("PRAGMA table_info(external_income)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'income_type' not in columns:
            cursor.execute("ALTER TABLE external_income ADD COLUMN income_type TEXT")
            
        if 'description' not in columns:
            cursor.execute("ALTER TABLE external_income ADD COLUMN description TEXT")
        
        # تحديث البيانات الفارغة
        cursor.execute("UPDATE external_income SET income_type = COALESCE(title, 'غير محدد') WHERE income_type IS NULL")
        cursor.execute("UPDATE external_income SET description = income_type WHERE description IS NULL")
        cursor.execute("UPDATE external_income SET category = 'أخرى' WHERE category IS NULL OR category = ''")
        
        logging.info("✓ تم إصلاح جدول external_income")
    
    def _fix_expenses_table(self, cursor):
        """إصلاح جدول المصروفات"""
        logging.info("إصلاح جدول expenses...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER NOT NULL,
                expense_type TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                expense_date DATE NOT NULL,
                description TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
            )
        """)
        
        # التحقق من الأعمدة المطلوبة
        cursor.execute("PRAGMA table_info(expenses)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'description' not in columns:
            cursor.execute("ALTER TABLE expenses ADD COLUMN description TEXT")
            
        # تحديث البيانات
        cursor.execute("UPDATE expenses SET expense_type = 'غير محدد' WHERE expense_type IS NULL")
        cursor.execute("UPDATE expenses SET description = expense_type WHERE description IS NULL")
        
        logging.info("✓ تم إصلاح جدول expenses")
    
    def _fix_salaries_table(self, cursor):
        """إصلاح جدول الرواتب"""
        logging.info("إصلاح جدول salaries...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS salaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                teacher_id INTEGER,
                employee_type TEXT NOT NULL CHECK (employee_type IN ('teacher', 'employee')),
                salary_month TEXT NOT NULL,
                salary_year INTEGER NOT NULL,
                base_salary DECIMAL(10,2) NOT NULL,
                bonuses DECIMAL(10,2) DEFAULT 0,
                deductions DECIMAL(10,2) DEFAULT 0,
                final_salary DECIMAL(10,2) NOT NULL,
                payment_date DATE,
                payment_status TEXT DEFAULT 'غير مدفوع' CHECK (payment_status IN ('مدفوع', 'غير مدفوع')),
                notes TEXT,
                staff_name TEXT,
                staff_type TEXT,
                paid_amount DECIMAL(10,2),
                from_date DATE,
                to_date DATE,
                days_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                CHECK ((employee_id IS NOT NULL AND teacher_id IS NULL) OR (employee_id IS NULL AND teacher_id IS NOT NULL))
            )
        """)
        
        # إضافة الأعمدة المفقودة إذا لم تكن موجودة
        cursor.execute("PRAGMA table_info(salaries)")
        columns = [col[1] for col in cursor.fetchall()]
        
        missing_columns = [
            ('staff_name', 'TEXT'),
            ('staff_type', 'TEXT'),
            ('paid_amount', 'DECIMAL(10,2)'),
            ('from_date', 'DATE'),
            ('to_date', 'DATE'),
            ('days_count', 'INTEGER')
        ]
        
        for column_name, column_type in missing_columns:
            if column_name not in columns:
                cursor.execute(f"ALTER TABLE salaries ADD COLUMN {column_name} {column_type}")
        
        # تحديث البيانات
        cursor.execute("UPDATE salaries SET staff_type = employee_type WHERE staff_type IS NULL")
        cursor.execute("UPDATE salaries SET paid_amount = final_salary WHERE paid_amount IS NULL")
        cursor.execute("UPDATE salaries SET staff_name = 'غير محدد' WHERE staff_name IS NULL OR staff_name = ''")
        
        logging.info("✓ تم إصلاح جدول salaries")
    
    def _fix_schools_table(self, cursor):
        """إصلاح جدول المدارس"""
        logging.info("إصلاح جدول schools...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_ar TEXT NOT NULL,
                name_en TEXT,
                logo_path TEXT,
                address TEXT,
                phone TEXT,
                principal_name TEXT,
                school_types TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logging.info("✓ تم إصلاح جدول schools")
    
    def _fix_students_table(self, cursor):
        """إصلاح جدول الطلاب"""
        logging.info("إصلاح جدول students...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                national_id_number TEXT,
                school_id INTEGER NOT NULL,
                grade TEXT NOT NULL,
                section TEXT NOT NULL,
                academic_year TEXT,
                gender TEXT NOT NULL,
                phone TEXT,
                guardian_name TEXT,
                guardian_phone TEXT,
                total_fee DECIMAL(10,2) NOT NULL,
                start_date DATE NOT NULL,
                status TEXT DEFAULT 'نشط',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
            )
        """)
        
        logging.info("✓ تم إصلاح جدول students")
    
    def _fix_teachers_table(self, cursor):
        """إصلاح جدول المعلمين"""
        logging.info("إصلاح جدول teachers...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                school_id INTEGER NOT NULL,
                class_hours INTEGER NOT NULL DEFAULT 0,
                monthly_salary DECIMAL(10,2) NOT NULL,
                phone TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
            )
        """)
        
        logging.info("✓ تم إصلاح جدول teachers")
    
    def _fix_employees_table(self, cursor):
        """إصلاح جدول الموظفين"""
        logging.info("إصلاح جدول employees...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                school_id INTEGER NOT NULL,
                job_type TEXT NOT NULL CHECK (job_type IN ('عامل', 'حارس', 'كاتب', 'مخصص')),
                monthly_salary DECIMAL(10,2) NOT NULL,
                phone TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
            )
        """)
        
        logging.info("✓ تم إصلاح جدول employees")
    
    def _create_indexes(self, cursor):
        """إنشاء الفهارس المطلوبة"""
        logging.info("إنشاء الفهارس...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_students_school_id ON students(school_id)",
            "CREATE INDEX IF NOT EXISTS idx_students_name ON students(name)",
            "CREATE INDEX IF NOT EXISTS idx_installments_student_id ON installments(student_id)",
            "CREATE INDEX IF NOT EXISTS idx_external_income_school_id ON external_income(school_id)",
            "CREATE INDEX IF NOT EXISTS idx_external_income_date ON external_income(income_date)",
            "CREATE INDEX IF NOT EXISTS idx_expenses_school_id ON expenses(school_id)",
            "CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date)",
            "CREATE INDEX IF NOT EXISTS idx_salaries_employee_type ON salaries(employee_type)",
            "CREATE INDEX IF NOT EXISTS idx_salaries_payment_date ON salaries(payment_date)",
        ]
        
        for index_query in indexes:
            try:
                cursor.execute(index_query)
            except Exception as e:
                logging.warning(f"تحذير في إنشاء فهرس: {e}")
        
        logging.info("✓ تم إنشاء الفهارس")
    
    def _clean_data(self, cursor):
        """تنظيف البيانات"""
        logging.info("تنظيف البيانات...")
        
        # تنظيف البيانات الفارغة والمكررة
        try:
            # تحديث القيم الفارغة في الجداول
            cursor.execute("UPDATE external_income SET notes = NULL WHERE notes = ''")
            cursor.execute("UPDATE expenses SET notes = NULL WHERE notes = ''")
            cursor.execute("UPDATE salaries SET notes = NULL WHERE notes = ''")
            
            logging.info("✓ تم تنظيف البيانات")
            
        except Exception as e:
            logging.warning(f"تحذير في تنظيف البيانات: {e}")
    
    def verify_database(self):
        """التحقق من سلامة قاعدة البيانات بعد الإصلاح"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            logging.info("التحقق من سلامة قاعدة البيانات...")
            
            # فحص تكامل قاعدة البيانات
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            if result[0] != 'ok':
                logging.error(f"مشكلة في تكامل قاعدة البيانات: {result[0]}")
                return False
            
            # التحقق من وجود الجداول الأساسية
            required_tables = [
                'users', 'schools', 'students', 'teachers', 'employees',
                'external_income', 'expenses', 'salaries', 'installments',
                'additional_fees', 'app_settings'
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                logging.warning(f"الجداول المفقودة: {missing_tables}")
            else:
                logging.info("جميع الجداول المطلوبة موجودة")
            
            # اختبار الاستعلامات الأساسية
            test_queries = [
                "SELECT COUNT(*) FROM schools",
                "SELECT COUNT(*) FROM external_income", 
                "SELECT COUNT(*) FROM expenses",
                "SELECT COUNT(*) FROM salaries"
            ]
            
            for query in test_queries:
                try:
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    table_name = query.split()[-1]
                    logging.info(f"جدول {table_name}: {count} سجل")
                except Exception as e:
                    logging.error(f"فشل في اختبار: {query} - {e}")
                    return False
            
            conn.close()
            logging.info("✅ تم التحقق من سلامة قاعدة البيانات بنجاح!")
            return True
            
        except Exception as e:
            logging.error(f"فشل في التحقق من قاعدة البيانات: {e}")
            return False
    
    def run_full_fix(self):
        """تشغيل الإصلاح الشامل"""
        logging.info("=" * 50)
        logging.info("بدء الإصلاح الشامل لقاعدة البيانات")
        logging.info("=" * 50)
        
        # 1. إنشاء نسخة احتياطية
        if not self.create_backup():
            logging.error("فشل في إنشاء النسخة الاحتياطية!")
            return False
        
        # 2. إصلاح بنية قاعدة البيانات
        if not self.fix_database_schema():
            logging.error("فشل في إصلاح بنية قاعدة البيانات!")
            return False
        
        # 3. التحقق من سلامة قاعدة البيانات
        if not self.verify_database():
            logging.error("فشل في التحقق من سلامة قاعدة البيانات!")
            return False
        
        logging.info("=" * 50)
        logging.info("✅ تم إنجاز الإصلاح الشامل بنجاح!")
        logging.info("🎉 قاعدة البيانات جاهزة للاستخدام")
        logging.info("=" * 50)
        
        return True

def main():
    """الدالة الرئيسية"""
    fixer = DatabaseFixer()
    success = fixer.run_full_fix()
    
    if success:
        print("\n🎉 تم إصلاح جميع مشاكل قاعدة البيانات!")
        print("✅ يمكنك الآن تشغيل التطبيق بدون مشاكل")
        print("📁 تم حفظ نسخة احتياطية في: data/backups/manual/")
    else:
        print("\n❌ فشل في إصلاح قاعدة البيانات!")
        print("⚠️  يرجى مراجعة سجل الأخطاء أعلاه")

if __name__ == "__main__":
    main()
