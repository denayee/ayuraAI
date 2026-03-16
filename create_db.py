from database import get_db

conn = get_db()
cur = conn.cursor()

# Create all tables
cur.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT,
    age INTEGER NOT NULL DEFAULT 0,
    gender TEXT,
    google_id TEXT UNIQUE,
    auth_provider TEXT DEFAULT 'local'
);

CREATE TABLE IF NOT EXISTS skin_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    skin_type TEXT,
    skin_color TEXT,
    skin_problems TEXT,
    sensitivity_level TEXT,
    oil_level TEXT,
    acne_presence TEXT,
    acne_level TEXT,
    dryness_presence TEXT,
    dryness_level TEXT,
    lifestyle TEXT,
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
    hair_fall_level TEXT,
    dryness_presence TEXT,
    dryness_level TEXT,
    scalp_itch_presence TEXT,
    scalp_itch_level TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS allergies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    ingredient TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS support_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    message TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
""")

conn.commit()
conn.close()

print("All tables created successfully")
