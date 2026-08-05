from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (
    BooleanField,
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    ValidationError,
)


MAX_UPLOAD_SIZE = 100 * 1024 * 1024


def validate_file_size(form, field):
    """Reject files larger than the configured 100 MB upload ceiling."""
    if not field.data:
        return

    file = field.data
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)

    if size > MAX_UPLOAD_SIZE:
        raise ValidationError("File size must not exceed 100 MB.")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=50)],
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8)],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    remember = BooleanField("Remember Me")
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Link")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=8, max=128)],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Reset Password")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Current Password",
        validators=[DataRequired()],
    )
    new_password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=8, max=128)],
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password")],
    )
    submit = SubmitField("Change Password")


class UploadForm(FlaskForm):
    project_name = StringField("Project Name", validators=[DataRequired()])
    file = FileField(
        "Project File",
        validators=[
            FileRequired(message="Please select a Python or ZIP file."),
            FileAllowed(["py", "zip"], "Only .py and .zip files are allowed."),
            validate_file_size,
        ],
    )
    submit = SubmitField("Analyze Project")


class ReviewForm(FlaskForm):
    rating = IntegerField(
        "",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        render_kw={"type": "hidden", "id": "rating"},
    )
    title = StringField(
        "Title",
        validators=[DataRequired(), Length(min=3, max=150)],
    )
    comment = TextAreaField(
        "Review",
        validators=[DataRequired(), Length(min=10, max=1000)],
    )
    submit = SubmitField("Save Changes")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    subject = StringField("Subject", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send Message")
