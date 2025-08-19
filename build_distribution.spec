# -*- mode: python ; coding: utf-8 -*-
"""
ملف إعدادات PyInstaller لبناء توزيع احترافي للتطبيق
يقوم بإنشاء مجلد توزيع منظم مع جميع الملفات والمجلدات
"""

import sys
import os
from pathlib import Path

# مسار المشروع
project_root = os.path.abspath('.')

# البيانات الإضافية والموارد
added_files = []

# إضافة الملفات والمجلدات الموجودة فقط
if os.path.exists('app/resources'):
    added_files.append(('app/resources', 'app/resources'))

if os.path.exists('app'):
    added_files.append(('app', 'app'))

if os.path.exists('core'):
    added_files.append(('core', 'core'))

if os.path.exists('ui'):
    added_files.append(('ui', 'ui'))

if os.path.exists('data'):
    added_files.append(('data', 'data'))

if os.path.exists('docs'):
    added_files.append(('docs', 'docs'))

if os.path.exists('config.py'):
    added_files.append(('config.py', '.'))

if os.path.exists('printing_config.json'):
    added_files.append(('printing_config.json', '.'))

if os.path.exists('version_info.txt'):
    added_files.append(('version_info.txt', '.'))

if os.path.exists('README.md'):
    added_files.append(('README.md', '.'))

if os.path.exists('README.md'):
    added_files.append(('README.md', '.'))

# الوحدات المخفية المطلوبة
hidden_imports = [
    # PyQt5 الأساسية
    'PyQt5.QtCore',
    'PyQt5.QtWidgets', 
    'PyQt5.QtGui',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtPrintSupport',
    'PyQt5.QtSql',
    'PyQt5.QtNetwork',
    'PyQt5.QtSvg',
    
    # قواعد البيانات والشبكة
    'supabase',
    'storage3',
    'postgrest',
    'gotrue',
    'realtime',
    'supafunc',
    'sqlite3',
    
    # التشفير والأمان
    'bcrypt',
    'hashlib',
    'base64',
    'secrets',
    
    # معالجة الملفات والتقارير
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.lib',
    'reportlab.platypus',
    'arabic_reshaper',
    'bidi',
    'PIL',
    'PIL.Image',
    'PIL.ImageFont',
    
    # القوالب والواجهات
    'jinja2',
    'jinja2.loaders',
    
    # الإعدادات والتكوين
    'dotenv',
    'configparser',
    'json',
    'yaml',
    
    # التواريخ والحسابات
    'datetime',
    'decimal',
    'math',
    'statistics',
    
    # معالجة البيانات
    'csv',
    'xml',
    'io',
    'urllib',
    're',
    'collections',
    
    # التسجيل والتشخيص
    'logging',
    'logging.handlers',
    'traceback',
    
    # الملفات والمسارات
    'pathlib',
    'os',
    'sys',
    'shutil',
    'tempfile',
    
    # الشبكة والاتصالات
    'requests',
    'urllib3',
    'ssl',
    'socket',
    
    # التحكم في العمليات
    'threading',
    'multiprocessing',
    'queue',
    'signal',
]

# تحليل التطبيق
a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # ملفات الاختبار
        'test_*',
        'tests',
        'testing',
        '_tests',
        'unittest',
        'nose',
        'pytest',
        
        # مكتبات غير مطلوبة
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
        
        # أدوات التطوير
        'pdb',
        'pydoc',
        'doctest',
        'distutils',
        'setuptools',
        'pip',
        
        # مكتبات اختيارية
        'babel',
        'sphinx',
        'pygments',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# إنشاء أرشيف Python
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# إعداد الملف التنفيذي
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PrivateSchoolsAccounting',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # تطبيق GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/resources/images/icon.ico',
    uac_admin=False,  # لا يتطلب صلاحيات المدير
)

# جمع جميع الملفات في مجلد التوزيع
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PrivateSchoolsAccounting_Distribution'
)
