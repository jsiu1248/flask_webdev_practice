from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from ..models import User


class LoginForm(FlaskForm):
# the validator is needed because a string is required
    email = StringField("Email", validators=[DataRequired(), Length(min = 1, max = 64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me on this site")
    submit = SubmitField("Submit")