# Placement Portal Application

## Overview
Institutes need efficient systems to manage campus recruitment activities involving companies, students, and placement drives. Currently, many institutes rely on spreadsheets, emails, or manual processes, which makes it difficult to manage company approvals, track student applications, avoid duplicate registrations, and maintain placement records.

## Project Description
You are required to build a **Placement Portal Application** web application that allows **Admin (Institute)**, **Company**, and **Students** to interact with the system based on their roles.

### Frameworks to be Used
- **Flask** for application back-end
- **Jinja2** templating, **HTML**, **CSS**, and **Bootstrap** for application front-end
- **SQLite** for database (no other database is permitted)
- **JS** should NOT be used for executing the core requirements

### Note
- All demos should be possible on your local machine.
- The database must be created programmatically (via table creation or model code).
- Manual database creation (such as using DB Browser for SQLite) is NOT allowed.

## Roles & Functionalities
### Admin (Institute Placement Cell)
- Admin is the pre-existing superuser of the application.
- Can approve or reject company registrations.
- Can approve or reject placement drives created by companies.
- Can view and manage all students, companies, and placement drives.
- Can edit, delete or blacklist students and companies if required.
- Can search students or companies by name or ID.

### Company
- Can register and create a company profile.
- Can log in only after admin approval.
- Can create placement drives (job postings).
- Can view student applications for their drives.
- Can shortlist students and update application status.

### Student
- Can register, log in, and update their profile.
- Can view approved placement drives.
- Can apply for placement drives.
- Can view application status and placement history.

## Key Terminologies
- **Admin (Institute)**: A user with the highest level of access who manages companies, students, and placement activities.
- **Company**: An organization registered in the system that conducts placement drives and recruits students.
- **Student**: A user who applies for placement drives and participates in recruitment activities.
- **Placement Drive**: A recruitment drive created by a company.
  - **Attributes**:
    - Drive ID
    - Company ID
    - Job Title
    - Job Description
    - Eligibility Criteria
    - Application Deadline
    - Status (Pending / Approved / Closed)
    - Extra fields etc.
- **Application**: A record of a student applying to a placement drive.
  - **Attributes**:
    - Application ID
    - Student ID
    - Drive ID
    - Application Date
    - Status (Applied / Shortlisted / Selected / Rejected)
    - Extra fields etc.
- **Company Profile**: Details of a registered company.
  - **Attributes**:
    - Company ID
    - Company Name
    - HR Contact
    - Website
    - Approval Status
    - Extra fields etc.

### Note
The above tables and fields are not exhaustive. Students may add additional tables and fields as required.

## Similar Apps
- [Internshala](https://internshala.com/)
- [Naukri](https://www.naukri.com/)
- [Indeed](https://www.indeed.com/)

## Application Wireframe
### Placement Portal Application
- The provided wireframe is intended only to illustrate the application's flow and navigation.
- Exact UI replication is NOT mandatory.
- Students are encouraged to design their own UI while maintaining the application's intended functionality.

## Core Features
### Authentication:
- Login system for admin, Company, and student.
- Registration is allowed only for Company and Student.
- Admin must pre-exist in the database (no admin registration).

### Admin Functionalities:
- The admin dashboard must display the total number of students, total number of companies, applications, and the total number of placement drives.
- Admin can approve or reject company registrations.
- Admin can approve or reject placement drives.
- Admin can view all placement drives and applications.
- Admin can search students by name, ID, or contact information.
- Admin can search companies by name.
- Admin can blacklist or deactivate student and company accounts.

### Company Functionalities
- Company registration and profile management.
- The company dashboard should display company details, created placement drives, and the number of applicants per drive.
- Companies can create (only after approval from admin), edit, remove or close placement drives.
- Companies can view student applications.
- Companies can shortlist students and update selection status (Shortlisted / Selected / Rejected)

### Student Functionalities
- Students have to self-register and login.
- Student’s dashboard should display all approved placement drives, applied placement drives and their status.
- Students can apply for placement drives.
- Students can view application status.
- Students can view past placement history.
- Students can edit their profile and upload a resume.

### Other Core Functionalities
- Prevent multiple applications by the same student for the same drive.
- Ensure only approved companies can create placement drives.
- Update application status dynamically.
- Allow students to view only approved placement drives.
- Maintain complete application history for each student.
- Allow admin to view all historical placement data.

## Recommended and/or Optional Functionalities
- API resources to interact with users, placement drives, and applications.
- Role-based access control using Flask extensions such as `flask_login` or `flask_security`.
- APIs can return JSON or be built using Flask extensions like `flask_restful`.
- Frontend validation using HTML5 or JavaScript.
- Backend validation inside Flask controllers.
- Clean and responsive UI using Bootstrap (no other CSS framework allowed).
- Charts for placement statistics using libraries like ChartJS.
- Any additional feature relevant to placement portal management.

## Possible Folder Structure
- `app/`
  - `__init__.py`
  - `models.py`
  - `routes.py`
  - `forms.py`
  - `templates/`
    - `layout.html`
    - `admin_dashboard.html`
    - `company_dashboard.html`
    - `student_dashboard.html`
  - `static/`
    - `css/`
    - `js/`
- `config.py`
- `run.py`
- `requirements.txt`