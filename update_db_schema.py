import sqlite3
from database import get_db

conn = get_db()
cur = conn.cursor()

# 1. Add 'name' column to tables if it doesn't exist
tables = ["skin_profile", "hair_profile", "allergies"]

for table in tables:
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN name TEXT")
        print(f"Added 'name' column to {table}")
    except sqlite3.OperationalError as e:
        print(f"Skipped {table}: {e}")

# 2. Backfill 'name' data from 'users' table
# For hair_profile
cur.execute("""
    UPDATE hair_profile
    SET name = (SELECT name FROM users WHERE users.id = hair_profile.user_id)
""")

# For skin_profile
cur.execute("""
    UPDATE skin_profile
    SET name = (SELECT name FROM users WHERE users.id = skin_profile.user_id)
""")

# For allergies
cur.execute("""
    UPDATE allergies
    SET name = (SELECT name FROM users WHERE users.id = allergies.user_id)
""")

conn.commit()
conn.close()
print("Migration completed successfully.")
