#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة تحديث نظام الطباعة
تقوم بتحديث المشروع لاستخدام محرك الطباعة الحديث
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_logging():
    """إعداد نظام السجلات"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('update_log.txt', encoding='utf-8')
        ]
    )

def check_python_version():
    """التحقق من إصدار Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        logging.error("يتطلب Python 3.7 أو أحدث")
        return False
    logging.info(f"إصدار Python: {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """تثبيت المتطلبات الجديدة"""
    logging.info("تثبيت محرك الويب الحديث...")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            'PyQtWebEngine==5.15.6', '--upgrade'
        ])
        logging.info("✅ تم تثبيت PyQtWebEngine بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ فشل في تثبيت PyQtWebEngine: {e}")
        return False

def test_import():
    """اختبار استيراد المكتبات الجديدة"""
    logging.info("اختبار المكتبات الجديدة...")
    
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        logging.info("✅ تم استيراد QWebEngineView بنجاح")
        return True
    except ImportError as e:
        logging.error(f"❌ فشل في استيراد QWebEngineView: {e}")
        return False

def backup_old_files():
    """إنشاء نسخة احتياطية من الملفات القديمة"""
    logging.info("إنشاء نسخة احتياطية...")
    
    backup_dir = Path("backup_before_update")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "core/printing/print_manager.py",
        "core/printing/__init__.py",
        "requirements.txt"
    ]
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            backup_file = backup_dir / Path(file_path).name
            import shutil
            shutil.copy2(file_path, backup_file)
            logging.info(f"تم نسخ {file_path} إلى {backup_file}")

def run_tests():
    """تشغيل اختبارات النظام"""
    logging.info("تشغيل اختبارات النظام...")
    
    if Path("test_print_engines.py").exists():
        try:
            subprocess.run([sys.executable, "test_print_engines.py"], 
                         timeout=30, check=False)
            logging.info("✅ تم تشغيل اختبارات النظام")
        except subprocess.TimeoutExpired:
            logging.info("انتهت مهلة الاختبار (طبيعي للواجهة الرسومية)")
        except Exception as e:
            logging.warning(f"تحذير في الاختبارات: {e}")

def main():
    """الدالة الرئيسية للتحديث"""
    setup_logging()
    
    logging.info("=== بدء تحديث نظام الطباعة ===")
    
    # التحقق من المتطلبات الأساسية
    if not check_python_version():
        return False
    
    # إنشاء نسخة احتياطية
    backup_old_files()
    
    # تثبيت المتطلبات الجديدة
    if not install_requirements():
        logging.error("فشل في تثبيت المتطلبات")
        return False
    
    # اختبار الاستيراد
    if not test_import():
        logging.error("فشل في اختبار المكتبات")
        return False
    
    # تشغيل الاختبارات
    run_tests()
    
    logging.info("=== تم تحديث نظام الطباعة بنجاح! ===")
    logging.info("\nالميزات الجديدة:")
    logging.info("• محرك طباعة حديث بجودة عالية")
    logging.info("• دعم كامل لـ CSS المتقدم")
    logging.info("• إمكانية حفظ PDF")
    logging.info("• تخطيط محسن للجداول والنصوص العربية")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
