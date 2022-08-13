
# can't just import like normal because we are in a Blueprint
# have to do it in a way that it records the actions

@app.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()
    # more code for index route...
    return render_template("index.html", name=name)
@app.route('/user/<username>')
def user(username):
    return render_template("user.html", user_name=username)