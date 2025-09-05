from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    balance = FloatField('Starting Balance', validators=[Optional()], default=100000)
    is_admin = BooleanField('Admin User')
    submit = SubmitField('Create User')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    balance = FloatField('Balance', validators=[DataRequired()])
    is_active = BooleanField('Active')
    is_admin = BooleanField('Admin User')
    submit = SubmitField('Update User')

class GlobalTOTPForm(FlaskForm):
    totp_secret = StringField('TOTP Code (6 digits)', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Generate Access Token')

class DirectTokenForm(FlaskForm):
    access_token = TextAreaField('Access Token', validators=[DataRequired(), Length(min=10)], 
                                render_kw={"placeholder": "Paste your TradJini access token here..."})
    submit = SubmitField('Save Access Token')