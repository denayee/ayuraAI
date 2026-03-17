from database import get_db
from werkzeug.security import generate_password_hash

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
    auth_provider TEXT DEFAULT 'local',
    is_admin INTEGER DEFAULT 0,
    reset_token TEXT,
    reset_token_expiry TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

CREATE TABLE IF NOT EXISTS user_stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS webinar_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    webinar_topic TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS webinars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# --- Migrations for existing tables ---
def add_column_if_not_exists(table, column, definition):
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        conn.commit()
        print(f"Migration: Added '{column}' column to '{table}'.")
    except Exception:
        pass

# Ensure webinars table exists (via executescript above, but being explicit)
add_column_if_not_exists("users", "is_admin", "INTEGER DEFAULT 0")
add_column_if_not_exists("users", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
add_column_if_not_exists("webinar_registrations", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
add_column_if_not_exists("webinar_registrations", "webinar_id", "INTEGER")
add_column_if_not_exists("users", "reset_token", "TEXT")
add_column_if_not_exists("users", "reset_token_expiry", "TIMESTAMP")

# Initialize Admin User
try:
    admin_email = "admin@ayuraai.com"
    admin_password = generate_password_hash("admin")
    cur.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (name, username, email, password, age, gender, is_admin) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("Admin", "admin", admin_email, admin_password, 99, "Other", 1))
        print("Admin user initialized.")
except Exception as e:
    print(f"Error initializing admin: {e}")

conn.commit()
conn.close()

print("All tables created successfully")
