import logging
from flask import Blueprint, render_template,request,flash,redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, send_grid
from flask_login import login_user, login_required, logout_user, current_user
import random
from Website import Timesheet as T, models
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
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

def verify(user,ph,Fn,ln,Fp,password1,password2):
    message = []
    if user:
        message.append('Email already exists. please login or contact support')
    elif len(Fn) < 2:
        message.append('First Name must be greater then 2 characters.')
    elif len(ln) < 2:
        message.append('Last Name must be greater then 2 characters.')
    elif len(Fp) < 7:
        message.append('password must be at least 7 characters')
    elif len(ph) < 10:
        message.append('Phone Number invalid. must match (xxx)xxx-xxxx')
    elif password1 != password2:
        message.append('Passwords do not match.')
    
    if len(message) > 1:
        return message, False
    else:
        return message, True
@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        ph = str(request.form.get('phone_number'))
        Fe = str(request.form.get('email')).lower()
        Fn = str(request.form.get('first_name')).upper()
        ln = str(request.form.get('last_name')).upper()
        Fp = str(password1)
        
        user = User.query.filter_by(email=Fe).first()
        message, check= verify(user,ph,Fn,ln,Fp,password1,password2)

        if check == True:
            try:
                emp_id = generate_employee_code(Fn,ln)
                new_user = User(email=Fe,phone_number=ph, roles=Admin, Emp_id=emp_id,FirstName=Fn, LastName=ln,password=generate_password_hash(Fp, method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash(f'Account Created! your Empoyee ID is: ({emp_id}) please Keep this code accessible you will need it to Clock in![view your profile to see your Employee ID]', category='success')
                
                #add to workbook
                #data = [emp_id,Fn,ln]
                #T.write_to_last_row(data)
                return redirect(url_for('views.index'))
            except Exception as e:
                flash('Error creating account', category='error')
                logging.error(e)
                return redirect(url_for('auth.sign_up'))    
        else:
            for element in message:
                flash(element, category='error')
            return redirect(url_for('auth.sign_up'))    
    return render_template("sign_up.html",user=current_user)

def send_mail(user):
    token = user.get_token()
    message = Mail(
    from_email='no-reply@rmspope.com',
    to_emails=[user.email],
    subject='Password Reset Request',
    html_content=f''' To Reset your Password please click the link below: \n\t
    
    {url_for('auth.reset_password', token=token, _external=True)} \n\n\n
    
    If you did not make this request, please ignore this email and no changes will be made.
    ''')
    
    try:
        sg = SendGridAPIClient(send_grid)
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(e)

@auth.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    form = models.SearchForm()
    email = form.searched.data
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=email).first()
        if user:
            send_mail(user)
            flash(f'Reset Link has been sent to: {email}', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email does not exist.', category='error')
    return render_template("Reset_request.html",form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_token(token)
    if user is None:
        flash('link is invalid or expired. Please try again.', category='warning')
        return redirect(url_for('auth.reset_request'))
    form = models.ResetpasswordForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match.', category='error')
        else:
            Fp = form.confirm_password.data
            User.password = generate_password_hash(Fp, method='sha256')
            db.session.commit()
            flash('Password Updated!', category='success')
            return redirect(url_for('auth.login'))
    return render_template("reset_password.html", form=form,token=token)
