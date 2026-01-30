import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Create all tables
cur.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    age INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS skin_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    skin_type TEXT,
    skin_color TEXT,
    skin_problems TEXT,
    sensitivity_level TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS hair_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    hair_type TEXT,
    hair_color TEXT,
    hair_problems TEXT,
    scalp_condition TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS allergies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    ingredient TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
""")

conn.commit()
conn.close()

print("All tables created successfully")
