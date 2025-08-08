#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.database.connection import db_manager
import logging

# إعداد نظام التسجيل
logging.basicConfig(level=logging.INFO)

print('إنشاء قاعدة البيانات...')
success = db_manager.initialize_database()

if success:
    print('✅ تم إنشاء قاعدة البيانات بنجاح!')
    # التحقق من الجداول
    with db_manager.get_cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print('الجداول المنشأة:')
        for table in tables:
            print(f'  - {table[0]}')
else:
    print('❌ فشل في إنشاء قاعدة البيانات')
