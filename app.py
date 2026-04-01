import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, date, time
from models import db, Admin, Company, Student
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
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_authenticated or current_user.get_id().startswith('admin_'):
        return "Unauthorized Access : Not an Admin ", 403
    
    return render_template('admin_dashboard.html')

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
    
    return render_template('student_dashboard.html')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)