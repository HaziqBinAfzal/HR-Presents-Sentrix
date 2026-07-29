from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    TextAreaField,
    IntegerField
)

from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    ValidationError
)


# ============================================================
# UPLOAD VALIDATION
# ============================================================

MAX_UPLOAD_SIZE = 100 * 1024 * 1024


def validate_file_size(form, field):
    """
    Validate uploaded file size.
    """

    if not field.data:
        return

    file = field.data

    # Move to the end of the uploaded file
    file.seek(0, 2)

    size = file.tell()

    # Reset file position
    file.seek(0)

    if size > MAX_UPLOAD_SIZE:

        raise ValidationError(
            "File size must not exceed 16 MB."
        )


# ============================================================
# REGISTER FORM
# ============================================================

class RegisterForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=50)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password")
        ]
    )

    submit = SubmitField("Register")


# ============================================================
# LOGIN FORM
# ============================================================

class LoginForm(FlaskForm):

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Login")


# ============================================================
# FORGOT PASSWORD FORM
# ============================================================

class ForgotPasswordForm(FlaskForm):

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    submit = SubmitField("Send Reset Link")


# ============================================================
# RESET PASSWORD FORM
# ============================================================

class ResetPasswordForm(FlaskForm):

    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password")
        ]
    )

    submit = SubmitField("Reset Password")


# ============================================================
# UPLOAD FORM
# ============================================================

class UploadForm(FlaskForm):

    file = FileField(
        "Project File",
        validators=[
            FileRequired(
                message="Please select a Python or ZIP file."
            ),
            FileAllowed(
                ["py", "zip"],
                "Only .py and .zip files are allowed."
            ),
            validate_file_size
        ]
    )

    submit = SubmitField("Analyze Project")


class ReviewForm(FlaskForm):

    rating = IntegerField(
    "",
    validators=[
        DataRequired(),
        NumberRange(min=1, max=5)
    ],
    render_kw={
        "type": "hidden",
        "id": "rating"
    }
)

    title = StringField(
        "Title",
        validators=[
            DataRequired(),
            Length(min=3, max=150)
        ]
    )

    comment = TextAreaField(
        "Review",
        validators=[
            DataRequired(),
            Length(min=10, max=1000)
        ]
    )

    submit = SubmitField(
        "Submit Review"
    )
