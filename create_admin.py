import sqlite3
from werkzeug.security import generate_password_hash
import os

# Connect to the database
conn = sqlite3.connect('database/cs50_shop.db')
db = conn.cursor()

# Check if username already exists
db.execute("SELECT * FROM users WHERE username = ?", ["adminUser"])
user = db.fetchone()

if user:
    print("Admin user 'adminUser' already exists!")
else:
    # Create the admin user with a secure password
    password = "admin123"
    hashed_password = generate_password_hash(password)
    
    # Insert the new admin user
    db.execute("INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)",
              ["adminUser", hashed_password, "adminuser@cs50shop.com", 1])
    
    # Commit the changes
    conn.commit()
    print("Admin user 'adminUser' created successfully!")
    print("Username: adminUser")
    print("Password: admin123")

# Close the connection
conn.close()