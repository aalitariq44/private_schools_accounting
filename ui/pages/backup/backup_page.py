#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة النسخ الاحتياطية
عرض وإدارة النسخ الاحتياطية المحفوظة على Supabase
"""

import logging
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QFrame, QHeaderView, QMessageBox, QProgressDialog,
    QTextEdit, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QGroupBox, QSplitter, QAbstractItemView, QTabWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

from core.backup.backup_manager import backup_manager
from core.backup.local_backup_manager import local_backup_manager
from core.utils.logger import log_user_action


class BackupWorker(QThread):
    """عامل إنشاء النسخ الاحتياطية في خيط منفصل"""
    
    finished = pyqtSignal(bool, str)  # نجح العملية، رسالة
    progress = pyqtSignal(str)  # رسالة التقدم
    
    def __init__(self, description=""):
        super().__init__()
        self.description = description
    
    def run(self):
        """تنفيذ عملية النسخ الاحتياطي"""
        try:
            self.progress.emit("جاري إنشاء النسخة الاحتياطية...")
            success, message = backup_manager.create_backup(self.description)
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, f"خطأ في إنشاء النسخة الاحتياطية: {e}")


class CreateBackupDialog(QDialog):
    """حوار إنشاء نسخة احتياطية جديدة"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إنشاء نسخة احتياطية جديدة")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        
        # معلومات النسخة الاحتياطية
        info_group = QGroupBox("معلومات النسخة الاحتياطية")
        info_layout = QFormLayout(info_group)
        
        # حقل الوصف
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("وصف اختياري للنسخة الاحتياطية...")
        info_layout.addRow("الوصف:", self.description_edit)
        
        # معلومات إضافية
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_label = QLabel(f"التاريخ والوقت: {current_time}")
        time_label.setStyleSheet("color: #666;")
        info_layout.addRow(time_label)
        
        layout.addWidget(info_group)
        
        # الأزرار
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # تخصيص النصوص
        buttons.button(QDialogButtonBox.Ok).setText("إنشاء النسخة")
        buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
        
        layout.addWidget(buttons)
    
    def get_description(self):
        """الحصول على وصف النسخة الاحتياطية"""
        return self.description_edit.text().strip()


