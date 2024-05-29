import logging
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, session, abort
from Website import models
from Website import Timesheet as T
from . import db   
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
from datetime import datetime
views = Blueprint(name='views',import_name=__name__)

@views.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')
@views.route("/Admin", methods=["GET","POST"])
def Admin():
    return render_template("Admin.html")
@login_required
@views.route("/Profile", methods=['GET', 'POST'])
def profile():
    code = False
    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    Emp_id = session.get('Emp_id')
    search = []
    total_hours = 0
    user=None
    if Emp_id is not None:
        for x in Emp_id[0]:
            if x.isdigit():
                code = True
                break

    if Emp_id is None:
        user = current_user
        Emp_id = str(user.Emp_id)
    elif len(Emp_id[0]) == 4 and code is True:
        _search = models.User.query.filter_by(Emp_id=Emp_id[0]).first()
        if _search is not None:
            Emp_id = str(_search.Emp_id)
            user = _search
        else:
            session.clear()
            flash('Employee ID not found', category='error')
            return redirect(url_for('views.employee_directory'))
    elif code is False:
        Firstname = Emp_id[0]
        Lastname = Emp_id[-1]
        search1 = models.User.query.filter_by(FirstName=Firstname,LastName=Lastname).first()
        search2 = models.User.query.filter_by(FirstName=Firstname).first()
        search3 = models.User.query.filter_by(LastName=Lastname).first()
        if search1 is not None:
            Emp_id = str(search1.Emp_id)
            user = search1
        elif search2 is not None:
            Emp_id = str(search2.Emp_id)
            user = search2
        elif search3 is not None:
            Emp_id = str(search3.Emp_id)
            user = search3
        else:
            session.clear()
            flash('Employee not found', category='error')
            return redirect(url_for('views.employee_directory'))
    try:
        search, total_hours = T.Search(EmpName_=Emp_id)
    except Exception as e:
        flash(str(e), category='error')
        logging.error(e)
        return redirect(url_for('views.employee_directory'))
    session.pop('Emp_id', None)
    session['view'] = Emp_id
    df = pd.DataFrame(search, columns=field)
    df_cleaned = df.replace([''], [np.nan])
    df_filled = df_cleaned.fillna('Error')
    return render_template("profile.html", user=user, field=field, df_filled=df_filled, total_hours=total_hours)
#add sms to phone number link in profile?
#add unique employee id to profile link i.e. profile/<user> -check pinned tabs(prettyprinted video)
@views.route("/Edit_Profile", methods=['GET', 'POST'])
def Edit_Profile():
    user = current_user
    if request.method == 'POST':
        user = current_user
        user.FirstName = request.form.get('first_name')
        user.LastName = request.form.get('last_name')
        user.Email = request.form.get('email')
        user.PhoneNumber = request.form.get('phone_number')
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('views.profile'))
    return render_template('edit_profile.html', user=user)

#Clockin/Clockout Card pages
@views.route("/Card", methods=["GET","POST"])
def Card():
    return render_template("card.html")
@views.route("/Card2", methods=["GET","POST"])
def Card2():
    return render_template("card2.html")

def generate_employee_code(user,date):
    code = date.strip().replace('/','').replace(':','').replace(' ','')
    code = code.strip()
    out_id = f'{code}{user.Emp_id}{user.id}'
    return out_id
