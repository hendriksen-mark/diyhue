# Form Based Imports
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    """
    Form for users to log in.

    Args:
        FlaskForm: Base class for creating forms in Flask.

    Attributes:
        email (StringField): Field for entering email.
        password (PasswordField): Field for entering password.
        submit (SubmitField): Field for submitting the form.
    """
    email: StringField = StringField(
        'Email', 
        validators=[DataRequired(), Email()]
    )
    password: PasswordField = PasswordField(
        'Password', 
        validators=[DataRequired()]
    )
    submit: SubmitField = SubmitField('Log In')
