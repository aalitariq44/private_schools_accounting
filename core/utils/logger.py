#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام التسجيل والأخطاء للتطبيق
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

import config


def setup_logging():
    """إعداد نظام التسجيل"""
    try:
        # التأكد من وجود مجلد السجلات
        config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # إعداد التنسيق العربي
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # إعداد السجل الرئيسي
        main_logger = logging.getLogger()
        main_logger.setLevel(logging.INFO)
        
        # إزالة المعالجات الموجودة
        for handler in main_logger.handlers[:]:
            main_logger.removeHandler(handler)
        
        # معالج ملف السجل العام
        app_log_path = config.LOGS_DIR / "app.log"
        app_handler = logging.handlers.RotatingFileHandler(
            str(app_log_path),
            maxBytes=10*1024*1024,  # 10 ميجابايت
            backupCount=5,
            encoding='utf-8'
        )
        app_handler.setFormatter(formatter)
        app_handler.setLevel(logging.INFO)
        main_logger.addHandler(app_handler)
        
        # معالج ملف الأخطاء
        error_log_path = config.LOGS_DIR / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            str(error_log_path),
            maxBytes=10*1024*1024,  # 10 ميجابايت
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        main_logger.addHandler(error_handler)
        
        # معالج وحدة التحكم للتطوير
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        main_logger.addHandler(console_handler)
        
        # إعداد سجلات مخصصة
        setup_database_logger()
        setup_auth_logger()
        
        logging.info("تم إعداد نظام التسجيل بنجاح")
        
    except Exception as e:
        print(f"خطأ في إعداد نظام التسجيل: {e}")
        raise


def setup_database_logger():
    """إعداد سجل قاعدة البيانات"""
    try:
        db_logger = logging.getLogger('database')
        db_logger.setLevel(logging.INFO)
        
        db_log_path = config.LOGS_DIR / "database.log"
        db_handler = logging.handlers.RotatingFileHandler(
            str(db_log_path),
            maxBytes=5*1024*1024,  # 5 ميجابايت
            backupCount=3,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        db_handler.setFormatter(formatter)
        db_logger.addHandler(db_handler)
        
    except Exception as e:
        logging.error(f"خطأ في إعداد سجل قاعدة البيانات: {e}")


def setup_auth_logger():
    """إعداد سجل المصادقة"""
    try:
        auth_logger = logging.getLogger('auth')
        auth_logger.setLevel(logging.INFO)
        
        auth_log_path = config.LOGS_DIR / "auth.log"
        auth_handler = logging.handlers.RotatingFileHandler(
            str(auth_log_path),
            maxBytes=5*1024*1024,  # 5 ميجابايت
            backupCount=3,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        auth_handler.setFormatter(formatter)
        auth_logger.addHandler(auth_handler)
        
    except Exception as e:
        logging.error(f"خطأ في إعداد سجل المصادقة: {e}")


def log_exception(logger_name: str, exception: Exception, context: str = ""):
    """تسجيل استثناء مع التفاصيل"""
    try:
        logger = logging.getLogger(logger_name)
        
        error_msg = f"استثناء: {type(exception).__name__}: {str(exception)}"
        if context:
            error_msg = f"{context} - {error_msg}"
            
        logger.error(error_msg, exc_info=True)
        
    except Exception as e:
        # في حالة فشل التسجيل، اطبع الخطأ
        print(f"خطأ في تسجيل الاستثناء: {e}")
        print(f"الاستثناء الأصلي: {exception}")


def log_user_action(action: str, details: str = ""):
    """تسجيل إجراء المستخدم"""
    try:
        logger = logging.getLogger('user_actions')
        
        message = f"إجراء المستخدم: {action}"
        if details:
            message += f" - {details}"
            
        logger.info(message)
        
    except Exception as e:
        logging.error(f"خطأ في تسجيل إجراء المستخدم: {e}")


def log_database_operation(operation: str, table: str, details: str = ""):
    """تسجيل عملية قاعدة البيانات"""
    try:
        logger = logging.getLogger('database')
        
        message = f"عملية قاعدة البيانات: {operation} في الجدول {table}"
        if details:
            message += f" - {details}"
            
        logger.info(message)
        
    except Exception as e:
        logging.error(f"خطأ في تسجيل عملية قاعدة البيانات: {e}")


def clean_old_logs(days_to_keep: int = 30):
    """تنظيف السجلات القديمة"""
    try:
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for log_file in config.LOGS_DIR.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
                logging.info(f"تم حذف السجل القديم: {log_file.name}")
                
    except Exception as e:
        logging.error(f"خطأ في تنظيف السجلات القديمة: {e}")


class DatabaseLogger:
    """مسجل مخصص لعمليات قاعدة البيانات"""
    
    def __init__(self):
        self.logger = logging.getLogger('database')
    
    def log_query(self, query: str, params: tuple = ()):
        """تسجيل استعلام قاعدة البيانات"""
        self.logger.debug(f"استعلام: {query} | المعاملات: {params}")
    
    def log_insert(self, table: str, record_id: int):
        """تسجيل عملية إدخال"""
        self.logger.info(f"تم إدخال سجل جديد في {table} بالمعرف {record_id}")
    
    def log_update(self, table: str, record_id: int, affected_rows: int):
        """تسجيل عملية تحديث"""
        self.logger.info(f"تم تحديث {affected_rows} سجل في {table} (المعرف: {record_id})")
    
    def log_delete(self, table: str, affected_rows: int):
        """تسجيل عملية حذف"""
        self.logger.info(f"تم حذف {affected_rows} سجل من {table}")
    
    def log_error(self, operation: str, error: Exception):
        """تسجيل خطأ في قاعدة البيانات"""
        self.logger.error(f"خطأ في {operation}: {error}", exc_info=True)


class AuthLogger:
    """مسجل مخصص لعمليات المصادقة"""
    
    def __init__(self):
        self.logger = logging.getLogger('auth')
    
    def log_login_attempt(self, username: str, success: bool):
        """تسجيل محاولة تسجيل دخول"""
        status = "نجحت" if success else "فشلت"
        self.logger.info(f"محاولة تسجيل دخول {status} للمستخدم: {username}")
    
    def log_password_change(self, username: str):
        """تسجيل تغيير كلمة مرور"""
        self.logger.info(f"تم تغيير كلمة مرور المستخدم: {username}")
    
    def log_logout(self, username: str):
        """تسجيل تسجيل خروج"""
        self.logger.info(f"تم تسجيل خروج المستخدم: {username}")
    
    def log_security_event(self, event: str, details: str = ""):
        """تسجيل حدث أمني"""
        message = f"حدث أمني: {event}"
        if details:
            message += f" - {details}"
        self.logger.warning(message)


# إنشاء مثيلات المسجلات المخصصة
db_logger = DatabaseLogger()
auth_logger = AuthLogger()
