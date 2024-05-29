from Website import secret_key, db, Timesheet as T
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
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
    emp_id = StringField("Employee ID", validators=[DataRequired()])
    date = StringField("Date")
    Submit = SubmitField("Submit")

class ResetpasswordForm(FlaskForm):
	password = PasswordField("Password", validators=[DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired()]) 
	Submit = SubmitField("Reset Password")
      

##########################################################################################
#TIMESHEET DATA#
##########################################################################################
#CLOCK OUT DATABASE TABLE
class ClockOut(db.Model):
    __tablename__ = 'clockout'

    id = db.Column(db.Integer, primary_key=True)
    Vehicle_2 = db.Column(db.String(150), nullable=True)
    Clock_Out = db.Column(db.DateTime(timezone=T.timezone_obj),nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    in_id = db.Column(db.String(150), db.ForeignKey('clockin.out_id'), unique=True)
    clock_in = db.relationship('ClockIn', backref='clockout', uselist=False, foreign_keys=[in_id], post_update=True)
    def __repr__(self):
        return '{}, {}'.format(self.Vehicle_2, self.Clock_Out)
#CLOCK IN DATABASE TABLE
class ClockIn(db.Model):
    __tablename__ = "clockin"

    id = db.Column(db.Integer, primary_key=True)
    Employee = db.Column(db.String(150))
    Date = db.Column(db.String(20))
    Description = db.Column(db.String(150))
    Vehicle = db.Column(db.String(150))
    Runs = db.Column(db.Integer)
    Location = db.Column(db.String(150))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    out_id = db.Column(db.String, db.ForeignKey('clockout.in_id'), unique=True)
   
    clock_out = db.relationship('ClockOut', backref='clockin', uselist=False, foreign_keys=[out_id], post_update=True)
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
    phone_number = db.Column(db.Integer)
    password = db.Column(db.String(150))
    roles = db.Column(db.String(50))
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    Emp_id = db.Column(db.String(5))
    active = db.Column(db.Boolean, default=False)
    data = db.relationship('ClockIn', backref='user', lazy=True)

    def get_token(self):
        serial = Serializer(secret_key=secret_key)
        return serial.dumps({'user_id': self.id})
        
    @staticmethod
    def verify_token(token,expires_sec=300):
        serial = Serializer(secret_key=secret_key)
        try:
            user_id = serial.loads(s=token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)