class BackupPage(QWidget):
    """صفحة إدارة النسخ الاحتياطيات"""
    
    def __init__(self):
        super().__init__()
        self.backup_worker = None
        self.progress_dialog = None
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        # إزالة الاستدعاء المباشر لـ refresh_backups لتجنب التأخير عند بدء التطبيق
        # self.refresh_backups()
        
        # بدء تحديث النسخ الاحتياطية في الخلفية بعد 5 ثوانٍ من الإقلاع
        self.start_background_refresh()
        
        # تحديث النسخ الاحتياطية المحلية
        self.refresh_local_backups()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # عنوان الصفحة
        title_label = QLabel("إدارة النسخ الاحتياطية")
        title_label.setObjectName("pageTitle")
        layout.addWidget(title_label)
        
        # إنشاء التبويبات
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # تبويب النسخ الاحتياطي عبر الإنترنت
        self.setup_online_backup_tab()
        
        # تبويب النسخ الاحتياطية المحلية
        self.setup_local_backup_tab()
        
        # معلومات إضافية
        self.setup_info_panel(layout)
    
    def setup_online_backup_tab(self):
        """إعداد تبويب النسخ الاحتياطي عبر الإنترنت"""
        online_tab = QWidget()
        online_layout = QVBoxLayout(online_tab)
        online_layout.setSpacing(15)
        
        # شريط الأدوات
        toolbar_layout = QHBoxLayout()
        
        # زر إنشاء نسخة احتياطية جديدة
        self.create_backup_btn = QPushButton("إنشاء نسخة احتياطية جديدة")
        self.create_backup_btn.setObjectName("primaryButton")
        self.create_backup_btn.setMinimumHeight(35)
        toolbar_layout.addWidget(self.create_backup_btn)
        
        # زر تحديث القائمة
        self.refresh_btn = QPushButton("تحديث القائمة")
        self.refresh_btn.setObjectName("secondaryButton")
        self.refresh_btn.setMinimumHeight(35)
        toolbar_layout.addWidget(self.refresh_btn)
        
        toolbar_layout.addStretch()
        
        # زر تنظيف النسخ القديمة
        self.cleanup_btn = QPushButton("حذف النسخ القديمة")
        self.cleanup_btn.setObjectName("dangerButton")
        self.cleanup_btn.setMinimumHeight(35)
        toolbar_layout.addWidget(self.cleanup_btn)
        
        online_layout.addLayout(toolbar_layout)
        
        # جدول النسخ الاحتياطية عبر الإنترنت
        self.setup_online_backups_table(online_layout)
        
        self.tab_widget.addTab(online_tab, "النسخ الاحتياطي عبر الإنترنت")
    
    def setup_online_backups_table(self, layout):
        """إعداد جدول النسخ الاحتياطية عبر الإنترنت"""
        # إنشاء الجدول
        self.backups_table = QTableWidget()
        self.backups_table.setColumnCount(5)
        self.backups_table.setHorizontalHeaderLabels([
            "اسم الملف", "تاريخ الإنشاء", "الحجم", "الوصف", "العمليات"
        ])
        
        # إعدادات الجدول
        self.backups_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backups_table.setAlternatingRowColors(True)
        self.backups_table.setSortingEnabled(True)
        
        # إعدادات الأعمدة
        header = self.backups_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # اسم الملف
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # التاريخ
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # الحجم
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # الوصف
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # العمليات
        
        layout.addWidget(self.backups_table)
    
    def setup_local_backup_tab(self):
        """إعداد تبويب النسخ الاحتياطية المحلية"""
        local_tab = QWidget()
        local_layout = QVBoxLayout(local_tab)
        local_layout.setSpacing(15)
        
        # شريط الأدوات
        toolbar_layout = QHBoxLayout()
        
        # زر إنشاء نسخة احتياطية محلية جديدة
        self.create_local_backup_btn = QPushButton("إنشاء نسخة احتياطية محلية")
        self.create_local_backup_btn.setObjectName("primaryButton")
        self.create_local_backup_btn.setMinimumHeight(35)
        self.create_local_backup_btn.clicked.connect(self.create_local_backup)
        toolbar_layout.addWidget(self.create_local_backup_btn)
        
        # زر تحديث القائمة
        self.refresh_local_btn = QPushButton("تحديث القائمة")
        self.refresh_local_btn.setObjectName("secondaryButton")
        self.refresh_local_btn.setMinimumHeight(35)
        self.refresh_local_btn.clicked.connect(self.refresh_local_backups)
        toolbar_layout.addWidget(self.refresh_local_btn)
        
        toolbar_layout.addStretch()
        
        local_layout.addLayout(toolbar_layout)
        
        # جدول النسخ الاحتياطية المحلية
        self.setup_local_backups_table(local_layout)
        
        self.tab_widget.addTab(local_tab, "النسخ الاحتياطية المحلية")
    
    def setup_local_backups_table(self, layout):
        """إعداد جدول النسخ الاحتياطية المحلية"""
        # إنشاء الجدول
        self.local_backups_table = QTableWidget()
        self.local_backups_table.setColumnCount(5)
        self.local_backups_table.setHorizontalHeaderLabels([
            "اسم الملف", "تاريخ الإنشاء", "الحجم", "الوصف", "العمليات"
        ])
        
        # إعدادات الجدول
        self.local_backups_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.local_backups_table.setAlternatingRowColors(True)
        self.local_backups_table.setSortingEnabled(True)
        
        # إعدادات الأعمدة
        header = self.local_backups_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # اسم الملف
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # التاريخ
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # الحجم
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # الوصف
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # العمليات
        
        layout.addWidget(self.local_backups_table)
    
    def setup_info_panel(self, layout):
        """إعداد لوحة المعلومات"""
        info_frame = QFrame()
        info_frame.setObjectName("infoPanel")
        info_layout = QHBoxLayout(info_frame)
        
        # معلومات التخزين
        storage_info = QLabel("التخزين: Supabase Storage")
        storage_info.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(storage_info)
        
        info_layout.addStretch()
        
        # آخر تحديث
        self.last_update_label = QLabel("آخر تحديث: --")
        self.last_update_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(self.last_update_label)
        
        layout.addWidget(info_frame)
    
    def setup_styles(self):
        """إعداد التنسيقات CSS"""
        self.setStyleSheet("""
            /* أزرار الصفحة الرئيسية */
            QPushButton#primaryButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton#primaryButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton#secondaryButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#secondaryButton:hover {
                background-color: #7f8c8d;
            }
            
            QPushButton#dangerButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#dangerButton:hover {
                background-color: #c0392b;
            }
            
            /* أزرار العمليات الصغيرة */
            QPushButton#smallButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 11px;
                min-width: 60px;
                min-height: 20px;
                font-weight: normal;
            }
            
            QPushButton#smallButton:hover {
                background-color: #27ae60;
            }
            
            QPushButton#smallDangerButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 11px;
                min-width: 60px;
                min-height: 20px;
                font-weight: normal;
            }
            
            QPushButton#smallDangerButton:hover {
                background-color: #c0392b;
            }
            
            /* الجدول */
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #e0e0e0;
                selection-background-color: #e3f2fd;
            }
            
            QTableWidget::item {
                padding: 0px;
                border-bottom: 1px solid #e0e0e0;
                min-height: 0px;
            }
            
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #ddd;
                font-weight: bold;
            }
            
            /* لوحة المعلومات */
            QFrame#infoPanel {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 10px;
            }
            
            /* عنوان الصفحة */
            QLabel#pageTitle {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px 0;
            }
        """)
    
    def setup_connections(self):
        """إعداد الروابط والأحداث"""
        self.create_backup_btn.clicked.connect(self.create_new_backup)
        self.refresh_btn.clicked.connect(self.refresh_backups)
        self.cleanup_btn.clicked.connect(self.cleanup_old_backups)
    
    def start_background_refresh(self):
        """بدء تحديث النسخ الاحتياطية في الخلفية بعد فترة قصيرة"""
        # استخدام QTimer لتأجيل التحديث لمدة 5 ثوانٍ
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setSingleShot(True)  # يعمل مرة واحدة فقط
        self.refresh_timer.timeout.connect(self.refresh_backups)
        self.refresh_timer.start(5000)  # 5000 مللي ثانية = 5 ثوانٍ
    
    def cleanup_resources(self):
        """تنظيف الموارد عند إغلاق الصفحة"""
        if hasattr(self, 'refresh_timer') and self.refresh_timer.isActive():
            self.refresh_timer.stop()
    
    def closeEvent(self, event):
        """معالجة إغلاق الصفحة"""
        self.cleanup_resources()
        super().closeEvent(event)
    
    def create_new_backup(self):
        """إنشاء نسخة احتياطية جديدة"""
        try:
            # عرض حوار إدخال الوصف
            dialog = CreateBackupDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                description = dialog.get_description()
                
                # عرض حوار التقدم
                self.progress_dialog = QProgressDialog(
                    "جاري إنشاء النسخة الاحتياطية...",
                    None, 0, 0, self
                )
                self.progress_dialog.setWindowTitle("إنشاء نسخة احتياطية")
                self.progress_dialog.setModal(True)
                self.progress_dialog.show()
                
                # بدء عملية النسخ الاحتياطي
                self.backup_worker = BackupWorker(description)
                self.backup_worker.progress.connect(self.update_progress)
                self.backup_worker.finished.connect(self.backup_finished)
                self.backup_worker.start()
                
                # تسجيل العملية
                log_user_action(f"backup - create_backup: {description}")
                
        except Exception as e:
            logging.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في إنشاء النسخة الاحتياطية:\n{e}")
    
    def update_progress(self, message):
        """تحديث رسالة التقدم"""
        if self.progress_dialog:
            self.progress_dialog.setLabelText(message)
    
    def backup_finished(self, success, message):
        """معالجة انتهاء عملية النسخ الاحتياطي"""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        if success:
            QMessageBox.information(self, "نجح", message)
            self.refresh_backups()  # تحديث القائمة
        else:
            QMessageBox.critical(self, "خطأ", message)
        
        self.backup_worker = None
    
    def refresh_backups(self):
        """تحديث قائمة النسخ الاحتياطية"""
        try:
            # جلب النسخ الاحتياطية
            backups = backup_manager.list_backups()
            
            # تحديث الجدول
            self.backups_table.setRowCount(len(backups))
            
            for row, backup in enumerate(backups):
                # تحديد ارتفاع الصف ليتناسب مع الأزرار الصغيرة
                self.backups_table.setRowHeight(row, 30)
                
                # اسم الملف
                filename_item = QTableWidgetItem(backup['filename'])
                filename_item.setFlags(filename_item.flags() & ~Qt.ItemIsEditable)
                self.backups_table.setItem(row, 0, filename_item)
                
                # تاريخ الإنشاء
                date_item = QTableWidgetItem(backup['formatted_date'])
                date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                self.backups_table.setItem(row, 1, date_item)
                
                # الحجم
                size_item = QTableWidgetItem(backup['formatted_size'])
                size_item.setFlags(size_item.flags() & ~Qt.ItemIsEditable)
                self.backups_table.setItem(row, 2, size_item)
                
                # الوصف (يمكن استخراجه من معلومات النسخة)
                description_item = QTableWidgetItem("--")
                description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
                self.backups_table.setItem(row, 3, description_item)
                
                # أزرار العمليات
                operations_widget = self.create_operations_widget(backup)
                self.backups_table.setCellWidget(row, 4, operations_widget)
            
            # تحديث وقت آخر تحديث
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_update_label.setText(f"آخر تحديث: {current_time}")
            
            logging.info(f"تم تحديث قائمة النسخ الاحتياطية: {len(backups)} نسخة")
            
        except Exception as e:
            logging.warning(f"فشل في تحديث قائمة النسخ الاحتياطية (ربما لا يوجد اتصال بالإنترنت): {e}")
            # لا نعرض رسالة خطأ للمستخدم إذا كان التحديث في الخلفية
            # فقط نسجل الخطأ ونترك الجدول فارغاً أو كما هو
            if hasattr(self, 'refresh_timer') and self.refresh_timer.isActive():
                # إذا كان التحديث في الخلفية، لا نعرض رسالة خطأ
                pass
            else:
                # إذا كان التحديث يدوياً (بالضغط على زر تحديث)، نعرض رسالة خطأ
                QMessageBox.critical(self, "خطأ", f"خطأ في تحديث القائمة:\n{e}")
    
    def create_operations_widget(self, backup):
        """إنشاء ويجيت العمليات لكل نسخة احتياطية"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        
        
        # زر الحذف
        delete_btn = QPushButton("حذف")
        delete_btn.setObjectName("smallDangerButton")
        delete_btn.clicked.connect(lambda: self.delete_backup(backup))
        layout.addWidget(delete_btn)
        
        return widget
    
    
    def delete_backup(self, backup):
        """حذف نسخة احتياطية"""
        try:
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                f"هل أنت متأكد من حذف النسخة الاحتياطية؟\n\n"
                f"الملف: {backup['filename']}\n"
                f"التاريخ: {backup['formatted_date']}\n"
                f"الحجم: {backup['formatted_size']}\n\n"
                f"هذه العملية لا يمكن التراجع عنها!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, message = backup_manager.delete_backup(backup['path'])
                
                if success:
                    QMessageBox.information(self, "نجح", message)
                    self.refresh_backups()  # تحديث القائمة
                    log_user_action(f"backup - delete_backup: {backup['filename']}")
                else:
                    QMessageBox.critical(self, "خطأ", message)
                    
        except Exception as e:
            logging.error(f"خطأ في حذف النسخة الاحتياطية: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في الحذف:\n{e}")
    
    def cleanup_old_backups(self):
        """تنظيف النسخ الاحتياطية القديمة"""
        try:
            # تأكيد العملية
            reply = QMessageBox.question(
                self, "تأكيد التنظيف",
                "هل تريد حذف جميع النسخ الاحتياطية الأقدم من 30 يوماً؟\n\n"
                "هذه العملية لا يمكن التراجع عنها!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, message = backup_manager.cleanup_old_backups(30)
                
                if success:
                    QMessageBox.information(self, "نجح", message)
                    self.refresh_backups()  # تحديث القائمة
                    log_user_action("backup - cleanup_old_backups: keep_days=30")
                else:
                    QMessageBox.critical(self, "خطأ", message)
                    
        except Exception as e:
            logging.error(f"خطأ في تنظيف النسخ الاحتياطية: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في التنظيف:\n{e}")
    
    def create_local_backup(self):
        """إنشاء نسخة احتياطية محلية"""
        try:
            from core.database.connection import db_manager
            
            # الحصول على مسار النسخ الاحتياطي المحلي من قاعدة البيانات
            query = "SELECT setting_value FROM app_settings WHERE setting_key = ?"
            result = db_manager.execute_fetch_one(query, ("local_backup_path",))
            
            if not result:
                QMessageBox.warning(self, "تحذير", "يرجى تحديد مسار النسخ الاحتياطي المحلي أولاً من صفحة الإعدادات")
                return
            
            backup_path = result[0]
            
            if not os.path.exists(backup_path):
                QMessageBox.warning(self, "تحذير", "مسار النسخ الاحتياطي المحلي غير موجود")
                return
            
            # إدخال الوصف
            from PyQt5.QtWidgets import QInputDialog
            description, ok = QInputDialog.getText(
                self,
                "وصف النسخة الاحتياطية",
                "أدخل وصفاً للنسخة الاحتياطية (اختياري):"
            )
            
            if not ok:
                return
            
            # إنشاء النسخة الاحتياطية
            success, message = local_backup_manager.create_local_backup(backup_path, description)
            
            if success:
                QMessageBox.information(self, "نجح", message)
                self.refresh_local_backups()
                log_user_action(f"تم إنشاء نسخة احتياطية محلية: {message}")
            else:
                QMessageBox.critical(self, "خطأ", message)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء النسخة الاحتياطية المحلية: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
    
    def refresh_local_backups(self):
        """تحديث قائمة النسخ الاحتياطية المحلية"""
        try:
            from core.database.connection import db_manager
            
            # الحصول على مسار النسخ الاحتياطي المحلي
            query = "SELECT setting_value FROM app_settings WHERE setting_key = ?"
            result = db_manager.execute_fetch_one(query, ("local_backup_path",))
            
            if not result:
                self.local_backups_table.setRowCount(0)
                return
            
            backup_path = result[0]
            
            if not os.path.exists(backup_path):
                self.local_backups_table.setRowCount(0)
                return
            
            # جلب النسخ الاحتياطية المحلية
            backups = local_backup_manager.list_local_backups(backup_path)
            
            # تحديث الجدول
            self.local_backups_table.setRowCount(len(backups))
            
            for row, backup in enumerate(backups):
                # تحديد ارتفاع الصف
                self.local_backups_table.setRowHeight(row, 30)
                
                # اسم الملف
                filename_item = QTableWidgetItem(backup.get('filename', ''))
                filename_item.setFlags(filename_item.flags() & ~Qt.ItemIsEditable)
                self.local_backups_table.setItem(row, 0, filename_item)
                
                # تاريخ الإنشاء
                date_item = QTableWidgetItem(backup.get('date', 'غير محدد'))
                date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                self.local_backups_table.setItem(row, 1, date_item)
                
                # الحجم
                file_size = backup.get('file_size', 0)
                size_item = QTableWidgetItem(f"{file_size} بايت")
                size_item.setFlags(size_item.flags() & ~Qt.ItemIsEditable)
                self.local_backups_table.setItem(row, 2, size_item)
                
                # الوصف
                description_item = QTableWidgetItem(backup.get('description', 'بدون وصف'))
                description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
                self.local_backups_table.setItem(row, 3, description_item)
                
                # أزرار العمليات
                operations_widget = self.create_local_operations_widget(backup)
                self.local_backups_table.setCellWidget(row, 4, operations_widget)
            
            logging.info(f"تم تحديث قائمة النسخ الاحتياطية المحلية: {len(backups)} نسخة")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث قائمة النسخ الاحتياطية المحلية: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تحديث القائمة:\n{e}")
    
    def create_local_operations_widget(self, backup):
        """إنشاء ويجيت العمليات للنسخ الاحتياطية المحلية"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        
        # زر الاستعادة
        restore_btn = QPushButton("استعادة")
        restore_btn.setObjectName("smallButton")
        restore_btn.clicked.connect(lambda: self.restore_local_backup(backup))
        layout.addWidget(restore_btn)
        
        # زر الحذف
        delete_btn = QPushButton("حذف")
        delete_btn.setObjectName("smallDangerButton")
        delete_btn.clicked.connect(lambda: self.delete_local_backup(backup))
        layout.addWidget(delete_btn)
        
        return widget
    
    def restore_local_backup(self, backup):
        """استعادة نسخة احتياطية محلية"""
        try:
            # تأكيد الاستعادة
            reply = QMessageBox.question(
                self, "تأكيد الاستعادة",
                f"هل أنت متأكد من استعادة هذه النسخة الاحتياطية؟\n\n"
                f"الملف: {backup.get('filename', '')}\n"
                f"التاريخ: {backup.get('date', '')}\n"
                f"الوصف: {backup.get('description', '')}\n\n"
                f"سيتم استبدال قاعدة البيانات الحالية بهذه النسخة!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                backup_file_path = backup.get('file_path', '')
                
                if not backup_file_path:
                    QMessageBox.critical(self, "خطأ", "مسار ملف النسخة الاحتياطية غير صحيح")
                    return
                
                success, message = local_backup_manager.restore_local_backup(backup_file_path)
                
                if success:
                    QMessageBox.information(self, "نجح", message)
                    log_user_action(f"تم استعادة نسخة احتياطية محلية: {backup.get('filename', '')}")
                    # قد نحتاج إلى إعادة تشغيل التطبيق أو تحديث البيانات
                else:
                    QMessageBox.critical(self, "خطأ", message)
            
        except Exception as e:
            logging.error(f"خطأ في استعادة النسخة الاحتياطية المحلية: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في الاستعادة: {str(e)}")
    
    def delete_local_backup(self, backup):
        """حذف نسخة احتياطية محلية"""
        try:
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                f"هل أنت متأكد من حذف النسخة الاحتياطية؟\n\n"
                f"الملف: {backup.get('filename', '')}\n"
                f"التاريخ: {backup.get('date', '')}\n"
                f"الوصف: {backup.get('description', '')}\n\n"
                f"هذه العملية لا يمكن التراجع عنها!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                backup_file_path = backup.get('file_path', '')
                
                if not backup_file_path:
                    QMessageBox.critical(self, "خطأ", "مسار ملف النسخة الاحتياطية غير صحيح")
                    return
                
                # حذف الملف
                import os
                if os.path.exists(backup_file_path):
                    os.remove(backup_file_path)
                    QMessageBox.information(self, "نجح", "تم حذف النسخة الاحتياطية بنجاح")
                    self.refresh_local_backups()
                    log_user_action(f"تم حذف نسخة احتياطية محلية: {backup.get('filename', '')}")
                else:
                    QMessageBox.warning(self, "تحذير", "الملف غير موجود")
            
        except Exception as e:
            logging.error(f"خطأ في حذف النسخة الاحتياطية المحلية: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في الحذف: {str(e)}")
