from accountant.root import app  # noqa: F401
from accountant.root.database import create_migration

create_migration()
