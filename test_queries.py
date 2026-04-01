from create_db import app
from models import Department, Admin

with app.app_context():
    all_depts = Department.query.all()
    
    for dept in all_depts:
        print(f"{dept.dept_id} : Name : {dept.dept_name}")
    
    admin_user = Admin.query.first()

    if admin_user:
        print(f"Username : {admin_user.username}")
        print(f"Email : {admin_user.email}")
        print(f"Password Hash : {admin_user.password_hash}")
    else:
        print("No admin found.")