#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة إنشاء رموز تفعيل جديدة
هذا الملف للاستخدام اليدوي فقط لإنشاء رموز التفعيل
"""

import sys
import os
import json
import uuid
import random
import string
from datetime import datetime, timezone

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import config
import requests

class LicenseGenerator:
    """مولد رموز التفعيل"""
    
    def __init__(self):
        self.supabase_url = config.SUPABASE_URL
        self.supabase_key = config.SUPABASE_KEY
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
    
    def generate_activation_code(self, prefix="PSA", year=None):
        """إنشاء رمز تفعيل فريد"""
        if year is None:
            year = datetime.now().year
        
        # إنشاء رقم عشوائي مكون من 4 أرقام
        random_num = ''.join(random.choices(string.digits, k=4))
        
        # إنشاء حروف عشوائية
        random_letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        
        # تكوين رمز التفعيل
        activation_code = f"{prefix}-{year}-{random_num}-{random_letters}"
        
        return activation_code
    
    def create_license(self, customer_name=None, customer_email=None, notes=None):
        """إنشاء ترخيص جديد"""
        try:
            # إنشاء رمز تفعيل فريد
            activation_code = self.generate_activation_code()
            
            # التحقق من عدم وجود الرمز مسبقاً
            while self.check_code_exists(activation_code):
                activation_code = self.generate_activation_code()
            
            # إعداد بيانات الترخيص
            license_data = {
                'activation_code': activation_code,
                'used': False,
                'issued_at': datetime.now(timezone.utc).isoformat(),
                'revoked': False
            }
            
            # إضافة معلومات العميل إذا توفرت
            if customer_name or customer_email:
                issued_to = {}
                if customer_name:
                    issued_to['name'] = customer_name
                if customer_email:
                    issued_to['email'] = customer_email
                license_data['issued_to'] = issued_to
            
            # إضافة الملاحظات
            if notes:
                license_data['notes'] = notes
            
            # إدراج في قاعدة البيانات
            url = f"{self.supabase_url}/rest/v1/licenses"
            response = requests.post(url, headers=self.headers, json=license_data)
            
            if response.status_code == 201:
                return True, activation_code, "تم إنشاء الترخيص بنجاح"
            else:
                return False, None, f"خطأ في إنشاء الترخيص: {response.status_code} - {response.text}"
                
        except Exception as e:
            return False, None, f"خطأ: {str(e)}"
    
    def check_code_exists(self, activation_code):
        """التحقق من وجود رمز التفعيل"""
        try:
            url = f"{self.supabase_url}/rest/v1/licenses?activation_code=eq.{activation_code}&select=id"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return len(response.json()) > 0
            return False
        except:
            return False
    
    def list_licenses(self, limit=50):
        """عرض قائمة التراخيص"""
        try:
            url = f"{self.supabase_url}/rest/v1/licenses?select=*&order=issued_at.desc&limit={limit}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"خطأ في جلب التراخيص: {response.status_code}"
                
        except Exception as e:
            return False, f"خطأ: {str(e)}"
    
    def revoke_license(self, activation_code):
        """إلغاء ترخيص"""
        try:
            url = f"{self.supabase_url}/rest/v1/licenses?activation_code=eq.{activation_code}"
            update_data = {
                'revoked': True,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.patch(url, headers=self.headers, json=update_data)
            
            if response.status_code in [200, 204]:
                return True, "تم إلغاء الترخيص بنجاح"
            else:
                return False, f"خطأ في إلغاء الترخيص: {response.status_code}"
                
        except Exception as e:
            return False, f"خطأ: {str(e)}"

def main():
    """الدالة الرئيسية"""
    print("=== مولد رموز التفعيل ===")
    print("1. إنشاء ترخيص جديد")
    print("2. عرض التراخيص")
    print("3. إلغاء ترخيص")
    print("4. خروج")
    
    generator = LicenseGenerator()
    
    while True:
        try:
            choice = input("\nاختر العملية (1-4): ").strip()
            
            if choice == '1':
                # إنشاء ترخيص جديد
                print("\n--- إنشاء ترخيص جديد ---")
                customer_name = input("اسم العميل (اختياري): ").strip() or None
                customer_email = input("إيميل العميل (اختياري): ").strip() or None
                notes = input("ملاحظات (اختياري): ").strip() or None
                
                success, activation_code, message = generator.create_license(
                    customer_name, customer_email, notes
                )
                
                if success:
                    print(f"✓ تم إنشاء الترخيص بنجاح!")
                    print(f"رمز التفعيل: {activation_code}")
                else:
                    print(f"✗ {message}")
            
            elif choice == '2':
                # عرض التراخيص
                print("\n--- قائمة التراخيص ---")
                success, data = generator.list_licenses()
                
                if success:
                    if data:
                        for license_item in data:
                            status = "مستخدم" if license_item.get('used') else "غير مستخدم"
                            revoked = "ملغي" if license_item.get('revoked') else "نشط"
                            issued_to = license_item.get('issued_to', {})
                            customer = issued_to.get('name', 'غير محدد') if issued_to else 'غير محدد'
                            
                            print(f"- {license_item['activation_code']} | {status} | {revoked} | {customer}")
                    else:
                        print("لا توجد تراخيص")
                else:
                    print(f"✗ {data}")
            
            elif choice == '3':
                # إلغاء ترخيص
                print("\n--- إلغاء ترخيص ---")
                activation_code = input("رمز التفعيل المراد إلغاؤه: ").strip()
                
                if activation_code:
                    success, message = generator.revoke_license(activation_code)
                    if success:
                        print(f"✓ {message}")
                    else:
                        print(f"✗ {message}")
                else:
                    print("يجب إدخال رمز التفعيل")
            
            elif choice == '4':
                print("خروج...")
                break
            
            else:
                print("اختيار غير صحيح")
                
        except KeyboardInterrupt:
            print("\nتم إيقاف البرنامج")
            break
        except Exception as e:
            print(f"خطأ: {e}")

if __name__ == "__main__":
    main()
