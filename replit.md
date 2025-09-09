# Fire Department Real-Time Monitoring and Evaluation System

## Overview

This is a web-based Fire Department Real-Time Monitoring and Evaluation System built with Flask. The application manages fire safety inspections, No Objection Certificates (NOCs), and license renewals for businesses. It provides role-based access for both applicants (who submit requests) and administrators (who process and manage applications). The system streamlines the entire workflow from application submission to approval, including inspection scheduling and NOC issuance.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Bootstrap with dark theme and Font Awesome icons
- **Responsive Design**: Mobile-first approach with Bootstrap grid system
- **User Interface**: Role-based navigation and dashboards for applicants vs administrators

### Backend Architecture
- **Web Framework**: Flask (Python) with modular structure
- **Authentication**: Flask-Login for session management with role-based access control
- **Security**: Werkzeug for password hashing and CSRF protection
- **Database ORM**: SQLAlchemy with declarative base for data modeling
- **Application Structure**: Separation of concerns with models in separate files

### Data Storage Solutions
- **Primary Database**: SQLite (development) with PostgreSQL support via DATABASE_URL environment variable
- **Connection Management**: SQLAlchemy connection pooling with health checks and automatic reconnection
- **Database Models**: 
  - User model with role-based authentication (applicant/admin)
  - Application model for tracking requests with status workflow
  - Inspection model for scheduling and tracking inspections
  - NOC model for certificate management

### Authentication and Authorization
- **Session Management**: Flask-Login with secure session handling
- **Password Security**: Werkzeug password hashing with salt
- **Role-Based Access**: Two-tier system (applicant/admin) with different UI and functionality
- **Session Security**: Configurable secret key via environment variables

### Application Workflow
- **Status Management**: Multi-stage workflow (pending → inspection_scheduled → approved/rejected)
- **Request Types**: Support for inspections, NOCs, and license renewals
- **Admin Functions**: Application review, inspection scheduling, and NOC issuance
- **User Functions**: Application submission and status tracking

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework and routing
- **Flask-SQLAlchemy**: ORM and database abstraction
- **Flask-Login**: User session management and authentication
- **Werkzeug**: Security utilities and WSGI utilities

### Frontend Dependencies
- **Bootstrap**: CSS framework via CDN for responsive design
- **Font Awesome**: Icon library via CDN for user interface elements

### Development and Deployment
- **Database**: SQLite for development, PostgreSQL for production (configurable via environment)
- **WSGI**: ProxyFix middleware for proper header handling in production deployments
- **Environment Configuration**: Support for DATABASE_URL and SESSION_SECRET environment variables

### Database Schema
The application uses a relational database structure with foreign key relationships between users, applications, inspections, and NOCs. The schema supports audit trails with created_at and updated_at timestamps, and maintains referential integrity across all entities.