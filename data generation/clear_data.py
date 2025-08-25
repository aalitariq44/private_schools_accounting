#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت حذف البيانات التجريبية وتصفير قاعدة البيانات
يقوم بحذف جميع البيانات من كل الجداول وإعادة تهيئة قاعدة البيانات
"""

import sqlite3
from pathlib import Path
import sys
import os

# إضافة مسار المشروع الجذر
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import config
    from core.database.connection import db_manager
except ImportError as e:
    print(f"❌ خطأ في استيراد الوحدات: {e}")
    print("⚠️ تأكد من أن الملف موجود في مجلد المشروع الصحيح")
    print(f"📁 المسار المتوقع: {project_root}")
    sys.exit(1)

class TestDataCleaner:
    """مُنظف البيانات التجريبية"""
    
    def __init__(self):
        """تهيئة المُنظف"""
        self.db_manager = db_manager
        
        # ترتيب الجداول حسب التبعيات (من التابع إلى الأساسي)
        self.tables_order = [
            'salaries',           # رواتب الموظفين والمعلمين
            'expenses',           # مصروفات المدارس
            'external_income',    # الإيرادات الخارجية
            'additional_fees',    # الرسوم الإضافية للطلاب
            'installments',       # أقساط الطلاب
            'employees',          # موظفين المدارس
            'teachers',           # معلمين المدارس
            'students',           # طلاب المدارس
            'schools'             # المدارس (الجدول الأساسي)
        ]
    
    def get_table_counts(self):
        """الحصول على عدد السجلات في كل جدول"""
        print("📊 فحص البيانات الحالية في قاعدة البيانات...")
        
        counts = {}
        total_records = 0
        
        try:
            for table in reversed(self.tables_order):  # عرض بالترتيب المنطقي
                try:
                    result = self.db_manager.execute_fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                    count = result['count'] if result else 0
                    counts[table] = count
                    total_records += count
                    
                    if count > 0:
                        print(f"   📋 {table}: {count:,} سجل")
                    else:
                        print(f"   ⭕ {table}: فارغ")
                        
                except Exception as e:
                    print(f"   ❌ خطأ في فحص جدول {table}: {e}")
                    counts[table] = 0
            
            print(f"\n📈 إجمالي السجلات: {total_records:,} سجل")
            return counts, total_records
            
        except Exception as e:
            print(f"❌ خطأ في فحص البيانات: {e}")
            return {}, 0
    
    def confirm_deletion(self, total_records):
        """طلب تأكيد الحذف من المستخدم"""
        if total_records == 0:
            print("ℹ️ قاعدة البيانات فارغة بالفعل، لا توجد بيانات للحذف.")
            return False
        
        print(f"\n⚠️ تحذير: سيتم حذف {total_records:,} سجل من قاعدة البيانات!")
        print("⚠️ هذه العملية لا يمكن التراجع عنها!")
        
        while True:
            choice = input("\n❓ هل تريد المتابعة؟ (نعم/ن) أو (لا/ل) للإلغاء: ").strip().lower()
            
            if choice in ['نعم', 'ن', 'yes', 'y']:
                return True
            elif choice in ['لا', 'ل', 'no', 'n']:
                return False
            else:
                print("⚠️ يرجى إدخال 'نعم' أو 'لا'")
    
    def clear_table(self, table_name):
        """حذف بيانات جدول محدد"""
        try:
            # التحقق من وجود الجدول
            result = self.db_manager.execute_fetch_one(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                (table_name,)
            )
            
            if not result:
                print(f"   ⚠️ الجدول {table_name} غير موجود")
                return False
            
            # الحصول على عدد السجلات قبل الحذف
            count_result = self.db_manager.execute_fetch_one(f"SELECT COUNT(*) as count FROM {table_name}")
            count_before = count_result['count'] if count_result else 0
            
            if count_before == 0:
                print(f"   ⭕ الجدول {table_name} فارغ بالفعل")
                return True
            
            # حذف البيانات
            self.db_manager.execute_query(f"DELETE FROM {table_name}")
            
            # التحقق من الحذف
            count_result = self.db_manager.execute_fetch_one(f"SELECT COUNT(*) as count FROM {table_name}")
            count_after = count_result['count'] if count_result else 0
            
            if count_after == 0:
                print(f"   ✅ تم حذف {count_before:,} سجل من جدول {table_name}")
                return True
            else:
                print(f"   ⚠️ لم يتم حذف جميع السجلات من جدول {table_name} (متبقي: {count_after})")
                return False
                
        except Exception as e:
            print(f"   ❌ خطأ في حذف جدول {table_name}: {e}")
            return False
    
    def reset_auto_increment(self, table_name):
        """إعادة تعيين قيم الترقيم التلقائي"""
        try:
            # في SQLite، نحذف من sqlite_sequence لإعادة تعيين AUTOINCREMENT
            self.db_manager.execute_query(
                "DELETE FROM sqlite_sequence WHERE name = ?", 
                (table_name,)
            )
            print(f"   🔄 تم إعادة تعيين الترقيم التلقائي لجدول {table_name}")
            return True
            
        except Exception as e:
            # إذا لم يكن هناك sqlite_sequence، فهذا طبيعي
            if "no such table: sqlite_sequence" not in str(e).lower():
                print(f"   ⚠️ تحذير في إعادة تعيين الترقيم لجدول {table_name}: {e}")
            return False
    
    def clear_all_data(self):
        """حذف جميع البيانات من قاعدة البيانات"""
        print("🗑️ بدء عملية حذف البيانات...")
        
        success_count = 0
        total_deleted = 0
        
        try:
            # تعطيل فحص المفاتيح الأجنبية مؤقتاً لتجنب مشاكل التبعيات
            with self.db_manager.get_cursor() as cursor:
                cursor.execute("PRAGMA foreign_keys = OFF")
                print("   🔓 تم تعطيل فحص المفاتيح الأجنبية مؤقتاً")
            
            # حذف البيانات من كل جدول حسب الترتيب
            for table in self.tables_order:
                print(f"\n🔄 معالجة جدول {table}...")
                
                if self.clear_table(table):
                    success_count += 1
                    # إعادة تعيين الترقيم التلقائي
                    self.reset_auto_increment(table)
            
            # إعادة تفعيل فحص المفاتيح الأجنبية
            with self.db_manager.get_cursor() as cursor:
                cursor.execute("PRAGMA foreign_keys = ON")
                print("\n   🔒 تم إعادة تفعيل فحص المفاتيح الأجنبية")
            
            print(f"\n✅ تم حذف البيانات بنجاح من {success_count}/{len(self.tables_order)} جدول")
            
            return success_count == len(self.tables_order)
            
        except Exception as e:
            print(f"❌ خطأ عام في حذف البيانات: {e}")
            
            # محاولة إعادة تفعيل المفاتيح الأجنبية في حالة الخطأ
            try:
                with self.db_manager.get_cursor() as cursor:
                    cursor.execute("PRAGMA foreign_keys = ON")
            except:
                pass
            
            return False
    
    def vacuum_database(self):
        """تنظيف قاعدة البيانات وتحسينها"""
        print("🧹 تنظيف قاعدة البيانات وتحسينها...")
        
        try:
            # VACUUM يقوم بإعادة بناء قاعدة البيانات وتقليل حجمها
            self.db_manager.execute_query("VACUUM")
            print("   ✅ تم تنظيف قاعدة البيانات بنجاح")
            
            # ANALYZE يقوم بتحديث إحصائيات الاستعلامات
            self.db_manager.execute_query("ANALYZE")
            print("   ✅ تم تحديث إحصائيات قاعدة البيانات")
            
            return True
            
        except Exception as e:
            print(f"   ⚠️ تحذير في تنظيف قاعدة البيانات: {e}")
            return False
    
    def verify_cleanup(self):
        """التحقق من نجاح عملية التنظيف"""
        print("\n🔍 التحقق من نجاح عملية التنظيف...")
        
        counts, total_records = self.get_table_counts()
        
        if total_records == 0:
            print("✅ تم تنظيف قاعدة البيانات بالكامل!")
            print("🎯 قاعدة البيانات جاهزة للاستخدام من جديد")
            return True
        else:
            print(f"⚠️ لا تزال هناك {total_records:,} سجل في قاعدة البيانات")
            
            # عرض الجداول التي لا تزال تحتوي على بيانات
            print("📋 الجداول التي لا تزال تحتوي على بيانات:")
            for table, count in counts.items():
                if count > 0:
                    print(f"   • {table}: {count:,} سجل")
            
            return False
    
    def get_database_info(self):
        """عرض معلومات قاعدة البيانات"""
        print("ℹ️ معلومات قاعدة البيانات:")
        
        try:
            # معلومات ملف قاعدة البيانات
            db_path = Path(config.DATABASE_PATH)
            if db_path.exists():
                size_bytes = db_path.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                print(f"   📁 المسار: {db_path}")
                print(f"   📏 الحجم: {size_mb:.2f} MB ({size_bytes:,} bytes)")
            else:
                print(f"   📁 المسار: {db_path} (غير موجود)")
            
            # عدد الجداول
            tables = self.db_manager.execute_fetch_all(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            print(f"   🗃️ عدد الجداول: {len(tables) if tables else 0}")
            
        except Exception as e:
            print(f"   ❌ خطأ في الحصول على معلومات قاعدة البيانات: {e}")
    
    def clean_database(self):
        """تشغيل عملية التنظيف الكاملة"""
        print("🚀 بدء عملية تنظيف قاعدة البيانات...")
        
        try:
            # تهيئة قاعدة البيانات
            self.db_manager.initialize_database()
            
            # عرض معلومات قاعدة البيانات
            self.get_database_info()
            
            # فحص البيانات الحالية
            counts, total_records = self.get_table_counts()
            
            # طلب تأكيد الحذف
            if not self.confirm_deletion(total_records):
                print("🚫 تم إلغاء عملية الحذف")
                return False
            
            print("\n" + "="*50)
            print("🔥 بدء عملية الحذف...")
            print("="*50)
            
            # حذف جميع البيانات
            if self.clear_all_data():
                print("\n" + "="*50)
                print("🧹 تنظيف قاعدة البيانات...")
                print("="*50)
                
                # تنظيف قاعدة البيانات
                self.vacuum_database()
                
                # التحقق من نجاح التنظيف
                success = self.verify_cleanup()
                
                print("\n" + "="*50)
                if success:
                    print("🎉 تم تنظيف قاعدة البيانات بنجاح!")
                    print("✨ قاعدة البيانات الآن فارغة وجاهزة للاستخدام")
                else:
                    print("⚠️ تم تنظيف معظم البيانات ولكن قد تبقى بعض السجلات")
                print("="*50)
                
                return success
            else:
                print("\n❌ فشلت عملية حذف البيانات")
                return False
                
        except Exception as e:
            print(f"❌ خطأ عام في تنظيف قاعدة البيانات: {e}")
            return False


def main():
    """الدالة الرئيسية"""
    print("="*60)
    print("🗑️ مُنظف البيانات التجريبية - نظام حسابات المدارس الأهلية")
    print("="*60)
    
    try:
        cleaner = TestDataCleaner()
        success = cleaner.clean_database()
        
        if success:
            print("\n✅ تمت عملية التنظيف بنجاح!")
            print("📱 يمكنك الآن تشغيل مولد البيانات التجريبية أو استخدام التطبيق")
        else:
            print("\n⚠️ لم تكتمل عملية التنظيف بالكامل")
            print("🔄 قد تحتاج لإعادة تشغيل المُنظف أو فحص المشكلة يدوياً")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف العملية من قبل المستخدم")
        return 1
    except Exception as e:
        print(f"❌ خطأ في تشغيل المُنظف: {e}")
        return 1


if __name__ == "__main__":
    exit(main())