import sqlite3
import re

def init_db():
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            warns INTEGER DEFAULT 0
        )
    """)

    # Bad words
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bad_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE
        )
    """)

    # Group configuration
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_config (
        group_id INTEGER PRIMARY KEY,
        kick_enabled BOOLEAN DEFAULT 0,
        ban_enabled BOOLEAN DEFAULT 0
    )
    """)
    #authorized users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authorized_users (
         user_id INTEGER PRIMARY KEY
       )
           """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS banned_users (
         user_id INTEGER PRIMARY KEY
       )
           """)

    cursor.execute("""
CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote TEXT NOT NULL,
    author TEXT NOT NULL,
    time_of_day TEXT NOT NULL CHECK(time_of_day IN ('morning', 'afternoon', 'evening', 'night'))
)
""")

    cursor.execute('''
CREATE TABLE IF NOT EXISTS group_quotes (
    group_id INTEGER PRIMARY KEY,
    enabled INTEGER DEFAULT 0
)
''')       

    conn.commit()
    conn.close()

    print("Database initialized.")

def get_all_enabled_groups():
    from database import conn
    cursor = conn.cursor()
    cursor.execute("SELECT group_id FROM group_quotes WHERE enabled = 1")
    return [row[0] for row in cursor.fetchall()]

# ban users
def ban_user(user_id: int) -> bool:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO banned_users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

# unban users
def unban_user(user_id: int) -> bool:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM banned_users WHERE user_id = ?", (user_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0

def add_user(user_id: int, name: str):
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, name, warns) VALUES (?, ?, 0)", (user_id, name))
    conn.commit()
    conn.close()

def add_bad_word(word: str) -> bool:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    word = word.lower()
    cursor.execute("SELECT 1 FROM bad_words WHERE word = ?", (word,))
    exists = cursor.fetchone()
    if exists:
        conn.close()
        return False
    cursor.execute("INSERT INTO bad_words (word) VALUES (?)", (word,))
    conn.commit()
    conn.close()
    return True 


def remove_bad_word(word: str) -> bool:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cleaned_word = word.strip().lower()
    cursor.execute("DELETE FROM bad_words WHERE LOWER(word) = ?", (cleaned_word,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0 

def get_users():
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, warns FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def get_bad_words():
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM bad_words")
    words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return words

def warn_user(user_id: int):
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET warns = warns + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_warns(user_id: int):
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("SELECT warns FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def load_bad_words() -> list[str]:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM bad_words")
    words = [row[0].strip().lower() for row in cursor.fetchall()]
    conn.close()
    return words

def is_bad_word_in_message(text: str) -> bool:
    text = text.lower()
    bad_words = load_bad_words()

    for word in bad_words:
        pattern = "".join([f"{char}+" for char in word])
        if re.search(pattern, text):
            return True
    return False

def get_group_config(group_id: int):
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("SELECT kick_enabled, ban_enabled FROM group_config WHERE group_id = ?", (group_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (False, False) 

def update_group_config(group_id: int, kick_enabled: bool, ban_enabled: bool):
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO group_config (group_id, kick_enabled, ban_enabled)
    VALUES (?, ?, ?)
    """, (group_id, kick_enabled, ban_enabled))
    conn.commit()
    conn.close()

def remove_group_config(group_id: int):
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM group_config WHERE group_id = ?", (group_id,))
    conn.commit()
    conn.close()

def is_authorized_user(user_id: int) -> bool:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM authorized_users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()
    conn.close()
    return exists is not None

def add_authorized_user(user_id: int) -> bool:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO authorized_users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def remove_authorized_user(user_id: int) -> bool:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM authorized_users WHERE user_id = ?", (user_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0

def get_authorized_users() -> list[int]:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM authorized_users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def add_quote(quote: str, author: str, time_of_day: str) -> bool:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO quotes (quote, author, time_of_day) VALUES (?, ?, ?)",
                   (quote, author, time_of_day))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_quote(time_of_day: str) -> tuple[str, str] | None:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("SELECT quote, author FROM quotes WHERE time_of_day=? ORDER BY RANDOM() LIMIT 1",
                   (time_of_day,))
    row = cursor.fetchone()
    conn.close()
    return row if row else None

def enable_quotes(group_id: int) -> bool:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO group_quotes (group_id, enabled) VALUES (?, 1)", (group_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def disable_quotes(group_id: int) -> bool:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO group_quotes (group_id, enabled) VALUES (?, 0)", (group_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def quotes_enabled(group_id: int) -> bool:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("SELECT enabled FROM group_quotes WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    conn.close()
    return row and row[0] == 1

def get_all_quotes() -> list[tuple[str, str, str]]:
    conn = sqlite3.connect("./storage/poison.db")
    cursor = conn.cursor()
    cursor.execute("SELECT quote, author, time_of_day FROM quotes")
    quotes = cursor.fetchall()
    conn.close()
    return quotes
