#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إدارة تسجيل الدخول والمصادقة
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional

from core.database.connection import db_manager
from core.utils.logger import auth_logger
import config


class AuthManager:
    """مدير المصادقة"""
    
    def __init__(self):
        """تهيئة مدير المصادقة"""
        self.current_user = None
        self.session_start = None
        self.session_timeout = config.SESSION_TIMEOUT
    
    def hash_password(self, password: str) -> str:
        """تشفير كلمة المرور"""
        try:
            # إنشاء salt عشوائي
            salt = secrets.token_hex(32)
            
            # تشفير كلمة المرور مع salt
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000  # عدد التكرارات
            )
            
            # دمج salt مع hash
            return salt + password_hash.hex()
            
        except Exception as e:
            logging.error(f"خطأ في تشفير كلمة المرور: {e}")
            raise
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """التحقق من كلمة المرور"""
        try:
            # استخراج salt (أول 64 حرف)
            salt = stored_hash[:64]
            stored_password_hash = stored_hash[64:]
            
            # تشفير كلمة المرور المدخلة
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            # مقارنة النتيجة
            return password_hash.hex() == stored_password_hash
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من كلمة المرور: {e}")
            return False
    
    def has_users(self) -> bool:
        """التحقق من وجود مستخدمين في النظام"""
        try:
            query = "SELECT COUNT(*) as count FROM users"
            result = db_manager.execute_query(query)
            
            if result and len(result) > 0:
                return result[0]['count'] > 0
            
            return False
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من وجود المستخدمين: {e}")
            return False
    
    def create_first_user(self, password: str) -> bool:
        """إنشاء المستخدم الأول"""
        try:
            # التحقق من قوة كلمة المرور
            if not self.validate_password(password):
                auth_logger.log_security_event("محاولة إنشاء مستخدم بكلمة مرور ضعيفة")
                return False
            
            # التحقق من عدم وجود مستخدمين
            if self.has_users():
                auth_logger.log_security_event("محاولة إنشاء مستخدم أول مع وجود مستخدمين")
                return False
            
            # تشفير كلمة المرور
            password_hash = self.hash_password(password)
            
            # إدخال المستخدم
            query = """
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
            """
            
            user_id = db_manager.execute_insert(query, ('admin', password_hash))
            
            if user_id:
                auth_logger.log_security_event("تم إنشاء المستخدم الأول", f"معرف المستخدم: {user_id}")
                logging.info("تم إنشاء المستخدم الأول بنجاح")
                return True
            
            return False
            
        except Exception as e:
            auth_logger.log_security_event("خطأ في إنشاء المستخدم الأول", str(e))
            logging.error(f"خطأ في إنشاء المستخدم الأول: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> bool:
        """مصادقة المستخدم"""
        try:
            # البحث عن المستخدم
            query = "SELECT id, password_hash FROM users WHERE username = ?"
            result = db_manager.execute_query(query, (username,))
            
            if not result:
                auth_logger.log_login_attempt(username, False)
                return False
            
            user = result[0]
            
            # التحقق من كلمة المرور
            if self.verify_password(password, user['password_hash']):
                # تسجيل دخول ناجح
                self.current_user = {
                    'id': user['id'],
                    'username': username
                }
                self.session_start = datetime.now()
                
                auth_logger.log_login_attempt(username, True)
                logging.info(f"تم تسجيل دخول المستخدم: {username}")
                return True
            else:
                auth_logger.log_login_attempt(username, False)
                return False
                
        except Exception as e:
            auth_logger.log_security_event("خطأ في المصادقة", str(e))
            logging.error(f"خطأ في مصادقة المستخدم: {e}")
            return False
    
    def logout(self):
        """تسجيل خروج المستخدم"""
        try:
            if self.current_user:
                username = self.current_user.get('username', 'غير معروف')
                auth_logger.log_logout(username)
                logging.info(f"تم تسجيل خروج المستخدم: {username}")
            
            self.current_user = None
            self.session_start = None
            
        except Exception as e:
            logging.error(f"خطأ في تسجيل الخروج: {e}")
    
    def is_authenticated(self) -> bool:
        """التحقق من حالة المصادقة"""
        try:
            if not self.current_user or not self.session_start:
                return False
            
            # التحقق من انتهاء الجلسة
            if self.is_session_expired():
                self.logout()
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من المصادقة: {e}")
            return False
    
    def is_session_expired(self) -> bool:
        """التحقق من انتهاء الجلسة"""
        try:
            if not self.session_start:
                return True
            
            elapsed_time = datetime.now() - self.session_start
            return elapsed_time.total_seconds() > self.session_timeout
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من انتهاء الجلسة: {e}")
            return True
    
    def extend_session(self):
        """تمديد الجلسة"""
        try:
            if self.current_user:
                self.session_start = datetime.now()
                
        except Exception as e:
            logging.error(f"خطأ في تمديد الجلسة: {e}")
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """تغيير كلمة المرور"""
        try:
            if not self.current_user:
                return False
            
            # التحقق من كلمة المرور القديمة
            user_id = self.current_user['id']
            username = self.current_user['username']
            
            query = "SELECT password_hash FROM users WHERE id = ?"
            result = db_manager.execute_query(query, (user_id,))
            
            if not result:
                return False
            
            stored_hash = result[0]['password_hash']
            
            if not self.verify_password(old_password, stored_hash):
                auth_logger.log_security_event("محاولة تغيير كلمة مرور بكلمة قديمة خاطئة", username)
                return False
            
            # التحقق من قوة كلمة المرور الجديدة
            if not self.validate_password(new_password):
                return False
            
            # تشفير كلمة المرور الجديدة
            new_password_hash = self.hash_password(new_password)
            
            # تحديث كلمة المرور
            update_query = """
                UPDATE users 
                SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """
            
            affected_rows = db_manager.execute_update(update_query, (new_password_hash, user_id))
            
            if affected_rows > 0:
                auth_logger.log_password_change(username)
                logging.info(f"تم تغيير كلمة مرور المستخدم: {username}")
                return True
            
            return False
            
        except Exception as e:
            auth_logger.log_security_event("خطأ في تغيير كلمة المرور", str(e))
            logging.error(f"خطأ في تغيير كلمة المرور: {e}")
            return False
    
    def validate_password(self, password: str) -> bool:
        """التحقق من قوة كلمة المرور"""
        try:
            # التحقق من الطول الأدنى
            if len(password) < config.PASSWORD_MIN_LENGTH:
                return False
            
            # يمكن إضافة قواعد أخرى هنا حسب المتطلبات
            # مثل: وجود أرقام، أحرف كبيرة، رموز خاصة
            
            return True
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من كلمة المرور: {e}")
            return False
    
    def get_current_user(self) -> Optional[dict]:
        """الحصول على المستخدم الحالي"""
        return self.current_user
    
    def get_session_info(self) -> dict:
        """الحصول على معلومات الجلسة"""
        try:
            if not self.current_user or not self.session_start:
                return {}
            
            elapsed_time = datetime.now() - self.session_start
            remaining_time = self.session_timeout - elapsed_time.total_seconds()
            
            return {
                'user': self.current_user,
                'session_start': self.session_start,
                'elapsed_seconds': elapsed_time.total_seconds(),
                'remaining_seconds': max(0, remaining_time),
                'is_expired': remaining_time <= 0
            }
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على معلومات الجلسة: {e}")
            return {}


# إنشاء مثيل مشترك من مدير المصادقة
auth_manager = AuthManager()
