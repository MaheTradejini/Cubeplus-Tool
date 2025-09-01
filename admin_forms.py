from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    balance = StringField('Starting Balance', default='100000')
    is_admin = BooleanField('Admin User')
    submit = SubmitField('Create User')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    balance = StringField('Balance')
    is_active = BooleanField('Active')
    is_admin = BooleanField('Admin')
    submit = SubmitField('Update User')

class GlobalTOTPForm(FlaskForm):
    totp_secret = StringField('Global TOTP Secret', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Update Global TOTP')

class CredentialForm(FlaskForm):
    credential_name = StringField('Credential Name', validators=[DataRequired()])
    credential_value = StringField('Credential Value', validators=[DataRequired()])
    submit = SubmitField('Add Credential')