from core.database.connection import db_manager

# Get table info
table_info = db_manager.get_table_info('students')
print("Current students table structure:")
for column in table_info:
    print(f"  {column['name']}: {column['type']} {'(PK)' if column['pk'] else ''}")