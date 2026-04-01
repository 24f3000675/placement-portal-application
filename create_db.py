import os
from flask import Flask

from models import db, Admin, Department, Student, Skills, Company, PlacementDrive, EligibleDepartments, Application

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'placement.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def seed_departments():
    with app.app_context():
        db.create_all()

        if not Department.query.first():            
            default_departments = [
                Department(dept_id='CS', dept_name='Computer Science and Engineering'),
                Department(dept_id='EC', dept_name='Electronics and Communication Engineering'),
                Department(dept_id='EE', dept_name='Electrical and Electonics Engineering'),
                Department(dept_id='ME', dept_name='Mechanical Engineering'),
                Department(dept_id='CH', dept_name='Chemical Engineering'),
                Department(dept_id='CV', dept_name='Civil Engineering')
            ]
            
            db.session.add_all(default_departments)
            db.session.commit()
            print("Depts added to DB")
        else:
            print("Depts already exist in the DB.")

        admin_email = "admin@placement.com"
        if not Admin.query.filter_by(email=admin_email).first():            
            default_admin = Admin(
                email=admin_email,
                username="Placement_Admin"
            )
            default_admin.set_password("admin123") 
            
            db.session.add(default_admin)
            db.session.commit()
            print("Admin Created")
        else:
            print("Admin already exists in DB")

if __name__ == '__main__':
    seed_departments()