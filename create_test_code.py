#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إنشاء رمز تفعيل تجريبي للاختبار
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def create_test_activation_code():
    """إنشاء رمز تفعيل تجريبي"""
    import uuid
    import random
    import string
    from datetime import datetime
    
    # إنشاء رمز تفعيل بصيغة PSA-YEAR-XXXX-XX
    year = datetime.now().year
    random_num = ''.join(random.choices(string.digits, k=4))
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    
    activation_code = f"PSA-{year}-{random_num}-{random_letters}"
    print(f"رمز التفعيل التجريبي: {activation_code}")
    
    # حفظ الرمز في ملف للاستخدام اللاحق
    with open("test_activation_code.txt", "w", encoding="utf-8") as f:
        f.write(f"رمز التفعيل التجريبي: {activation_code}\n")
        f.write(f"تم إنشاؤه في: {datetime.now()}\n")
        f.write("ملاحظة: هذا رمز تجريبي للاختبار فقط\n")
    
    print("تم حفظ الرمز في ملف test_activation_code.txt")
    return activation_code

if __name__ == "__main__":
    create_test_activation_code()
