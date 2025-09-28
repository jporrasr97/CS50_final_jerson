# Tienda E-commerce

## Overview

Tienda is a comprehensive e-commerce web application built with Flask, designed to provide a seamless online shopping experience. The application allows users to browse products, manage a shopping cart, place orders, and receive email confirmations. It also includes an administrative panel for managing products and categories. This project serves as a full-featured example of a modern web application using Python and Flask framework, incorporating user authentication, database management, and email functionality.

The name "Tienda" is Spanish for "store," reflecting its purpose as an online retail platform. The application is structured using Flask blueprints for modular routing, SQLAlchemy for database operations, and includes security features like rate limiting and content security policies.

## Features

### User Features
- **User Registration and Authentication**: Secure user registration with password hashing, login/logout functionality, and session management.
- **Product Browsing**: View products organized by categories, with search functionality to find specific items.
- **Product Details**: Detailed view of individual products including descriptions, prices, and images.
- **Shopping Cart**: Session-based cart allowing users to add, remove, and modify item quantities.
- **Checkout Process**: Complete order placement with shipping information validation and email notifications.
- **Order History**: View past orders for logged-in users.
- **Guest Checkout**: Allow non-registered users to place orders by providing email.

### Administrative Features
- **Admin Panel**: Restricted access for administrators to manage the store.
- **Product Management**: Add, edit, and delete products with details like name, description, price, and category.
- **Category Management**: Create and manage product categories for better organization.
- **Dashboard**: Overview of all products and categories for easy management.

### Security and Performance
- **Rate Limiting**: Prevents brute-force attacks on login with Flask-Limiter.
- **Content Security Policy**: Implemented using Flask-Talisman for enhanced security.
- **Password Security**: Uses Werkzeug for secure password hashing.
- **Email Notifications**: Automated email sending for order confirmations using Flask-Mail.

## Architecture

### Application Structure
The application follows a modular architecture using Flask blueprints:

- **app.py**: Main application file that initializes the Flask app, configures extensions, and registers blueprints.
- **models/models.py**: Database models defined using SQLAlchemy, including Usuario (User), Categoria (Category), Producto (Product), Pedido (Order), and OrderItem.
- **routes/**: Contains blueprint modules for different functionalities:
  - **auth.py**: Handles user registration, login, and logout.
  - **productos.py**: Manages product listing and detail views.
  - **carrito.py**: Implements shopping cart and checkout functionality.
  - **admin.py**: Provides administrative routes for managing products and categories.
- **templates/**: Jinja2 templates for rendering HTML pages.
- **static/**: CSS, JavaScript, and image files for frontend styling and interactivity.
- **extensions.py**: Initializes Flask extensions like Mail, Limiter, and Talisman.

### Database Design
The application uses SQLite as the database backend with the following schema:

- **Usuario**: Stores user information including name, email, hashed password, and role (admin/client).
- **Categoria**: Product categories for organization.
- **Producto**: Product details with foreign key to Categoria.
- **Pedido**: Order records with user association and order status.
- **OrderItem**: Individual items within an order, linking to products and quantities.

### Session Management
Shopping cart functionality is implemented using Flask sessions, storing cart items in the user's session data. This allows for a stateless cart that persists across page visits without requiring database storage for temporary cart data.

### Email System
Order confirmations are sent via email using Flask-Mail. The system constructs both plain text and HTML email bodies containing order details, shipping information, and itemized product lists.

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Steps
1. Clone the repository:
   ```
   git clone <repository-url>
   cd tienda
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a .env file):
   ```
   SECRET_KEY=your-secret-key-here
   DATABASE_URI=sqlite:///instance/tienda.db
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

## Conda environment (alternative to venv)

If you prefer Conda over Python venv, use the provided environment.yml.

1) Create and activate the Conda environment:
   ```
   conda env create -f environment.yml
   conda activate tienda
   ```
   - To update later:
     ```
     conda env update -f environment.yml --prune
     ```
   - To remove:
     ```
     conda remove -n tienda --all
     ```

2) Prepare environment variables:
   ```
   copy .env.example .env   # Windows
   # or:
   cp .env.example .env     # macOS/Linux
   ```
   Edit .env with your secrets (Gmail app password, etc.)

3) Initialize the database:
   ```
   python init_db.py
   ```

4) Run the app:
   ```
   python app.py
   ```
   Then open http://localhost:5000

Note: environment.yml pins Python 3.11 and installs all pip dependencies (Flask, SQLAlchemy, Flask-Mail, etc.) inside the Conda env.

## Setup

### Database Initialization
1. Run the database initialization script to create tables and populate with sample data:
   ```
   python init_db.py
   ```

   This will create the database schema and add sample categories (Herramientas, Hogar, Jardín) and products.

2. The first user to register will automatically be assigned admin privileges.

### Running the Application
Start the development server:
```
python app.py
```

The application will be available at `http://localhost:5000`.

For production deployment, use Gunicorn:
```
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```

## Usage

### For Customers

1. **Registration**: Visit the registration page to create an account. The first user becomes an admin.
2. **Browsing Products**: Navigate to the products page to view all items. Use the search bar or category filters to find specific products.
3. **Product Details**: Click on any product to view detailed information.
4. **Adding to Cart**: Use the "Add to Cart" button on product pages or the "Buy Now" option to add items directly to the cart.
5. **Managing Cart**: View the cart, adjust quantities, or remove items as needed.
6. **Checkout**: Proceed to checkout, fill in shipping details, and confirm the order. An email confirmation will be sent.
7. **Order History**: Logged-in users can view their past orders.

### For Administrators

1. **Access Admin Panel**: Log in with an admin account and navigate to `/admin`.
2. **Manage Products**: Add new products with details, edit existing ones, or delete products.
3. **Manage Categories**: Create new categories or modify existing ones.
4. **Dashboard Overview**: View all products and categories from the admin dashboard.

### Email Configuration
To enable email notifications:
1. Use a Gmail account with app passwords for SMTP.
2. Configure the environment variables as shown in the setup section.
3. Orders will be emailed to the configured recipient (default: jersonprs31@gmail.com).

## Technologies Used

- **Flask**: Web framework for Python
- **SQLAlchemy**: ORM for database operations
- **Flask-Login**: User session management
- **Flask-Mail**: Email functionality
- **Flask-Limiter**: Rate limiting for security
- **Flask-Talisman**: Security headers and CSP
- **Werkzeug**: Password hashing utilities
- **Jinja2**: Template engine
- **SQLite**: Database backend
- **Gunicorn**: WSGI server for production

## Security Considerations

- Passwords are hashed using Werkzeug's security functions.
- Login attempts are rate-limited to prevent brute-force attacks.
- Content Security Policy is enforced to mitigate XSS attacks.
- User input is validated on both client and server sides.
- Admin routes are protected with role-based access control.

## Future Enhancements

- Payment gateway integration (Stripe, PayPal)
- User profile management
- Product reviews and ratings
- Inventory management
- Order status tracking
- Mobile-responsive design improvements
- API endpoints for mobile app integration

## License

This project is Opensource

