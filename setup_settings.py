#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إضافة بيانات تجريبية للإعدادات
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from core.database.connection import db_manager

def setup_initial_settings():
    """إعداد الإعدادات الأولية"""
    try:
        # تهيئة قاعدة البيانات
        db_manager.initialize_database()
        
        # التحقق من وجود العام الدراسي الحالي
        query = "SELECT setting_value FROM app_settings WHERE setting_key = 'academic_year'"
        result = db_manager.execute_query(query)
        
        if not result:
            # إضافة العام الدراسي الافتراضي
            insert_query = """
                INSERT INTO app_settings (setting_key, setting_value, created_at, updated_at)
                VALUES ('academic_year', '2024 - 2025', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            db_manager.execute_update(insert_query)
            print("تم إضافة العام الدراسي الافتراضي: 2024 - 2025")
        else:
            print(f"العام الدراسي الحالي: {result[0]['setting_value']}")
            
        print("تم إعداد الإعدادات الأولية بنجاح")
        
    except Exception as e:
        print(f"خطأ في إعداد الإعدادات: {e}")

if __name__ == "__main__":
    setup_initial_settings()
