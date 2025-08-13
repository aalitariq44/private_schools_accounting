# -*- coding: utf-8 -*-
"""
اختبار منطق استخراج بيانات المدرسة من قاعدة البيانات
"""

import os
import sys
import sqlite3

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config

def test_database_school_data():
    """اختبار جلب بيانات المدرسة من قاعدة البيانات"""
    
    try:
        # الاتصال بقاعدة البيانات
        db_path = os.path.join(config.DATA_DIR, 'database', 'schools.db')
        print(f"🔗 الاتصال بقاعدة البيانات: {db_path}")
        
        if not os.path.exists(db_path):
            print("❌ ملف قاعدة البيانات غير موجود")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # جلب المدارس
        print("\n📋 المدارس الموجودة:")
        cursor.execute("SELECT id, name_ar, address, phone FROM schools")
        schools = cursor.fetchall()
        
        if not schools:
            print("❌ لا توجد مدارس في قاعدة البيانات")
            return
            
        for school in schools:
            school_id, name, address, phone = school
            print(f"  🏫 المدرسة {school_id}: {name}")
            print(f"     📍 العنوان: {address or 'غير محدد'}")
            print(f"     📞 الهاتف: {phone or 'غير محدد'}")
            print()
        
        # اختبار الاستعلام المحدث
        print("🧪 اختبار الاستعلام المحدث للطلاب:")
        student_query = """
            SELECT s.*, sc.name_ar as school_name, sc.address as school_address, sc.phone as school_phone
            FROM students s
            LEFT JOIN schools sc ON s.school_id = sc.id
            LIMIT 3
        """
        
        cursor.execute(student_query)
        students = cursor.fetchall()
        
        if students:
            print(f"✅ تم جلب {len(students)} طالب/طالبة مع بيانات المدرسة:")
            
            # الحصول على أسماء الأعمدة
            column_names = [description[0] for description in cursor.description]
            
            for i, student in enumerate(students, 1):
                print(f"\n👤 الطالب {i}:")
                student_dict = dict(zip(column_names, student))
                
                print(f"  📝 الاسم: {student_dict.get('name', 'غير محدد')}")
                print(f"  🏫 المدرسة: {student_dict.get('school_name', 'غير محدد')}")
                print(f"  📍 عنوان المدرسة: {student_dict.get('school_address', 'غير محدد')}")
                print(f"  📞 هاتف المدرسة: {student_dict.get('school_phone', 'غير محدد')}")
                print(f"  📚 الصف: {student_dict.get('grade', 'غير محدد')}")
                print(f"  🏷️ الشعبة: {student_dict.get('section', 'غير محدد')}")
        else:
            print("❌ لا توجد طلاب في قاعدة البيانات")
        
        conn.close()
        
        print("\n✅ تم اختبار استخراج بيانات المدرسة بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ في اختبار قاعدة البيانات: {e}")
        import traceback
        traceback.print_exc()

def test_receipt_data_structure():
    """اختبار هيكل بيانات الوصل"""
    
    print("\n🧪 اختبار هيكل بيانات الوصل:")
    
    # محاكاة البيانات التي سيتم تمريرها للطباعة
    sample_student_data = [
        1,  # id
        'أحمد محمد علي',  # name
        1,  # school_id
        'الرابع الابتدائي',  # grade
        'أ',  # section
        'ذكر',  # gender
        '07701234567',  # phone
        'احمد محمود',  # guardian_name
        '07709876543',  # guardian_phone
        1000000,  # total_fee
        '2024-09-01',  # start_date
        'نشط',  # status
        '2024-09-01 10:00:00',  # created_at
        '2024-09-01 10:00:00',  # updated_at
        'مدرسة النور الأهلية',  # school_name (من الاستعلام الجديد)
        'شارع الجامعة، حي المنصور، بغداد',  # school_address (من الاستعلام الجديد)
        '07701234567 - 07709876543'  # school_phone (من الاستعلام الجديد)
    ]
    
    print(f"📊 عدد عناصر البيانات: {len(sample_student_data)}")
    print(f"📍 عنوان المدرسة (المؤشر -2): {sample_student_data[-2]}")
    print(f"📞 هاتف المدرسة (المؤشر -1): {sample_student_data[-1]}")
    
    # تكوين بيانات الوصل
    receipt_data = {
        'id': 123,
        'installment_id': 123,
        'student_name': sample_student_data[1],
        'school_name': sample_student_data[-3],  # school_name
        'school_address': sample_student_data[-2],  # school_address
        'school_phone': sample_student_data[-1],  # school_phone
        'grade': sample_student_data[3],
        'section': sample_student_data[4],
        'amount': 250000,
        'payment_date': '2025-01-15',
        'total_fee': sample_student_data[9],
        'total_paid': 500000,
        'remaining': 500000
    }
    
    print("\n📋 بيانات الوصل المكونة:")
    for key, value in receipt_data.items():
        print(f"  {key}: {value}")
    
    print("\n✅ تم تكوين بيانات الوصل بنجاح!")
    return receipt_data

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 اختبار استخراج بيانات المدرسة للطباعة")
    print("=" * 70)
    
    # اختبار قاعدة البيانات
    test_database_school_data()
    
    # اختبار هيكل البيانات
    test_receipt_data_structure()
    
    print("\n" + "=" * 70)
    print("📝 الخلاصة:")
    print("✅ تم تحديث الاستعلام لجلب عنوان المدرسة ورقم الهاتف")
    print("✅ تم تحديث دالة الطباعة لاستخدام البيانات الحقيقية")
    print("✅ تم إضافة النصوص الافتراضية عند عدم توفر البيانات")
    print("🔄 يجب اختبار الطباعة الفعلية من داخل التطبيق")
    print("=" * 70)
