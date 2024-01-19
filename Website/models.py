from Website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from wtforms import SearchField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import  SQLAlchemy
from datetime import datetime


###########################################################################################
#FORMS#
##########################################################################################
class UserForm(FlaskForm):
    Employee = StringField("EmpName", validators=[DataRequired()])
    Description = StringField("EmpDes", validators=[DataRequired()])
    Vehicle = StringField("EmpVeh", validators=[DataRequired()])
    Runs = StringField("EmpRuns", validators=[DataRequired()])
    Location = StringField("EmpArea", validators=[DataRequired()])
    submit = SubmitField("Submit")

class EditForm(FlaskForm):
    Employee = StringField("EmpName", validators=[DataRequired()])
    Date = StringField("Date YYYY/mm/dd", validators=[DataRequired()])
    Description = StringField("EmpDes", validators=[DataRequired()])
    Vehicle = StringField("EmpVeh", validators=[DataRequired()])
    Runs = StringField("EmpRuns", validators=[DataRequired()])
    Location = StringField("EmpArea", validators=[DataRequired()])
    Clock_in = StringField("Clock In Time", validators=[DataRequired()])
    Veh2 = StringField("EmpVeh2")
    Clock_out = StringField("Clock out Time")

    Submit = SubmitField("Submit")


class ClockoutForm(FlaskForm):
    Employee = StringField("EmpName", validators=[DataRequired()])
    Vehicle = StringField("EmpVeh", validators=[DataRequired()])
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
	searched = StringField("Searched", validators=[DataRequired()])
	Submit = SubmitField("Submit")
        
class DeleteForm(FlaskForm):
    Emp_ID = StringField("Employee ID", validators=[DataRequired()])
    Date = StringField("Date", validators=[DataRequired()])
    Submit = SubmitField("Submit")

        

##########################################################################################
#TIMESHEET DATA#
##########################################################################################
#CLOCK OUT DATABASE TABLE
class ClockOut(db.Model):
    __tablename__ = 'clockout'

    id = db.Column(db.Integer, primary_key=True)
    Vehicle_2 = db.Column(db.String(150), nullable=True)
    Clock_Out = db.Column(db.DateTime(timezone=True),default=func.now(),nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    in_id = db.Column(db.Integer, db.ForeignKey('clockin.id'), unique=True)
    clock_in = db.relationship('ClockIn', backref='clockout', uselist=False, foreign_keys=[in_id])
    def __repr__(self):
        return '{}, {}'.format(self.Vehicle_2, self.Clock_Out)
#CLOCK IN DATABASE TABLE
class ClockIn(db.Model):
    __tablename__ = "clockin"

    id = db.Column(db.Integer, primary_key=True)
    Employee = db.Column(db.String(150))
    Date = db.Column(db.DateTime(timezone=True),default=func.now())
    Description = db.Column(db.String(150))
    Vehicle = db.Column(db.String(150))
    Runs = db.Column(db.Integer)
    Location = db.Column(db.String(150))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    out_id = db.Column(db.Integer, db.ForeignKey('clockout.id'), unique=True)
   
    clock_out = db.relationship('ClockOut', backref='clockin', uselist=False, foreign_keys=[out_id])
    def __repr__(self):
        return '{}, {},{}, {},{}, {}'.format(self.Employee, self.Date, self.Description,self.Vehicle,self.Runs,self.Location)

##########################################################################################
#EMPLOYEE DATABASE#
###########################################################################################class Employee_id(db.Model):
#    id = db.Column(db.Integer, primary_key=True, db.ForeignKey('user.id' )
#    data_in = db.relationship('Data')
#Create A String
#    def __repr__(self):
#        return '{} {}'.format(self.Vehicle_2, self.Clock_Out)

##########################################################################################
#ACCOUNT DATABASE#
##########################################################################################   
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    roles = db.Column(db.String(50))
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    Emp_id = db.Column(db.String(5))
    data = db.relationship('ClockIn', backref='user', lazy=True)
