#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لوظائف التصدير المحسنة
"""

import sys
import os
from datetime import datetime
import csv

def create_sample_external_income_csv():
    """إنشاء ملف CSV نموذجي للواردات الخارجية"""
    
    sample_data = [
        {'id': 1, 'income_type': 'رسوم الحانوت', 'description': 'بيع الأدوات المدرسية', 'amount': 50000, 'category': 'الحانوت', 'income_date': '2025-01-15', 'school_name': 'مدرسة النور', 'notes': 'دفعة شهر يناير'},
        {'id': 2, 'income_type': 'رسوم النقل', 'description': 'رسوم نقل الطلاب', 'amount': 75000, 'category': 'النقل', 'income_date': '2025-01-20', 'school_name': 'مدرسة الأمل', 'notes': 'خدمة النقل الشهرية'},
        {'id': 3, 'income_type': 'تبرع خيري', 'description': 'تبرع من أحد المحسنين', 'amount': 100000, 'category': 'التبرعات', 'income_date': '2025-01-25', 'school_name': None, 'notes': 'للمساعدة في تطوير المرافق'},
        {'id': 4, 'income_type': 'إيجار قاعة', 'description': 'إيجار قاعة للمناسبات', 'amount': 200000, 'category': 'إيجارات', 'income_date': '2025-02-01', 'school_name': 'مدرسة الأمل', 'notes': 'حفل زفاف'},
        {'id': 5, 'income_type': 'نشاط رياضي', 'description': 'رسوم المشاركة في البطولة', 'amount': 25000, 'category': 'الأنشطة', 'income_date': '2025-02-10', 'school_name': 'مدرسة النور', 'notes': 'بطولة كرة القدم'},
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"External_Income_Report_Sample_{timestamp}.csv"
    
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow([f"تقرير الواردات الخارجية - {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
        writer.writerow([f"إجمالي عدد الواردات: {len(sample_data)}"])
        writer.writerow([f"إجمالي المبلغ: {sum(income['amount'] for income in sample_data):,.2f} د.ع"])
        writer.writerow([])
        
        headers = ["ID", "Income Type", "Description", "Amount (IQD)", "Category", "Date", "School", "Notes"]
        writer.writerow(headers)
        
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
        
        writer.writerow([])
        writer.writerow(['Statistics:'])
        writer.writerow(['Total Records:', len(sample_data)])
        writer.writerow(['Total Amount:', f"{sum(income['amount'] for income in sample_data):,.2f} IQD"])
        writer.writerow(['Average Amount:', f"{sum(income['amount'] for income in sample_data) / len(sample_data):,.2f} IQD"])
        writer.writerow(['Max Amount:', f"{max(income['amount'] for income in sample_data):,.2f} IQD"])
        writer.writerow(['Min Amount:', f"{min(income['amount'] for income in sample_data):,.2f} IQD"])
    
    return filename

def create_sample_expenses_csv():
    """إنشاء ملف CSV نموذجي للمصروفات"""
    
    sample_data = [
        {'id': 1, 'expense_type': 'رواتب المعلمين', 'amount': 500000, 'description': 'رواتب شهر يناير', 'expense_date': '2025-01-31', 'school_name': 'مدرسة النور', 'notes': 'رواتب 10 معلمين'},
        {'id': 2, 'expense_type': 'فواتير الكهرباء', 'amount': 75000, 'description': 'فاتورة الكهرباء', 'expense_date': '2025-01-15', 'school_name': 'مدرسة الأمل', 'notes': 'فاتورة شهر ديسمبر'},
        {'id': 3, 'expense_type': 'مواد تنظيف', 'amount': 25000, 'description': 'شراء مواد تنظيف', 'expense_date': '2025-01-20', 'school_name': None, 'notes': 'للفصل الدراسي الثاني'},
        {'id': 4, 'expense_type': 'صيانة أجهزة', 'amount': 150000, 'description': 'صيانة أجهزة الحاسوب', 'expense_date': '2025-02-05', 'school_name': 'مدرسة النور', 'notes': 'صيانة 20 جهاز'},
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Expenses_Report_Sample_{timestamp}.csv"
    
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow([f"تقرير المصروفات - {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
        writer.writerow([f"إجمالي عدد المصروفات: {len(sample_data)}"])
        writer.writerow([f"إجمالي المبلغ: {sum(expense['amount'] for expense in sample_data):,.2f} د.ع"])
        writer.writerow([])
        
        headers = ["ID", "Expense Type", "Amount (IQD)", "Description", "Date", "School", "Notes"]
        writer.writerow(headers)
        
        for expense in sample_data:
            row = [
                expense['id'],
                expense['expense_type'] or '',
                f"{expense['amount']:,.2f}",
                expense['description'] or '',
                expense['expense_date'] or '',
                expense['school_name'] or 'General',
                expense['notes'] or ''
            ]
            writer.writerow(row)
        
        writer.writerow([])
        writer.writerow(['Statistics:'])
        writer.writerow(['Total Records:', len(sample_data)])
        writer.writerow(['Total Amount:', f"{sum(expense['amount'] for expense in sample_data):,.2f} IQD"])
        writer.writerow(['Average Amount:', f"{sum(expense['amount'] for expense in sample_data) / len(sample_data):,.2f} IQD"])
        writer.writerow(['Max Amount:', f"{max(expense['amount'] for expense in sample_data):,.2f} IQD"])
        writer.writerow(['Min Amount:', f"{min(expense['amount'] for expense in sample_data):,.2f} IQD"])
    
    return filename

def create_sample_fees_csv():
    """إنشاء ملف CSV نموذجي للرسوم الإضافية"""
    
    sample_data = [
        (1, 'أحمد محمد علي', 'مدرسة النور', 'رسوم امتحانات', 50000, True, '2025-01-15', 'دُفعت في الوقت المحدد', '2025-01-10'),
        (2, 'فاطمة حسن', 'مدرسة الأمل', 'رسوم أنشطة', 30000, False, None, 'لم تُدفع بعد', '2025-01-12'),
        (3, 'علي أحمد', 'مدرسة النور', 'رسوم كتب', 75000, True, '2025-01-20', 'دُفعت مع تأخير', '2025-01-08'),
        (4, 'سارة محمود', 'مدرسة الأمل', 'رسوم نقل', 40000, False, None, 'متأخرة عن الدفع', '2025-01-05'),
        (5, 'محمد عبدالله', None, 'رسوم تسجيل', 100000, True, '2025-02-01', 'رسوم تسجيل جديد', '2025-01-25'),
    ]
    
    total_amount = sum(fee[4] or 0 for fee in sample_data)
    paid_fees = [fee for fee in sample_data if fee[5]]
    unpaid_fees = [fee for fee in sample_data if not fee[5]]
    total_paid = sum(fee[4] or 0 for fee in paid_fees)
    total_unpaid = sum(fee[4] or 0 for fee in unpaid_fees)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Additional_Fees_Report_Sample_{timestamp}.csv"
    
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow([f"تقرير الرسوم الإضافية - {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
        writer.writerow([f"إجمالي عدد الرسوم: {len(sample_data)}"])
        writer.writerow([f"إجمالي المبلغ: {total_amount:,.2f} د.ع"])
        writer.writerow([f"المبلغ المدفوع: {total_paid:,.2f} د.ع"])
        writer.writerow([f"المبلغ المتبقي: {total_unpaid:,.2f} د.ع"])
        writer.writerow([])
        
        headers = ["ID", "Student Name", "School", "Fee Type", "Amount (IQD)", "Status", "Payment Date", "Notes", "Created Date"]
        writer.writerow(headers)
        
        for fee in sample_data:
            row = [
                fee[0] or '',
                fee[1] or '',
                fee[2] or 'General',
                fee[3] or '',
                f"{fee[4] or 0:,.2f}",
                "Paid" if fee[5] else "Unpaid",
                fee[6] or '',
                fee[7] or '',
                fee[8] or ''
            ]
            writer.writerow(row)
        
        writer.writerow([])
        writer.writerow(['Statistics:'])
        writer.writerow(['Total Records:', len(sample_data)])
        writer.writerow(['Total Amount:', f"{total_amount:,.2f} IQD"])
        writer.writerow(['Paid Amount:', f"{total_paid:,.2f} IQD"])
        writer.writerow(['Unpaid Amount:', f"{total_unpaid:,.2f} IQD"])
        writer.writerow(['Paid Fees Count:', len(paid_fees)])
        writer.writerow(['Unpaid Fees Count:', len(unpaid_fees)])
        if sample_data:
            avg_amount = total_amount / len(sample_data)
            writer.writerow(['Average Amount:', f"{avg_amount:,.2f} IQD"])
            amounts = [fee[4] or 0 for fee in sample_data]
            writer.writerow(['Max Amount:', f"{max(amounts):,.2f} IQD"])
            writer.writerow(['Min Amount:', f"{min(amounts):,.2f} IQD"])
    
    return filename

def main():
    """تشغيل اختبار شامل للتصدير"""
    
    print("=== اختبار وظائف التصدير المحسنة ===\n")
    
    try:
        print("1. إنشاء تقرير الواردات الخارجية...")
        income_file = create_sample_external_income_csv()
        print(f"✓ تم إنشاء: {income_file}")
        
        print("\n2. إنشاء تقرير المصروفات...")
        expenses_file = create_sample_expenses_csv()
        print(f"✓ تم إنشاء: {expenses_file}")
        
        print("\n3. إنشاء تقرير الرسوم الإضافية...")
        fees_file = create_sample_fees_csv()
        print(f"✓ تم إنشاء: {fees_file}")
        
        print("\n=== تم إنشاء جميع التقارير بنجاح! ===")
        print("\nالملفات المُنشأة:")
        print(f"- {income_file}")
        print(f"- {expenses_file}")
        print(f"- {fees_file}")
        
        print("\nجرب فتح هذه الملفات في Excel لرؤية التنسيق الجديد!")
        
        # محاولة فتح الملفات
        try:
            print("\nمحاولة فتح الملفات...")
            os.startfile(income_file)
            os.startfile(expenses_file)
            os.startfile(fees_file)
            print("تم فتح الملفات في Excel...")
        except Exception as e:
            print(f"لم يتمكن من فتح الملفات تلقائياً: {e}")
            
    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == "__main__":
    main()
