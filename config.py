# إعدادات التطبيق العامة
import os
from pathlib import Path

# مسارات المشروع
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = DATA_DIR / "database"
UPLOADS_DIR = DATA_DIR / "uploads"
BACKUPS_DIR = DATA_DIR / "backups"
EXPORTS_DIR = DATA_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
RESOURCES_DIR = BASE_DIR / "app" / "resources"

# إعدادات قاعدة البيانات
DATABASE_NAME = "schools.db"
DATABASE_PATH = DATABASE_DIR / DATABASE_NAME

# إعدادات التطبيق
APP_NAME = "حسابات المدارس الأهلية"
APP_VERSION = "1.0.0"
APP_ORGANIZATION = "Tech Solu Company"

# إعدادات النافذة - متجاوبة مع حجم الشاشة
WINDOW_TITLE = f"{APP_NAME} - الإصدار {APP_VERSION}"
WINDOW_MIN_WIDTH = 1000  # تقليل الحد الأدنى للعرض
WINDOW_MIN_HEIGHT = 700  # تقليل الحد الأدنى للارتفاع

# إعدادات responsive design
SIDEBAR_MIN_WIDTH = 250
SIDEBAR_MAX_WIDTH = 320
BUTTON_MIN_HEIGHT = 40
BUTTON_FONT_SIZE = 14

# إعدادات الأمان
PASSWORD_MIN_LENGTH = 6
SESSION_TIMEOUT = 3600  # ساعة واحدة بالثواني

# إعدادات النسخ الاحتياطي
BACKUP_INTERVAL_DAYS = 7
MAX_BACKUP_FILES = 30

# إعدادات النسخ الاحتياطي التلقائي عند الخروج
AUTO_BACKUP_ON_EXIT = True  # تفعيل النسخ الاحتياطي التلقائي عند إغلاق التطبيق
AUTO_BACKUP_SHOW_SUCCESS_MESSAGE = True  # عرض رسالة نجاح النسخ الاحتياطي
AUTO_BACKUP_CONFIRMATION_DIALOG = True  # عرض حوار تأكيد قبل الخروج

# إنشاء المجلدات المطلوبة
for directory in [DATA_DIR, DATABASE_DIR, UPLOADS_DIR, BACKUPS_DIR, EXPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# إنشاء مجلدات فرعية للرفوعات
(UPLOADS_DIR / "school_logos").mkdir(exist_ok=True)
(UPLOADS_DIR / "temp").mkdir(exist_ok=True)

# إنشاء مجلدات فرعية للنسخ الاحتياطية
(BACKUPS_DIR / "daily").mkdir(exist_ok=True)
(BACKUPS_DIR / "weekly").mkdir(exist_ok=True)
(BACKUPS_DIR / "manual").mkdir(exist_ok=True)

# إنشاء مجلدات فرعية للصادرات
(EXPORTS_DIR / "reports").mkdir(exist_ok=True)
(EXPORTS_DIR / "prints").mkdir(exist_ok=True)

# إنشاء مجلد الموارد وخطوط التطبيق
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
(RESOURCES_DIR / "fonts").mkdir(parents=True, exist_ok=True)

# إضافة مسار الخطوط
FONTS_DIR = RESOURCES_DIR / "fonts"

# إعدادات Supabase للنسخ الاحتياطية
SUPABASE_URL = "https://tsyvpjhpogxmqcpeaowb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzeXZwamhwb2d4bXFjcGVhb3diIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTY2ODE1MjgsImV4cCI6MjAzMjI1NzUyOH0.30rbkShbpM_h06pZIAw39Ma2SC0thZi9WiV__lhh4Lk"
SUPABASE_BUCKET = "private-schools-accounting"

# وضع التطوير (True لتفعيل وضع التطوير، False للإنتاج)
DEBUG_MODE = True
