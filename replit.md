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
- Enhanced sidebar with "Join Us" section
- Performance optimizations (lazy loading, preload hints)

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

## Recent Changes (December 2025)
- Enhanced sidebar with prominent "Join Us" section and call-to-action button
- Improved admin dashboard with:
  - Detailed statistics (games count, applications count)
  - Quick action buttons
  - Recent apps list
  - Tips section
- Performance optimizations:
  - CSS preloading
  - JavaScript deferred loading
  - Image lazy loading support
  - Combined font loading for faster render
