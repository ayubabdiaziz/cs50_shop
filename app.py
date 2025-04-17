import os
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import datetime
from helpers import login_required, admin_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
conn = sqlite3.connect('database/cs50_shop.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
db = conn.cursor()

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure upload folder for product images
UPLOAD_FOLDER = 'static/images/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    # Get featured products (limit to 4)
    db.execute("SELECT * FROM products WHERE featured = 1 LIMIT 4")
    featured_products = db.fetchall()
    
    # Get all categories
    db.execute("SELECT * FROM categories")
    categories = db.fetchall()
    
    return render_template("index.html", featured_products=featured_products, categories=categories)


@app.route("/products")
def products():
    category_id = request.args.get('category')
    search_query = request.args.get('q')
    sort_by = request.args.get('sort', 'name_asc')  # Default sort by name ascending
    page = request.args.get('page', 1, type=int)  # Current page, default to 1
    per_page = 9  # Number of products per page
    
    # Base query for counting total products
    count_query = "SELECT COUNT(*) FROM products p JOIN categories c ON p.category_id = c.id"
    count_params = []
    
    # Base query for fetching products
    query = "SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id"
    params = []
    
    # Add filters
    if category_id:
        query += " WHERE p.category_id = ?"
        count_query += " WHERE p.category_id = ?"
        params.append(category_id)
        count_params.append(category_id)
    
    if search_query:
        if 'WHERE' in query:
            query += " AND (p.name LIKE ? OR p.description LIKE ?)"
            count_query += " AND (p.name LIKE ? OR p.description LIKE ?)"
        else:
            query += " WHERE (p.name LIKE ? OR p.description LIKE ?)"
            count_query += " WHERE (p.name LIKE ? OR p.description LIKE ?)"
        search_param = f'%{search_query}%'
        params.extend([search_param, search_param])
        count_params.extend([search_param, search_param])
    
    # Add sorting
    if sort_by == 'price_low':
        query += " ORDER BY p.price ASC"
    elif sort_by == 'price_high':
        query += " ORDER BY p.price DESC"
    elif sort_by == 'name_desc':
        query += " ORDER BY p.name DESC"
    else:  # name_asc
        query += " ORDER BY p.name ASC"
    
    # Get total count of products
    db.execute(count_query, count_params)
    total_products = db.fetchone()[0]
    
    # Calculate pagination
    total_pages = (total_products + per_page - 1) // per_page  # Ceiling division
    offset = (page - 1) * per_page
    
    # Add pagination to query
    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    
    # Execute query with pagination
    db.execute(query, params)
    products = db.fetchall()
    
    # Get all categories for the filter
    db.execute("SELECT * FROM categories")
    categories = db.fetchall()
    
    # Helper function for pagination URLs
    def make_pagination_url(page_num):
        args = request.args.copy()
        args['page'] = page_num
        return url_for('products', **args)
    
    return render_template("products.html", 
                          products=products, 
                          categories=categories,
                          selected_category=category_id, 
                          search_query=search_query, 
                          sort_by=sort_by,
                          page=page,
                          pages=total_pages,
                          total_products=total_products,
                          pagination_url=make_pagination_url)


@app.route("/product/<int:product_id>")
def product(product_id):
    # Get product details
    db.execute("SELECT p.*, c.name as category_name FROM products p "
               "JOIN categories c ON p.category_id = c.id "
               "WHERE p.id = ?", [product_id])
    product = db.fetchone()
    
    if not product:
        flash("Product not found", "danger")
        return redirect("/products")
    
    # Get related products (same category, excluding current product)
    db.execute("SELECT * FROM products WHERE category_id = ? AND id != ? LIMIT 4", 
               [product['category_id'], product_id])
    related_products = db.fetchall()
    
    return render_template("product.html", product=product, related_products=related_products)


@app.route("/cart")
def cart():
    # Initialize cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []
    
    # Get cart items with product details
    cart_items = []
    total = 0
    
    for item in session['cart']:
        db.execute("SELECT * FROM products WHERE id = ?", [item['product_id']])
        product = db.fetchone()
        
        if product:
            item_total = product['price'] * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'total': item_total
            })
            total += item_total
    
    return render_template("cart.html", cart_items=cart_items, total=total, cart_total=total)


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    # Get product details from form
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))
    
    # Initialize cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if product already in cart
    found = False
    for item in session['cart']:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            found = True
            break
    
    # If not found, add new item
    if not found:
        session['cart'].append({
            'product_id': product_id,
            'quantity': quantity
        })
    
    # Mark session as modified
    session.modified = True
    
    flash("Product added to cart", "success")
    return redirect("/cart")


