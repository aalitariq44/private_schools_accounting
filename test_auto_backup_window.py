#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق اختبار مبسط للنسخ الاحتياطي التلقائي
يعرض نافذة بسيطة لاختبار closeEvent
"""

import sys
from pathlib import Path

# إضافة المجلد الرئيسي للتطبيق إلى المسار
sys.path.insert(0, str(Path(__file__).parent))

import config
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from datetime import datetime
from core.backup.backup_manager import backup_manager
from core.utils.logger import log_user_action

class TestAutoBackupWindow(QMainWindow):
    """نافذة اختبار للنسخ الاحتياطي التلقائي"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار النسخ الاحتياطي التلقائي عند الخروج")
        self.setGeometry(300, 300, 500, 300)
        
        # إعداد الواجهة
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # عنوان
        title = QLabel("🧪 اختبار النسخ الاحتياطي التلقائي عند الخروج")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # معلومات
        info = QLabel(f"""
الإعدادات الحالية:
• AUTO_BACKUP_ON_EXIT: {config.AUTO_BACKUP_ON_EXIT}
• AUTO_BACKUP_SHOW_SUCCESS_MESSAGE: {config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE}
• AUTO_BACKUP_CONFIRMATION_DIALOG: {config.AUTO_BACKUP_CONFIRMATION_DIALOG}

🎯 لاختبار الميزة:
1. اضغط زر "اختبار النسخ التلقائي" لاختبار الدالة مباشرة
2. أو اضغط زر إغلاق النافذة (❌) لاختبار closeEvent
        """)
        info.setStyleSheet("margin: 20px; background: #f0f0f0; padding: 15px; border-radius: 5px;")
        layout.addWidget(info)
        
        # أزرار الاختبار
        test_btn = QPushButton("🔧 اختبار النسخ التلقائي مباشرة")
        test_btn.clicked.connect(self.test_auto_backup)
        test_btn.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addWidget(test_btn)
        
        close_btn = QPushButton("🚪 إغلاق التطبيق (اختبار closeEvent)")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("padding: 10px; font-size: 14px; background: #e74c3c; color: white;")
        layout.addWidget(close_btn)
        
        # رسالة الحالة
        self.status_label = QLabel("✅ التطبيق جاهز للاختبار")
        self.status_label.setStyleSheet("margin: 10px; color: green;")
        layout.addWidget(self.status_label)
    
    def test_auto_backup(self):
        """اختبار دالة النسخ الاحتياطي التلقائي مباشرة"""
        try:
            self.status_label.setText("🔄 جاري اختبار النسخ الاحتياطي...")
            QApplication.processEvents()
            
            # محاولة النسخ الاحتياطي
            result = self.create_auto_backup_on_exit()
            
            if result:
                self.status_label.setText("✅ تم اختبار النسخ الاحتياطي بنجاح!")
                QMessageBox.information(self, "نجح الاختبار", "🎉 تم اختبار النسخ الاحتياطي التلقائي بنجاح!")
            else:
                self.status_label.setText("❌ فشل اختبار النسخ الاحتياطي")
                QMessageBox.warning(self, "فشل الاختبار", "❌ فشل في اختبار النسخ الاحتياطي التلقائي")
                
        except Exception as e:
            self.status_label.setText(f"💥 خطأ: {e}")
            QMessageBox.critical(self, "خطأ في الاختبار", f"💥 خطأ أثناء الاختبار:\n\n{e}")
    
    def create_auto_backup_on_exit(self):
        """نسخة مبسطة من دالة النسخ الاحتياطي التلقائي"""
        try:
            from PyQt5.QtWidgets import QProgressDialog
            
            # عرض شريط التقدم
            progress = QProgressDialog(
                "🔄 جاري إنشاء نسخة احتياطية تلقائية للاختبار...",
                None, 0, 0, self
            )
            progress.setWindowTitle("اختبار النسخ الاحتياطي")
            progress.setModal(True)
            progress.show()
            QApplication.processEvents()
            
            # إنشاء وصف
            description = f"اختبار نسخة احتياطية تلقائية - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # محاولة النسخ الاحتياطي
            success, message = backup_manager.create_backup(description)
            
            # إغلاق شريط التقدم
            progress.close()
            
            if success:
                if config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE:
                    QMessageBox.information(
                        self, "نجح النسخ الاحتياطي",
                        "✅ تم إنشاء النسخة الاحتياطية التلقائية بنجاح!\n\n" + message
                    )
                log_user_action("backup auto-exit test", description)
                return True
            else:
                QMessageBox.warning(
                    self, "فشل النسخ الاحتياطي",
                    f"❌ فشل في النسخ الاحتياطي:\n\n{message}"
                )
                return False
                
        except Exception as e:
            QMessageBox.critical(
                self, "خطأ في النسخ الاحتياطي",
                f"💥 خطأ أثناء النسخ الاحتياطي:\n\n{e}"
            )
            return False
    
    def closeEvent(self, event):
        """اختبار closeEvent مع النسخ الاحتياطي التلقائي"""
        try:
            # التحقق من تفعيل النسخ الاحتياطي التلقائي
            if config.AUTO_BACKUP_ON_EXIT:
                reply = QMessageBox.question(
                    self,
                    "اختبار إغلاق التطبيق",
                    "🧪 هذا اختبار لميزة النسخ الاحتياطي التلقائي!\n\n"
                    "هل تريد إغلاق التطبيق؟\n\n"
                    "🔄 سيتم إنشاء نسخة احتياطية تلقائية قبل الإغلاق.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
            else:
                reply = QMessageBox.question(
                    self,
                    "إغلاق التطبيق",
                    "هل تريد إغلاق التطبيق؟\n\n"
                    "(النسخ الاحتياطي التلقائي معطل في الإعدادات)",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
            
            if reply == QMessageBox.Yes:
                if config.AUTO_BACKUP_ON_EXIT:
                    # إنشاء نسخة احتياطية تلقائية
                    backup_success = self.create_auto_backup_on_exit()
                    
                    if backup_success is False:
                        # فشل النسخ الاحتياطي - اسأل المستخدم
                        continue_reply = QMessageBox.question(
                            self,
                            "فشل النسخ الاحتياطي",
                            "❌ فشل في النسخ الاحتياطي التلقائي.\n\n"
                            "هل تريد المتابعة والخروج بدون نسخة احتياطية؟",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        
                        if continue_reply == QMessageBox.No:
                            event.ignore()
                            return
                
                print("✅ تم اختبار closeEvent بنجاح!")
                print("🎉 الميزة تعمل بشكل صحيح!")
                event.accept()
            else:
                event.ignore()
                
        except Exception as e:
            print(f"❌ خطأ في closeEvent: {e}")
            QMessageBox.critical(
                self, "خطأ",
                f"💥 خطأ أثناء إغلاق التطبيق:\n\n{e}"
            )
            event.accept()

def main():
    """الدالة الرئيسية للاختبار"""
    app = QApplication(sys.argv)
    
    # إنشاء النافذة
    window = TestAutoBackupWindow()
    window.show()
    
    print("🚀 تطبيق اختبار النسخ الاحتياطي التلقائي")
    print("📋 اختبر الميزة عبر:")
    print("   1. الضغط على 'اختبار النسخ التلقائي مباشرة'")
    print("   2. الضغط على زر إغلاق النافذة (❌)")
    print("   3. أو الضغط على 'إغلاق التطبيق'")
    
    # تشغيل التطبيق
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
