from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
    # the validator is needed because a string is required
    name = StringField("What is your name?", validators=[DataRequired()])
    #stores as a datetime.date
    birthday = DateField("What is your birthday?", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Submit")

