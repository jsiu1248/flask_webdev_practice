from ast import Str
from xmlrpc.client import Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp

class NameForm(FlaskForm):
    # the validator is needed because a string is required
    name = StringField("What is your name?", validators=[DataRequired()])
    #stores as a datetime.date
    birthday = DateField("What is your birthday?", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Submit")

class EditProfileForm(FlaskForm):
    # these two details have length validating limits
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0,64)])

    # users can write bios as long as they want
    bio = TextAreaField("Bio")
    submit = SubmitField("Submit")

class AdminLevelEditProfileForm(FlaskForm):
    username =     username = StringField('Username', validators=[
        DataRequired(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                   'Usernames must have only letters, numbers, dots, or underscores',
        )])

    confirmed = BooleanField()
    role = SelectField("Role")
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0,64)])
    bio = TextAreaField("Bio") 