@views.route("/Clock-IN", methods=["GET","POST"])
def Clock_in():
    form = models.UserForm()
    Time_IN = T.now.strftime("%H:%M")
    date = T.now.strftime("%Y/%m/%d %H:%M")
    Time_OUT = datetime.strptime(date, '%Y/%m/%d %H:%M')
    if form.validate_on_submit():
        Fn= str(form.Employee.data).upper()
        Fd= str(form.Description.data).upper()
        Fv= str(form.Vehicle.data).upper()
        Fr=str(form.Runs.data).upper()
        Fa=str(form.Location.data).upper()
        
        user = models.User.query.filter_by(id=current_user.id).first()
        if user is None:
            flash('User not found', category='error')
            return redirect(url_for('auth.sign_up'))
        elif Fn != current_user.Emp_id:
            flash('Incorrect Employee ID', category='error')
            return render_template("input_form.html",form=form,user=current_user)
        
        
        out_id = generate_employee_code(user,date)
        T.Add(Fn,Fd,Fv,Fr,Fa)
        data_in = models.ClockIn(Employee=Fn,Date=date,Description=Fd , Vehicle=Fv, Runs=Fr, Location=Fa, user_id=current_user.id,out_id=out_id)
        data_out = models.ClockOut(Clock_Out=Time_OUT, user_id=current_user.id, in_id=out_id)
        
        user.active = True
        db.session.add(data_in)
        db.session.add(data_out)
        db.session.commit()
        flash('Congratulations you are Clocked In!')
        try:
            return render_template("card.html", Employee=Fn, Time_IN=Time_IN, Description=Fd , Vehicle=Fv, Runs=Fr, Location=Fa)
        except FileNotFoundError:
            abort(404)  # File not found
        except Exception as e:
            abort(500, description=str(e))
    try:
        return render_template("input_form.html",form=form,user=current_user)
    except Exception as e:
        abort(500, description=str(e))

@views.route("/Clock-Out", methods=["GET","POST"])
def Clock_Out():
    form = models.ClockoutForm()
    date = T.now.strftime("%Y/%m/%d %H:%M")
    time_out = datetime.strptime(date, '%Y/%m/%d %H:%M')

    if form.validate_on_submit():
        user = models.User.query.filter_by(id=current_user.id).first()
        if user is None:
            flash('User not found', category='error')
            return redirect(url_for('auth.sign_up'))

        emp_name= str(form.Employee.data).upper()
        emp_veh= str(form.Vehicle.data).upper()
        message = T.Clock_out(EmpVeh_=emp_veh,EmpName_=emp_name)
        
        if emp_name != user.Emp_id:
            flash('Incorrect Employee ID', category='error')
            return render_template("Clock_Out_form.html",form=form)

        clock_in_record = models.ClockIn.query.filter_by(user_id=user.id).order_by(models.ClockIn.Date.desc()).first()
        if clock_in_record is None:
            flash('No clock in record found', category='error')
            return redirect(url_for('views.Clock_in'))

        clock_out_record = models.ClockOut.query.filter_by(in_id=clock_in_record.out_id).first()
        if clock_out_record is None:
            flash('No clock out record found', category='error')
            return render_template("Clock_Out_form.html", form=form)

        if message[0]:
            if clock_out_record.Vehicle_2 is None and user.active == True:
                clock_out_record.Clock_Out = time_out
                clock_out_record.Vehicle_2 = emp_veh
                user.active = False
                db.session.commit()
                flash(message[1], 'success')
            else:
                flash('You are Already Clocked out. Please Clock in to Start logging your hours.', category='error')
                return redirect(url_for('views.Clock_in'))
            return render_template("card2.html", Employee=emp_name, Time_OUT=time_out,Vehicle=emp_veh)
        else:
            flash(message[1], category='error')
            return redirect(url_for('views.index'))
    try:   
        return render_template("Clock_Out_form.html",form=form)
    except Exception as e:
        abort(500, description=str(e))

#check and review remaining open functions
# - check/test edit
@login_required
@views.route("/ViewHours", methods=["GET", "POST"])
def ViewHours():
    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    Emp_id = session.get('view')
    if Emp_id is None:
        user = current_user
        Emp_id = str(user.Emp_id)
    else:
        user = models.User.query.filter_by(Emp_id=Emp_id).first()

    if user is None:
        abort(404, description="User not found")
    
    try:
        search, total_hours = T.Search(EmpName_=Emp_id)
    except Exception as e:
        abort(500, description=str(e))
        
    session.pop('view', None)
    df = pd.DataFrame(search, columns=field)
    df_cleaned = df.replace([''], [np.nan])
    df_filled = df_cleaned.fillna('Error')
    try:
        return render_template("ViewHours.html",user=user, field=field,df_filled=df_filled,total_hours=total_hours)
    except Exception as e:
        abort(500, description=str(e))

