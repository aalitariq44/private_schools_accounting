#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.printing.template_manager import TemplateManager
from core.printing import TemplateType

manager = TemplateManager()

# بيانات بسيطة
data = {
    'students': [
        {'name': 'أحمد محمد', 'grade': 'الأول', 'section': 'أ'},
    ], 
    'total': 1
}

try:
    result = manager.render_template(TemplateType.STUDENT_LIST, data)
    print(f"✅ Template rendered: {len(result)} chars")
    print(f"Contains أحمد: {'أحمد' in result}")
    
    if result:
        # حفظ النتيجة لفحصها
        with open('test_output.html', 'w', encoding='utf-8') as f:
            f.write(result)
        print("✅ Output saved to test_output.html")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
