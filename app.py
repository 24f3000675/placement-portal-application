import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, date, time
from models import *
from config import Config

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'placement.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'placement-portal'

db.init_app(app)

#Login and Auth
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader #Run this fn everytime the user clicks a new page 
def load_user(user_id):
    try:
        role, uid = user_id.split('_', 1)

        if role == 'admin':
            return Admin.query.get(int(uid))
        elif role == 'student':
            return Student.query.get(uid)
        elif role == 'company':
            return Company.query.get(int(uid))
    except Exception as e:
        return None
    return None

#Auth Routes (Login and Reg)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if not (email and password and role):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        
        if role == 'admin':
            user = Admin.query.filter_by(email=email).first()

            if not user or not user.check_password(password):
                flash('User not found or invalid password', 'danger')
                return redirect(url_for('login'))
            
            login_user(user)
            flash('Welcome Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        elif role == 'student':
            user = Student.query.filter_by(email=email).first()

            if not user or not user.check_password(password):
                flash('User not found or invalid password', 'danger')
                return redirect(url_for('login'))
            
            if user.is_blacklisted:
                flash('Your account has been blacklisted.', 'danger')
                return redirect(url_for('login'))
            
            if user.approval_status == 'pending':
                flash('Your registration is waiting for Admin approval.', 'warning')
                return redirect(url_for('login'))
            
            elif user.approval_status == 'rejected':
                flash('Your registration has been rejected by Admin.', 'danger')
                return redirect(url_for('login'))

            login_user(user)
            flash(f"Welcome {user.roll_no} to student portal!", 'success')
            return redirect(url_for('student_dashboard'))
        
        elif role == 'company':
            user = Company.query.filter_by(email=email).first()

            if not user or not user.check_password(password):
                flash('User not found or invalid password', 'danger')
                return redirect(url_for('login'))
            
            if user.is_blacklisted:
                flash('Your account has been blacklisted.', 'danger')
                return redirect(url_for('login'))
            
            if user.approval_status == 'pending':
                flash('Your registration is waiting for Admin approval.', 'warning')
                return redirect(url_for('login'))
            
            elif user.approval_status == 'rejected':
                flash('Your registration has been rejected by Admin.', 'danger')
                return redirect(url_for('login'))

            login_user(user)
            flash(f"Welcome {user.company_name} to company portal!", 'success')
            return redirect(url_for('company_dashboard'))
        
        else:
            flash('Invalid Role', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Registration Routes
@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        roll_no = request.form.get('roll_no')
        email = request.form.get('email')

        if Student.query.filter_by(roll_no=roll_no).first() or Student.query.filter_by(email=email).first():
            flash("Student record already exists!", 'danger')
            return redirect(url_for('register_student'))
        
        new_student = Student(
            name = request.form.get('name'),
            roll_no = roll_no,
            email = email,
            phone_no = request.form.get('phone_no'),
            gender = request.form.get('gender'),
            dob=datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date(),
            dept_id = request.form.get('dept_id'),
            graduation_year = int(request.form.get('graduation_year')),
            cgpa = float(request.form.get('cgpa')),
            has_backlogs = bool(request.form.get('has_backlogs')),
            location = request.form.get('location')
        )
        new_student.set_password(request.form.get('password'))
        db.session.add(new_student)
        db.session.commit()
        flash('Student Registration Successful. Please wait for admin approval to login', 'success')
        return redirect(url_for('login'))
    
    departments = Department.query.all()
    
    return render_template('register_student.html', departments=departments)

@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        email = request.form.get('email')
        company_name = request.form.get('company_name')

        if Company.query.filter_by(email=email).first() or Company.query.filter_by(company_name=company_name).first():
            flash('Company record already exists!', 'danger')
            return redirect(url_for('register_company'))
        
        new_company = Company(
            email = email,
            company_name = company_name,
            hr_name = request.form.get('hr_name'),
            hr_email = request.form.get('hr_email'),
            hr_phone = request.form.get('hr_phone'),
            company_desc = request.form.get('company_desc'),
            website = request.form.get('website'),
        )
        new_company.set_password(request.form.get('password'))
        db.session.add(new_company)
        db.session.commit()
        flash('Company Registration Successful. Please wait for admin approval to login', 'success')
        return redirect(url_for('login'))
    return render_template('register_company.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

#Dashboard Routes

#Admin Dashbaord
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403

    company_search = request.args.get('company_search', '')
    student_search = request.args.get('student_search', '')
    drive_search = request.args.get('drive_search', '')
    
    stats = {
        'total_companies' : Company.query.count(),
        'total_students' : Student.query.count(),
        'total_drives' : PlacementDrive.query.count(),
        'pending_students' : Student.query.filter_by(approval_status='pending').count(),
        'total_applications' : Application.query.count(),
        'pending_companies' : Company.query.filter_by(approval_status='pending').count(),
        'pending_drives' : PlacementDrive.query.filter_by(status='Pending').count()
    }

    if company_search:
        companies = Company.query.filter(
            Company.company_name.ilike(f'%{company_search}%')
        ).all()
    else:
        companies = Company.query.filter_by(approval_status='approved').all()

    if student_search:
        students = Student.query.filter(
            (Student.name.ilike(f'%{student_search}%')) |
            (Student.roll_no.ilike(f'%{student_search}%')) |
            (Student.phone_no.ilike(f'%{student_search}%'))
        ).all()
    else:
        students = Student.query.filter_by(approval_status='approved').all()

    if drive_search:
        drives = PlacementDrive.query.filter(
            PlacementDrive.name.ilike(f'%{drive_search}%')
        ).all()
    else:
        drives = PlacementDrive.query.filter_by(status='approved').all()

    pending_students = Student.query.filter_by(approval_status='pending').all()
    pending_companies = Company.query.filter_by(approval_status='pending').all()
    pending_drives = PlacementDrive.query.filter_by(status='Pending').all()

    return render_template(
        'admin_dashboard.html',
        stats=stats,
        companies=companies,
        students=students,
        drives=drives,
        pending_students=pending_students,
        pending_companies=pending_companies,
        pending_drives=pending_drives,
        company_search=company_search,
        student_search=student_search,
        drive_search=drive_search)


@app.route('/admin/company/action/<int:company_id>/<action>') #Approve/Reject/Blacklist the company
@login_required
def admin_company_action(company_id, action):
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    company = Company.query.get_or_404(company_id)

    if action not in ['approve', 'reject', 'blacklist']:
        flash('Invalid Action', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if not company:
        flash('comapny not found', 'danger')
        return redirect(url_for('admin_dashboard'))

    if action == 'approve':
        if company.approval_status == 'approved':
            flash('Company is already approved', 'warning')
        else:
            company.approval_status = 'approved'
            flash(f"{company.company_name} has been approved", 'success')
    elif action == 'reject':
        if company.approval_status == 'rejected':
            flash('Company is already rejected', 'warning')
        else:
            company.approval_status = 'rejected'
            flash(f"{company.company_name} has been rejected", 'danger')
    elif action == 'blacklist':
        if company.is_blacklisted:
            flash('Company is already blacklisted', 'warning')
        else:
            company.is_blacklisted = True
            flash(f"{company.company_name} has been blacklisted", 'danger')
    
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/student/action/<string:roll_no>/<action>') #Approve/Reject/Blacklist the student
@login_required
def admin_student_action(roll_no, action):
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    student = Student.query.get_or_404(roll_no)

    if action not in ['approve', 'reject', 'blacklist']:
        flash('Invalid Action', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if action == 'approve':
        if student.approval_status == 'approved':
            flash('Student is already approved', 'warning')
        elif student.is_blacklisted:
            flash('Student is blacklisted, cannot approve.', 'warning')
        else:
            student.approval_status = 'approved'
            flash(f"{student.name} has been approved", 'success')
    elif action == 'reject':
        if student.approval_status == 'rejected':
            flash('Student is already rejected', 'warning')
        else:
            student.approval_status = 'rejected'
            flash(f"{student.name} has been rejected", 'danger')
    elif action == 'blacklist':
        if student.is_blacklisted:
            flash('Student is already blacklisted', 'warning')
        else:
            student.is_blacklisted = True
            flash(f"{student.name} has been blacklisted", 'danger')
    
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/drive/action/<int:drive_id>/<action>') #Approve/Reject the Placement Drive
@login_required
def admin_drive_action(drive_id, action):
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    drive = PlacementDrive.query.get_or_404(drive_id)

    if action not in ['approve', 'reject']:
        flash('Invalid Action', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if not drive:
        flash('Placement Drive not found', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if action == 'approve':
        if drive.status == 'approved':
            flash('Placement Drive is already approved', 'warning')
        else:
            drive.status = 'approved'
            flash(f"{drive.name} has been approved", 'success')
    elif action == 'reject':
        if drive.status == 'rejected':
            flash('Placement Drive is already rejected', 'warning')
        else:
            drive.status = 'rejected'
            flash(f"{drive.name} has been rejected", 'danger')
    
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


#Student Dashboard
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if not current_user.is_authenticated or not current_user.get_id().startswith('student_'):
        return "Unauthorized Access : Not a Student ", 403
    
    if current_user.approval_status == 'pending':
        logout_user()
        flash('Your account has not yet been approved by the admin.', 'warning')
        return redirect(url_for('login'))
    
    if current_user.approval_status == 'rejected':
        logout_user()
        flash('Your account has been rejected by the admin.', 'warning')
        return redirect(url_for('login'))
    
    if current_user.is_blacklisted:
        logout_user()
        flash('Your account has been rejected by the admin.', 'warning')
        return redirect(url_for('login'))
    
    companies = Company.query.filter_by(approval_status='approved').all()

    applications = Application.query.filter_by(student_roll=current_user.roll_no).all()

    return render_template('student_dashboard.html', companies=companies, applications=applications)

@app.route('/student/profile/edit', methods=['GET', 'POST']) #Create and edit a student's profile 
@login_required
def student_profile():
    if not current_user.is_authenticated or not current_user.get_id().startswith('student_'):
        return "Unauthorized Access : Not a Student ", 403
    
    student = Student.query.filter_by(roll_no=current_user.roll_no).first()

    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('login'))

    profile = student.skills
    
    if request.method == 'POST':
        if not profile:
            profile = Skills(student_roll=student.roll_no, resume_link='')
            db.session.add(profile)

        profile.resume_link = request.form.get('resume_link', '').strip()
        profile.github_url = request.form.get('github_link', '').strip()
        profile.linkedin_url = request.form.get('linkedin_link', '').strip()
        profile.skills = request.form.get('skills', '').strip()
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('student_profile.html', student=student, profile=profile)

@app.route('/student/company/<int:company_id>') #View a specific company
@login_required
def student_company(company_id):
    if not current_user.is_authenticated or not current_user.get_id().startswith('student_'):
        return "Unauthorized Access : Not a Student ", 403
    
    if not company_id:
        flash('Company not found', 'danger')
        return redirect(url_for('student_dashboard'))
    
    company = Company.query.filter_by(company_id=company_id).all()

    if not company:
        flash('Requested Company does not exist', 'warning')
        return redirect(url_for('student_dashboard'))
    
    drive = PlacementDrive.query.filter_by(comp_id=company_id).first()

    return render_template('student_company.html', company=company, drive=drive)


@app.route('/student/drive/<int:drive_id>', methods=['GET', 'POST']) #View drive details
@login_required
def student_drive_details(drive_id):
    if not current_user.is_authenticated or not current_user.get_id().startswith('student_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    if not drive_id:
        flash('Drive not found', 'danger')
        return redirect(url_for('student_dashboard'))
    
    drive = PlacementDrive.query.filter_by(id=drive_id).first()

    if not drive:
        flash('Drive not found', 'warning')
        return redirect(url_for('student_dashboard'))

    existing_application = Application.query.filter_by(student_roll=current_user.roll_no, drive_id=drive_id).first()

    if request.method == 'POST':
        if existing_application:
            flash('You have already applied for this drive', 'warning')
        else:
            new_application = Application(student_roll=current_user.roll_no, drive_id=drive_id, application_status='applied')
            db.session.add(new_application)
            db.session.commit()
            flash(f'Application submitted successfully for {drive.name}!', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('student_drive_details.html', drive=drive, existing_application=existing_application)


@app.route('/admin/applications') #Fetch and manage student job applications
@login_required
def admin_applications():
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    applications = Application.query.all()
    return render_template('admin_applications.html', applications=applications)


#Company Dashboard
@app.route('/company/dashboard')
@login_required
def company_dashboard():
    if not current_user.is_authenticated or not current_user.get_id().startswith('company_'):
        return "Unauthorized Access : Not a Company ", 403

    if current_user.approval_status == 'pending':
        logout_user()
        flash('Company registration not yet approved by admin', 'warning')
        return redirect(url_for('login'))
    
    if current_user.approval_status == 'rejected':
        logout_user()
        flash('Company registration rejected by admin', 'danger')
        return redirect(url_for('login'))

    if current_user.is_blacklisted:
        logout_user()
        flash('Company is blacklisted', 'danger')
        return redirect(url_for('login'))
    
    company = Company.query.filter_by(company_id=current_user.company_id).first()

    if not company:
        flash('Company profile not found', 'danger')
        return redirect(url_for('login'))

    drives = PlacementDrive.query.filter_by(comp_id=company.company_id).all()

    drive_ids = []

    for i in drives:
        drive_ids.append(i.id)
    
    if drive_ids:
        applications = Application.query.filter(Application.drive_id.in_(drive_ids)).all()
    else:
        applications = []    

    upcoming_drives = PlacementDrive.query.filter(
        PlacementDrive.comp_id == company.company_id,
        PlacementDrive.status.in_(['Active', 'Pending', 'approved'])
    ).all()
    closed_drives = PlacementDrive.query.filter(
        PlacementDrive.comp_id == company.company_id,
        PlacementDrive.status.in_(['Closed', 'Rejected'])
    ).all()

    return render_template('company_dashboard.html', company=company, upcoming_drives=upcoming_drives, closed_drives=closed_drives, applications=applications)

@app.route('/company/drive/create', methods=['GET', 'POST']) #Create a new drive
@login_required
def company_create_drive():
    if not current_user.is_authenticated or not current_user.get_id().startswith('company_'):
        return "Unauthorized Access : Not a Company ", 403
    
    company = Company.query.filter_by(company_id=current_user.company_id).first()

    if request.method == 'POST':
        name = request.form.get('name')
        job_title = request.form.get('job_title')
        job_desc = request.form.get('job_desc')
        min_cgpa = float(request.form.get('min_cgpa'))
        eligible_grad_yr = request.form.get('eligible_grad_yr')
        salary = int(request.form.get('salary'))
        location = request.form.get('location')
        deadline = datetime.strptime(request.form.get('deadline'), '%Y-%m-%d')

        eligible_departments_ids = request.form.getlist('departments') 

        new_drive = PlacementDrive(
            name=name,
            comp_id=company.company_id,
            job_title=job_title,
            job_desc=job_desc,
            min_cgpa=min_cgpa,
            eligible_grad_yr=eligible_grad_yr,
            salary=salary,
            location=location,
            deadline=deadline
        )
        db.session.add(new_drive)
        db.session.commit()

        for dept_id in eligible_departments_ids:
            if dept_id and dept_id.strip():
                new_dept = EligibleDepartments(drive_id=new_drive.id, dept_id=dept_id)
                db.session.add(new_dept)
        db.session.commit()

        flash(f'{name} Drive created successfully!', 'success')
        return redirect(url_for('company_dashboard'))
    
    all_depts = Department.query.all()    
    return render_template('company_create_drive.html', company=company, departments=all_depts)

@app.route('/company/drive/update/<int:drive_id>', methods=['POST']) #Update drive details
@login_required
def company_drive_update(drive_id):
    if not current_user.is_authenticated or not current_user.get_id().startswith('company_'):
        return "Unauthorized Access : Not a Company ", 403
    
    drive = PlacementDrive.query.filter_by(id=drive_id).first()
    
    if not drive:
        flash('Drive not found', 'danger')
        return redirect(url_for('company_dashboard'))
    
    drive.name = request.form.get('name', drive.name)
    drive.job_title = request.form.get('job_title', drive.job_title)
    drive.job_desc = request.form.get('job_desc', drive.job_desc)
    drive.min_cgpa = float(request.form.get('min_cgpa', drive.min_cgpa)) if request.form.get('min_cgpa') else drive.min_cgpa
    drive.eligible_grad_yr = request.form.get('eligible_grad_yr', drive.eligible_grad_yr)
    drive.salary = int(request.form.get('salary', drive.salary)) if request.form.get('salary') else drive.salary
    drive.location = request.form.get('location', drive.location)
    
    if request.form.get('deadline'):
        drive.deadline = datetime.strptime(request.form.get('deadline'), '%Y-%m-%d')
    
    db.session.commit()
    flash(f'{drive.name} updated successfully!', 'success')
    return redirect(url_for('company_dashboard'))

@app.route('/company/drive/<string:action>/<int:drive_id>') #Take action on a drive
@login_required
def company_drive_action(action, drive_id):
    drive = PlacementDrive.query.filter_by(id=drive_id).first()

    if action == 'close':
        drive.status = 'Closed'
        db.session.commit()
        flash(f'{drive.name} Drive closed successfully!', 'success')
        return redirect(url_for('company_dashboard'))

    if action == 'fetch_applications':
        applications = Application.query.filter_by(drive_id=drive_id).all()
        return render_template('company_drive_applications.html', drive=drive, applications=applications)
    
@app.route('/company/application/<int:app_id>/<string:action>', methods=['GET', 'POST']) #Take action on an application
@login_required
def company_application_action(app_id, action):
    application = Application.query.filter_by(id=app_id).first()

    if not application:
        flash('Application not found', 'danger')
        return redirect(url_for('company_dashboard'))
    
    student = Student.query.filter_by(roll_no=application.student_roll).first()

    if request.method == 'POST':
        if action == 'review':
            new_status = request.form.get('status')
            application.application_status = new_status
            db.session.commit()
            flash(f'Application status updated to {new_status}!', 'success')
            return redirect(url_for('company_drive_applications', drive_id=application.drive_id))
        
    return render_template('company_review_application.html', application=application, student=student)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)