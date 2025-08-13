#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف إعداد ما قبل البناء - يحضر التطبيق للتصدير
"""

import os
import sys
import shutil
import json
from pathlib import Path

def prepare_for_build():
    """تحضير المشروع للبناء"""
    
    print("🔧 تحضير المشروع للبناء...")
    
    # إنشاء مجلدات البناء
    build_dirs = ['dist', 'build', 'temp_build']
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.makedirs(dir_name, exist_ok=True)
    
    # إنشاء ملف إعدادات البناء
    build_config = {
        "app_name": "Private Schools Accounting",
        "version": "1.0.0",
        "author": "Private Schools Team",
        "description": "نظام محاسبة المدارس الأهلية",
        "icon": "app/resources/images/icon.ico",
        "console": False,
        "onefile": False,
        "optimize": True
    }
    
    with open('build_config.json', 'w', encoding='utf-8') as f:
        json.dump(build_config, f, ensure_ascii=False, indent=2)
    
    # التحقق من الملفات المطلوبة
    required_files = [
        'main.py',
        'config.py', 
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ ملفات مفقودة: {', '.join(missing_files)}")
        return False
    
    # التحقق من المجلدات المطلوبة  
    required_dirs = [
        'app',
        'core', 
        'ui',
        'data'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ مجلدات مفقودة: {', '.join(missing_dirs)}")
        return False
    
    print("✅ تم تحضير المشروع بنجاح!")
    return True

def create_icon():
    """إنشاء أيقونة التطبيق إذا لم تكن موجودة"""
    
    icon_path = Path('app/resources/images/icon.ico')
    
    if icon_path.exists():
        print("✅ أيقونة التطبيق موجودة")
        return True
    
    print("🎨 إنشاء أيقونة افتراضية...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # إنشاء أيقونة بسيطة
        img = Image.new('RGBA', (256, 256), (65, 105, 225, 255))
        draw = ImageDraw.Draw(img)
        
        # رسم دائرة
        draw.ellipse([50, 50, 206, 206], fill=(255, 255, 255, 255))
        
        # رسم نص
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        text = "مدرسة"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (256 - text_width) // 2
        y = (256 - text_height) // 2
        
        draw.text((x, y), text, fill=(65, 105, 225, 255), font=font)
        
        # حفظ الأيقونة
        icon_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(icon_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        
        print("✅ تم إنشاء الأيقونة بنجاح")
        return True
        
    except Exception as e:
        print(f"⚠️  لم يتم إنشاء الأيقونة: {e}")
        return False

def check_dependencies():
    """التحقق من المتطلبات"""
    
    print("📦 التحقق من المتطلبات...")
    
    try:
        import PyQt5
        print("✅ PyQt5 متوفر")
    except ImportError:
        print("❌ PyQt5 غير متوفر")
        return False
    
    try:
        import supabase
        print("✅ Supabase متوفر")
    except ImportError:
        print("❌ Supabase غير متوفر")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("    إعداد تطبيق نظام محاسبة المدارس الأهلية")
    print("=" * 50)
    
    if not check_dependencies():
        print("\n❌ يرجى تثبيت المتطلبات أولاً:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    if not prepare_for_build():
        print("\n❌ فشل في تحضير المشروع")
        sys.exit(1)
    
    create_icon()
    
    print("\n🎉 المشروع جاهز للبناء!")
    print("يمكنك الآن تشغيل: build_exe.bat")
