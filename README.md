# 🏆 Sportify — Sports Management Platform

> A dynamic Django-based web platform that connects sports enthusiasts with events, coaching sessions, venues, and societies — with integrated online payments via Razorpay.

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Models](#database-models)
- [URL Routes](#url-routes)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Admin Panel](#admin-panel)
- [Payment Integration](#payment-integration)
- [Screenshots / Pages](#screenshots--pages)
- [Team](#team)
- [Contact](#contact)

---

## 🏅 About the Project

**Sportify** is a full-stack web application built with Django that serves as a centralized sports management platform. It allows users to:

- Browse and register for upcoming **sports events**
- Explore and join **sports societies/organizations**
- Book **sports venues** for matches and practice
- Enroll in **coaching sessions** with professional coaches
- Make **secure online payments** for event registrations via Razorpay
- Contact the organization via a built-in **contact form**

The platform supports both regular users (athletes, participants) and administrators who manage all content via Django's admin panel.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎉 **Event Management** | View all upcoming sports events with names, dates, venues, fees, and images |
| 💳 **Online Payment** | Razorpay-integrated payment gateway for event registration fees |
| 🏫 **Societies** | Browse sports societies/organizations with their associated coaches |
| 🏟️ **Sports Venues** | Discover and explore sports venues with location and description |
| 🥊 **Coaching Sessions** | View coaching programs with coach details, sport type, and descriptions |
| 👤 **User Authentication** | Register, login, and logout with Django's built-in auth system |
| 🛡️ **Admin Panel** | Full-featured Django admin for managing all data |
| 📬 **Contact Form** | Users can send messages directly from the website |
| 🔒 **Duplicate Registration Prevention** | Users cannot double-register for the same event |
| 📧 **Email Support** | SMTP email backend configured (Gmail) |
| 📁 **Media Uploads** | Image uploads for events, venues, societies, and coaching sessions |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.x, Django 5.1.1 |
| **Database** | MySQL (`sportify_db`) |
| **Payment Gateway** | Razorpay |
| **Frontend** | HTML5, CSS3, JavaScript (Django Templates) |
| **Authentication** | Django Built-in Auth (`django.contrib.auth`) |
| **Email** | SMTP via Gmail |
| **Media Storage** | Local file system (`/media/`) |
| **Static Files** | Django static files (`/static/`) |
| **Web Server** | Django dev server / WSGI (production) |

---

## 📁 Project Structure

```
sportify/
│
├── manage.py                    # Django management script
├── sportify_db                  # MySQL database file reference
├── README.md                    # Project documentation
│
├── sportify/                    # Django project config
│   ├── settings.py              # Project settings (DB, email, Razorpay, etc.)
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI application entry point
│   └── asgi.py                  # ASGI application entry point
│
├── registration/                # Main Django app
│   ├── models.py                # Database models
│   ├── views.py                 # View functions
│   ├── urls.py                  # App-level URL patterns
│   ├── forms.py                 # Django forms
│   ├── admin.py                 # Admin panel configuration
│   ├── apps.py                  # App configuration
│   ├── migrations/              # Database migrations
│   ├── static/                  # App-specific static files
│   └── templates/
│       └── registration/        # HTML templates
│           ├── base.html        # Base template (navbar, footer)
│           ├── home.html        # Landing page
│           ├── event_list.html  # All events listing
│           ├── register_event.html  # Event registration confirmation
│           ├── payment.html     # Razorpay payment page
│           ├── payment_success.html # Payment success page
│           ├── coaching.html    # Coaching sessions listing
│           ├── sports_venues.html   # Venues listing
│           ├── society_list.html    # Societies listing
│           ├── about.html       # About us page
│           ├── contact.html     # Contact page
│           ├── login.html       # Login page
│           └── register.html    # User registration page
│
└── media/                       # Uploaded media files
    ├── events/                  # Event images
    ├── venues/                  # Venue images
    ├── societies/               # Society images
    └── coaching/                # Coaching session images
```

---

## 🗄️ Database Models

### `Society`
Represents a sports organization/club.
| Field | Type | Description |
|---|---|---|
| `name` | CharField | Society name |
| `location` | CharField | Society location |
| `description` | TextField | Detailed description |
| `image` | ImageField | Society logo/image |
| `coaches` | ManyToManyField | Associated coaching sessions |

### `Event`
Represents a sports event or tournament.
| Field | Type | Description |
|---|---|---|
| `name` | CharField | Event name |
| `date` | DateField | Event date |
| `venue` | CharField | Event venue |
| `registration_fee` | DecimalField | Fee amount (INR) |
| `image` | ImageField | Event banner image |

### `SportsVenue`
Represents a sports facility or ground.
| Field | Type | Description |
|---|---|---|
| `name` | CharField | Venue name |
| `location` | CharField | Venue location |
| `description` | TextField | Venue details |
| `image` | ImageField | Venue image |
| `societies` | ManyToManyField | Societies using this venue |

### `Registration`
Tracks user registrations for events.
| Field | Type | Description |
|---|---|---|
| `user` | ForeignKey | Registered user |
| `event` | ForeignKey | Event registered for |
| `registration_date` | DateField | Auto-set registration date |
| `payment_status` | CharField | `Pending` / `Completed` |

> ℹ️ Each user-event pair is **unique** (no duplicate registrations).

### `Payment`
Tracks Razorpay payment transactions.
| Field | Type | Description |
|---|---|---|
| `order_id` | CharField | Razorpay order ID (unique) |
| `payment_id` | CharField | Razorpay payment ID |
| `amount` | DecimalField | Amount paid (INR) |
| `status` | CharField | `Pending` / `Completed` / `Failed` |
| `event` | ForeignKey | Event the payment is for |
| `user` | ForeignKey | User who made the payment |
| `created_at` | DateTimeField | Timestamp of payment creation |

### `Sport`
Simple reference model for sport types.
| Field | Type |
|---|---|
| `name` | CharField |

### `Coaching`
Represents a coaching program or session.
| Field | Type | Description |
|---|---|---|
| `title` | CharField | Coaching program title |
| `coach_name` | CharField | Coach's name |
| `sport` | ForeignKey | Associated sport |
| `society` | ForeignKey | Associated society |
| `description` | TextField | Program description |
| `image` | ImageField | Coach/program image |

### `Contact`
Stores messages submitted via the contact form.
| Field | Type | Description |
|---|---|---|
| `name` | CharField | Sender's name |
| `email` | EmailField | Sender's email |
| `mobile_number` | CharField | Sender's mobile number |
| `message` | TextField | Message content |
| `created_at` | DateTimeField | Submission timestamp |

---

## 🔗 URL Routes

| URL | View | Name | Description |
|---|---|---|---|
| `/` | `home` | `home` | Landing / home page |
| `/events/` | `event_list` | `event_list` | All sports events |
| `/events/register/<id>/` | `register_event` | `register_event` | Register for an event |
| `/events/register/<id>/payment/` | `process_payment` | `process_payment` | Initiate Razorpay payment |
| `/payment-success/` | `payment_success` | `payment_success` | Payment confirmation callback |
| `/coaching/` | `coaching` | `coaching` | All coaching sessions |
| `/sports_venues/` | `sports_venues` | `sports_venues` | All sports venues |
| `/societies/` | `society_list` | `society_list` | All sports societies |
| `/about/` | `about` | `about` | About the platform |
| `/contact/` | `contact` | `contact` | Contact form page |
| `/register/` | `register` | `register` | New user registration |
| `/login/` | `login_view` | `login` | User login |
| `/logout/` | `logout_view` | `logout` | User logout |
| `/admin/` | Django Admin | — | Admin dashboard |

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.8 or above
- MySQL Server
- pip (Python package manager)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/omkary357/sportify.git
cd sportify
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

### 3. Install Dependencies

```bash
pip install django mysqlclient razorpay pillow
```

Or if a `requirements.txt` is present:

```bash
pip install -r requirements.txt
```

### 4. Set Up the MySQL Database

Open MySQL and run:

```sql
CREATE DATABASE sportify_db;
```

Make sure your MySQL server is running on **port 3305** (or update the port in `settings.py`).

---

## 🔧 Configuration

Open `sportify/settings.py` and update the following:

### Database Settings

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sportify_db',
        'USER': 'root',            # Your MySQL username
        'PASSWORD': 'root',        # Your MySQL password
        'HOST': 'localhost',
        'PORT': '3305',            # Your MySQL port
    }
}
```

### Email Settings (Gmail SMTP)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'       # Replace with your Gmail
EMAIL_HOST_PASSWORD = 'your_app_password'      # Use Gmail App Password
```

> ⚠️ Use a **Gmail App Password**, not your regular Gmail password. Enable 2FA and generate one from [Google Account Security](https://myaccount.google.com/security).

### Razorpay Settings

```python
RAZORPAY_KEY_ID = 'your_razorpay_key_id'
RAZORPAY_KEY_SECRET = 'your_razorpay_key_secret'
```

> Get your API keys from your [Razorpay Dashboard](https://dashboard.razorpay.com/).

---

## 🚀 Running the Project

### Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

### Start the Development Server

```bash
python manage.py runserver
```

The app will be available at: **http://127.0.0.1:8000/**

---

## 🖥️ Admin Panel

Access the Django Admin at: **http://127.0.0.1:8000/admin/**

Log in with the superuser credentials you created. You can manage:

| Model | Features |
|---|---|
| **Events** | Add/edit/delete sports events |
| **Registrations** | View all user event registrations |
| **Payments** | Monitor payment statuses |
| **Sports Venues** | Manage venues with society associations |
| **Coaching** | Manage coaching programs and coaches |
| **Societies** | Manage sports clubs/organizations with coaches |
| **Sports** | Manage sport categories |
| **Contacts** | View all messages submitted via contact form |

---

## 💳 Payment Integration

Sportify uses **Razorpay** for processing event registration payments.

### Payment Flow

```
User clicks "Register" on an event
        ↓
Login required (redirects if not logged in)
        ↓
Event registration page shown
        ↓
User clicks "Proceed to Payment"
        ↓
Razorpay order created → Payment page rendered
        ↓
User completes payment on Razorpay modal
        ↓
Razorpay sends callback to /payment-success/
        ↓
Signature verified → Payment marked "Completed"
        ↓
Registration record created → Success page shown
```

### Payment Statuses

| Status | Meaning |
|---|---|
| `Pending` | Payment initiated but not completed |
| `Completed` | Payment verified and successful |
| `Failed` | Signature verification failed |

> ℹ️ A user **cannot register twice** for the same event. The platform checks for existing `Completed` registrations before initiating a new payment.

---

## 📸 Screenshots / Pages

| Page | URL |
|---|---|
| 🏠 Home | `/` |
| 📅 Events | `/events/` |
| 🏟️ Venues | `/sports_venues/` |
| 🥊 Coaching | `/coaching/` |
| 🏫 Societies | `/societies/` |
| ℹ️ About | `/about/` |
| 📬 Contact | `/contact/` |
| 🔑 Login | `/login/` |
| 📝 Register | `/register/` |

---

## 👥 Team

| Name | Role |
|---|---|
| **Omkar** | CEO & Lead Developer |
| **Atul** | Head Coach & Sports Advisor |
| **Sameer** | Operations Manager |

---

## 📬 Contact

| Channel | Details |
|---|---|
| 📧 Email | omkary357@gmail.com |
| 📞 Phone | +91 7715078272 |
| 🏢 Address | MIDC, Andheri East, Mumbai, Maharashtra 400093, India |
| 🌐 Website | www.sportify.com |

---

## 📄 License

This project is for educational and personal use. All rights reserved © Sportify.

---

<div align="center">
  <strong>Built with ❤️ using Django</strong>
</div>
