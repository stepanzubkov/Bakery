from flask_wtf import FlaskForm
from wtforms import (
    BooleanField, EmailField, PasswordField, StringField,
    SubmitField, SelectField, TextAreaField, FileField,
    RadioField
)
from wtforms.validators import DataRequired, Email, Length, ValidationError

import os


class Extensions(object):
    """
    Validator that took list with exceptions
    and check if the file extension is in it list
    """

    def __init__(self, extensions, message=None):
        self.extensions = extensions
        self.message = message

    def __call__(self, form, field):
        if not field.data:
            return
        _, ext = os.path.splitext(field.data.filename.lower())
        if ext[1:] not in self.extensions:
            raise ValidationError(self.message)


class RegistrationForm(FlaskForm):
    email = EmailField('Email', validators=[
        Email('Incorrect email'),
        Length(min=10, max=100, message='Incorrect length'),
        DataRequired()
    ])
    password = PasswordField('Password', validators=[
        Length(min=4, max=100, message='Incorrect length'),
        DataRequired()
    ])
    first_name = StringField('First name', validators=[
        Length(min=2, max=50, message='Incorrect length'),
        DataRequired()
    ])
    last_name = StringField('Last name', validators=[
        Length(min=2, max=50, message='Incorrect length'),
        DataRequired()
    ])
    address = StringField('Address', validators=[
        Length(min=0, max=100, message='Incorrect length'),
    ])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Create account')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[
        Email('Incorrect email'),
        Length(min=10, max=100, message='Incorrect length'),
        DataRequired()
    ])
    password = PasswordField('Password', validators=[
        Length(min=4, max=100, message='Incorrect length'),
        DataRequired()
    ])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class SettingsForm(FlaskForm):
    first_name = StringField('First name', validators=[
        Length(min=2, max=50, message='Incorrect length'),
        DataRequired()
    ])
    last_name = StringField('Last name', validators=[
        Length(min=2, max=50, message='Incorrect length'),
        DataRequired()
    ])
    address = StringField('Address', validators=[
        Length(min=-1, max=100, message='Incorrect length'),
    ])
    submit = SubmitField('Save settings')


class EmailChangeForm(FlaskForm):
    email = EmailField('Email', validators=[
        Email('Incorrect email'),
        Length(min=10, max=100, message='Incorrect length'),
        DataRequired()
    ])
    submit = SubmitField('Save email')


class PasswordChangeForm(FlaskForm):
    password = PasswordField('Password', validators=[
        Length(min=4, max=100, message='Incorrect length'),
        DataRequired()
    ])
    submit = SubmitField('Save password')


class SortForm(FlaskForm):
    sort = SelectField('Sort', choices=[
        ('', 'Default'),
        ('popular', 'Popular first'),
        ('asc_price', 'By ascending price'),
        ('desc_price', 'By descending price'),
        ('alphabet', 'By alphabet')
    ])

    submit = SubmitField('Sort')


class ReviewForm(FlaskForm):
    text = TextAreaField('Text (optional)')

    '''this element will not be shown on the page
    as we will make our own special element'''
    image = FileField('Image (optional)', validators=[
                      Extensions(['png', 'jpg', 'jpeg'],
                                 'File must be only .png or .jpg file')])
    rating = StringField('Rating')
    submit = SubmitField('Create review')


class BuyForm(FlaskForm):
    wishes = TextAreaField('Wishes (optional)')
    address_choose = RadioField(choices=[
        ('default', 'Use account address'),
        ('custom', 'Use custom address')
    ])
    address = StringField('Custom address', validators=[
        Length(min=-1, max=100, message='Incorrect length')])
    submit = SubmitField('Buy product')
