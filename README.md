# Placement Portal Application

This is a web application built to help institutes manage their campus recruitment process. It serves as a centralized platform connecting the institute admin, recruiting companies, and students to handle job postings and applications efficiently.

## Features

### Admin (Institute)
* **Approval System:** The admin must approve company registrations and placement drives before they go live on the platform.
* **Master Dashboard:** Allows the admin to view a complete log of all student applications across every company and drive.
* **User Management:** Monitor and manage all student and company profiles.

### Company
* **Profile Creation:** Companies can register and create a profile (requires admin approval to access the system).
* **Post Jobs (Placement Drives):** Companies can create job postings with specific eligibility requirements like minimum CGPA, graduation year, and eligible departments.
* **Review Applications:** Companies can view the students who applied, check their resumes and technical skills, and update their application status (e.g., Shortlisted, Interview, Placed, Rejected).

### Student
* **Registration:** Students can create an account and fill out their academic details and professional links.
* **Browse Jobs:** Students can view all active, admin-approved placement drives.
* **Apply:** Students can apply to eligible drives with a single click. The backend prevents duplicate applications.
* **Track Status:** Students can track the progress of their applications directly from their dashboard.

## Tech Stack

This project was built using a standard MVC architecture with server-side rendering, keeping core logic out of the frontend.

* **Backend:** Flask (Python)
* **Database:** SQLite with Flask-SQLAlchemy
* **Authentication:** Flask-Login and Werkzeug for password hashing
* **Frontend:** HTML5, CSS3, Bootstrap 5, and Jinja2 templates