@app.route("/update_cart", methods=["POST"])
def update_cart():
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity"))
    
    # Update cart
    for item in session['cart']:
        if item['product_id'] == product_id:
            if quantity > 0:
                item['quantity'] = quantity
            else:
                session['cart'].remove(item)
            break
    
    # Mark session as modified
    session.modified = True
    
    return redirect("/cart")


@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    product_id = request.form.get("product_id")
    
    # Remove item from cart
    for item in session['cart']:
        if item['product_id'] == product_id:
            session['cart'].remove(item)
            break
    
    # Mark session as modified
    session.modified = True
    
    return redirect("/cart")


@app.route("/cart/remove/<item_id>", methods=["POST"])
def cart_remove_item(item_id):
    # Remove item from cart
    for item in session['cart']:
        if item['product_id'] == item_id:
            session['cart'].remove(item)
            break
    
    # Mark session as modified
    session.modified = True
    
    return jsonify({'success': True, 'message': 'Item removed from cart'})


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    if request.method == "POST":
        # Process checkout form
        name = request.form.get("name")
        email = request.form.get("email")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        zip_code = request.form.get("zip")
        payment_method = request.form.get("payment_method")
        
        # Validate form data
        if not name or not email or not address or not city or not state or not zip_code or not payment_method:
            flash("Please fill out all required fields", "danger")
            return redirect("/checkout")
        
        # Calculate order total
        total = 0
        for item in session['cart']:
            db.execute("SELECT price FROM products WHERE id = ?", [item['product_id']])
            product = db.fetchone()
            if product:
                total += product['price'] * item['quantity']
        
        # Create order in database
        db.execute("INSERT INTO orders (user_id, total, name, email, address, city, state, zip, payment_method, status, created_at) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   [session['user_id'], total, name, email, address, city, state, zip_code, payment_method, 'pending', datetime.datetime.now()])
        conn.commit()
        
        # Get the order ID
        db.execute("SELECT last_insert_rowid()")
        order_id = db.fetchone()[0]
        
        # Add order items
        for item in session['cart']:
            db.execute("SELECT price FROM products WHERE id = ?", [item['product_id']])
            product = db.fetchone()
            if product:
                db.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                           [order_id, item['product_id'], item['quantity'], product['price']])
        
        conn.commit()
        
        # Clear the cart
        session['cart'] = []
        session.modified = True
        
        flash("Order placed successfully!", "success")
        return redirect("/profile")
    
    # GET request - show checkout form
    # Calculate order total
    cart_items = []
    total = 0
    
    for item in session['cart']:
        db.execute("SELECT * FROM products WHERE id = ?", [item['product_id']])
        product = db.fetchone()
        
        if product:
            item_total = product['price'] * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'total': item_total
            })
            total += item_total
    
    # Get user info for pre-filling the form
    db.execute("SELECT * FROM users WHERE id = ?", [session['user_id']])
    user = db.fetchone()
    
    return render_template("checkout.html", cart_items=cart_items, total=total, user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username", "danger")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password", "danger")
            return render_template("login.html")

        # Query database for username
        db.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
        rows = db.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("Invalid username and/or password", "danger")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["is_admin"] = rows[0]["is_admin"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        
        # Ensure username was submitted
        if not username:
            flash("Must provide username", "danger")
            return render_template("register.html")
            
        # Ensure email was submitted
        elif not email:
            flash("Must provide email", "danger")
            return render_template("register.html")

        # Ensure password was submitted
        elif not password:
            flash("Must provide password", "danger")
            return render_template("register.html")
            
        # Ensure confirmation was submitted
        elif not confirmation:
            flash("Must confirm password", "danger")
            return render_template("register.html")
            
        # Ensure password and confirmation match
        elif password != confirmation:
            flash("Passwords do not match", "danger")
            return render_template("register.html")

        # Query database for username
        db.execute("SELECT * FROM users WHERE username = ?", [username])
        rows = db.fetchall()

        # Ensure username doesn't already exist
        if len(rows) > 0:
            flash("Username already exists", "danger")
            return render_template("register.html")
            
        # Query database for email
        db.execute("SELECT * FROM users WHERE email = ?", [email])
        rows = db.fetchall()
        
        # Ensure email doesn't already exist
        if len(rows) > 0:
            flash("Email already exists", "danger")
            return render_template("register.html")

        # Insert new user into database
        db.execute("INSERT INTO users (username, password, email, created_at) VALUES (?, ?, ?, ?)",
                   [username, generate_password_hash(password), email, datetime.datetime.now()])
        conn.commit()

        # Redirect user to login page
        flash("Registered successfully! Please log in.", "success")
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/profile")
@login_required
def profile():
    # Get user info
    db.execute("SELECT * FROM users WHERE id = ?", [session['user_id']])
    user = db.fetchone()
    
    # Convert created_at string to datetime object
    if user:
        user = dict(user)  # Convert to regular dict to make it mutable
        if 'created_at' in user and user['created_at'] and isinstance(user['created_at'], str):
            try:
                user['created_at'] = datetime.datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                # If conversion fails, use current time as fallback
                user['created_at'] = datetime.datetime.now()
    
    # Get user's orders
    db.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", [session['user_id']])
    orders = db.fetchall()
    
    # Convert order dates to datetime objects
    if orders:
        orders_list = []
        for order in orders:
            order_dict = dict(order)
            if 'created_at' in order_dict and order_dict['created_at'] and isinstance(order_dict['created_at'], str):
                try:
                    order_dict['created_at'] = datetime.datetime.strptime(order_dict['created_at'], '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    order_dict['created_at'] = datetime.datetime.now()
            orders_list.append(order_dict)
        orders = orders_list
    
    return render_template("profile.html", user=user, orders=orders, get_order_items=get_order_items)

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    # Get user info
    db.execute("SELECT * FROM users WHERE id = ?", [session['user_id']])
    user = db.fetchone()
    
    # Convert to regular dict to make it mutable
    if user:
        user = dict(user)
    
    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        email = request.form.get("email")
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        # Validate current password
        if not current_password:
            return render_template("edit_profile.html", user=user, error="Current password is required to save changes")
        
        # Check if current password is correct
        if not check_password_hash(user["password"], current_password):
            return render_template("edit_profile.html", user=user, error="Current password is incorrect")
        
        # Check if new passwords match
        if new_password and new_password != confirm_password:
            return render_template("edit_profile.html", user=user, error="New passwords do not match")
        
        # Update user information
        if new_password:
            # Update username, email, and password
            db.execute("UPDATE users SET username = ?, email = ?, password = ? WHERE id = ?",
                      [username, email, generate_password_hash(new_password), session["user_id"]])
        else:
            # Update username and email only
            db.execute("UPDATE users SET username = ?, email = ? WHERE id = ?",
                      [username, email, session["user_id"]])
        
        conn.commit()
        
        # Get updated user info
        db.execute("SELECT * FROM users WHERE id = ?", [session['user_id']])
        user = db.fetchone()
        if user:
            user = dict(user)
        
        return render_template("edit_profile.html", user=user, success="Profile updated successfully")
    
    # GET request
    return render_template("edit_profile.html", user=user)


@app.route("/admin")
@login_required
@admin_required
def admin_redirect():
    return redirect("/admin/dashboard")

@app.route("/admin/dashboard")
@login_required
@admin_required
def admin_dashboard():
    # Get counts for dashboard
    db.execute("SELECT COUNT(*) as count FROM products")
    product_count_row = db.fetchone()
    product_count = product_count_row[0] if product_count_row else 0
    
    db.execute("SELECT COUNT(*) as count FROM users")
    user_count_row = db.fetchone()
    user_count = user_count_row[0] if user_count_row else 0
    
    db.execute("SELECT COUNT(*) as count FROM orders")
    order_count_row = db.fetchone()
    order_count = order_count_row[0] if order_count_row else 0
    
    db.execute("SELECT SUM(total) as total FROM orders")
    total_sales_row = db.fetchone()
    total_sales = total_sales_row[0] if total_sales_row and total_sales_row[0] is not None else 0
    
    # Get recent orders
    db.execute("SELECT o.id, o.total, o.status, o.created_at, u.username FROM orders o JOIN users u ON o.user_id = u.id ORDER BY o.created_at DESC LIMIT 5")
    recent_orders = [dict(row) for row in db.fetchall()]
    
    # Convert created_at string to datetime object for proper formatting
    for order in recent_orders:
        if order['created_at'] and isinstance(order['created_at'], str):
            try:
                # Parse the date string into a datetime object
                order['created_at'] = datetime.datetime.strptime(order['created_at'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                # If parsing fails, set a default date
                order['created_at'] = datetime.datetime.now()
    
    return render_template("admin/dashboard.html", product_count=product_count, user_count=user_count,
                           order_count=order_count, total_sales=total_sales, recent_orders=recent_orders)


@app.route("/admin/products", methods=["GET", "POST"])
@login_required
@admin_required
def admin_products():
    if request.method == "POST":
        # Handle product form submission (add/edit)
        product_id = request.form.get("product_id")
        name = request.form.get("name")
        description = request.form.get("description")
        price = float(request.form.get("price"))
        stock = int(request.form.get("stock"))
        category_id = request.form.get("category_id")
        featured = 1 if request.form.get("featured") else 0
        
        # Handle file upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to avoid duplicates
                filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = f"/static/images/products/{filename}"
        
        if product_id:  # Edit existing product
            if image_url:  # If new image uploaded
                db.execute("UPDATE products SET name = ?, description = ?, price = ?, stock = ?, "
                           "category_id = ?, featured = ?, image_url = ? WHERE id = ?",
                           [name, description, price, stock, category_id, featured, image_url, product_id])
            else:  # Keep existing image
                db.execute("UPDATE products SET name = ?, description = ?, price = ?, stock = ?, "
                           "category_id = ?, featured = ? WHERE id = ?",
                           [name, description, price, stock, category_id, featured, product_id])
            
            flash("Product updated successfully", "success")
        else:  # Add new product
            if not image_url:  # Use default image if none uploaded
                image_url = "/static/images/products/default.jpg"
                
            db.execute("INSERT INTO products (name, description, price, stock, category_id, featured, image_url) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?)",
                       [name, description, price, stock, category_id, featured, image_url])
            
            flash("Product added successfully", "success")
        
        conn.commit()
        return redirect("/admin/products")
    
    # GET request - show products list
    db.execute("SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id ORDER BY p.id DESC")
    products = db.fetchall()
    
    # Get categories for the form
    db.execute("SELECT * FROM categories")
    categories = db.fetchall()
    
    return render_template("admin/products.html", products=products, categories=categories)


@app.route("/admin/products/delete", methods=["POST"])
@login_required
@admin_required
def admin_products_delete():
    product_id = request.form.get("product_id")
    
    if not product_id:
        flash("Product ID is required", "danger")
        return redirect("/admin/products")
    
    # Check if product exists
    db.execute("SELECT * FROM products WHERE id = ?", [product_id])
    product = db.fetchone()
    
    if not product:
        flash("Product not found", "danger")
        return redirect("/admin/products")
    
    # Delete product
    db.execute("DELETE FROM products WHERE id = ?", [product_id])
    conn.commit()
    
    flash("Product deleted successfully", "success")
    return redirect("/admin/products")


@app.route("/api/cart", methods=["GET", "POST", "DELETE"])
def api_cart():
    # Initialize cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []
    
    if request.method == "GET":
        # Return cart items with product details
        cart_items = []
        total = 0
        
        for item in session['cart']:
            db.execute("SELECT * FROM products WHERE id = ?", [item['product_id']])
            product = db.fetchone()
            
            if product:
                item_total = product['price'] * item['quantity']
                cart_items.append({
                    'product_id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'image_url': product['image_url'],
                    'quantity': item['quantity'],
                    'total': item_total
                })
                total += item_total
        
        return jsonify({
            'items': cart_items,
            'total': total,
            'count': len(cart_items)
        })
    
    elif request.method == "POST":
        # Add item to cart
        data = request.json
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        
        # Check if product exists
        db.execute("SELECT * FROM products WHERE id = ?", [product_id])
        product = db.fetchone()
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if product already in cart
        found = False
        for item in session['cart']:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                found = True
                break
        
        # If not found, add new item
        if not found:
            session['cart'].append({
                'product_id': product_id,
                'quantity': quantity
            })
        
        # Mark session as modified
        session.modified = True
        
        return jsonify({'success': True, 'message': 'Product added to cart'})
    
    elif request.method == "DELETE":
        # Remove item from cart
        data = request.json
        product_id = str(data.get('product_id'))
        
        for item in session['cart']:
            if item['product_id'] == product_id:
                session['cart'].remove(item)
                break
        
        # Mark session as modified
        session.modified = True
        
        return jsonify({'success': True, 'message': 'Product removed from cart'})


# Helper function to get order items
def get_order_items(order_id):
    # Create a new connection and cursor for this query to avoid interfering with other operations
    order_conn = sqlite3.connect('database/cs50_shop.db')
    order_conn.row_factory = sqlite3.Row
    order_cursor = order_conn.cursor()
    order_cursor.execute("""SELECT oi.*, p.name as product_name, p.image_url 
               FROM order_items oi 
               JOIN products p ON oi.product_id = p.id 
               WHERE oi.order_id = ?""", [order_id])
    items = order_cursor.fetchall()
    order_cursor.close()
    order_conn.close()
    return items


# Add orders route that redirects to profile
@app.route("/orders")
@login_required
def orders():
    # Redirect to profile page which already shows orders
    return redirect("/profile")


@app.route("/admin/orders")
@login_required
@admin_required
def admin_orders():
    # Get filter parameters
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Base query
    query = """SELECT o.*, u.username 
             FROM orders o 
             JOIN users u ON o.user_id = u.id"""
    params = []
    
    # Add filters
    if status:
        query += " WHERE o.status = ?"
        params.append(status)
    
    if date_from:
        if 'WHERE' in query:
            query += " AND"
        else:
            query += " WHERE"
        query += " o.created_at >= ?"
        params.append(date_from)
    
    if date_to:
        if 'WHERE' in query:
            query += " AND"
        else:
            query += " WHERE"
        query += " o.created_at <= ?"
        params.append(date_to + " 23:59:59")  # Include the entire day
    
    # Add sorting
    query += " ORDER BY o.created_at DESC"
    
    db.execute(query, params)
    orders = db.fetchall()
    
    # Convert string dates to datetime objects
    from datetime import datetime
    # Convert sqlite3.Row objects to dictionaries
    orders_list = [dict(order) for order in orders]
    for order in orders_list:
        if order['created_at'] and isinstance(order['created_at'], str):
            try:
                order['created_at'] = datetime.strptime(order['created_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Handle timestamps with microseconds
                order['created_at'] = datetime.strptime(order['created_at'].split('.')[0], '%Y-%m-%d %H:%M:%S')
    
    return render_template("admin/orders.html", orders=orders_list, status=status, date_from=date_from, date_to=date_to)


@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    # Get all users
    db.execute("""SELECT id, username, email, is_admin, created_at,
               (SELECT COUNT(*) FROM orders WHERE user_id = users.id) as order_count
               FROM users ORDER BY username""")
    users = db.fetchall()
    
    # Convert string dates to datetime objects
    from datetime import datetime
    # Convert sqlite3.Row objects to dictionaries
    users_list = [dict(user) for user in users]
    for user in users_list:
        if user['created_at'] and isinstance(user['created_at'], str):
            try:
                user['created_at'] = datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Handle timestamps with microseconds
                user['created_at'] = datetime.strptime(user['created_at'].split('.')[0], '%Y-%m-%d %H:%M:%S')
    
    return render_template("admin/users.html", users=users_list)


@app.route("/admin/orders/<int:order_id>")
@login_required
@admin_required
def admin_order_detail(order_id):
    # Get order details
    db.execute("""SELECT o.*, u.username 
               FROM orders o 
               JOIN users u ON o.user_id = u.id 
               WHERE o.id = ?""", [order_id])
    order = db.fetchone()
    
    if not order:
        flash("Order not found", "danger")
        return redirect("/admin/orders")
    
    # Get order items
    order_items = get_order_items(order_id)
    
    # Get order history
    db.execute("""SELECT oh.*, u.username as admin_username 
               FROM order_history oh 
               JOIN users u ON oh.admin_id = u.id 
               WHERE oh.order_id = ? 
               ORDER BY oh.created_at DESC""", [order_id])
    order_history = db.fetchall()
    
    # Convert string dates to datetime objects
    from datetime import datetime
    # Convert sqlite3.Row objects to dictionaries
    order = dict(order)
    if order['created_at'] and isinstance(order['created_at'], str):
        try:
            order['created_at'] = datetime.strptime(order['created_at'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            # Handle timestamps with microseconds
            order['created_at'] = datetime.strptime(order['created_at'].split('.')[0], '%Y-%m-%d %H:%M:%S')
    
    order_history_list = [dict(history) for history in order_history]
    for history in order_history_list:
        if history['created_at'] and isinstance(history['created_at'], str):
            try:
                history['created_at'] = datetime.strptime(history['created_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Handle timestamps with microseconds
                history['created_at'] = datetime.strptime(history['created_at'].split('.')[0], '%Y-%m-%d %H:%M:%S')
    
    return render_template("admin/order_detail.html", order=order, order_items=order_items, order_history=order_history_list)


@app.route("/admin/orders/update_status", methods=["POST"])
@login_required
@admin_required
def update_order_status():
    order_id = request.form.get("order_id")
    status = request.form.get("status")
    notes = request.form.get("notes")
    
    if not order_id or not status:
        flash("Missing required information", "danger")
        return redirect("/admin/orders")
    
    # Update order status
    db.execute("UPDATE orders SET status = ? WHERE id = ?", [status, order_id])
    
    # Add to order history
    db.execute("""INSERT INTO order_history (order_id, status, notes, admin_id, created_at) 
               VALUES (?, ?, ?, ?, ?)""", 
               [order_id, status, notes, session['user_id'], datetime.datetime.now()])
    
    conn.commit()
    
    flash("Order status updated successfully", "success")
    return redirect(f"/admin/orders/{order_id}")


@app.route("/product/<int:product_id>/review", methods=["POST"])
@login_required
def add_review(product_id):
    rating = request.form.get("rating")
    comment = request.form.get("comment")
    
    if not rating:
        flash("Missing required information", "danger")
        return redirect(f"/product/{product_id}")
    
    # Check if user has already reviewed this product
    db.execute("SELECT * FROM reviews WHERE product_id = ? AND user_id = ?", [product_id, session['user_id']])
    existing_review = db.fetchone()
    
    if existing_review:
        # Update existing review
        db.execute("UPDATE reviews SET rating = ?, comment = ?, created_at = ? WHERE id = ?", 
                   [rating, comment, datetime.datetime.now(), existing_review['id']])
        flash("Your review has been updated", "success")
    else:
        # Add new review
        db.execute("INSERT INTO reviews (product_id, user_id, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)", 
                   [product_id, session['user_id'], rating, comment, datetime.datetime.now()])
        flash("Your review has been added", "success")
    
    conn.commit()
    return redirect(f"/product/{product_id}")


@app.route("/api/reviews/<int:product_id>")
def api_reviews(product_id):
    # Get reviews for a product
    db.execute("""SELECT r.*, u.username 
               FROM reviews r 
               JOIN users u ON r.user_id = u.id 
               WHERE r.product_id = ? 
               ORDER BY r.created_at DESC""", [product_id])
    reviews = db.fetchall()
    
    # Convert to list of dicts for JSON serialization
    reviews_list = []
    for review in reviews:
        reviews_list.append({
            'id': review['id'],
            'username': review['username'],
            'rating': review['rating'],
            'comment': review['comment'],
            'created_at': review['created_at']
        })
    
    # Calculate average rating
    if reviews:
        avg_rating = sum(review['rating'] for review in reviews) / len(reviews)
    else:
        avg_rating = 0
    
    return jsonify({
        'reviews': reviews_list,
        'count': len(reviews_list),
        'average_rating': round(avg_rating, 1)
    })


@app.route("/search")
def search():
    # Get search query from URL parameters
    search_query = request.args.get('q', '')
    
    if not search_query:
        return redirect("/products")
    
    # Redirect to products page with search query
    return redirect(url_for('products', q=search_query))


if __name__ == "__main__":
    app.run(debug=True)