@login_required
@views.route("/Delete", methods=["GET", "POST"])
def delete():
    try:
        form = models.DeleteForm()
        if form.validate_on_submit():
            emp_id = form.emp_id.data
            date = form.date.data
            try:
                found_records, remaining_records, deletion_successful, message = T.Delete(emp_id, date, False)
            except ValueError:
                flash('An error occurred while deleting the record.', 'error')
                return render_template("Delete_P_template.html", form=form)

            return render_template("confirm_deletion.html", 
                                form=form,
                                found_records=found_records, 
                                remaining_records=remaining_records, 
                                deletion_successful=deletion_successful,
                                message=message)
        return render_template("Delete_P_template.html", form=form)
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        abort(500)  # Error reading the file
@views.route("/confirm_deletion", methods=["GET", "POST"])
def confirm_deletion():
    #Initialize variables
    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    form = models.DeleteForm()
    found_records = []
    remaining_records = []  
    deletion_successful = False
    confirmation_message = ''
    
    if form.validate_on_submit():
        emp_name = str(form.emp_id.data).upper()
        date = str(form.date.data)
        try:
            found_records, remaining_records, deletion_successful, confirmation_message = T.Delete(emp_name, date, True)         
            update_database(emp_name,date)
        except Exception as e:
            logging.error(f"An error occurred while reading the file: {e}")
            return render_template("confirm_deletion.html", form=form, remaining_records=remaining_records, found_records=found_records)
        
        if deletion_successful:
            flash(confirmation_message, category='confirmation')
        else:
            flash(confirmation_message, category='error')
            return redirect(url_for('views.confirm_deletion'))
        return redirect(url_for('views.time_report'))
    try:
        return render_template("confirm_deletion.html", form=form, remaining_records=remaining_records, found_records=found_records, field=field)
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        abort(500)  # Error reading the file
def update_database(emp_name, date):
    try:
        if date == 'delete':
            T.delete_all_records(emp_name)
        else:
            T.delete_records_by_date(emp_name, date)
        db.session.commit()
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        abort(500)  
@login_required
@views.route("/Report")
def time_report():
        workbook_path = T.Time_Card
        try:
            df = pd.read_csv(workbook_path)
        except ValueError:
            T.check_columns()
        except FileNotFoundError:
            print(f"File not found: {workbook_path}. Please ensure the file exists and the path is correct.")

        now = datetime.now(T.timezone_obj)
        Current_day  = now.strftime(" %Y/%m/%d")
        
        df = df.replace([''], [np.nan])
        df_cleaned = df.replace([' '], [np.nan])
        df_filled = df_cleaned.fillna('Error')
        df_errors = df_filled[df_filled.eq('Error').any(axis=1)]
        
        mask = df_errors[' Date'] == Current_day
        df_errors.loc[mask, ' Clock_Out'] = '00:00 Clocked -IN'       
        try:
            return render_template("Report_P_template.html",user=current_user, df_filled=df_filled, df_errors=df_errors)
        except FileNotFoundError:
            abort(404)  # File not found
        except Exception as e:
            logging.error(e)
            abort(500)  # Error reading the file
