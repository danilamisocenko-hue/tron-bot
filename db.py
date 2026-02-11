import sqlite3

conn = sqlite3.connect("wallets.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    address TEXT,
    network TEXT
)
""")
conn.commit()

def add_wallet(user_id, address, network):
    cursor.execute(
        "INSERT INTO wallets (user_id, address, network) VALUES (?, ?, ?)",
        (user_id, address, network)
    )
    conn.commit()

def get_wallets():
    cursor.execute("SELECT user_id, address, network FROM wallets")
    return cursor.fetchall()