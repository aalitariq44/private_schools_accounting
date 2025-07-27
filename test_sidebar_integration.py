#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ربط الصفحات الجديدة بالشريط الجانبي
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """اختبار استيراد الصفحات الجديدة"""
    try:
        # اختبار استيراد الواردات الخارجية
        from ui.pages.external_income.external_income_page import ExternalIncomePage
        print("✅ تم استيراد صفحة الواردات الخارجية بنجاح")
        
        # اختبار استيراد المصروفات
        from ui.pages.expenses.expenses_page import ExpensesPage
        print("✅ تم استيراد صفحة المصروفات بنجاح")
        
        # اختبار استيراد الحزم
        from ui.pages.external_income import ExternalIncomePage as EI
        from ui.pages.expenses import ExpensesPage as E
        print("✅ تم استيراد الحزم بنجاح")
        
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        return False

def test_main_window_integration():
    """اختبار تكامل النافذة الرئيسية"""
    try:
        from app.main_window import MainWindow
        
        # التحقق من وجود دوال تحميل الصفحات
        if hasattr(MainWindow, 'load_external_income_page'):
            print("✅ دالة تحميل الواردات الخارجية موجودة")
        else:
            print("❌ دالة تحميل الواردات الخارجية غير موجودة")
            
        if hasattr(MainWindow, 'load_expenses_page'):
            print("✅ دالة تحميل المصروفات موجودة")
        else:
            print("❌ دالة تحميل المصروفات غير موجودة")
            
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار النافذة الرئيسية: {e}")
        return False

def test_database_tables():
    """اختبار إنشاء جداول قاعدة البيانات"""
    try:
        from core.database.connection import db_manager
        
        # اختبار إنشاء جدول الواردات الخارجية
        create_income_table = """
            CREATE TABLE IF NOT EXISTS external_income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                category VARCHAR(100),
                income_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id)
            )
        """
        
        # اختبار إنشاء جدول المصروفات
        create_expenses_table = """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                category VARCHAR(100),
                supplier VARCHAR(255),
                expense_date DATE NOT NULL,
                payment_method VARCHAR(50),
                reference_number VARCHAR(100),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id)
            )
        """
        
        db_manager.execute_update(create_income_table)
        print("✅ تم إنشاء جدول الواردات الخارجية")
        
        db_manager.execute_update(create_expenses_table)
        print("✅ تم إنشاء جدول المصروفات")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء جداول قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    print("🔍 اختبار ربط الصفحات الجديدة...")
    print("=" * 50)
    
    print("\n1. اختبار الاستيرادات:")
    test_imports()
    
    print("\n2. اختبار تكامل النافذة الرئيسية:")
    test_main_window_integration()
    
    print("\n3. اختبار جداول قاعدة البيانات:")
    test_database_tables()
    
    print("\n" + "=" * 50)
    print("✨ اكتمل الاختبار!")
    print("\n💡 لتشغيل التطبيق:")
    print("   python main.py")
    print("\n📚 للمزيد من المعلومات:")
    print("   راجع ملف NEW_SECTIONS_README.md")
