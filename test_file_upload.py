#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة اختبار رفع وقراءة الملفات - Supabase Storage Test
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QLabel, QTextEdit, QFileDialog,
    QMessageBox, QListWidget, QSplitter, QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent))

import config

try:
    from supabase import create_client
except ImportError:
    print("supabase library not installed; please install with: pip install supabase")
    sys.exit(1)


class UploadThread(QThread):
    """خيط رفع الملفات"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, file_path, content, filename):
        super().__init__()
        self.file_path = file_path
        self.content = content
        self.filename = filename
        
    def run(self):
        try:
            # إنشاء عميل Supabase
            supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            bucket_name = config.SUPABASE_BUCKET
            
            self.progress.emit("بدء عملية الرفع...")
            
            # إنشاء مسار الملف
            upload_path = f"test_files/{self.filename}"
            
            # رفع الملف
            upload_result = supabase.storage.from_(bucket_name).upload(
                upload_path, 
                self.content.encode('utf-8')
            )
            
            # التحقق من النتيجة
            if hasattr(upload_result, 'error') and upload_result.error:
                self.finished.emit(False, f"فشل في الرفع: {upload_result.error}")
            else:
                self.finished.emit(True, f"تم رفع الملف بنجاح: {upload_path}")
                
        except Exception as e:
            self.finished.emit(False, f"خطأ في الرفع: {str(e)}")


class ListFilesThread(QThread):
    """خيط عرض الملفات"""
    files_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def run(self):
        try:
            # إنشاء عميل Supabase
            supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            bucket_name = config.SUPABASE_BUCKET
            
            # جلب قائمة الملفات
            files = supabase.storage.from_(bucket_name).list("test_files")
            
            file_list = []
            for file_item in files:
                if file_item.get('name', '').endswith('.txt'):
                    file_info = {
                        'name': file_item['name'],
                        'path': f"test_files/{file_item['name']}",
                        'size': file_item.get('metadata', {}).get('size', 0),
                        'created_at': file_item.get('created_at', '')
                    }
                    file_list.append(file_info)
            
            self.files_loaded.emit(file_list)
            
        except Exception as e:
            self.error_occurred.emit(f"خطأ في جلب قائمة الملفات: {str(e)}")


class ReadFileThread(QThread):
    """خيط قراءة الملفات"""
    file_content = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        try:
            # إنشاء عميل Supabase
            supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            bucket_name = config.SUPABASE_BUCKET
            
            # قراءة الملف
            file_data = supabase.storage.from_(bucket_name).download(self.file_path)
            
            # تحويل البيانات إلى نص
            content = file_data.decode('utf-8')
            self.file_content.emit(content)
            
        except Exception as e:
            self.error_occurred.emit(f"خطأ في قراءة الملف: {str(e)}")


class FileUploadTestWindow(QMainWindow):
    """نافذة اختبار رفع الملفات"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار رفع وقراءة الملفات - Supabase Storage")
        self.setGeometry(100, 100, 1000, 700)
        
        # إعداد الخط
        font = QFont("Arial", 10)
        self.setFont(font)
        
        self.setup_ui()
        self.setup_connections()
        
        # تحديث قائمة الملفات عند البدء
        self.refresh_files()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(central_widget)
        
        # عنوان
        title_label = QLabel("اختبار رفع وقراءة الملفات - Supabase Storage")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # تقسيم إلى قسمين
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # القسم الأيسر - رفع الملفات
        upload_widget = self.create_upload_section()
        splitter.addWidget(upload_widget)
        
        # القسم الأيمن - عرض الملفات
        files_widget = self.create_files_section()
        splitter.addWidget(files_widget)
        
        # تعيين النسب
        splitter.setSizes([400, 600])
        
    def create_upload_section(self):
        """إنشاء قسم رفع الملفات"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # عنوان القسم
        section_title = QLabel("رفع ملف جديد")
        section_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(section_title)
        
        # اسم الملف
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("اسم الملف:"))
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("example.txt")
        filename_layout.addWidget(self.filename_input)
        layout.addLayout(filename_layout)
        
        # محتوى الملف
        layout.addWidget(QLabel("محتوى الملف:"))
        self.content_editor = QTextEdit()
        self.content_editor.setPlaceholderText("اكتب محتوى الملف هنا...")
        layout.addWidget(self.content_editor)
        
        # أزرار
        buttons_layout = QHBoxLayout()
        
        self.load_file_btn = QPushButton("تحميل ملف من الجهاز")
        self.load_file_btn.clicked.connect(self.load_file_from_disk)
        buttons_layout.addWidget(self.load_file_btn)
        
        self.upload_btn = QPushButton("رفع الملف")
        self.upload_btn.clicked.connect(self.upload_file)
        buttons_layout.addWidget(self.upload_btn)
        
        layout.addLayout(buttons_layout)
        
        # رسائل الحالة
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        return widget
        
    def create_files_section(self):
        """إنشاء قسم عرض الملفات"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # عنوان القسم
        section_title = QLabel("الملفات المرفوعة")
        section_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(section_title)
        
        # زر التحديث
        self.refresh_btn = QPushButton("تحديث القائمة")
        self.refresh_btn.clicked.connect(self.refresh_files)
        layout.addWidget(self.refresh_btn)
        
        # قائمة الملفات
        self.files_list = QListWidget()
        self.files_list.itemClicked.connect(self.file_selected)
        layout.addWidget(self.files_list)
        
        # عرض محتوى الملف
        layout.addWidget(QLabel("محتوى الملف المختار:"))
        self.file_content_viewer = QTextEdit()
        self.file_content_viewer.setReadOnly(True)
        layout.addWidget(self.file_content_viewer)
        
        return widget
        
    def setup_connections(self):
        """إعداد الاتصالات"""
        pass
        
    def load_file_from_disk(self):
        """تحميل ملف من القرص الصلب"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "اختر ملف نصي", 
            "", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.content_editor.setText(content)
                
                # استخراج اسم الملف
                filename = os.path.basename(file_path)
                self.filename_input.setText(filename)
                
                self.status_label.setText(f"تم تحميل الملف: {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في قراءة الملف: {str(e)}")
                
    def upload_file(self):
        """رفع الملف"""
        filename = self.filename_input.text().strip()
        content = self.content_editor.toPlainText()
        
        if not filename:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم الملف")
            return
            
        if not content:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال محتوى الملف")
            return
            
        # إضافة امتداد .txt إذا لم يكن موجود
        if not filename.endswith('.txt'):
            filename += '.txt'
            
        # إضافة timestamp لتجنب تضارب الأسماء
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        # بدء عملية الرفع
        self.upload_btn.setEnabled(False)
        self.status_label.setText("جاري الرفع...")
        
        self.upload_thread = UploadThread("", content, filename)
        self.upload_thread.progress.connect(self.status_label.setText)
        self.upload_thread.finished.connect(self.upload_finished)
        self.upload_thread.start()
        
    def upload_finished(self, success, message):
        """انتهاء عملية الرفع"""
        self.upload_btn.setEnabled(True)
        
        if success:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: green;")
            # تحديث قائمة الملفات
            self.refresh_files()
            # مسح المحرر
            self.content_editor.clear()
            self.filename_input.clear()
        else:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: red;")
            
    def refresh_files(self):
        """تحديث قائمة الملفات"""
        self.files_list.clear()
        self.file_content_viewer.clear()
        
        self.list_thread = ListFilesThread()
        self.list_thread.files_loaded.connect(self.files_loaded)
        self.list_thread.error_occurred.connect(self.files_error)
        self.list_thread.start()
        
    def files_loaded(self, files):
        """تم تحميل قائمة الملفات"""
        self.files_list.clear()
        
        for file_info in files:
            item_text = f"{file_info['name']} ({file_info['size']} bytes)"
            self.files_list.addItem(item_text)
            # حفظ مسار الملف في البيانات
            item = self.files_list.item(self.files_list.count() - 1)
            item.setData(Qt.UserRole, file_info['path'])
            
    def files_error(self, error_message):
        """خطأ في تحميل الملفات"""
        self.status_label.setText(error_message)
        self.status_label.setStyleSheet("color: red;")
        
    def file_selected(self, item):
        """تم اختيار ملف"""
        file_path = item.data(Qt.UserRole)
        
        if file_path:
            self.file_content_viewer.clear()
            self.file_content_viewer.setText("جاري تحميل المحتوى...")
            
            self.read_thread = ReadFileThread(file_path)
            self.read_thread.file_content.connect(self.file_content_loaded)
            self.read_thread.error_occurred.connect(self.file_read_error)
            self.read_thread.start()
            
    def file_content_loaded(self, content):
        """تم تحميل محتوى الملف"""
        self.file_content_viewer.setText(content)
        
    def file_read_error(self, error_message):
        """خطأ في قراءة الملف"""
        self.file_content_viewer.setText(f"خطأ في قراءة الملف: {error_message}")


def main():
    app = QApplication(sys.argv)
    
    # التحقق من وجود إعدادات Supabase
    if not hasattr(config, 'SUPABASE_URL') or not config.SUPABASE_URL:
        QMessageBox.critical(None, "خطأ", "لم يتم العثور على إعدادات Supabase في config.py")
        sys.exit(1)
        
    window = FileUploadTestWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
