# PhoneShop - Django E-commerce Website

A comprehensive e-commerce platform built with Django for selling mobile phones and accessories. The application features user authentication, shopping cart, order management, admin dashboard, and inventory tracking.

## Features

### User Features
- User registration and authentication with email verification
- Password reset via OTP email
- Product browsing with filtering and sorting
- Shopping cart functionality
- Secure checkout process
- Order tracking and history
- Responsive design for mobile and desktop

### Product Management
- Mobile phones with variants (capacity, color, price)
- Accessories with multiple color options
- Product categories and brand filtering
- Search functionality
- Product specifications in JSON format

### Admin Features
- Admin dashboard with sales analytics
- Product and accessory management (CRUD operations)
- Order management and status tracking
- Inventory management
- User management
- Sales reports and statistics

### Technical Features
- Custom user model with email authentication
- Session-based shopping cart
- Email notifications for password reset
- MySQL database with proper indexing
- Bootstrap-based responsive UI
- Vietnamese language support

## Technology Stack

- **Backend**: Django 4.2
- **Database**: MySQL 8.0+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Email**: SMTP (Gmail)
- **Deployment**: Ready for production deployment

## Installation

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PhoneShop
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv_new
   venv_new\Scripts\activate  # On Windows
   # or
   source venv_new/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database setup**
   - Create MySQL database named `webbandienthoai`
   - Update database credentials in `webbandienthoai/settings.py`:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'webbandienthoai',
             'USER': 'your_mysql_username',
             'PASSWORD': 'your_mysql_password',
             'HOST': '127.0.0.1',
             'PORT': '3306',
         }
     }
     ```

5. **Email configuration**
   - Set up Gmail app password or use another SMTP provider
   - Update email settings in `webbandienthoai/settings.py`:
     ```python
     EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")  # Set environment variable
     ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Load sample data (optional)**
   ```bash
   python manage.py loaddata sample_data.json  # If available
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    - Main site: http://127.0.0.1:8000/
    - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### For Customers
1. Register an account or login
2. Browse products and accessories
3. Add items to cart
4. Proceed to checkout
5. Track order status

### For Administrators
1. Login with admin credentials
2. Access admin dashboard at `/admin/`
3. Manage products, orders, and inventory
4. View sales analytics

## Screenshots

Here are some example screenshots of the PhoneShop application:

### Homepage
<img width="908" height="865" alt="image" src="https://github.com/user-attachments/assets/385d0f5c-69b1-44a9-b739-e65639946443" />

### Product Listing
<img width="877" height="870" alt="image" src="https://github.com/user-attachments/assets/05909788-6fa6-4218-9924-80f0a56054cc" />

### Product Detail
<img width="873" height="868" alt="image" src="https://github.com/user-attachments/assets/8d6d78ff-ae8f-4cea-ac3c-782963fd25f0" />

### Shopping Cart
<img width="864" height="332" alt="image" src="https://github.com/user-attachments/assets/845bc671-129e-4e76-9b51-b244f98f2665" />

### Checkout Process
<img width="1906" height="604" alt="image" src="https://github.com/user-attachments/assets/e6b49f86-40fc-4ec3-82d2-a44691206d71" />

### Admin Dashboard
<img width="1919" height="864" alt="image" src="https://github.com/user-attachments/assets/e01d658b-7652-4965-a932-dd8be2bcdb78" />

## Project Structure

```
PhoneShop/
├── app/                          # Main Django app
│   ├── migrations/              # Database migrations
│   ├── templates/               # HTML templates
│   │   ├── admin/              # Admin templates
│   │   ├── cart/               # Cart templates
│   │   ├── checkout/           # Checkout templates
│   │   ├── products/           # Product templates
│   │   └── registration/       # Auth templates
│   ├── static/                 # Static files (CSS, JS, images)
│   ├── templatetags/           # Custom template tags
│   ├── models.py               # Database models
│   ├── views.py                # View functions
│   ├── forms.py                # Django forms
│   ├── urls.py                 # URL patterns
│   └── context_processors.py   # Template context processors
├── webbandienthoai/            # Django project settings
│   ├── settings.py            # Main settings
│   ├── urls.py                # Root URL configuration
│   └── wsgi.py                # WSGI configuration
├── static/                     # Global static files
├── db/                         # Database files
├── venv_new/                   # Virtual environment
├── manage.py                   # Django management script
└── README.md                   # This file
```

## Database Models

### Core Models
- **CustomUser**: Extended user model with email authentication
- **Category**: Product categories
- **Product**: Mobile phones with specifications
- **Accessory**: Phone accessories
- **ProductVariant/AccessoryVariant**: Product variations with pricing
- **Order/OrderItem**: Order management
- **Inventory**: Stock tracking
- **Banner**: Homepage banners

## API Endpoints

### Public Endpoints
- `/` - Homepage
- `/products/` - Product listing
- `/accessories/` - Accessory listing
- `/product/<slug>/` - Product detail
- `/accessory/<slug>/` - Accessory detail
- `/cart/` - Shopping cart
- `/checkout/` - Checkout process

### User Endpoints
- `/signup/` - User registration
- `/login/` - User login
- `/logout/` - User logout
- `/forgot-password/` - Password reset
- `/orders/` - Order history

### Admin Endpoints
- `/admin/dashboard/` - Admin dashboard
- `/admin/products/` - Product management
- `/admin/accessories/` - Accessory management
- `/admin/sales/` - Sales analytics
- `/admin/inventory/` - Inventory management

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Django framework
- Bootstrap CSS framework
- MySQL database
- Python community
