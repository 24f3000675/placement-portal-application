from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# ADMIN MODEL
class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return f"admin_{self.id}"
    
    def __repr__(self):
        return f'<Admin {self.username}>' #Dev purposes only


# DEPARTMENT MODEL
class Department(db.Model):
    __tablename__ = 'departments'
    
    dept_id = db.Column(db.String(10), primary_key=True)
    dept_name = db.Column(db.String(100), unique=True, nullable=False)
    
    students = db.relationship('Student', backref='department')
    eligible_departments = db.relationship('EligibleDepartments', backref='department')
    
    def __repr__(self):
        return f'<Department {self.dept_id}: {self.dept_name}>'


# STUDENT MODEL
class Student(db.Model, UserMixin):
    __tablename__ = 'student'
    
    roll_no = db.Column(db.String(50), primary_key=True)
    
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    phone_no = db.Column(db.String(15), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(255))
    
    dept_id = db.Column(db.String(10), db.ForeignKey('departments.dept_id'), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Numeric(4, 2), nullable=False)
    has_backlogs = db.Column(db.Boolean, nullable=False, default=False) 
    
    approval_status = db.Column(db.String(50), nullable=False, default='pending') #'Pending', 'Approved', 'Rejected'
    is_blacklisted = db.Column(db.Boolean, default=False)
    
    skills = db.relationship('Skills', backref='student', uselist=False)
    applications = db.relationship('Application', backref='student')
    
    def get_id(self):
        return f"student_{self.roll_no}"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Student {self.roll_no}: {self.name}>'


# SKILLS MODEL
class Skills(db.Model):
    __tablename__ = 'skills'
    
    student_roll = db.Column(db.String(50), db.ForeignKey('student.roll_no'), primary_key=True)
    linkedin_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    resume_link = db.Column(db.String(255), nullable=False)
    skills = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Skills for {self.student_roll}>'

# COMPANY MODEL
class Company(db.Model, UserMixin):
    __tablename__ = 'company'
    
    company_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    company_name = db.Column(db.String(255), nullable=False)
    hr_name = db.Column(db.String(255), nullable=False)
    hr_email = db.Column(db.String(255), nullable=False)
    hr_phone = db.Column(db.String(15), nullable=False)
    company_desc = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(255), unique=True, nullable=False)
    
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    approval_status = db.Column(db.String(50), nullable=False, default='pending') #'pending' 'approved' 'rejected' 'blacklisted'
    
    placement_drives = db.relationship('PlacementDrive', backref='company')
    
    def get_id(self):
        return f"company_{self.company_id}"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Company {self.company_name}>'

# PLACEMENT DRIVE MODEL
class PlacementDrive(db.Model):
    __tablename__ = 'placement_drive'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    comp_id = db.Column(db.Integer, db.ForeignKey('company.company_id'), nullable=False)
    
    job_title = db.Column(db.String(255), nullable=False)
    job_desc = db.Column(db.String(255), nullable=False)
    
    min_cgpa = db.Column(db.Numeric(4, 2))
    eligible_grad_yr = db.Column(db.Integer)
    
    salary = db.Column(db.Integer)
    location = db.Column(db.String(255))
    deadline = db.Column(db.DateTime, nullable=False)
    
    status = db.Column(db.String(50), nullable=False, default='Pending') #Pending/Approved/Rejected/Closed
    remarks = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    applications = db.relationship('Application', backref='drive')
    eligible_departments = db.relationship('EligibleDepartments', backref='placement_drive', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PlacementDrive {self.job_title} by Company {self.comp_id}>'


#ELIGIBLE DEPARTMENTS MODEL
class EligibleDepartments(db.Model):
    __tablename__ = 'eligible_departments'
    
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), primary_key=True)
    dept_id = db.Column(db.String(10), db.ForeignKey('departments.dept_id'), primary_key=True)
    
    def __repr__(self):
        return f'<EligibleDepartments Drive:{self.drive_id} Dept:{self.dept_id}>'

# APPLICATION MODEL
class Application(db.Model):
    __tablename__ = 'application'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_roll = db.Column(db.String(50), db.ForeignKey('student.roll_no'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    
    application_status = db.Column(db.String(20), default='applied')
    applied_on = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    remarks = db.Column(db.String(255))
    
    __table_args__ = (
        db.UniqueConstraint('student_roll', 'drive_id', name='unique_student_drive'),
    )
    
    def __repr__(self):
        return f'<Application Student:{self.student_roll} Drive:{self.drive_id} Status:{self.application_status}>'