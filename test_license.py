#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام التراخيص
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.licensing.hardware_info import HardwareInfo
from core.licensing.license_manager import LicenseManager
import json

def test_hardware_info():
    """اختبار جمع معلومات الهارد وير"""
    print("=== اختبار جمع معلومات الهارد وير ===")
    
    hardware = HardwareInfo()
    
    try:
        info = hardware.get_all_hardware_info()
        print("معلومات الهارد وير:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        fingerprint = hardware.create_hardware_fingerprint()
        print(f"بصمة الجهاز: {fingerprint}")
        
        return True
    except Exception as e:
        print(f"خطأ في جمع معلومات الهارد وير: {e}")
        return False

def test_license_manager():
    """اختبار مدير التراخيص"""
    print("\n=== اختبار مدير التراخيص ===")
    
    license_manager = LicenseManager()
    
    try:
        # فحص وجود ملف الترخيص
        file_exists, license_data = license_manager.check_license_file()
        print(f"ملف الترخيص موجود: {file_exists}")
        
        if file_exists:
            print("بيانات الترخيص:")
            print(json.dumps(license_data, ensure_ascii=False, indent=2))
        
        # فحص صحة الترخيص
        is_valid, message = license_manager.validate_license()
        print(f"صحة الترخيص: {is_valid}")
        print(f"الرسالة: {message}")
        
        return True
    except Exception as e:
        print(f"خطأ في اختبار مدير التراخيص: {e}")
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("بدء اختبار نظام التراخيص...\n")
    
    success = True
    
    # اختبار معلومات الهارد وير
    if not test_hardware_info():
        success = False
    
    # اختبار مدير التراخيص
    if not test_license_manager():
        success = False
    
    if success:
        print("\n✓ جميع الاختبارات نجحت!")
    else:
        print("\n✗ بعض الاختبارات فشلت!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
