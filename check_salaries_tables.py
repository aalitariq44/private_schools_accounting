#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.database.connection import db_manager

# قائمة بجميع الجداول
query = "SELECT name FROM sqlite_master WHERE type='table'"
tables = db_manager.execute_query(query)

print("جميع الجداول:")
for table in tables:
    print(f"- {table['name']}")

# فحص بنية جدول salaries
print("\n=== بنية جدول salaries ===")
salaries_info = db_manager.execute_query("PRAGMA table_info(salaries)")
for col in salaries_info:
    print(f"العمود: {col['name']}, النوع: {col['type']}")
