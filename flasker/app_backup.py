from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager , login_required, logout_user, current_user

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# create a Flask Instance
app = Flask(__name__)

# ADD database (URI-UNIFORM RESOURCE INDICATOR)
# old SQLite DB

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"

# New MySQL DB
# password = "Aditi23*10" byy
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root2:{password}@localhost/our_users"


# secret key
app.config['SECRET_KEY'] = "MY SUPER KEY"




# initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#  Flask login_stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Login form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # check the hash
            if check_password_hash(user.pass_hash, form.password.data):
                login_user(user)
                flash("Login Successfully!!! ")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong password - Try Again!")
        else:
            flash("That User Doesn't Exists - Try Again!")
    return render_template('login.html', form=form)


# Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Logout Successfully!!! ")
    return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # form = LoginForm()

    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    
   
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        
        # # Only update password if provided
        # if form.pass_hash.data:
        #     name_to_update.pass_hash = generate_password_hash(form.pass_hash.data)

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return redirect(url_for('dashboard'))
        except:
            flash("Error! Could not update user.")
            return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)

    return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)


# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text())
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime(), default=datetime.utcnow)
    slug = db.Column(db.String(255))


# Create Post
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField('Submit')

# Delete Post
@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()

        # Msg
        flash("Blog Post was Deleted! ")
        posts  = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)


    except:
        flash("Oops! Try again later")
        posts  = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)




@app.route('/posts')
def posts():
    # Grab all the posts from the database
    posts  = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update DB

        db.session.add(post)
        db.session.commit()
        flash("Post has been updated! ")
        return redirect(url_for('post', id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', form=form)


# Add Post Page
@app.route("/add-post", methods=["GET", "POST"])
# @login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        # clear form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        # add to database
        db.session.add(post)
        db.session.commit()

        # Return a Message
        flash("Blog Post Submitted Successfully!!")

        # Redirect to the webpage
    return render_template('add_post.html', form=form)

# Json 
@app.route('/date')
def get_current_date():
    # fav_pizza = {
    #     "A": "Chesse",
    #     "B": "Pepperoni",
    #     "C": "Corn"
    # }
    # return fav_pizza
    return {
        "Date": date.today()
    }




# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    fav_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Do some pass
    pass_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute ")
    @password.setter
    def password(self, pass_):
        self.pass_hash = generate_password_hash(pass_)
    def verify_password(self, pass_):
        return check_password_hash(self.pass_hash, pass_)


    # Create a string representation
    def __repr__(self):
        return '<Name %r>' % self.name

# delete 
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully!")

        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html',form=form,
        name=name,
        our_users = our_users)

    except:
        flash("There is a problem deleting the user. Please try again later...")
        return render_template('add_user.html',form=form,
        name=name,
        our_users = our_users)


# Create a UserForm class

class UserForm(FlaskForm):
    name = StringField("Name",validators=[DataRequired()])
    username = StringField("Username",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    fav_color = StringField("Favourite Color")
    pass_hash = PasswordField("Password",validators=[DataRequired(), EqualTo('pass_hash2', message="Passwords must match")])
    pass_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Update database
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    
    # Check if user has permission to update this profile
    if current_user.id != id:
        flash("You don't have permission to edit this profile!")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        
        # # Only update password if provided
        # if form.pass_hash.data:
        #     name_to_update.pass_hash = generate_password_hash(form.pass_hash.data)

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return redirect(url_for('dashboard'))
        except:
            flash("Error! Could not update user.")
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

    return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

# Create a Form class
class PasswordForm(FlaskForm):
    email = StringField("What's your Email",validators=[DataRequired()])
    pass_hash = PasswordField("What's your Password",validators=[DataRequired()])

    submit = SubmitField("Submit")

class NamerForm(FlaskForm):
    name = StringField("What's your name",validators=[DataRequired()])

    submit = SubmitField("Submit")




# def index():
#     return "<h1><i><center/>Hellooooooooo!</i></h1>"


@app.route('/user/add',methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash pass
            hashed_pw = generate_password_hash(form.pass_hash.data, method="pbkdf2:sha256")
            user = Users(username= form.username.data, name=form.name.data, email=form.email.data,fav_color=form.fav_color.data, pass_hash = hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.fav_color.data = ''
        form.pass_hash = ''

        flash("User added successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html',form=form,
                           name=name,
                           our_users = our_users)

# create a route decorator
@app.route('/')
def index():
    first_name = "Akshara"
    stuff = "This is <strong/> bold text   "
    # flash("Welcome to our website !")
    favourite_pizza = ["Pepperoni","Mashroom","Chesse",23]
    return render_template("index.html",first_name=first_name,
                           stuff=stuff,favourite_pizza=favourite_pizza)



# localhost: http://127.0.0.1:5000/user/akshara
@app.route('/user/<name>')
# def user(name):
#     return "<h1>Hello {}!</h1>".format(name)


def user(name):
    return render_template('user.html', user_name=name)

# Create Custom Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
# Internal Server Error URL
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# Create pass page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()


    # validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.pass_hash.data
        form.email.data = ''
        form.pass_hash.data = ''

        # Look up the user by email
        pw_to_check = Users.query.filter_by(email=email).first()

        if pw_to_check:
        # Check the hashed password
            passed = check_password_hash(pw_to_check.pass_hash, password)
        else:
            flash("User not found. Please check the email.")
            #  flash("Form Submitted Successfully")
    return render_template('test_pw.html',
                        email=email,
                        password=password,
                        pw_to_check=pw_to_check,
                        passed=passed,
                        form=form)



# Create name page
@app.route('/name', methods=['GET', 'POST'])
def name():
        name = None
        form = NamerForm()
        # validate form
        if form.validate_on_submit():
             name = form.name.data
             form.name.data = ''
             flash("Form Submitted Successfully")
        return render_template('name.html',name=name,form=form)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
