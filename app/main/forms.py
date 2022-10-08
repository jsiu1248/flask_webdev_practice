from ast import Str
from xmlrpc.client import Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp
from ..models import ReleaseType

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
    # the admin can change the username
    username = StringField('Username', validators=[
        DataRequired(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                   'Usernames must have only letters, numbers, dots, or underscores',
        )])
    # the admin can change the confirmation
    confirmed = BooleanField("Confirmed")

    # field values are coerced into ints instead of str
    role = SelectField(u"Role", choices=[(1,"User"), (2, "Moderator"), (3, "Administrator")], coerce = int)
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0,64)])
    bio = TextAreaField("Bio") 
    submit = SubmitField("Submit")

class CompositionForm(FlaskForm):
    release_type = SelectField("Release Type", coerce=int, default=ReleaseType.SINGLE, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Tell us about your composition")
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.release_type.choices = [
            (ReleaseType.SINGLE, 'Single'),
            (ReleaseType.EXTENDED_PLAY, 'EP'),
            (ReleaseType.ALBUM, 'Album')]