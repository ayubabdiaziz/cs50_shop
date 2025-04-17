# CS50 Shop - E-commerce Application

![CS50 Shop](https://cs50.harvard.edu/x/2023/project/cs50.png)

## Overview

CS50 Shop is a full-featured e-commerce web application built as a final project for Harvard's CS50X course. The application provides a complete online shopping experience with product browsing, user authentication, shopping cart functionality, and checkout process. It also includes an admin dashboard for managing products, categories, users, and orders.

## Features

### User Features
- **User Authentication**
  - Register new account
  - Login/logout functionality
  - Password hashing for security
  - Profile management
- **Product Browsing**
  - Browse all products
  - Filter by category
  - Search functionality
  - Sort by price (low to high, high to low) and name
  - Pagination for product listings
- **Product Details**
  - Detailed product information
  - Product images
  - Related products suggestions
- **Shopping Cart**
  - Add products to cart
  - Update product quantities
  - Remove products from cart
  - Persistent cart (stays in session)
- **Checkout Process**
  - Address information collection
  - Order summary
  - Order confirmation
- **Responsive Design**
  - Mobile-friendly interface
  - Desktop optimized views

### Admin Features
- **Product Management**
  - Add new products
  - Edit existing products
  - Delete products
  - Upload product images
- **Category Management**
  - Create and manage product categories
- **Order Management**
  - View all orders
  - View order details
  - Update order status
- **User Management**
  - View registered users
  - Edit user information

## Technologies Used

### Backend
- **Flask**: Python web framework
- **SQLite**: Database for storing product, user, and order information
- **Flask-Session**: For managing user sessions
- **Werkzeug**: For password hashing and file uploads

### Frontend
- **HTML/CSS/JavaScript**: Core frontend technologies
- **Bootstrap 5**: CSS framework for responsive design
- **Bootstrap Icons**: Icon library
- **jQuery**: JavaScript library for DOM manipulation

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cs50_shop.git
   cd cs50_shop
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python database/models.py
   ```

4. **Create an admin user** (optional)
   ```bash
   python create_admin.py
   ```

5. **Run the application**
   ```bash
   flask run
   ```

6. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:5000`

## Project Structure

```
cs50_shop/
├── app.py                 # Main application file with routes
├── create_admin.py        # Script to create admin user
├── helpers.py             # Helper functions
├── requirements.txt       # Python dependencies
├── database/
│   ├── cs50_shop.db       # SQLite database
│   ├── models.py          # Database models
│   └── reviews.py         # Review functionality
├── static/
│   ├── css/               # CSS stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Image assets
│       └── products/      # Product images
└── templates/
    ├── admin/             # Admin templates
    │   ├── dashboard.html
    │   ├── products.html
    │   ├── orders.html
    │   ├── order_detail.html
    │   └── users.html
    ├── layout.html        # Base template
    ├── index.html         # Homepage
    ├── products.html      # Product listing
    ├── product.html       # Product detail
    ├── cart.html          # Shopping cart
    ├── checkout.html      # Checkout process
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── profile.html       # User profile
    └── edit_profile.html  # Edit profile
```

## API Endpoints

### Product Endpoints
- `GET /products` - Get all products with optional filtering and sorting
- `GET /product/<product_id>` - Get details for a specific product

### Cart Endpoints
- `GET /cart` - View shopping cart
- `POST /add_to_cart` - Add a product to cart
- `POST /update_cart` - Update cart item quantity
- `POST /remove_from_cart` - Remove item from cart

### User Endpoints
- `GET/POST /register` - Register new user
- `GET/POST /login` - User login
- `GET /logout` - User logout
- `GET/POST /profile` - View/edit user profile

### Admin Endpoints
- `GET /admin/dashboard` - Admin dashboard
- `GET/POST /admin/products` - Manage products
- `GET/POST /admin/categories` - Manage categories
- `GET /admin/orders` - View orders
- `GET /admin/order/<order_id>` - View order details
- `GET /admin/users` - View users

## Database Schema

### Users Table
- `id` - Primary key
- `username` - User's username
- `password` - Hashed password
- `email` - User's email
- `is_admin` - Admin status flag
- `created_at` - Account creation timestamp

### Products Table
- `id` - Primary key
- `name` - Product name
- `description` - Product description
- `price` - Product price
- `image` - Product image filename
- `category_id` - Foreign key to categories
- `stock` - Available stock
- `featured` - Featured product flag

### Categories Table
- `id` - Primary key
- `name` - Category name

### Orders Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `status` - Order status
- `created_at` - Order timestamp
- `total` - Order total
- `address` - Shipping address

### Order_Items Table
- `id` - Primary key
- `order_id` - Foreign key to orders
- `product_id` - Foreign key to products
- `quantity` - Item quantity
- `price` - Item price at time of order

## User Roles

### Regular User
- Can browse products
- Can add products to cart
- Can checkout and place orders
- Can view and edit their profile
- Can view their order history

### Admin User
- Has all regular user privileges
- Can access admin dashboard
- Can manage products and categories
- Can view all orders and update order status
- Can view all registered users

## Default Admin Account

- **Username**: admin
- **Password**: admin123

## Development

### Adding New Features
1. Fork the repository
2. Create a feature branch
3. Implement your feature
4. Submit a pull request

### Running Tests
Currently, the application does not have automated tests. This is an area for future improvement.

## Deployment

The application can be deployed to various platforms:

### Heroku Deployment
1. Create a Heroku account and install Heroku CLI
2. Create a new Heroku app
3. Add a `Procfile` with: `web: gunicorn app:app`
4. Add `gunicorn` to requirements.txt
5. Deploy using Git: `git push heroku main`

### Other Platforms
The application can also be deployed on platforms like PythonAnywhere, AWS, or DigitalOcean with appropriate configuration.

## Future Enhancements

- User reviews and ratings for products
- Wishlist functionality
- Payment gateway integration
- Email notifications for orders
- Advanced search filters
- Product recommendations based on purchase history
- Discount codes and promotions
- Inventory management system

## CS50X Final Project Requirements

This project fulfills the CS50X final project requirements by:

1. Being more complex than previous course problem sets
2. Implementing a web application with both frontend and backend components
3. Using a database to store persistent data
4. Providing user authentication and different user roles
5. Implementing CRUD operations for products and orders

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is part of the CS50X course and is intended for educational purposes.

## Acknowledgements

- Harvard CS50X course staff and instructors
- Bootstrap team for the frontend framework
- Flask team for the web framework
- All open-source contributors whose libraries made this project possible