from flask import Blueprint, render_template,request,flash,redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import random
import string
import xlwings as xw
from Website import Timesheet as T
from Website import models 


auth = Blueprint('auth', __name__)

def generate_employee_code(first_name, last_name):
    # Extract the first letters of the first and last names
    first_initial = first_name[0].upper()
    last_initial = last_name[0].upper()

    # Generate a random 2-digit number
    random_number = random.randint(10, 99)

    # Create the employee code by combining the initials and random number
    emp_id = f"{first_initial}{last_initial}{random_number}"

    return emp_id

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        Fp = str(password)
        user = User.query.filter_by(email=email).first()

        if user:
            if user.id == 1:
                user.roles = "Admin"
                db.session.commit()
            if check_password_hash(user.password, Fp):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('Incorrect password, try again.', category='error')   
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        Fe = str(email)
        Fn = str(first_name)
        ln = str(last_name)
        Fp = str(password1)

        user = User.query.filter_by(email=email).first()
        if user:
             flash('Email already exists.', category='error')
        elif len(Fe) < 4:
            flash('Email must be greater then 4 characters.', category='error')
        elif len(Fn) < 2:
            flash('First Name must be greater then 2 characters.', category='error')
        elif len(ln) < 2:
            flash('Last Name must be greater then 2 characters.', category='error')
        elif len(Fp) < 7:
            flash('password must be at least 7 characters', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        else:
            emp_id = generate_employee_code(Fn,ln)
            new_user = User(email=email, Emp_id=emp_id,FirstName=first_name, LastName=last_name,password=generate_password_hash(Fp, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash(f'Account Created! your Empoyee ID is: ({emp_id}) please write this code down you will need it to Clock in!')
            
            #add to workbook
            data = [emp_id,Fn,ln]
            T.write_to_last_row(data)
            return redirect(url_for('views.index'))
    return render_template("sign_up.html",user=current_user)