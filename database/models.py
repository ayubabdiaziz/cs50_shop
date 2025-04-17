import sqlite3
import os

# Ensure the database directory exists
os.makedirs('database', exist_ok=True)

# Connect to SQLite database
conn = sqlite3.connect('database/cs50_shop.db')
db = conn.cursor()

# Create users table
db.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    is_admin INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create categories table
db.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
)
''')

# Create products table
db.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock INTEGER DEFAULT 0,
    image_url TEXT,
    category_id INTEGER,
    featured INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories (id)
)
''')

# Create orders table
db.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total REAL NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Create order_items table
db.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
)
''')

# Insert sample categories
db.execute("INSERT OR IGNORE INTO categories (id, name, description) VALUES (1, 'CS50 Merchandise', 'Official CS50 branded merchandise')")
db.execute("INSERT OR IGNORE INTO categories (id, name, description) VALUES (2, 'Programming Books', 'Books to help you learn programming')")
db.execute("INSERT OR IGNORE INTO categories (id, name, description) VALUES (3, 'Coding Accessories', 'Accessories to enhance your coding experience')")

# Insert sample products
db.execute('''
INSERT OR IGNORE INTO products (id, name, description, price, stock, image_url, category_id, featured) 
VALUES (1, 'CS50 T-Shirt', 'Official CS50 T-Shirt with the CS50 logo', 19.99, 100, '/static/images/products/cs50_tshirt.jpg', 1, 1)
''')

db.execute('''
INSERT OR IGNORE INTO products (id, name, description, price, stock, image_url, category_id, featured) 
VALUES (2, 'CS50 Hoodie', 'Stay warm while coding with this comfortable CS50 hoodie', 39.99, 50, '/static/images/products/cs50_hoodie.jpg', 1, 1)
''')

db.execute('''
INSERT OR IGNORE INTO products (id, name, description, price, stock, image_url, category_id, featured) 
VALUES (3, 'Introduction to Algorithms', 'Classic textbook on algorithms by Cormen, Leiserson, Rivest, and Stein', 59.99, 30, '/static/images/products/algorithms_book.jpg', 2, 1)
''')

db.execute('''
INSERT OR IGNORE INTO products (id, name, description, price, stock, image_url, category_id, featured) 
VALUES (4, 'Mechanical Keyboard', 'Enhance your coding experience with this mechanical keyboard', 89.99, 20, '/static/images/products/keyboard.jpg', 3, 1)
''')

db.execute('''
INSERT OR IGNORE INTO products (id, name, description, price, stock, image_url, category_id, featured) 
VALUES (5, 'CS50 Mug', 'Start your day with coffee in this CS50 mug', 14.99, 75, '/static/images/products/cs50_mug.jpg', 1, 0)
''')

db.execute('''
INSERT OR IGNORE INTO products (id, name, description, price, stock, image_url, category_id, featured) 
VALUES (6, 'Python Crash Course', 'A hands-on, project-based introduction to programming', 29.99, 40, '/static/images/products/python_book.jpg', 2, 0)
''')

db.execute('''
INSERT OR IGNORE INTO products (id, name, description, price, stock, image_url, category_id, featured) 
VALUES (7, 'Wireless Mouse', 'Comfortable wireless mouse for programming', 24.99, 35, '/static/images/products/mouse.jpg', 3, 0)
''')

db.execute('''
INSERT OR IGNORE INTO products (id, name, description, price, stock, image_url, category_id, featured) 
VALUES (8, 'CS50 Stickers Pack', 'Decorate your laptop with CS50 stickers', 4.99, 200, '/static/images/products/cs50_stickers.jpg', 1, 0)
''')

# Create an admin user (password: admin123)
db.execute("INSERT OR IGNORE INTO users (id, username, password, email, is_admin) VALUES (1, 'admin', 'pbkdf2:sha256:150000$KJrjy4Ul$3b5fef5a85631a9a4d577fbd42a1098ba2cb9895df3f6b9152a5f7a11c48b386', 'admin@cs50shop.com', 1)")

# Commit changes and close connection
conn.commit()
conn.close()

print("Database initialized with sample data.")