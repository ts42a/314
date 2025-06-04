# Start Flask shell
flask shell

# Then run:
from backend.models import db
from sqlalchemy import inspect

# Get table info
inspector = inspect(db.engine)
columns = inspector.get_columns('event')
for column in columns:
    print(f"{column['name']}: {column['type']}")

# Or get all tables
tables = inspector.get_table_names()
print(tables)
