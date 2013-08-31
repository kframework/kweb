# WTForms class to define all forms used on-site 

from wtforms import Form, BooleanField, TextField, PasswordField, validators
from config import DEFAULT_TOOL

class RegistrationForm(Form):
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [validators.Required()])

class ForgotForm(Form):
    email = TextField('Email Address', [validators.Length(min=6, max=35)])

class ResetForm(Form):
    password = PasswordField('New password', [validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

class EditCollectionForm(Form):
    id = TextField('Collection ID to edit', [validators.Required()])
    name = TextField('Change collection name', [validators.Length(max=100)])
    tool = TextField('Change tool', [validators.Length(max=35)])
    description = TextField('Change description', [validators.length(max=160)])

class SettingsForm(Form):
    email = TextField('Change login email', [validators.Length(min=6, max=35)])
    password = PasswordField('Change password', [validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')