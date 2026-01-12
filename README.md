# 🎯 Face Recognition Attendance System

A modern, secure, and efficient Django-based attendance management system with facial recognition capabilities.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Django](https://img.shields.io/badge/Django-4.2%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Features
- ✅ **Face Recognition** - Advanced facial recognition for touchless attendance
- ✅ **Real-time Tracking** - Track employee check-in/check-out with timestamps
- ✅ **Leave Management** - Complete leave request and approval workflow
- ✅ **Department Management** - Organize employees by departments
- ✅ **Role-based Access** - Admin and employee role separation
- ✅ **Attendance Reports** - Generate detailed attendance reports
- ✅ **Analytics Dashboard** - Visual insights and statistics

### Additional Features
- 📊 **Interactive Charts** - Visual representation of attendance data
- 📧 **Email Notifications** - Automated notifications for leave approvals
- 📱 **Responsive Design** - Works perfectly on mobile devices
- 🔒 **Secure Authentication** - Password encryption and secure sessions
- 📥 **Data Export** - Export attendance data to Excel/PDF
- 🎨 **Modern UI** - Clean and intuitive user interface

## 🛠️ Technology Stack

### Backend
- **Framework:** Django 4.2+
- **Database:** SQLite (development) / PostgreSQL (production)
- **Cache:** Redis (optional)
- **Task Queue:** Celery (optional)

### Frontend
- **CSS Framework:** Bootstrap 5
- **Icons:** Font Awesome 6
- **JavaScript:** Vanilla JS / jQuery

### Face Recognition
- **OpenCV** - Face detection
- **NumPy** - Numerical operations
- **Pillow** - Image processing

### Additional Tools
- **Gunicorn** - WSGI HTTP Server
- **Whitenoise** - Static file serving
- **Sentry** - Error tracking (optional)

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/attendance-system.git
cd attendance-system
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your configurations
# Generate a new SECRET_KEY using:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 5: Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 6: Collect Static Files

```bash
python manage.py collectstatic --no-input
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

## ⚙️ Configuration

### Environment Variables

Key environment variables in `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
USE_POSTGRES=False
DB_NAME=attendance_db
DB_USER=postgres
DB_PASSWORD=password

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Time Zone
TIME_ZONE=Asia/Karachi
```

### Database Configuration

#### SQLite (Default - Development)
No additional configuration needed.

#### PostgreSQL (Production)

```env
USE_POSTGRES=True
DB_NAME=attendance_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### Email Configuration

For Gmail:
1. Enable 2-Factor Authentication
2. Generate App Password
3. Update `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-digit-app-password
```

## 🎯 Usage

### For Employees

1. **Login** - Access your account
2. **Mark Attendance** - Upload your face image to mark attendance
3. **Apply for Leave** - Submit leave requests
4. **View Records** - Check your attendance history
5. **Track Leaves** - Monitor leave status

### For Administrators

1. **Register Faces** - Upload employee face images
2. **Manage Attendance** - View and edit attendance records
3. **Approve Leaves** - Review and approve/reject leave requests
4. **Generate Reports** - Create attendance reports
5. **Manage Employees** - Add/edit employee information

### First Time Setup

1. **Create Superuser:**
```bash
python manage.py createsuperuser
```

2. **Access Admin Panel:**
```
http://127.0.0.1:8000/admin/
```

3. **Add Departments:**
- Go to Admin Panel → Departments → Add Department

4. **Add Employees:**
- Go to Admin Panel → Employees → Add Employee

5. **Register Faces:**
- Navigate to Admin → Register Faces
- Upload clear frontal face images

## 📁 Project Structure

```
attendance-system/
│
├── attendance/                 # Attendance app
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── leave_views.py
│   ├── utils.py               # Face recognition utilities
│   └── urls.py
│
├── users/                      # User management app
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── core/                       # Core app (homepage, dashboard)
│   ├── templates/
│   ├── views.py
│   └── urls.py
│
├── attendance_system/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── templates/                  # Global templates
│   ├── base.html
│   ├── core/
│   └── registration/
│
├── static/                     # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                      # User uploads
│   └── face_images/
│
├── logs/                       # Application logs
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore
├── manage.py
└── README.md
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test attendance
python manage.py test users

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Face Recognition

```bash
python test_webcam.py
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL database
- [ ] Configure email backend
- [ ] Set up HTTPS/SSL
- [ ] Configure static files with CDN
- [ ] Set up backup strategy
- [ ] Configure logging
- [ ] Set up monitoring (Sentry)
- [ ] Use environment variables
- [ ] Enable security headers

### Deploy to Heroku

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### Deploy with Docker

```bash
# Build image
docker build -t attendance-system .

# Run container
docker run -p 8000:8000 attendance-system
```

## 📊 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Mark Attendance
![Mark Attendance](screenshots/mark-attendance.png)

### Leave Management
![Leave Management](screenshots/leave-management.png)

## 🔧 Troubleshooting

### Common Issues

**Issue: Face recognition not working**
- Solution: Ensure OpenCV is properly installed
- Check image quality and lighting
- Verify face encodings are stored correctly

**Issue: Email not sending**
- Solution: Check email configuration in `.env`
- Verify app password for Gmail
- Check firewall settings

**Issue: Database migration errors**
- Solution: Delete migration files (except `__init__.py`)
- Run `python manage.py makemigrations`
- Run `python manage.py migrate`

## 📝 API Documentation

API endpoints will be added in future versions using Django REST Framework.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Write docstrings for functions
- Add unit tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Django Documentation
- OpenCV Community
- Bootstrap Team
- Font Awesome
- All contributors

## 📞 Support

For support, email support@attendance.com or open an issue on GitHub.

## 🗺️ Roadmap

- [ ] Mobile app integration
- [ ] REST API
- [ ] Real-time notifications
- [ ] Advanced analytics
- [ ] Multi-language support
- [ ] Biometric integration
- [ ] Payroll integration
- [ ] Shift management

---

**Made with ❤️ using Django**
