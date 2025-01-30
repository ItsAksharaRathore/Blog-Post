from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

# Search Form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Login form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")



# Create Post
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author')
    slug = StringField('Slug', validators=[DataRequired()])
    # content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content',validators=[DataRequired()]) 
    submit = SubmitField('Submit')



# Create a UserForm class

class UserForm(FlaskForm):
    name = StringField("Name",validators=[DataRequired()])
    username = StringField("Username",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    fav_color = StringField("Favourite Color")
    about_author_a = TextAreaField("About Author")

    pass_hash = PasswordField("Password",validators=[DataRequired(), EqualTo('pass_hash2', message="Passwords must match")])
    pass_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit = SubmitField("Submit")


# Create a Form class
class PasswordForm(FlaskForm):
    email = StringField("What's your Email",validators=[DataRequired()])
    pass_hash = PasswordField("What's your Password",validators=[DataRequired()])

    submit = SubmitField("Submit")

class NamerForm(FlaskForm):
    name = StringField("What's your name",validators=[DataRequired()])

    submit = SubmitField("Submit")
