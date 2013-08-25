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

class EditCollectionForm(Form):
    id = TextField('Collection ID to edit', [validators.Required()])
    name = TextField('Change collection name', [validators.Length(max=100)])
    tool = TextField('Change tool', [validators.Length(max=35)])
    description = TextField('Change description', [validators.length(max=160)])

class NewCollectionForm(Form):
    name = TextField('Collection name', [validators.Length(max=100), validators.Required()])
    owner = TextField('Owner email', [validators.Length(min=6, max=35), validators.Required()], default='default')
    tool = TextField('Tool', [validators.Length(max=35), validators.Required()], default=DEFAULT_TOOL)
    description = TextField('Description', [validators.Length(min=20, max=160), validators.Required()])

class SettingsForm(Form):
    email = TextField('Change login email', [validators.Length(min=6, max=35)])
    password = PasswordField('Change password', [validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')