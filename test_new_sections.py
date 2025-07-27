#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للقسمين الجديدين
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.pages.external_income.external_income_page import ExternalIncomePage
from ui.pages.expenses.expenses_page import ExpensesPage

def test_external_income():
    """اختبار صفحة الواردات الخارجية"""
    app = QApplication(sys.argv)
    
    try:
        window = ExternalIncomePage()
        window.show()
        print("تم تحميل صفحة الواردات الخارجية بنجاح")
        
        app.exec_()
        
    except Exception as e:
        print(f"خطأ في تحميل صفحة الواردات الخارجية: {e}")

def test_expenses():
    """اختبار صفحة المصروفات"""
    app = QApplication(sys.argv)
    
    try:
        window = ExpensesPage()
        window.show()
        print("تم تحميل صفحة المصروفات بنجاح")
        
        app.exec_()
        
    except Exception as e:
        print(f"خطأ في تحميل صفحة المصروفات: {e}")

if __name__ == "__main__":
    print("اختيار الاختبار:")
    print("1. اختبار صفحة الواردات الخارجية")
    print("2. اختبار صفحة المصروفات")
    
    choice = input("أدخل رقم الاختبار (1 أو 2): ")
    
    if choice == "1":
        test_external_income()
    elif choice == "2":
        test_expenses()
    else:
        print("اختيار غير صحيح")
