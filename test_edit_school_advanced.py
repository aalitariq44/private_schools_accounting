#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تعديل المدرسة في الإعدادات المتقدمة
"""

import logging
import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from core.database.connection import db_manager

def test_edit_school_function():
    """اختبار جلب بيانات المدرسة للتعديل"""
    try:
        print("=== اختبار تعديل المدرسة في الإعدادات المتقدمة ===")
        
        # استعلام لجلب أول مدرسة
        query = """
            SELECT id, name_ar, name_en, principal_name, phone, address, 
                   school_types, logo_path, created_at
            FROM schools 
            LIMIT 1
        """
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                school_id = result[0]
                print(f"✅ تم العثور على المدرسة بالمعرف: {school_id}")
                
                # تحويل النتيجة إلى قاموس
                school_data = {
                    'id': result[0],
                    'name_ar': result[1],
                    'name_en': result[2],
                    'principal_name': result[3],
                    'phone': result[4],
                    'address': result[5],
                    'school_types': result[6],
                    'logo_path': result[7],
                    'created_at': result[8]
                }
                
                print("✅ بيانات المدرسة:")
                for key, value in school_data.items():
                    print(f"   {key}: {value}")
                
                print("\n✅ الاختبار نجح - يمكن جلب بيانات المدرسة للتعديل")
                return True
            else:
                print("❌ لم يتم العثور على أي مدرسة في قاعدة البيانات")
                return False
                
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

if __name__ == "__main__":
    test_edit_school_function()
