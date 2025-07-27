#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

try:
    from core.printing.template_manager import TemplateManager
    from core.printing import TemplateType
    
    print("🔍 اختبار تفصيلي لعرض القالب...")
    
    manager = TemplateManager()
    data = {
        'students': [
            {'name': 'أحمد محمد', 'grade': 'الأول', 'section': 'أ'},
            {'name': 'فاطمة علي', 'grade': 'الثاني', 'section': 'ب'}
        ], 
        'total': 2
    }
    
    html = manager.render_template(TemplateType.STUDENT_LIST, data)
    
    print(f"✅ Template rendered successfully")
    print(f"Length: {len(html)}")
    print(f"Contains أحمد: {'أحمد' in html}")
    print(f"Contains students: {'students' in html}")
    
    if html:
        print("\nFirst 300 characters:")
        print(html[:300])
        print("\n" + "="*50)
        
        # البحث عن أسماء الطلاب
        if 'أحمد' in html:
            print("✅ Found student name أحمد")
        else:
            print("❌ Student name أحمد not found")
            
        # فحص الجدول
        if '<table' in html:
            print("✅ Table found in HTML")
        else:
            print("❌ No table found")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
