from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, session, send_file, abort
from jinja2 import Environment
from Website import models
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import pandas as pd
import xlwings as xw
from Website import Timesheet as T
from flask_wtf import FlaskForm
from wtforms import SearchField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import  SQLAlchemy
import datetime
import numpy as np

views = Blueprint('views',__name__)



@views.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@views.route("/Profile", methods=['GET', 'POST'])
def profile():
    usr = current_user.id
    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    Hours = current_user.Emp_id
    Emp_id = str(Hours)
    search = T.Search(EmpName_=Emp_id)
    return render_template("profile.html",user=usr, field=field,search=search)


@views.route("/Cancel", methods=['Get'])
def Cancel():
   menu = T.main()
   return render_template("input_form.html",menu=menu)

#Clockin/Clockout Card pages
@views.route("/Card", methods=["GET","POST"])
def Card():
    return render_template("card.html")
@views.route("/Card2", methods=["GET","POST"])
def Card2():
    return render_template("card2.html")

#For searching records pages
@views.route("/Card3", methods=["GET", "POST"])
def card3():
    return render_template("card3.html")


@views.route("/Clock-IN", methods=["GET","POST"])
def Clock_in():
    Employee = None
    id = current_user.id
    form = models.UserForm()
    now = datetime.datetime.now()
    Time_IN = now.strftime("%H:%M")

    if form.validate_on_submit():
        user = models.User.query.filter_by(id=current_user.id).first()
        if user is None:
            user = models.Clock_in(Employee=form.Employee.data, Description=form.Description.data , Vehicle=form.Vehicle.data, Runs=form.Runs.data, Location=form.Location.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.sign_up'))
        
        FormName = form.Employee.data
        FormDes = form.Description.data
        FormVeh = form.Vehicle.data
        FormRuns = form.Runs.data
        FormArea = form.Location.data
        Fn= str(FormName)
        Fd= str(FormDes)
        Fv= str(FormVeh)
        Fr=str(FormRuns)
        Fa=str(FormArea)
        Add = T.Add(Fn,Fd,Fv,Fr,Fa)

        Emp_ID = FormName.upper()
        Emp_Des = FormDes.upper()
        Emp_Veh = FormVeh.upper()
        Emp_Runs = FormRuns.upper()
        Emp_Area = FormArea.upper()
        data_in = models.ClockIn(Employee=Emp_ID,Date=now,Description=Emp_Des , Vehicle=Emp_Veh, Runs=Emp_Runs, Location=Emp_Area, user_id=current_user.id)
        data_out = models.ClockOut(Vehicle_2='', Clock_Out=now, user_id=current_user.id)
        if request.method == "POST":
            user = models.User.query.filter_by(id=id).first()
            if len(Fn) == 0 or Fd == '' or len(Fv) == 0 or Fr == '' or len(Fa) == 0:
                flash('Please do Not leave section Blank.', category='error')

            elif id == range(1,6):
                time_log = data_in
                db.session.add(time_log)
                db.session.add(data_out)
                db.session.commit()
                flash('Congratulations you are Clocked In!')
                return render_template("card.html",user=current_user.id, Employee=Emp_ID, Time_IN=Time_IN, Description=Emp_Des , Vehicle=Emp_Veh, Runs=Emp_Runs, Location=Emp_Area)
            else:
                time_log = data_in
                db.session.add(time_log)
                db.session.add(data_out)
                db.session.commit()
                flash('Congratulations you are Clocked In!')
                return render_template("card.html",user=current_user.id, Employee=Emp_ID, Time_IN=Time_IN, Description=Emp_Des , Vehicle=Emp_Veh, Runs=Emp_Runs, Location=Emp_Area)
            
            
            form.Employee.data = ''
            form.Description.data = ''
            form.Vehicle.data = ''
            form.Runs.data = ''
            form.Location.data = ''
            return render_template('input_form.html',Add=Add,user=current_user.id)
        
    return render_template("input_form.html",form=form,Employee=Employee,user=current_user)


@views.route("/Clock-Out", methods=["GET","POST"])
def Clock_Out():
    usr = current_user.id
    form = models.ClockoutForm()
    now = datetime.datetime.now()
    Time_OUT = now.strftime("%H:%M")

    if form.validate_on_submit():
        user = models.User.query.filter_by(id=usr).first()
        if user is None:
            return redirect(url_for('auth.sign_up'))
        
        FormName = form.Employee.data
        FormVeh = form.Vehicle.data
        Fn= str(FormName)
        Fv= str(FormVeh)
        out = T.Clock_out(Fv,Fn)

        Emp_Name = FormName.upper()
        Emp_Veh = FormVeh.upper()

        in_id = db.session.query(models.ClockIn).filter(models.ClockIn.user_id == usr).order_by(models.ClockIn.Date.desc()).first()
        out_id = db.session.query(models.ClockOut).filter(models.ClockOut.user_id == usr).order_by(models.ClockOut.Clock_Out.desc()).first()
        

        if Emp_Name != current_user.Emp_id:
            flash('Incorrect Employee ID', category='error')
        elif usr in range(1,6):####add more admins   
            if out_id and in_id is not None:
                in_id.out_id = out_id.id
                out_id.in_id = in_id.id
                out_id.Clock_Out = now
                out_id.Vehicle_2 = Fv
                db.session.flush()
            else:
                out_id = out_id.id
                update = db.session.query(models.ClockIn).filter_by(user_id=usr).update({models.ClockIn.out_id: out_id}).first()            
                in_id = in_id.id
                update2 = db.session.query(models.ClockOut).filter_by(user_id=usr).update({models.ClockOut.in_id: in_id, models.ClockOut.Clock_Out: now, models.ClockOut.Vehicle_2: Fv}).first()
                db.session.execute(update,update2)
                out_id.Clock_Out = now
                out_id.Vehicle_2 = Fv
            db.session.commit()
            flash('Congratulations you are Clocked OUT!')
            return render_template("card2.html",user=usr, Employee=Emp_Name, Time_OUT=Time_OUT,Vehicle=Emp_Veh)
        else:
            if out_id and in_id is not None:
                in_id.out_id = out_id.id
                out_id.in_id = in_id.id
                out_id.Clock_Out = now
                out_id.Vehicle_2 = Fv
            else:
                out_id = out_id.id
                update = db.session.query(models.ClockIn).filter_by(user_id=usr).update({models.ClockIn.out_id: out_id}).first()            
                in_id = in_id.id
                update2 = db.session.query(models.ClockOut).filter_by(user_id=usr).update({models.ClockOut.in_id: in_id, models.ClockOut.Clock_Out: now, models.ClockOut.Vehicle_2: Fv}).first()
                db.session.execute(update,update2)
                out_id.Clock_Out = now
                out_id.Vehicle_2 = Fv
            db.session.commit()
            flash('Congratulations you are Clocked OUT!')
            return render_template("card2.html",user=usr, Employee=Emp_Name, Time_OUT=Time_OUT,Vehicle=Emp_Veh)
        form.Employee.data = ''
        form.Vehicle.data = ''
        return render_template("Clock_Out_form.html",out=out,form=form,user=usr)
    return render_template("Clock_Out_form.html",form=form,user=current_user.id)


@login_required
@views.route("/ViewHours", methods=["GET", "POST"])
def ViewHours():
    usr = current_user.id
    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    Hours = current_user.Emp_id
    Emp_id = str(Hours)
    search = T.Search(EmpName_=Emp_id)
    return render_template("ViewHours.html",user=usr, field=field,search=search)

@views.route("/search", methods=["GET", "POST"])
@login_required
def find():
    form = models.SearchForm()
    usr = current_user.id
    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    search_results = []  # Initialize the variable with an empty list
    if form.validate_on_submit():
        form_name = form.searched.data
        search_results = T.Search(form_name) 
        return render_template("card3.html", user=usr, field=field, form=form, search=search_results)
    return render_template("Search_template.html", form=form, user=usr)


@login_required
@views.route("/Delete", methods=["GET", "POST"])
def Delete():
    form = models.DeleteForm()
    usr = current_user.id

    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    
    found_records = []  # Initialize the variable with an empty list
    remaining_records = []

    if form.validate_on_submit():
            Emp_ID = form.Emp_ID.data
            Date = form.Date.data
            session["Emp_ID"] = Emp_ID
            session["Date"] = Date
            found_records, remaining_records, deletion_successful, message = T.Delete(Emp_ID, Date, False)
            return render_template("confirm_deletion.html", user=usr, field=field, form=form,
                           found_records=found_records, 
                           remaining_records=remaining_records, 
                           deletion_successful=deletion_successful,
                           message=message)
    return render_template("Delete_P_template.html",user=usr, field=field, form=form)

def resultToDict(result):
    ds = []
    for rows in result:
        d = {}
        for row in rows:
            for col in row.__table__.columns:
                d[col.name] = str(getattr(row, col.name))
        ds.append(d)
    return ds

@views.route("/confirm_deletion", methods=["GET", "POST"])
def confirm_deletion():
    usr = current_user.id
    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    form = models.DeleteForm()
    remaining_records = []  # Initialize as an empty list
    deletion_successful = False
    confirmation_message = ''
    if form.validate_on_submit():
        emp_name = form.Emp_ID.data
        date = form.Date.data
        found_records, remaining_records, deletion_successful, confirmation_message = T.Delete(emp_name, date, True)

        if deletion_successful:
            flash(confirmation_message, category='confirmation')
        else:
            flash(confirmation_message, category='error')

    return render_template("confirm_deletion.html", form=form, remaining_records=remaining_records, found_records=found_records,user=usr, field=field)
#build databbase delete function


@login_required
@views.route("/Report")
def time_report():
        workbook_path = T.Time_Card
        df = pd.read_csv(workbook_path)

        df_cleaned = df.replace([''], [np.nan])
        df_filled = df_cleaned.fillna('Error')

        try:
            return render_template("Report_P_template.html",user=current_user, df_filled=df_filled)

        except FileNotFoundError:
            abort(404)  # File not found
        except IOError:
            abort(500)  # Error reading the file



@login_required
@views.route("/Edit", methods=["GET", "POST"])
def Edit():
    form = models.DeleteForm()
    usr = current_user.id
    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    remaining_records = []
    found_records = []
    if form.validate_on_submit():
        emp_id = form.Emp_ID.data
        date = form.Date.data
        session["Emp_ID"] = emp_id
        session["Date"] = date
        remaining_records, found_records = T.Edit(emp_id,date)
        session["remaining_records"] = remaining_records
        session["found_records"] = found_records
        return redirect(url_for('views.confirm_update'))
    return render_template("Edit_P_Template.html", user=usr, field=field, form=form)

@views.route("/confirm_update", methods=["GET","POST"])
def confirm_update():
    usr = current_user.id
    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    form = models.EditForm()

#initialize variables
    remaining_records = []
    found_records = []
    deletion_successful = False
    confirmation_message = ''
    found_records = session.get('found_records', [])
    remaining_records = session.get('remaining_records', [])
   #found_records = [item for sublist in found_records for item in sublist]
    #remaining_records = [item for sublist in remaining_records for item in sublist]

    if form.validate_on_submit():
        emp_name = form.Employee.data.upper()
        date = form.Date.data.upper()
        des = form.Description.data.upper()
        veh = form.Vehicle.data.upper()
        runs = form.Runs.data.upper()
        location = form.Location.data.upper()
        clock_in = form.Clock_in.data.upper()
        veh2 = form.Veh2.data.upper()
        clock_out = form.Clock_out.data.upper()

        remaining_records, found_records, deletion_successful, confirmation_message = T.update_records(emp_name,date,des,veh,runs,location,clock_in,veh2,clock_out,True)

        if deletion_successful:
            flash(confirmation_message, category='confirmation')
        else:
            flash(confirmation_message, category='error')

        return render_template("confirm_update.html",form=form,
                                remaining_records=remaining_records,found_records=found_records,user=usr, field=field)

    return render_template("confirm_update.html",user=current_user, form=form, remaining_records=remaining_records,found_records=found_records,feild=field)


# Create Custom Error Pages
# Invalid URL
@views.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal Server Error
@views.errorhandler(500)
def page_not_found2(e):
	return render_template("500.html"), 500