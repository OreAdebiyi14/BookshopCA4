from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[InputRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class BookForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    author = StringField('Author', validators=[InputRequired()])
    price = FloatField('Price', validators=[InputRequired()])
    stock = IntegerField('Stock', validators=[InputRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Save Book')