#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.database.connection import db_manager

print('=== بنية جدول teachers ===')
teachers_info = db_manager.execute_query('PRAGMA table_info(teachers)')
for col in teachers_info:
    print(f'العمود: {col["name"]}, النوع: {col["type"]}')

print('\n=== بنية جدول employees ===')
employees_info = db_manager.execute_query('PRAGMA table_info(employees)')
for col in employees_info:
    print(f'العمود: {col["name"]}, النوع: {col["type"]}')

print('\n=== عينة من بيانات المعلمين ===')
teachers_sample = db_manager.execute_query('SELECT id, name, monthly_salary, school_id FROM teachers LIMIT 3')
for teacher in teachers_sample:
    print(f'ID: {teacher["id"]}, Name: {teacher["name"]}, Salary: {teacher["monthly_salary"]}, School: {teacher["school_id"]}')

print('\n=== عينة من بيانات الموظفين ===')
employees_sample = db_manager.execute_query('SELECT id, name, monthly_salary, school_id FROM employees LIMIT 3')
for employee in employees_sample:
    print(f'ID: {employee["id"]}, Name: {employee["name"]}, Salary: {employee["monthly_salary"]}, School: {employee["school_id"]}')
