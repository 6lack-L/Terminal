''' This file contains the database models for the website '''
from datetime import datetime
from Website import secret_key, db
import pytz
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired
from itsdangerous import URLSafeTimedSerializer as Serializer
###############################################################################
# FORMS#
###############################################################################


class UserForm(FlaskForm):
    ''' User form '''

    Employee = StringField("EmpName", validators=[DataRequired()])
    Description = StringField("EmpDes", validators=[DataRequired()])
    Vehicle = StringField("EmpVeh", validators=[DataRequired()])
    Runs = StringField("EmpRuns", validators=[DataRequired()])
    Location = StringField("EmpArea", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EditForm(FlaskForm):
    ''' Edit form '''

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
    ''' Clock out form '''

    Employee = StringField("EmpName", validators=[DataRequired()])
    Vehicle = StringField("EmpVeh", validators=[DataRequired()])
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    ''' Search form '''

    searched = StringField("Searched", validators=[DataRequired()])
    Submit = SubmitField("Submit")


class DeleteForm(FlaskForm):
    ''' Delete form '''

    emp_id = StringField("Employee ID", validators=[DataRequired()])
    date = StringField("Date")
    Submit = SubmitField("Submit")


class ResetpasswordForm(FlaskForm):
    ''' Reset password form '''

    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    Submit = SubmitField("Reset Password")


class ContactForm(FlaskForm):
    ''' Contact form '''

    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired()])
    message = StringField("Message", validators=[DataRequired()])
    Submit = SubmitField("Submit")

##########################################################################################
# TIME LOG DATA #
# Timezone settings #
DESIRED_TIMEZONE = "Canada/Newfoundland"
timezone_obj = pytz.timezone(DESIRED_TIMEZONE)
now = datetime.now(timezone_obj)

##########################################################################################
# CLOCK OUT DATABASE TABLE #
##########################################################################################


class ClockOut(db.Model):
    ''' Clock out database table '''
    __tablename__ = 'clockout'

    id = db.Column(db.Integer, primary_key=True)
    Vehicle_2 = db.Column(db.String(150), nullable=True)
    Clock_Out = db.Column(db.DateTime(timezone=timezone_obj), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    in_id = db.Column(db.String(150), db.ForeignKey('clockin.out_id'), unique=True)
    clock_in = db.relationship('ClockIn', backref='clockout',
                               uselist=False,
                               foreign_keys=[in_id],
                               post_update=True)
    def __repr__(self):
        return '{}, {}'.format(self.Vehicle_2, self.Clock_Out)

##########################################################################################
# CLOCK IN DATABASE TABLE #
##########################################################################################


class ClockIn(db.Model):
    ''' Clock in database table '''

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

    clock_out = db.relationship('ClockOut',
                                backref='clockin',
                                uselist=False,
                                foreign_keys=[out_id],
                                post_update=True)
    def __repr__(self):
        return '{}, {},{}, {},{}, {}'.format(
            self.Employee,
            self.Date,
            self.Description,
            self.Vehicle,
            self.Runs,
            self.Location
            )

##########################################################################################
#ACCOUNT DATABASE#
##########################################################################################


class User(db.Model, UserMixin):
    ''' User database table '''

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    phone_number = db.Column(db.Integer)
    password = db.Column(db.String(150))
    roles = db.Column(db.String(50))
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    Emp_id = db.Column(db.String(5))
    active = db.Column(db.Integer, default=0)
    data = db.relationship('ClockIn', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.FirstName} {self.LastName}>'

    def get_token(self):
        ''' Generate token '''

        serial = Serializer(secret_key=secret_key)
        return serial.dumps({'user_id': self.id})

    @staticmethod
    def verify_token(token,expires_sec=300):
        ''' Verify token '''

        serial = Serializer(secret_key=secret_key)
        try:
            user_id = serial.loads(s=token, max_age=expires_sec)['user_id']
        except (TypeError, ValueError, KeyError):
            return None
        return User.query.get(user_id)
