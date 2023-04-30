from flask import Blueprint, render_template,redirect, url_for, request, jsonify, flash, session
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
import json
from sqlalchemy import update, text



views = Blueprint('views',__name__)


@views.route("/")
def home():
    if id == 1:
        flash('admin',category='success')
        return render_template('home.html',user=current_user.id)
    else:
        return render_template('index.html',user=current_user)


@login_required
@views.route("/Admin", methods=['GET', 'POST'])
def index():
    id = current_user.id
    if id == 1:
        flash('admin',category='success')
        return render_template('home.html',user=current_user.id)
    else:
        flash('user',category='success')
        return redirect(url_for('views.home'))


@views.route("/Cancel", methods=['Get'])
def Cancel():
   menu = T.main()
   return render_template("input_form.html",menu=menu)

@views.route("/Card", methods=(["GET","POST"]))
def Card():
    return render_template("card.html")
@views.route("/Card2", methods=(["GET","POST"]))
def Card2():
    return render_template("card2.html")

@login_required
@views.route("/Search", methods=(["GET","POST"]))
def Search():
   return render_template("Search_template.html",user=current_user)


@views.route("/Clock-IN", methods=(["GET","POST"]))
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
        

        if len(Fn) != current_user.Emp_id:
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
        return render_template("Clock_Out_form.html",out=out,user=usr)
    return render_template("Clock_Out_form.html",form=form,user=current_user.id)


@views.route("/Sub_search", methods=(["GET","POST"]))
def Find():
   FormName = request.form.get("EmpName_")
   Fn = str(FormName)
   Search = T.Search(Fn)
   x = print('TimeCard')

#  Employee = Timecard(name=Fn, Vehicle2=Fv, Time_OUT=Time_OUT)
#            db.session.add(Employee)
#            db.session.commit()
#  delete?   login_user(Employee, remember=True)

   if request.method == "POST":
      return redirect(url_for("views.Searchdata"))
   return render_template("Search_template.html",Search=Search, x=x,user=current_user)


@views.route("/Delete")
def Delete():
   #T.Delete()
   return render_template("Delete_P_template.html",user=current_user)

@login_required
@views.route("/Report")
def TimeReport():
   #T.TimeReport()
   return render_template("Report_P_Template.html",user=current_user)

@login_required
@views.route("/Edit")
def Edit():
   #T.Edit()
   return render_template("Edit_P_Template.html",user=current_user)


# Create Custom Error Pages
# Invalid URL
@views.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal Server Error
@views.errorhandler(500)
def page_not_found2(e):
	return render_template("500.html"), 500