import sqlite3, os, hashlib, binascii
from datetime import datetime

DB_NAME = "inventory.db"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# ----- Tables -----
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER CHECK(quantity >= 0),
    price REAL CHECK(price >= 0)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total_price REAL NOT NULL,
    date TEXT NOT NULL,
    sold_by TEXT NOT NULL
)
""")

conn.commit()

# ----- Password hashing -----
def _hash_password(password: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return binascii.hexlify(hashed).decode(), binascii.hexlify(salt).decode()

def create_user(username, password, role="user"):
    try:
        pw_hash, salt_hex = _hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt, role) VALUES (?,?,?,?)",
            (username, pw_hash, salt_hex, role.lower()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_login(username: str, password: str):
    cursor.execute("SELECT password_hash, salt, role FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    if not row:
        return False, None
    stored_hash, stored_salt_hex, role = row
    salt = binascii.unhexlify(stored_salt_hex)
    new_hash, _ = _hash_password(password, salt)
    return (new_hash == stored_hash, role if new_hash == stored_hash else None)

# Default admin account if none exists
cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
if cursor.fetchone()[0] == 0:
    create_user("admin", "1234", "admin")

# ----- Inventory functions -----
def get_products():
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()

def add_product(name, category, quantity, price):
    cursor.execute(
        "INSERT INTO products (name, category, quantity, price) VALUES (?,?,?,?)",
        (name, category, quantity, price))
    conn.commit()

def sell_product(product_id, quantity, user="cashier"):
    cursor.execute("SELECT name, quantity, price FROM products WHERE id=?", (product_id,))
    p = cursor.fetchone()
    if not p:
        return False, "Product not found"
    name, stock, price = p
    if quantity > stock:
        return False, f"Only {stock} available"

    new_stock = stock - quantity
    total = price * quantity
    cursor.execute("UPDATE products SET quantity=? WHERE id=?", (new_stock, product_id))
    cursor.execute(
        "INSERT INTO sales (product_id, quantity, total_price, date, sold_by) VALUES (?,?,?,?,?)",
        (product_id, quantity, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user))
    conn.commit()
    return True, f"Sold {quantity} x {name} = ₱{total:,.2f} (Remaining: {new_stock})"
