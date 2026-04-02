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
login_manager.login_view = 'auth.login'

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
            
            login_user(user)
            flash(f"Welcome {user.roll_no} to student portal!", 'success')
            return redirect(url_for('student_dashboard'))
        
        elif role == 'company':
            user = Company.query.filter_by(email=email).first()

            if not user or not user.check_password(password):
                flash('User not found or invalid password', 'danger')
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
        flash('Student Registration Succesful', 'success')
        return redirect(url_for('login'))
    
    return render_template('register_student.html')

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
    
    stats = {
        'total_companies' : Company.query.count(),
        'total_students' : Student.query.count(),
        'total_drives' : PlacementDrive.query.count(),
        'total_applications' : Application.query.count(),
        'pending_companies' : Company.query.filter_by(approval_status='pending').count(),
        'pending_drives' : PlacementDrive.query.filter_by(status='Pending').count()
    }

    return render_template('admin_dashboard.html', stats = stats)

@app.route('/admin/companies') #Fetch and manage comapny details
@login_required
def admin_companies():
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    search_query = request.args.get('search', '')
    if search_query:
        companies = Company.query.filter(
            (Company.company_name.ilike(f'%{search_query}%'))
        ).all()
    else:
        companies = Company.query.all()

    return render_template('admin_companies.html', companies=companies, search_query=search_query)

@app.route('/admin/company/action/<int:company_id>/<action>') #Approve/Reject/Blacklist the company
@login_required
def admin_company_action(company_id, action):
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    company = Company.query.get_or_404(company_id)

    if action not in ['approve', 'reject', 'blacklist']:
        flash('Invalid Action', 'danger')
        return redirect(url_for('admin_companies'))
    
    if not company:
        flash('comapny not found', 'danger')
        return redirect(url_for('admin_companies'))

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
    return redirect(url_for('admin_companies'))

@app.route('/admin/students') #Fetch and manage student details
@login_required
def admin_students():
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    search_query = request.args.get('search', '')

    if search_query:
        students = Student.query.filter(
            (Student.name.ilike(f'%{search_query}%')) |
            (Student.roll_no.ilike(f'%{search_query}%')) | 
            (Student.phone_no.ilike(f'%{search_query}%'))
        ).all()
    else:
        students = Student.query.all()

    return render_template('admin_students.html', students=students, search_query=search_query)

@app.route('/admin/student/action/<string:roll_no>/<action>') #Approve/Reject the student
@login_required
def admin_student_action(roll_no, action):
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    student = Student.query.get_or_404(roll_no)

    if action not in ['approve', 'reject', 'blacklist']:
        flash('Invalid Action', 'danger')
        return redirect(url_for('admin_students'))
    
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('admin_students'))
    
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
    return redirect(url_for('admin_students'))

@app.route('/admin/drives') #Fetch and manage Placement Drives
@login_required
def admin_drives():
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    search_query = request.args.get('search', '')

    if search_query:
        drives = PlacementDrive.query.filter(
            (PlacementDrive.name.ilike(f'%{search_query}%'))
        ).all()
    else:
        drives = PlacementDrive.query.all()

    return render_template('admin_drives.html', drives=drives, search_query=search_query)

@app.route('/admin/drive/action/<int:drive_id>/<action>') #Approve/Reject the Placement Drive
@login_required
def admin_drive_action(drive_id, action):
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    drive = PlacementDrive.query.get_or_404(drive_id)

    if action not in ['approve', 'reject']:
        flash('Invalid Action', 'danger')
        return redirect(url_for('admin_drives'))
    
    if not drive:
        flash('Placement Drive not found', 'danger')
        return redirect(url_for('admin_drives'))
    
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
    return redirect(url_for('admin_drives'))

@app.route('/admin/applications') #Fetch and manage student job applications
@login_required
def admin_applications():
    if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    applications = Application.query.all()
    return render_template('admin_applications.html', applications=applications)


@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if not current_user.is_authenticated or current_user.get_id().startswith('student_'):
        return "Unauthorized Access : Not a Student ", 403
    
    return render_template('student_dashboard.html')



@app.route('/company/dashboard')
@login_required
def company_dashboard():
    if not current_user.is_authenticated or current_user.get_id().startswith('company_'):
        return "Unauthorized Access : Not a Company ", 403
    
    return render_template('company_dashboard.html')

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)