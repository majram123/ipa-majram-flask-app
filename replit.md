# IPA MAJRAM - App Store

## Overview
A modern Arabic app store website built with Flask, featuring a beautiful purple theme and admin dashboard for managing apps, categories, and settings.

## Features
- Browse apps by categories (Games, Applications)
- Search functionality
- Admin dashboard with full CRUD operations
- Customizable site settings (colors, title)
- Social media links management
- RTL (Right-to-Left) support for Arabic

## Tech Stack
- **Backend**: Flask with SQLAlchemy
- **Database**: SQLite
- **Authentication**: Flask-Login
- **Frontend**: HTML, CSS, JavaScript, jQuery

## Project Structure
```
.
├── app.py              # Main Flask application
├── templates/          # HTML templates
│   ├── base.html       # Base template with sidebar
│   ├── index.html      # Homepage
│   ├── apps.html       # Apps listing
│   ├── search.html     # Search page
│   ├── contact.html    # Contact page
│   └── admin/          # Admin panel templates
├── static/             # Static files
│   ├── css/style.css   # Main styles
│   ├── js/             # JavaScript files
│   └── images/         # Images and icons
└── instance/           # Database files
```

## Admin Access
- **URL**: /admin/login
- **Username**: admin
- **Password**: admin123

## Running the Application
The app runs on port 5000:
```bash
python app.py
```

## Recent Changes
- Extracted and organized project files
- Fixed port configuration (changed to 5000)
- Cleaned up temporary files
