from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager , login_required, logout_user, current_user

from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# create a Flask Instance
app = Flask(__name__)
# Add CK editor
ckeditor = CKEditor(app)

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


# Pass Stuff To Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Create Admin Page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html')
    else:
        flash('Sorry You must be the admin to access the admin page')
        return redirect(url_for('dashboard'))



# Create Search Function
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from submitted databse
        post.searched = form.searched.data
        # Query the database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html', form=form, searched = post.searched, posts = posts)

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

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static\\profile_pics'  # Specify the folder for uploaded files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        name_to_update.about_author_a = request.form['about_author_a']
               # Handle file upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            # Handle file upload
            if file.filename != '':
                # Save the file with a secure name
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace("\\", "/")
                file.save(file_path)
                # Update the database with the forward-slash file path
                name_to_update.profile_pic = file_path


        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error! Could not update user: {e}")
            return redirect(url_for('dashboard'))

        # # Only update password if provided
        # if form.pass_hash.data:
        #     name_to_update.pass_hash = generate_password_hash(form.pass_hash.data)

        # try:
            
        # except:
        #     flash("Error! Could not update user.")
        #     return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)

    return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)




# Delete Post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:

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

    else:
            flash("You aren't authorized to delete that post! ")
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
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update DB

        db.session.add(post)
        db.session.commit()
        flash("Post has been updated! ")
        return redirect(url_for('post', id=post.id))
    
    if current_user.id == post.poster_id:
            
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You arn't authorized to edit this post")
        posts  = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

# Add Post Page
@app.route("/add-post", methods=["GET", "POST"])
# @login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
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


# @app.route('/user')
# def all_user():
#     user = Users.query.all()
#     print(user)  # Debugging
#     return render_template('user.html', user=user)




# delete 
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:

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

    else:
            flash("Sorry, you can't delete that user! ")
            return redirect(url_for('dashboard'))



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


# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text())
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime(), default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Foreign key to link users (refer to primary key of the users)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    fav_color = db.Column(db.String(120))
    about_author_a = db.Column(db.Text(500), nullable = True)

    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable = True)
    # Do some pass
    pass_hash = db.Column(db.String(128))

    # user can have many posts
    posts = db.relationship('Posts', backref='poster')

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


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
