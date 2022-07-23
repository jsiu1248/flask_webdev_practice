from datetime import date
from wsgiref.validate import validator
from flask import Flask, render_template, abort, url_for, redirect, session, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy

class NameForm(FlaskForm):
    # the validator is needed because a string is required
    name = StringField("What is your name?", validators=[DataRequired()])
    #stores as a datetime.date
    birthday = DateField("What is your birthday?", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Submit")

# flask directory
basedir = os.path.abspath(os.path.dirname(__file__))

#app is an instance of a Flask object
# generally the __name__ passed as argument is correct
app=Flask(__name__)

# Flask object has dictionary built in for config variables
#will store this at a safer place later
app.config['SECRET_KEY'] = "keep it secret, keep it safe"

# sqlite works for creating instance. It would be nice if I can do it later in mysql
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'sqlite:///{os.path.join(basedir, "data-dev.sqlite")}'

# supressing errors
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initalize the extension
db = SQLAlchemy(app)

#it is initalized by passing in the flask_bootstrap instance
#so here app is passed into the constructor
bootstrap=Bootstrap(app)

# don't have to manually import objects
# now you add objects by passing a dictionary
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

# setting up a model
class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    # linking the role model and the user model
    users = db.relationship('User', backref='role', lazy = 'dynamic')
    # returning a string with the name
    def __repr__(self):
        return f"<Role {self.name}>"

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return f"<User {self.username}>"

# "flask shell" creates an instance of a database
# "from app import db" imports the database instance
# "db.create_all()" creates the tables
# mysql -u root -p checks password of mysql
# db.drop_all() - drops all tables
# print(admin.role.id) checks the object
# only when there is a commit where a row is added to a database

# add an object - db.session.add(admin_role)
# adding all object - add_all
# db.session.commit()

# adding methods that it accepts
# to get data out, each model has a query object
# Role.query.all()
# User.query.filter_by(role=user_role).all()
# str(query) you can see underlying SQL command

# backref - adds a back reference to the other model in the relationship
# uselist - use a scalar instead of a list if false
# paginate - returns a pagination object that contains a range of results
# lazy loading allows for data only needed to be loaded

@app.route('/', methods=['GET','POST'] )

#handler
def index():
    #create the form
    form = NameForm()
    if form.validate_on_submit():
        # name=None # we need a session variable now instead
        name_entered = form.name.data
        # query checking if the name is in the database
        user = User.query.filter_by(user_name = name_entered).first()
        if user is None:
            # setting username to data that has just been entered
            user = User(username = name_entered)
            db.session.add(user)
            db.session.commit()
            # indicating that a user is new
            session['known'] = False
        else:
            # user does exist in the database?
            session['known'] = True
        session['name']= name_entered

        # name=form.name.data # we can clear the line because it already gets cleared
        form.name.data="" # what does this do?
        name_entered = form.name.data
        #whenever a post function happens then you can go back to get function so it doesn't error
        flash('Please enjoy this place!')
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known = session.get('known', False))
        # pass in known into the template



@app.route('/zodiac', methods=["GET", "POST"])
def zodiac():
    # creating form
    form = NameForm()
    print(f'xx {form.validate_on_submit()}')
    if form.validate_on_submit():
        # a session object is a dictionary object
        # name is a session variable and setting it equal to the form's name's data.
        session['name']= form.name.data
        # date is a session variable and setting it equal to the form's birthday data
        session['date']=form.birthday.data
        form_date=session['date']
        # new variable for storing animal name
        zodiac_animal = zodiac_year(form_date)
        flash("Your zodiac sign is "+zodiac_animal)
        return redirect(url_for('zodiac'))
    #
    return render_template('zodiac.html', form=form, name=session.get('name'),
    date_year=session.get('date_year'))

def zodiac_year(user_date):
    """Find zodiac animal based on birth year.
    The input is a datetime object and the output is a string."""

    zodiac_dict = {"Rat":1948, "Ox":1949, "Tiger":1950, "Rabbit":1951, "Dragon":1952,
    "Snake":1953, "Horse":1954, "Goat":1955, "Monkey":1956, "Rooster":1957, "Dog":1958,"Pig":1959}

    # extracting the year portion from the datetime from the user
    date_year=user_date.year
    while True:
        # if date_year in zodiac_dict then loop over the dictionary.
        if date_year in zodiac_dict.values():
            for animal, date in zodiac_dict.items():

                # if the date
                if date == date_year:
                    zodiac_animal = animal
            break
        else:
            # if the date_year isn't in zodiac year, then decrease by 12
            date_year = date_year - 12
    return zodiac_animal



# figured out how to make a link and reroute it
@app.route('/link_page')
def link_page():
    page='<a href="/about">Link to songs</a> <a href="/songs">Link to about</a>'
    return page

# trying to run the app with
# run "export FLASK_APP=app.py" in the terminal
# "flask run" will run it.
# Go to "localhost:5000" and you will see the result

# You can turn on the debugger and it can be reloader - which reloads as you go or debugger -
# export FLASK_DEBUG=1
#testing if pushing to github

#export FLASK_ENV=development

#two dynamic arguments in a view function name and age
@app.route('/user/<name>/<age>')
def user(name, age):
    return f"Hello, {name} are you {age} years old?!"
# make another funciton that takes numeric dymnaic and return the square
@app.route('/number/<num>')
def number(num):
    return f"{int(num)**2}"
# dynamic argument with spaces

#when creating the templates folder. Make sure it is named templates and not template

@app.route('/users/<username>')
def users(username):
    return render_template('user_test.html', username1=username)

@app.route('/derived')
def derived():
    return render_template('derived.html')

@app.errorhandler(404)
def page_not_found(e):
    error_title = "Not Found"
    error_msg= "That page doesn't exist."
    return render_template('error.html', error_title=error_title, error_msg=error_msg),404 # why is there just a number here


@app.errorhandler(403)
def forbidden(e):
    error_title = "Forbidden"
    error_msg = "You shouldn't be here!"
    return render_template('error.html',
                           error_title=error_title,
                           error_msg=error_msg), 403

@app.errorhandler(500)
def internal_server_error(e):
    error_title = "Internal Server Error"
    error_msg = "Sorry, we seem to be experiencing some technical difficulties"
    # this is because of a flask response object that 500 is just a parameter
    return render_template('error.html',
                           error_title=error_title,
                           error_msg=error_msg), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)