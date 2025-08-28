#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة التراخيص الرئيسي
"""

import json
import logging
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
import base64
from cryptography.fernet import Fernet
import requests

import config
from .hardware_info import HardwareInfo


@dataclass
class LicenseData:
    """بيانات الترخيص"""
    activation_code: str
    hardware_info: Dict[str, str]
    first_used_at: str
    issued_to: Optional[str] = None
    notes: Optional[str] = None


class LicenseManager:
    """مدير نظام التراخيص"""
    
    # مفتاح التشفير الثابت (يجب أن يكون نفسه لجميع المستخدمين)
    ENCRYPTION_KEY = b'kB8vW2r5u8x/A?D(G+KbPeSgVkYp3s6v9y$B&E)H@McQ'
    
    def __init__(self):
        """تهيئة مدير التراخيص"""
        self.logger = logging.getLogger(__name__)
        self.hardware_info = HardwareInfo()
        self.license_file_path = config.BASE_DIR / "license.json"
        
        # إنشاء مفتاح التشفير
        key = hashlib.sha256(self.ENCRYPTION_KEY).digest()
        self.cipher = Fernet(base64.urlsafe_b64encode(key))
        
        # إعدادات Supabase
        self.supabase_url = config.SUPABASE_URL
        self.supabase_key = config.SUPABASE_KEY
        self.supabase_headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
    
    def check_license_file(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        فحص وجود ملف الترخيص وصحته
        Returns: (file_exists, license_data)
        """
        try:
            if not self.license_file_path.exists():
                self.logger.info("ملف الترخيص غير موجود")
                return False, None
            
            # قراءة وفك تشفير ملف الترخيص
            with open(self.license_file_path, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            try:
                decrypted_data = self.cipher.decrypt(encrypted_data.encode())
                license_data = json.loads(decrypted_data.decode())
                self.logger.info("تم فك تشفير ملف الترخيص بنجاح")
                return True, license_data
            except Exception as e:
                self.logger.error(f"خطأ في فك تشفير ملف الترخيص: {e}")
                return False, None
                
        except Exception as e:
            self.logger.error(f"خطأ في قراءة ملف الترخيص: {e}")
            return False, None
    
    def validate_license(self) -> Tuple[bool, str]:
        """
        التحقق من صحة الترخيص
        Returns: (is_valid, message)
        """
        try:
            file_exists, license_data = self.check_license_file()
            
            if not file_exists:
                return False, "ملف الترخيص غير موجود"
            
            if not license_data:
                return False, "ملف الترخيص تالف أو مشفر بشكل خاطئ"
            
            # التحقق من وجود البيانات المطلوبة
            required_fields = ['activation_code', 'hardware_info', 'first_used_at']
            for field in required_fields:
                if field not in license_data:
                    return False, f"ملف الترخيص ناقص - مفقود: {field}"
            
            # مقارنة معلومات الهارد وير
            stored_hardware = license_data['hardware_info']
            matching_count = self.hardware_info.get_matching_count(stored_hardware)
            
            if matching_count < 2:  # يجب أن يتطابق على الأقل 2 من 4 عناصر
                return False, f"معلومات الجهاز غير متطابقة (تطابق {matching_count} من 4)"
            
            if matching_count == 2:
                self.logger.warning("تحذير: تطابق جزئي لمعلومات الجهاز (2 من 4)")
            
            self.logger.info(f"تم التحقق من الترخيص بنجاح - تطابق {matching_count} من 4 عناصر")
            return True, f"الترخيص صحيح - تطابق {matching_count} من 4 عناصر"
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من الترخيص: {e}")
            return False, f"خطأ في التحقق من الترخيص: {str(e)}"
    
    def verify_activation_code_online(self, activation_code: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        التحقق من رمز التفعيل عبر الإنترنت
        Returns: (is_valid, license_info, message)
        """
        try:
            # استعلام جدول licenses في Supabase
            url = f"{self.supabase_url}/rest/v1/licenses?activation_code=eq.{activation_code}&select=*"
            response = requests.get(url, headers=self.supabase_headers, timeout=10)
            
            if response.status_code != 200:
                return False, {}, f"خطأ في الاتصال بالخادم: {response.status_code}"
            
            licenses = response.json()
            
            if not licenses:
                return False, {}, "رمز التفعيل غير صحيح"
            
            license_info = licenses[0]
            
            # التحقق من حالة الاستخدام
            if license_info.get('used', False):
                # إذا كان مستخدماً، تحقق من تطابق معلومات الجهاز
                return self._verify_used_license(license_info)
            else:
                # إذا لم يكن مستخدماً، قم بتفعيله
                return self._activate_new_license(license_info)
                
        except requests.exceptions.Timeout:
            return False, {}, "انتهت مهلة الاتصال بالإنترنت"
        except requests.exceptions.ConnectionError:
            return False, {}, "لا يمكن الاتصال بالإنترنت"
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من رمز التفعيل: {e}")
            return False, {}, f"خطأ في التحقق: {str(e)}"
    
    def _verify_used_license(self, license_info: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """التحقق من ترخيص مستخدم سابقاً"""
        try:
            current_hardware = self.hardware_info.get_all_hardware_info()
            
            # مقارنة معلومات الهارد وير المحفوظة
            stored_hardware = {
                'motherboard': license_info.get('motherboard', ''),
                'cpu': license_info.get('cpu', ''),
                'mac': license_info.get('mac', ''),
                'drive': license_info.get('drive', '')
            }
            
            matching_count = self.hardware_info.get_matching_count(stored_hardware)
            
            if matching_count < 2:
                return False, {}, f"هذا الترخيص مرتبط بجهاز آخر (تطابق {matching_count} من 4)"
            
            # إنشاء ملف الترخيص المحلي
            self._create_local_license_file(license_info['activation_code'], current_hardware, license_info)
            
            return True, license_info, f"تم تفعيل الترخيص بنجاح (تطابق {matching_count} من 4)"
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من الترخيص المستخدم: {e}")
            return False, {}, f"خطأ في التحقق: {str(e)}"
    
    def _activate_new_license(self, license_info: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """تفعيل ترخيص جديد"""
        try:
            current_hardware = self.hardware_info.get_all_hardware_info()
            current_time = datetime.now(timezone.utc).isoformat()
            
            # تحديث بيانات الترخيص في Supabase
            update_data = {
                'used': True,
                'motherboard': current_hardware['motherboard'],
                'cpu': current_hardware['cpu'],
                'mac': current_hardware['mac'],
                'drive': current_hardware['drive'],
                'first_used_at': current_time,
                'last_checkin_at': current_time
            }
            
            url = f"{self.supabase_url}/rest/v1/licenses?activation_code=eq.{license_info['activation_code']}"
            response = requests.patch(url, headers=self.supabase_headers, json=update_data, timeout=10)
            
            if response.status_code not in [200, 204]:
                return False, {}, f"خطأ في تحديث بيانات الترخيص: {response.status_code}"
            
            # إنشاء ملف الترخيص المحلي
            license_info.update(update_data)
            self._create_local_license_file(license_info['activation_code'], current_hardware, license_info)
            
            self.logger.info("تم تفعيل ترخيص جديد بنجاح")
            return True, license_info, "تم تفعيل الترخيص بنجاح"
            
        except Exception as e:
            self.logger.error(f"خطأ في تفعيل الترخيص الجديد: {e}")
            return False, {}, f"خطأ في التفعيل: {str(e)}"
    
    def _create_local_license_file(self, activation_code: str, hardware_info: Dict[str, str], 
                                 license_info: Dict[str, Any]):
        """إنشاء ملف الترخيص المحلي"""
        try:
            license_data = {
                'activation_code': activation_code,
                'hardware_info': hardware_info,
                'first_used_at': license_info.get('first_used_at', datetime.now(timezone.utc).isoformat()),
                'issued_to': license_info.get('issued_to'),
                'notes': license_info.get('notes'),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # تشفير البيانات
            json_data = json.dumps(license_data, ensure_ascii=False, indent=2)
            encrypted_data = self.cipher.encrypt(json_data.encode())
            
            # حفظ الملف
            with open(self.license_file_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_data.decode())
            
            self.logger.info("تم إنشاء ملف الترخيص المحلي بنجاح")
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء ملف الترخيص المحلي: {e}")
            raise
    
    def delete_license_file(self):
        """حذف ملف الترخيص المحلي"""
        try:
            if self.license_file_path.exists():
                os.remove(self.license_file_path)
                self.logger.info("تم حذف ملف الترخيص المحلي")
        except Exception as e:
            self.logger.error(f"خطأ في حذف ملف الترخيص: {e}")
    
    def get_license_info(self) -> Optional[Dict[str, Any]]:
        """الحصول على معلومات الترخيص الحالي"""
        file_exists, license_data = self.check_license_file()
        return license_data if file_exists else None
    
    def update_last_checkin(self):
        """تحديث آخر فحص للترخيص (اختياري - للاستخدام المستقبلي)"""
        try:
            license_info = self.get_license_info()
            if license_info and 'activation_code' in license_info:
                current_time = datetime.now(timezone.utc).isoformat()
                
                url = f"{self.supabase_url}/rest/v1/licenses?activation_code=eq.{license_info['activation_code']}"
                update_data = {'last_checkin_at': current_time}
                
                requests.patch(url, headers=self.supabase_headers, json=update_data, timeout=5)
                self.logger.debug("تم تحديث آخر فحص للترخيص")
                
        except Exception as e:
            self.logger.debug(f"لم يتم تحديث آخر فحص للترخيص: {e}")
            # لا نرفع خطأ هنا لأن هذا ليس ضرورياً لعمل التطبيق
