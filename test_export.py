#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لوظيفة التصدير المحسنة
"""

import sys
import os
from datetime import datetime
import csv

def create_sample_csv():
    """إنشاء ملف CSV نموذجي لتجربة التنسيق"""
    
    # بيانات نموذجية للواردات الخارجية
    sample_data = [
        {'id': 1, 'income_type': 'رسوم الحانوت', 'description': 'بيع الأدوات المدرسية', 'amount': 50000, 'category': 'الحانوت', 'income_date': '2025-01-15', 'school_name': 'مدرسة النور', 'notes': 'دفعة شهر يناير'},
        {'id': 2, 'income_type': 'رسوم النقل', 'description': 'رسوم نقل الطلاب', 'amount': 75000, 'category': 'النقل', 'income_date': '2025-01-20', 'school_name': 'مدرسة الأمل', 'notes': 'خدمة النقل الشهرية'},
        {'id': 3, 'income_type': 'تبرع خيري', 'description': 'تبرع من أحد المحسنين', 'amount': 100000, 'category': 'التبرعات', 'income_date': '2025-01-25', 'school_name': None, 'notes': 'للمساعدة في تطوير المرافق'},
    ]
    
    # إنشاء اسم الملف
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"External_Income_Report_Test_{timestamp}.csv"
    
    # كتابة الملف بالتنسيق المحسن
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        # كتابة معلومات التقرير
        writer.writerow([f"تقرير الواردات الخارجية - {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
        writer.writerow([f"إجمالي عدد الواردات: {len(sample_data)}"])
        writer.writerow([f"إجمالي المبلغ: {sum(income['amount'] for income in sample_data):,.2f} د.ع"])
        writer.writerow([])  # سطر فارغ
        
        # كتابة رأس الجدول
        headers = ["ID", "Income Type", "Description", "Amount (IQD)", "Category", "Date", "School", "Notes"]
        writer.writerow(headers)
        
        # كتابة البيانات
        for income in sample_data:
            row = [
                income['id'],
                income['income_type'] or '',
                income['description'] or '',
                f"{income['amount']:,.2f}",
                income['category'] or '',
                income['income_date'] or '',
                income['school_name'] or 'General',
                income['notes'] or ''
            ]
            writer.writerow(row)
        
        # إضافة إحصائيات في النهاية
        writer.writerow([])  # سطر فارغ
        writer.writerow(['Statistics:'])
        writer.writerow(['Total Records:', len(sample_data)])
        writer.writerow(['Total Amount:', f"{sum(income['amount'] for income in sample_data):,.2f} IQD"])
        writer.writerow(['Average Amount:', f"{sum(income['amount'] for income in sample_data) / len(sample_data):,.2f} IQD"])
        writer.writerow(['Max Amount:', f"{max(income['amount'] for income in sample_data):,.2f} IQD"])
        writer.writerow(['Min Amount:', f"{min(income['amount'] for income in sample_data):,.2f} IQD"])
    
    print(f"تم إنشاء ملف CSV نموذجي: {filename}")
    print("جرب فتحه في Excel لرؤية التنسيق الجديد!")
    
    return filename

if __name__ == "__main__":
    try:
        filename = create_sample_csv()
        
        # محاولة فتح الملف تلقائياً
        try:
            os.startfile(filename)
            print("تم فتح الملف في Excel...")
        except:
            print(f"لم يتمكن من فتح الملف تلقائياً. يمكنك فتحه يدوياً: {filename}")
            
    except Exception as e:
        print(f"خطأ: {e}")
