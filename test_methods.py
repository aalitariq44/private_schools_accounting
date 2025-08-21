#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

try:
    from ui.pages.teachers.teachers_page import TeachersPage
    from ui.pages.employees.employees_page import EmployeesPage
    
    print("SUCCESS: Pages loaded successfully")
    
    # Check if the methods exist
    teachers_page = TeachersPage.__dict__
    employees_page = EmployeesPage.__dict__
    
    if 'delete_teacher' in teachers_page:
        print("SUCCESS: delete_teacher method exists in TeachersPage")
    else:
        print("ERROR: delete_teacher method not found")
    
    if 'delete_employee' in employees_page:
        print("SUCCESS: delete_employee method exists in EmployeesPage")
    else:
        print("ERROR: delete_employee method not found")
    
    print("Feature check completed successfully!")
    
except Exception as e:
    print(f"ERROR: {e}")