#add function for report to total working hours for each individual,
#as a whole and if employees can be grouped by rates then total $
# -> excel/printable
@login_required
@views.route("/Edit", methods=["GET", "POST"])
def Edit():
    form = models.DeleteForm()
    usr = current_user.id
    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    form_errors = None
    if form.validate_on_submit():
        emp_id = str(form.emp_id.data).upper()
        date = str(form.date.data)
        session["Emp_ID"] = emp_id
        session["Date"] = date
        try:
            remaining_records, found_records = T.Edit(emp_id,date)
            session["remaining_records"] = remaining_records[-10:]
            session["found_records"] = found_records[-10:]
            return redirect(url_for('views.confirm_update'))
        except Exception as e:
            form_errors = str(e)
    try:
        return render_template("Edit_P_Template.html", user=usr, field=field, form=form, form_errors=form_errors)
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        abort(500)  # Error reading the file
@views.route("/confirm_update", methods=["GET","POST"])
def confirm_update():
    field = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']
    form = models.EditForm()
    form_errors = None
    remaining_records = session.get('remaining_records', [])
    found_records = session.get('found_records', [])
    
    date_to_change = session.get('Date')
    emp_to_change = session.get('Emp_ID')

    try:
        user = models.User.query.filter_by(Emp_id=emp_to_change).first()
        if form.validate_on_submit():
            employee_name = str(form.Employee.data).upper()
            date = str(form.Date.data).upper()
            description = str(form.Description.data).upper()
            vehicle = str(form.Vehicle.data).upper()
            runs = str(form.Runs.data).upper()
            location = str(form.Location.data).upper()
            clock_in = str(form.Clock_in.data).upper()
            vehicle_2 = str(form.Veh2.data).upper()
            clock_out = str(form.Clock_out.data).upper()
            if user is None:
                user = employee_name
            if clock_out:
                dateify = f'{date} {clock_out}'
            else:
                dateify = f'{date} {clock_in}'
            date_dt = datetime.strptime(dateify, '%Y/%m/%d %H:%M')
            date_str = f'{date} {clock_in}'
        
            if date_to_change and emp_to_change:
                date_query_arg = T.get_date(emp_to_change, date_to_change)
            else:
                date_query_arg = T.get_date(employee_name, date)
            remaining_records, found_records, deletion_successful, confirmation_message = T.update_records(employee_name, date, description, vehicle, runs, location, clock_in, vehicle_2, clock_out, True)
            #delete db record
            delete = db.session.query(models.ClockIn).filter(models.ClockIn.Employee == user.Emp_id, models.ClockIn.Date == date_query_arg).order_by(models.ClockIn.Date.desc()).first()
            if delete is None:
                flash('No clock in record found', category='error')
                return render_template("confirm_update.html", form=form, remaining_records=remaining_records,found_records=found_records,field=field, form_errors=form_errors)
            delete_out = db.session.query(models.ClockOut).filter(models.ClockOut.user_id == user.id, models.ClockOut.in_id == delete.out_id).order_by(models.ClockOut.Clock_Out.desc()).first()
            if delete_out is None:
                flash('No clock out record found', category='error')
                return render_template("confirm_update.html", form=form, remaining_records=remaining_records,found_records=found_records,field=field, form_errors=form_errors)
            db.session.delete(delete)
            db.session.delete(delete_out)
            db.session.flush()
            #add new record
            out_id = generate_employee_code(user,date_str)    
            data_in = models.ClockIn(Employee=employee_name, Date=date_str, Description=description, Vehicle=vehicle, Runs=runs, Location=location, user_id=user.id, out_id=out_id)
            data_out = models.ClockOut(Vehicle_2=vehicle_2, Clock_Out=date_dt, user_id=user.id, in_id=out_id)
            db.session.add(data_in)
            db.session.add(data_out)
            db.session.commit()
            if deletion_successful:
                session.clear()
            else:
                flash(confirmation_message, category='error')
            return redirect(url_for('views.time_report')), flash(confirmation_message, category='Success')
    except Exception as e:
        logging.error(e)
        abort(500)  # Error reading the file
    try:
        return render_template("confirm_update.html", form=form, remaining_records=remaining_records,found_records=found_records,field=field, form_errors=form_errors)
    except FileNotFoundError:
        abort(404)  #File not found
@login_required
@views.route("/Directory", methods=["GET","POST"])
def employee_directory():
    try:
        page = request.args.get('page', 1, type=int)
        if page < 1:
            flash('Invalid page number', category='error')
            return redirect(url_for('views.employee_directory'))

        per_page = 10  # change this as needed
        users = models.User.query.paginate(page=page, per_page=per_page, error_out=False)
        form = models.SearchForm()

        if form.validate_on_submit():
            emp_id = form.searched.data.split()
            emp_id = [x.strip().upper() for x in emp_id]
            session['Emp_id'] = emp_id
            return redirect(url_for('views.profile'))

        return render_template('Driver_Dir.html', form=form, users=users)
    except FileNotFoundError:
            abort(404)  # File not found
    except Exception as e:
            logging.error(e)
            abort(500)  # Error reading the file

@login_required
@views.route("/Maintenance_Schedule", methods=["GET","POST"])
def maintenance_schedule():
    try:
        return render_template("MaintenceSchedule.html")
    except FileNotFoundError:
            logging.error(e)
            abort(404)  # File not found
    except Exception as e:
            logging.error(e)
            abort(500)  # Error reading the file

@views.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404
# Internal Server Error
@views.errorhandler(500)
def page_not_found2(e):
    return render_template("500.html"), 500