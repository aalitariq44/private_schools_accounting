#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
النافذة الرئيسية لتطبيق حسابات المدارس الأهلية
"""

import logging
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QFrame, QLabel, QPushButton, 
    QMessageBox, QMenuBar, QStatusBar, QAction,
    QSplitter, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QKeySequence

import config
from core.auth.login_manager import auth_manager
from core.utils.logger import log_user_action
from core.backup.backup_manager import backup_manager
from core.utils.responsive_design import responsive


class MainWindow(QMainWindow):
    """النافذة الرئيسية للتطبيق"""
    
    # إشارات مخصصة
    page_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_page = None
        self.pages = {}
        self.sidebar_buttons = {}
        
        self.setup_window()
        self.create_ui()
        self.setup_styles()
        self.setup_responsive_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_session_timer()
        
        # عرض الصفحة الرئيسية
        self.show_dashboard()
        
        log_user_action("تم فتح النافذة الرئيسية")
    
    def setup_window(self):
        """إعداد النافذة الرئيسية"""
        try:
            # عنوان النافذة
            self.setWindowTitle(config.WINDOW_TITLE)
            
            # حجم النافذة المتجاوب مع DPI
            self.setup_responsive_sizing()
            
            # توسيط النافذة
            self.center_window()
            
            # اتجاه التخطيط
            self.setLayoutDirection(Qt.RightToLeft)
            
            # أيقونة النافذة
            self.setup_window_icon()

            # افتح النافذة بوضع موسع افتراضياً
            self.setWindowState(Qt.WindowMaximized)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد النافذة الرئيسية: {e}")
            raise
    
    def setup_responsive_sizing(self):
        """إعداد الأحجام المتجاوبة مع DPI الحالي"""
        try:
            from PyQt5.QtWidgets import QApplication
            
            # الحصول على معلومات الشاشة
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            
            # التحقق من Scale 150% والتعامل معه خصيصاً
            if responsive.is_windows_scale_150():
                print("🔧 تم اكتشاف Windows Scale 150% - تطبيق إعدادات خاصة")
                window_width, window_height = responsive.get_scale_150_window_size(
                    config.WINDOW_MIN_WIDTH, 
                    config.WINDOW_MIN_HEIGHT
                )
                # تعيين أحجام خاصة لـ Scale 150%
                self.setMinimumSize(900, 600)
            else:
                # حساب الأحجام المناسبة للمقاييس الأخرى
                window_width, window_height = responsive.get_window_size(
                    config.WINDOW_MIN_WIDTH, 
                    config.WINDOW_MIN_HEIGHT
                )
                self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
            
            # تعيين الحجم المفضل
            self.resize(window_width, window_height)
            
            # حفظ معلومات DPI للاستخدام في باقي المكونات
            self.dpi_scale = responsive.dpi_scale
            
            logging.info(f"DPI Scale: {responsive.dpi_scale:.2f}, Window: {window_width}x{window_height}")
            if responsive.is_windows_scale_150():
                logging.info("تم تطبيق إعدادات خاصة لـ Windows Scale 150%")
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الأحجام المتجاوبة: {e}")
            # في حالة الخطأ، استخدم الأحجام الافتراضية
            self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
            self.resize(1200, 800)
            self.dpi_scale = 1.0
    
    def center_window(self):
        """توسيط النافذة في الشاشة"""
        try:
            from PyQt5.QtWidgets import QDesktopWidget
            
            screen = QDesktopWidget().screenGeometry()
            window = self.geometry()
            
            x = (screen.width() - window.width()) // 2
            y = (screen.height() - window.height()) // 2
            
            self.move(x, y)
            
        except Exception as e:
            logging.error(f"خطأ في توسيط النافذة: {e}")
    
    def setup_window_icon(self):
        """إعداد أيقونة النافذة"""
        try:
            icon_path = config.RESOURCES_DIR / "images" / "icons" / "logo.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            logging.warning(f"تحذير: لم يتم تحميل أيقونة النافذة: {e}")
    
    def create_ui(self):
        """إنشاء واجهة المستخدم"""
        try:
            # الويدجت المركزي
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # التخطيط الرئيسي
            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # إنشاء القائمة الجانبية
            self.create_sidebar()
            
            # إنشاء منطقة المحتوى
            self.create_content_area()
            
            # إضافة المكونات للتخطيط (نص إلى اليمين)
            main_layout.addWidget(self.sidebar_frame)
            main_layout.addWidget(self.content_frame, 1)  # تمديد منطقة المحتوى
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء واجهة المستخدم: {e}")
            raise
    
    def create_sidebar(self):
        """إنشاء القائمة الجانبية"""
        try:
            # إطار القائمة الجانبية
            self.sidebar_frame = QFrame()
            self.sidebar_frame.setObjectName("sidebarFrame")
            
            # حساب عرض الشريط الجانبي بناءً على نظام التصميم المتجاوب
            sidebar_width = responsive.get_sidebar_width(280)
            self.sidebar_frame.setFixedWidth(sidebar_width)

            sidebar_layout = QVBoxLayout(self.sidebar_frame)
            sidebar_layout.setContentsMargins(0, 0, 0, 0)
            sidebar_layout.setSpacing(0)
            
            # رأس القائمة الجانبية
            self.create_sidebar_header(sidebar_layout)
            
            # منطقة التمرير للأزرار
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setObjectName("sidebarScrollArea")
            
            # ويدجت الأزرار
            buttons_widget = QWidget()
            buttons_layout = QVBoxLayout(buttons_widget)
            buttons_layout.setContentsMargins(0, 10, 0, 10)
            buttons_layout.setSpacing(5)
            
            # إنشاء أزرار القائمة
            self.create_sidebar_buttons(buttons_layout)
            
            # إضافة مساحة مرنة في النهاية
            buttons_layout.addStretch()
            
            scroll_area.setWidget(buttons_widget)
            sidebar_layout.addWidget(scroll_area)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء القائمة الجانبية: {e}")
            raise
    
    def create_sidebar_header(self, layout):
        """إنشاء رأس القائمة الجانبية"""
        try:
            # إطار الرأس
            header_frame = QFrame()
            header_frame.setObjectName("sidebarHeader")
            
            # حساب ارتفاع متجاوب
            header_height = responsive.get_scaled_size(100)
            header_frame.setFixedHeight(max(80, header_height))
            
            header_layout = QVBoxLayout(header_frame)
            header_layout.setAlignment(Qt.AlignCenter)
            
            # تقليل الهوامش للشاشات الصغيرة
            margin = responsive.get_margin(15)
            header_layout.setContentsMargins(margin, margin, margin, margin)
            
            # عنوان التطبيق
            title_label = QLabel("حسابات المدارس")
            title_label.setObjectName("appTitle")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setWordWrap(True)
            header_layout.addWidget(title_label)
            
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس القائمة الجانبية: {e}")
            raise
    
    def create_sidebar_buttons(self, layout):
        """إنشاء أزرار القائمة الجانبية"""
        try:
            # تعريف أزرار القائمة
            menu_items = [
                {"name": "dashboard", "text": "الرئيسية", "icon": "dashboard.png", "active": True},
                {"name": "schools", "text": "المدارس", "icon": "schools.png", "active": True},
                {"name": "students", "text": "الطلاب", "icon": "students.png", "active": True},
                {"name": "teachers", "text": "المعلمين", "icon": "teachers.png", "active": True},
                {"name": "employees", "text": "الموظفين", "icon": "employees.png", "active": True},
                {"name": "installments", "text": "الأقساط", "icon": "installments.png", "active": True},
                {"name": "additional_fees", "text": "الرسوم الإضافية", "icon": "fees.png", "active": True},
                {"name": "separator1", "text": "---", "icon": None, "active": False},
                {"name": "external_income", "text": "الواردات الخارجية", "icon": "income.png", "active": True},
                {"name": "expenses", "text": "المصروفات", "icon": "expenses.png", "active": True},
                {"name": "salaries", "text": "الرواتب", "icon": "salaries.png", "active": True},
                {"name": "separator2", "text": "---", "icon": None, "active": False},
                {"name": "backup", "text": "النسخ الاحتياطية", "icon": "backup.png", "active": True},
                
                {"name": "settings", "text": "الإعدادات", "icon": "settings.png", "active": True},
                {"name": "logout", "text": "تسجيل خروج", "icon": "logout.png", "active": True},
            ]
            
            for item in menu_items:
                if item["text"] == "---":
                    # إضافة فاصل
                    separator = QFrame()
                    separator.setFrameShape(QFrame.HLine)
                    separator.setObjectName("menuSeparator")
                    layout.addWidget(separator)
                else:
                    # إنشاء زر القائمة
                    button = self.create_menu_button(
                        item["name"], 
                        item["text"], 
                        item["icon"], 
                        item["active"]
                    )
                    self.sidebar_buttons[item["name"]] = button
                    layout.addWidget(button)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء أزرار القائمة الجانبية: {e}")
            raise
    
    def create_menu_button(self, name: str, text: str, icon: str, active: bool):
        """إنشاء زر القائمة"""
        try:
            button = QPushButton(text)
            button.setObjectName("menuButton")
            button.setCheckable(True)
            
            # حساب ارتفاع متجاوب للزر
            button_height = responsive.get_button_height(45)
            button.setFixedHeight(button_height)
            
            # إضافة خصائص للزر
            button.setProperty("page_name", name)
            button.setProperty("active", active)
            
            # ربط الإشارة
            if name == "logout":
                button.clicked.connect(self.logout)
            elif active:
                # Capture page name in lambda to avoid late binding closure issue
                button.clicked.connect(lambda checked, page=name: self.navigate_to_page(page))
            else:
                button.clicked.connect(self.show_coming_soon)
                button.setProperty("coming_soon", True)
            
            return button
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء زر القائمة {name}: {e}")
            return QPushButton(text)
    
    def create_content_area(self):
        """إنشاء منطقة المحتوى"""
        try:
            # إطار المحتوى
            self.content_frame = QFrame()
            self.content_frame.setObjectName("contentFrame")
            
            content_layout = QVBoxLayout(self.content_frame)
            content_layout.setContentsMargins(20, 20, 20, 20)
            content_layout.setSpacing(0)
            
            # شريط العنوان
            self.create_content_header(content_layout)
            
            # منطقة الصفحات
            self.pages_stack = QStackedWidget()
            self.pages_stack.setObjectName("pagesStack")
            content_layout.addWidget(self.pages_stack)
            
            # تحميل الصفحات
            self.load_pages()
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء منطقة المحتوى: {e}")
            raise
    
    def create_content_header(self, layout):
        """إنشاء شريط عنوان المحتوى"""
        try:
            # إطار شريط العنوان
            header_frame = QFrame()
            header_frame.setObjectName("contentHeader")
            header_frame.setFixedHeight(60)
            
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(20, 5, 20, 5) # Reduced vertical margins
            header_layout.setAlignment(Qt.AlignVCenter) # Align content vertically in the center
            
            # عنوان الصفحة
            self.page_title = QLabel("لوحة التحكم")
            self.page_title.setObjectName("pageTitle")
            header_layout.addWidget(self.page_title)
            
            # مساحة مرنة
            header_layout.addStretch()
            
            # ويدجت العام الدراسي
            try:
                from ui.widgets.academic_year_widget import AcademicYearWidget
                self.academic_year_widget = AcademicYearWidget(show_label=True, auto_refresh=True)
                header_layout.addWidget(self.academic_year_widget)
            except ImportError as e:
                logging.warning(f"لم يتم تحميل ويدجت العام الدراسي: {e}")

            # زر النسخ الاحتياطي السريع
            self.quick_backup_btn = QPushButton("نسخ احتياطي سريع")
            self.quick_backup_btn.setObjectName("quickBackupButton")
            self.quick_backup_btn.setToolTip("إنشاء نسخة احتياطية فورية من قاعدة البيانات")
            self.quick_backup_btn.setStyleSheet("font-size: 18px;")
            self.quick_backup_btn.clicked.connect(self.create_quick_backup)
            header_layout.addWidget(self.quick_backup_btn)
            
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط عنوان المحتوى: {e}")
            raise
    
    def create_user_info(self):
        """إنشاء معلومات المستخدم"""
        try:
            user_frame = QFrame()
            user_frame.setObjectName("userInfo")
            
            user_layout = QHBoxLayout(user_frame)
            user_layout.setContentsMargins(15, 8, 15, 8)
            
            return user_frame
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء معلومات المستخدم: {e}")
            return QFrame()
    
    def load_pages(self):
        """تحميل صفحات التطبيق"""
        try:
            # صفحة لوحة التحكم
            self.load_dashboard_page()
            
            # صفحة المدارس
            self.load_schools_page()
            
            # صفحة الطلاب
            self.load_students_page()
            
            # صفحة المعلمين
            self.load_teachers_page()
            
            # صفحة الموظفين
            self.load_employees_page()
            
            # صفحة الأقساط
            self.load_installments_page()
            
            # صفحة الرسوم الإضافية
            self.load_additional_fees_page()
            
            # صفحة الواردات الخارجية
            self.load_external_income_page()
            
            # صفحة المصروفات
            self.load_expenses_page()
            
            # صفحة الرواتب
            self.load_salaries_page()
            
            # صفحة النسخ الاحتياطية
            self.load_backup_page()
            
            # صفحة الإعدادات
            self.load_settings_page()
            
            
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الصفحات: {e}")
            raise
    
    def load_dashboard_page(self):
        """تحميل صفحة لوحة التحكم"""
        try:
            from ui.pages.dashboard.dashboard_page import DashboardPage
            
            dashboard = DashboardPage()
            self.pages["dashboard"] = dashboard
            self.pages_stack.addWidget(dashboard)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة لوحة التحكم: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("لوحة التحكم", "مرحباً بك في نظام حسابات المدارس الأهلية")
            self.pages["dashboard"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_schools_page(self):
        """تحميل صفحة المدارس"""
        try:
            from ui.pages.schools.schools_page import SchoolsPage
            
            schools = SchoolsPage()
            self.pages["schools"] = schools
            self.pages_stack.addWidget(schools)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة المدارس: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("المدارس", "صفحة إدارة المدارس")
            self.pages["schools"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_students_page(self):
        """تحميل صفحة الطلاب"""
        # Always load StudentsPage; let errors surface rather than showing generic placeholder
        from ui.pages.students.students_page import StudentsPage
        students = StudentsPage()
        self.pages["students"] = students
        self.pages_stack.addWidget(students)
    
    def load_teachers_page(self):
        """تحميل صفحة المعلمين"""
        try:
            from ui.pages.teachers.teachers_page import TeachersPage
            teachers = TeachersPage()
            self.pages["teachers"] = teachers
            self.pages_stack.addWidget(teachers)
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة المعلمين: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("المعلمين", "صفحة إدارة المعلمين")
            self.pages["teachers"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_employees_page(self):
        """تحميل صفحة الموظفين"""
        try:
            from ui.pages.employees.employees_page import EmployeesPage
            employees = EmployeesPage()
            self.pages["employees"] = employees
            self.pages_stack.addWidget(employees)
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة الموظفين: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("الموظفين", "صفحة إدارة الموظفين")
            self.pages["employees"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_installments_page(self):
        """تحميل صفحة الأقساط"""
        try:
            from ui.pages.installments.installments_page import InstallmentsPage
            
            installments = InstallmentsPage()
            self.pages["installments"] = installments
            self.pages_stack.addWidget(installments)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة الأقساط: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("الأقساط", "صفحة إدارة الأقساط")
            self.pages["installments"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_additional_fees_page(self):
        """تحميل صفحة الرسوم الإضافية"""
        try:
            from ui.pages.additional_fees.additional_fees_page import AdditionalFeesPage
            
            additional_fees = AdditionalFeesPage()
            self.pages["additional_fees"] = additional_fees
            self.pages_stack.addWidget(additional_fees)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة الرسوم الإضافية: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("الرسوم الإضافية", "صفحة إدارة الرسوم الإضافية")
            self.pages["additional_fees"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_external_income_page(self):
        """تحميل صفحة الواردات الخارجية"""
        try:
            from ui.pages.external_income.external_income_page import ExternalIncomePage
            
            external_income = ExternalIncomePage()
            self.pages["external_income"] = external_income
            self.pages_stack.addWidget(external_income)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة الواردات الخارجية: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("الواردات الخارجية", "صفحة إدارة الواردات الخارجية")
            self.pages["external_income"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_expenses_page(self):
        """تحميل صفحة المصروفات"""
        try:
            from ui.pages.expenses.expenses_page import ExpensesPage
            
            expenses = ExpensesPage()
            self.pages["expenses"] = expenses
            self.pages_stack.addWidget(expenses)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة المصروفات: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("المصروفات", "صفحة إدارة المصروفات")
            self.pages["expenses"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_salaries_page(self):
        """تحميل صفحة الرواتب"""
        try:
            from ui.pages.salaries.salaries_page import SalariesPage
            salaries = SalariesPage()
            self.pages["salaries"] = salaries
            self.pages_stack.addWidget(salaries)
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة الرواتب: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("الرواتب", "صفحة إدارة الرواتب")
            self.pages["salaries"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_backup_page(self):
        """تحميل صفحة النسخ الاحتياطية"""
        try:
            from ui.pages.backup.backup_page import BackupPage
            backup = BackupPage()
            self.pages["backup"] = backup
            self.pages_stack.addWidget(backup)
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة النسخ الاحتياطية: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("النسخ الاحتياطية", "صفحة إدارة النسخ الاحتياطية")
            self.pages["backup"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_settings_page(self):
        """تحميل صفحة الإعدادات"""
        try:
            from ui.pages.settings.settings_page import SettingsPage
            settings = SettingsPage()
            self.pages["settings"] = settings
            self.pages_stack.addWidget(settings)
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة الإعدادات: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("الإعدادات", "صفحة إعدادات التطبيق")
            self.pages["settings"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    
    
    def create_placeholder_page(self, title: str, message: str):
        """إنشاء صفحة بديلة"""
        try:
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setAlignment(Qt.AlignCenter)

            # رسالة
            label = QLabel(message)
            label.setAlignment(Qt.AlignCenter)
            label.setObjectName("placeholderMessage")
            layout.addWidget(label)

            return widget

        except Exception as e:
            logging.error(f"خطأ في إنشاء الصفحة البديلة: {e}")
            return QWidget()
    
    def navigate_to_page(self, page_name: str):
        """الانتقال إلى صفحة معينة"""
        try:
            if page_name not in self.pages:
                logging.warning(f"الصفحة غير موجودة: {page_name}")
                return

            # تحديث حالة الأزرار
            self.update_sidebar_buttons(page_name)

            # عرض الصفحة
            page_widget = self.pages[page_name]
            self.pages_stack.setCurrentWidget(page_widget)

            # تحديث عنوان الصفحة
            self.update_page_title(page_name)

            # تحديث الصفحة الحالية
            self.current_page = page_name

            # إرسال إشارة تغيير الصفحة
            self.page_changed.emit(page_name)

            # تسجيل الإجراء
            log_user_action("تم الانتقال إلى صفحة", page_name)

        except Exception as e:
            logging.error(f"خطأ في الانتقال إلى الصفحة {page_name}: {e}")
    
    def update_sidebar_buttons(self, active_page: str):
        """تحديث حالة أزرار القائمة الجانبية"""
        try:
            for page_name, button in self.sidebar_buttons.items():
                button.setChecked(page_name == active_page)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث أزرار القائمة الجانبية: {e}")
    
    def update_page_title(self, page_name: str):
        """تحديث عنوان الصفحة"""
        try:
            titles = {
                "dashboard": "لوحة التحكم",
                "schools": "المدارس",
                "students": "الطلاب",
                "teachers": "المعلمين",
                "employees": "الموظفين",
                "installments": "الأقساط",
                "additional_fees": "الرسوم الإضافية",
                
                "external_income": "الواردات الخارجية",
                "expenses": "المصروفات",
                "salaries": "الرواتب",
                "backup": "النسخ الاحتياطية",
                "settings": "الإعدادات"
            }
            
            title = titles.get(page_name, "غير معروف")
            self.page_title.setText(title)
            
        except Exception as e:
            logging.error(f"خطأ في تحديث عنوان الصفحة: {e}")
    
    def show_dashboard(self):
        """عرض صفحة لوحة التحكم"""
        self.navigate_to_page("dashboard")
    def show_coming_soon(self):
        """عرض رسالة قريباً"""
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("قريباً")
            msg.setText("هذه الميزة قيد التطوير وستكون متاحة قريباً")
            msg.setLayoutDirection(Qt.RightToLeft)
            msg.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة قريباً: {e}")
    
    def setup_menu_bar(self):
        """إعداد شريط القوائم"""
        try:
            menubar = self.menuBar()
            menubar.setLayoutDirection(Qt.RightToLeft)
            
            # قائمة ملف
            file_menu = menubar.addMenu("ملف")
            
            # خروج
            exit_action = QAction("خروج", self)
            exit_action.setShortcut(QKeySequence.Quit)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # قائمة عرض
            view_menu = menubar.addMenu("عرض")
            
            # تحديث
            refresh_action = QAction("تحديث", self)
            refresh_action.setShortcut(QKeySequence.Refresh)
            refresh_action.triggered.connect(self.refresh_current_page)
            view_menu.addAction(refresh_action)
            
            # قائمة مساعدة
            help_menu = menubar.addMenu("مساعدة")
            
            # حول
            about_action = QAction("حول التطبيق", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد شريط القوائم: {e}")
    
    def setup_status_bar(self):
        """إعداد شريط الحالة"""
        try:
            statusbar = self.statusBar()
            statusbar.setLayoutDirection(Qt.RightToLeft)
            
            # رسالة الحالة
            statusbar.showMessage("جاهز")
            
            # معلومات إضافية (يمكن إضافتها لاحقاً)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد شريط الحالة: {e}")
    
    def setup_session_timer(self):
        """إعداد مؤقت الجلسة"""
        try:
            # مؤقت للتحقق من انتهاء الجلسة
            self.session_timer = QTimer()
            self.session_timer.timeout.connect(self.check_session)
            self.session_timer.start(60000)  # كل دقيقة
            
        except Exception as e:
            logging.error(f"خطأ في إعداد مؤقت الجلسة: {e}")
    
    def check_session(self):
        """التحقق من حالة الجلسة"""
        try:
            if not auth_manager.is_authenticated():
                self.show_session_expired()
                
        except Exception as e:
            logging.error(f"خطأ في التحقق من الجلسة: {e}")
    
    def show_session_expired(self):
        """عرض رسالة انتهاء الجلسة"""
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("انتهت الجلسة")
            msg.setText("انتهت جلسة العمل. يرجى تسجيل الدخول مرة أخرى.")
            msg.setLayoutDirection(Qt.RightToLeft)
            msg.finished.connect(self.close)
            msg.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة انتهاء الجلسة: {e}")
            self.close()
    
    def refresh_current_page(self):
        """تحديث الصفحة الحالية"""
        try:
            if self.current_page and self.current_page in self.pages:
                page_widget = self.pages[self.current_page]
                if hasattr(page_widget, 'refresh'):
                    page_widget.refresh()
                    
                log_user_action("تم تحديث الصفحة", self.current_page)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث الصفحة الحالية: {e}")
    
    def show_about(self):
        """عرض معلومات التطبيق"""
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("حول التطبيق")
            msg.setText(f"""
                {config.APP_NAME}
                الإصدار: {config.APP_VERSION}
                
                تطبيق محاسبي متكامل لإدارة حسابات المدارس الأهلية
                
                تطوير: {config.APP_ORGANIZATION}
            """)
            msg.setLayoutDirection(Qt.RightToLeft)
            msg.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض معلومات التطبيق: {e}")
    
    def logout(self):
        """تسجيل خروج"""
        try:
            reply = QMessageBox.question(
                self,
                "تسجيل خروج",
                "هل تريد تسجيل الخروج من التطبيق؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                auth_manager.logout()
                log_user_action("تم تسجيل الخروج")
                self.close()
                
        except Exception as e:
            logging.error(f"خطأ في تسجيل الخروج: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات النافذة"""
        try:
            # الحصول على متغيرات التصميم المتجاوب
            style_vars = responsive.get_responsive_stylesheet_vars()
            
            style = f"""
                /* Apply Cairo font to all widgets */
                * {{
                    font-family: 'Cairo';
                    font-size: {style_vars['base_font_size']}px;
                }}
                QMainWindow {{
                    background-color: #F8F9FA;
                    font-family: 'Cairo', 'Segoe UI', Tahoma, Arial;
                }}
                
                /* القائمة الجانبية */
                #sidebarFrame {{
                    background-color: #1F2937;
                    border-right: 1px solid #2d3748;
                }}
                
                #sidebarHeader {{
                    background-color: transparent;
                    border-bottom: 1px solid #2d3748;
                    padding: 0;
                }}
                
                #appTitle {{
                    color: #FFFFFF;
                    font-size: {style_vars['header_font_size']}px;
                    font-weight: bold;
                    padding: {style_vars['base_padding']}px;
                }}
                
                #sidebarScrollArea {{
                    background-color: transparent;
                    border: none;
                }}
                
                #menuButton {{
                    background-color: transparent;
                    border: none;
                    color: #000000;
                    text-align: center;
                    padding: {style_vars['button_padding']}px;
                    font-size: {style_vars['button_font_size']}px;
                    border-radius: {style_vars['border_radius']}px;
                    margin: 2px {style_vars['base_padding']}px;
                }}
                
                #menuButton:hover {{
                    background-color: #374151;
                    color: #000000;
                }}
                
                #menuButton:checked {{
                    background-color: #3B82F6;
                    color: #000000;
                    font-weight: bold;
                }}
                
                #menuButton[coming_soon="true"] {{
                    color: #000000;
                    font-style: italic;
                }}
                
                #menuSeparator {{
                    background-color: #374151;
                    margin: {style_vars['base_padding']}px {style_vars['base_padding'] * 2}px;
                    height: 1px;
                    border: none;
                }}
                
                /* منطقة المحتوى */
                #contentFrame {{
                    background-color: #F8F9FA;
                }}
                
                #contentHeader {{
                    background-color: white;
                    border-bottom: 1px solid #E9ECEF;
                    border-radius: 8px 8px 0 0;
                    padding: {style_vars['base_padding']}px {style_vars['base_padding'] * 2}px;
                }}
                
                #pageTitle {{
                    font-size: {style_vars['title_font_size']}px;
                    font-weight: bold;
                    color: #2C3E50;
                }}
                
                #userInfo {{
                    background-color: #ECF0F1;
                    border-radius: {style_vars['base_padding'] * 2}px;
                    padding: {style_vars['button_padding']}px {style_vars['base_padding'] + 2}px;
                }}
                
                #userName {{
                    color: #2C3E50;
                    font-size: {style_vars['button_font_size']}px;
                    font-weight: bold;
                }}
                
                #pagesStack {{
                    background-color: white;
                    border-radius: 0 0 8px 8px;
                    border: 1px solid #E9ECEF;
                }}
                
                #placeholderMessage {{
                    font-size: {style_vars['title_font_size']}px;
                    color: #7F8C8D;
                    padding: {style_vars['base_padding'] * 5}px;
                }}
                
                /* شريط القوائم */
                QMenuBar {{
                    background-color: #2C3E50;
                    color: white;
                    border-bottom: 1px solid #34495E;
                    font-size: {style_vars['base_font_size']}px;
                }}
                
                QMenuBar::item {{
                    background-color: transparent;
                    padding: {style_vars['button_padding']}px {style_vars['base_padding'] + 4}px;
                }}
                
                QMenuBar::item:selected {{
                    background-color: #34495E;
                }}
                
                QMenu {{
                    background-color: white;
                    border: 1px solid #BDC3C7;
                    font-size: {style_vars['base_font_size']}px;
                }}
                
                QMenu::item {{
                    padding: {style_vars['button_padding']}px {style_vars['base_padding'] + 4}px;
                    color: #2C3E50;
                }}
                
                QMenu::item:selected {{
                    background-color: #3498DB;
                    color: white;
                }}
                
                /* شريط الحالة */
                QStatusBar {{
                    background-color: #34495E;
                    color: white;
                    border-top: 1px solid #2C3E50;
                    font-size: {int(style_vars['base_font_size'] * 0.9)}px;
                }}
                
                /* شريط التمرير */
                QScrollBar:vertical {{
                    background-color: #ECF0F1;
                    width: {style_vars['scrollbar_width']}px;
                    border: none;
                }}
                
                QScrollBar::handle:vertical {{
                    background-color: #BDC3C7;
                    min-height: {max(20, int(20 * responsive.dpi_scale))}px;
                    border-radius: {style_vars['border_radius']}px;
                }}
                
                QScrollBar::handle:vertical:hover {{
                    background-color: #95A5A6;
                }}
                
                /* زر النسخ الاحتياطي السريع */
                QPushButton#quickBackupButton {{
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    border-radius: {style_vars['border_radius']}px;
                    padding: {style_vars['button_padding']}px {style_vars['base_padding'] + 4}px;
                    font-weight: bold;
                    font-size: {style_vars['small_font_size']}px;
                    min-width: 140px;
                }}
                
                QPushButton#quickBackupButton:hover {{
                    background-color: #229954;
                }}
                
                QPushButton#quickBackupButton:pressed {{
                    background-color: #1E8449;
                }}
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
            # استخدام تنسيق بسيط في حالة الخطأ
            basic_style = """
                QMainWindow {
                    background-color: #F8F9FA;
                    font-family: 'Cairo', 'Segoe UI', Tahoma, Arial;
                }
            """
            self.setStyleSheet(basic_style)
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
    
    def setup_responsive_ui(self):
        """إعداد واجهة المستخدم المتجاوبة"""
        try:
            # تحديث الأحجام بناءً على نظام التصميم المتجاوب
            if hasattr(self, 'sidebar_frame'):
                sidebar_width = responsive.get_sidebar_width(280)
                self.sidebar_frame.setFixedWidth(sidebar_width)
            
            # تحديث ارتفاع الأزرار
            button_height = responsive.get_button_height(45)
            for button in self.sidebar_buttons.values():
                button.setFixedHeight(button_height)
                
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة المستخدم المتجاوبة: {e}")
    
    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        try:
            reply = QMessageBox.question(
                self,
                "إغلاق التطبيق",
                "هل تريد إغلاق التطبيق؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # تنظيف الموارد
                if hasattr(self, 'session_timer'):
                    self.session_timer.stop()
                
                auth_manager.logout()
                log_user_action("تم إغلاق التطبيق")
                event.accept()
            else:
                event.ignore()
                
        except Exception as e:
            logging.error(f"خطأ في إغلاق النافذة: {e}")
            event.accept()
    
    def show_page_widget(self, widget):
        """عرض ويدجت كصفحة مؤقتة"""
        try:
            # إضافة الويدجت للمكدس
            self.pages_stack.addWidget(widget)
            
            # عرض الويدجت
            self.pages_stack.setCurrentWidget(widget)
            
            # تحديث عنوان الصفحة
            if hasattr(widget, 'windowTitle'):
                title = widget.windowTitle()
                if title:
                    self.page_title.setText(title)
                else:
                    self.page_title.setText("تفاصيل الطالب")
            else:
                self.page_title.setText("تفاصيل الطالب")
            
            # إلغاء تفعيل أزرار الشريط الجانبي
            self.update_sidebar_buttons("")
            
        except Exception as e:
            logging.error(f"خطأ في عرض الويدجت: {e}")
    
    def show_students_page(self):
        """العودة لصفحة الطلاب"""
        try:
            self.navigate_to_page("students")
            
        except Exception as e:
            logging.error(f"خطأ في العودة لصفحة الطلاب: {e}")
    
    def create_quick_backup(self):
        """إنشاء نسخة احتياطية سريعة"""
        try:
            from PyQt5.QtWidgets import QProgressDialog, QMessageBox
            from PyQt5.QtCore import QThread, pyqtSignal
            from datetime import datetime
            
            # عرض حوار التقدم
            progress = QProgressDialog(
                "جاري إنشاء النسخة الاحتياطية...",
                None, 0, 0, self
            )
            progress.setWindowTitle("نسخ احتياطي سريع")
            progress.setModal(True)
            progress.show()
            
            # إنشاء وصف للنسخة الاحتياطية
            description = f"نسخة احتياطية سريعة - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # إنشاء النسخة الاحتياطية
            success, message = backup_manager.create_backup(description)

            # إغلاق حوار التقدم
            progress.close()

            if success:
                # عرض رسالة النجاح المبسطة دون التكرار
                QMessageBox.information(
                    self, "نجح النسخ الاحتياطي",
                    message
                )
                # تسجيل الإجراء مع وصف النسخ الاحتياطي السريع
                log_user_action("backup quick", description)
            else:
                # تحقق من تعطيل النظام
                if "disabled" in message.lower():
                    QMessageBox.critical(
                        self, "خطأ في النسخ الاحتياطي",
                        "نظام النسخ الاحتياطي معطل. يرجى التحقق من صحة API Key واسم البوكت في ملف الإعدادات (config.py)."
                    )
                else:
                    QMessageBox.critical(
                        self, "خطأ في النسخ الاحتياطي",
                        f"فشل في إنشاء النسخة الاحتياطية:\n\n{message}"
                    )
                
        except Exception as e:
            logging.error(f"خطأ في النسخ الاحتياطي السريع: {e}")
            QMessageBox.critical(
                self, "خطأ", 
                f"حدث خطأ أثناء النسخ الاحتياطي:\n{e}"
            )