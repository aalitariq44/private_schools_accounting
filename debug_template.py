#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.printing.template_manager import TemplateManager
from core.printing import TemplateType

try:
    manager = TemplateManager()
    
    # اختبار get_template مباشرة
    template = manager.get_template(TemplateType.STUDENT_LIST)
    print(f"Template object: {template}")
    
    if template:
        print("✅ Template loaded successfully")
        
        # اختبار البيانات
        data = {
            'students': [
                {'name': 'أحمد محمد', 'grade': 'الأول', 'section': 'أ'},
            ], 
            'total': 1
        }
        
        # اختبار render مباشرة
        try:
            result = template.render(data)
            print(f"Render result length: {len(result)}")
            print(f"Contains أحمد: {'أحمد' in result}")
            
            if 'أحمد' in result:
                print("✅ Template rendering works correctly")
            else:
                print("❌ Template rendering failed - checking content...")
                print("First 500 chars:")
                print(result[:500])
                
        except Exception as e:
            print(f"❌ Render error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Template not loaded")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
