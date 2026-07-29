import os
import uuid
import tempfile
from analyzer.extractor import extract_project
from analyzer.formatter import run_black
from analyzer.lint import run_pylint
from analyzer.security import run_bandit
from analyzer.complexity import run_radon
from analyzer.ai import generate_ai_summary
from flask import (
    abort,
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_from_directory
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.utils import secure_filename

from helpers.upload_service import (
     validate_upload,
    build_metadata,
    generate_unique_filename,
    generate_project_id,
    create_project_workspace
)

from helpers.review_service import (
    create_review,
    update_review,
    delete_review,
    get_review,
    get_latest_reviews,
    get_all_reviews,
    get_review_statistics
)

from forms import (
    LoginForm,
    RegisterForm,
    UploadForm,
    ReviewForm
)
from database import db
from models import User, Project, Review


main = Blueprint("main", __name__)


# ============================================================
# ALLOWED PROFILE PICTURE TYPES
# ============================================================

ALLOWED_PROFILE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}


def allowed_profile_picture(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_PROFILE_EXTENSIONS
    )


# ============================================================
# HOME
# ============================================================

@main.route("/")
def home():

    latest_reviews = get_latest_reviews(3)

    review_stats = get_review_statistics()

    return render_template(
        "home.html",
        latest_reviews=latest_reviews,
        review_stats=review_stats
    )


# ============================================================
# LOGIN
# ============================================================

@main.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for("main.dashboard")
        )

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and user.check_password(
            form.password.data
        ):

            login_user(user)

            flash(
                "Login successful!",
                "success"
            )

            return redirect(
                url_for("main.dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html",
        form=form
    )


# ============================================================
# REGISTER
# ============================================================

@main.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(
                url_for("main.register")
            )

        existing_username = User.query.filter_by(
            username=form.username.data
        ).first()

        if existing_username:

            flash(
                "Username already exists.",
                "danger"
            )

            return redirect(
                url_for("main.register")
            )

        user = User(
            username=form.username.data,
            email=form.email.data
        )

        user.set_password(
            form.password.data
        )

        db.session.add(user)

        db.session.commit()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(
            url_for("main.login")
        )

    return render_template(
        "register.html",
        form=form
    )


# ============================================================
# FORGOT PASSWORD
# ============================================================

@main.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email")

        if email:

            flash(
                "If an account exists with this email, "
                "password reset instructions will be sent.",
                "success"
            )

            return redirect(
                url_for("main.login")
            )

        flash(
            "Please enter your email address.",
            "error"
        )

    return render_template(
        "forgot_password.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@main.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html"
    )


# ============================================================
# UPLOAD
# ============================================================

@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():

    form = UploadForm()

    if not form.validate_on_submit():
        return render_template(
            "upload.html",
            form=form
        )

    uploaded_file = form.file.data

    current_app.logger.info(
        f"Upload requested by user {current_user.id}: "
        f"{uploaded_file.filename}"
    )

    # --------------------------------------------------
    # Validate uploaded file
    # --------------------------------------------------

    is_valid, message = validate_upload(
        uploaded_file
    )

    if not is_valid:

        flash(
            message,
            "danger"
        )

        current_app.logger.warning(
            f"Upload rejected: {message}"
        )

        return render_template(
            "upload.html",
            form=form
        )

    # --------------------------------------------------
    # Generate Project ID
    # --------------------------------------------------

    project_id = generate_project_id()

    # --------------------------------------------------
    # Create project workspace
    # --------------------------------------------------

    projects_folder = current_app.config[
        "PROJECT_FOLDER"
    ]

    workspace = create_project_workspace(
        projects_folder,
        project_id
    )

    # --------------------------------------------------
    # Generate unique filename
    # --------------------------------------------------

    original_filename = uploaded_file.filename

    stored_filename = generate_unique_filename(
        original_filename
    )

    # --------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------

    source_path = os.path.join(
        workspace["source"],
        stored_filename
    )

    try:

        uploaded_file.save(
            source_path
        )

    except Exception as error:

        current_app.logger.exception(
            "Failed to save uploaded file."
        )

        flash(
            "Unable to save the uploaded file.",
            "danger"
        )

        return render_template(
            "upload.html",
            form=form
        )

    # --------------------------------------------------
    # Build metadata
    # --------------------------------------------------

    metadata = build_metadata(
        uploaded_file,
        stored_filename=stored_filename
    )

    # --------------------------------------------------
    # Create database record
    # --------------------------------------------------

    project = Project(

        project_id=project_id,

        project_name=metadata[
            "project_name"
        ],

        original_filename=metadata[
            "original_filename"
        ],

        stored_filename=stored_filename,

        file_type=metadata[
            "extension"
        ],

        file_size=metadata[
            "size"
        ],

        project_path=workspace[
            "root"
        ],

        user_id=current_user.id
    )

    db.session.add(project)

try:

        db.session.commit()

        current_app.logger.info(
            f"Project {project.project_id} uploaded successfully."
        )

        flash(
            "Project uploaded successfully. Analysis is starting...",
            "success"
        )

        return redirect(
            url_for(
                "main.results",
                filename=stored_filename
            )
        )

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Database error while creating project."
        )

        flash(
            "An unexpected error occurred while saving the project.",
            "danger"
        )

        return render_template(
            "upload.html",
            form=form
        )

# ============================================================
# RESULTS
# ============================================================

@main.route("/results")
@login_required
def results():

    print("=== NEW RESULTS ROUTE IS RUNNING ===")

    filename = request.args.get("filename")

    if not filename:
        flash(
            "No uploaded project was specified.",
            "error"
        )

        return redirect(
            url_for("main.upload")
        )

    # --------------------------------------------------
    # Find project belonging to current user
    # --------------------------------------------------

    project = Project.query.filter_by(
        stored_filename=filename,
        user_id=current_user.id
    ).first()

    if not project:

        flash(
            "Project not found.",
            "error"
        )

        return redirect(
            url_for("main.upload")
        )

    # --------------------------------------------------
    # Build project source path
    # --------------------------------------------------

    project_folder = os.path.abspath(
        project.project_path
    )

    source_folder = os.path.join(
        project_folder,
        "source"
    )

    upload_path = os.path.join(
        source_folder,
        project.stored_filename
    )

    # --------------------------------------------------
    # Security check
    # --------------------------------------------------

    if not os.path.isfile(upload_path):

        flash(
            "Uploaded project file could not be found.",
            "error"
        )

        return redirect(
            url_for("main.upload")
        )

    print("=== PROJECT FOUND ===")
    print("Project ID:", project.project_id)
    print("Project Name:", project.project_name)
    print("Source File:", upload_path)

    extract_folder = tempfile.mkdtemp(prefix="codesentinel_")

    python_files = extract_project(
        upload_path,
        extract_folder
    )

    formatting_status = "Passed"

    pylint_scores = []

    pylint_issues = []

    complexity_rows = []

    for file in python_files:

        black = run_black(file)

        if black["status"] != "Passed":
            formatting_status = black["status"]

        pylint_result = run_pylint(file)

        pylint_scores.append(
            pylint_result["score"]
        )

        pylint_issues.extend(
            pylint_result["issues"]
        )

        complexity_rows.extend(
            run_radon(file)
        )

    bandit_result = run_bandit(
        extract_folder
    )

    average_score = 0

    if pylint_scores:

        average_score = round(
            sum(pylint_scores) /
            len(pylint_scores),
            2
        )

    ai_summary = generate_ai_summary(
        average_score,
        bandit_result["count"],
        formatting_status,
        complexity_rows
    )

    return render_template(
        "results.html",

        filename=filename,

        quality=int(
            average_score * 10
        ),

        pylint_score=average_score,

        pylint_issues=pylint_issues,

        formatting=formatting_status,

        security_count=bandit_result["count"],

        security_issues=bandit_result["issues"],

        complexity=complexity_rows,

        ai_summary=ai_summary
    )


# ============================================================
# HISTORY
# ============================================================

@main.route("/history")
@login_required
def history():

    return render_template(
        "history.html"
    )


# ============================================================
# SETTINGS
# ============================================================

@main.route("/settings")
@login_required
def settings():

    return render_template(
        "settings.html"
    )


# ============================================================
# PROFILE
# ============================================================

@main.route(
    "/profile",
    methods=["GET", "POST"]
)
@login_required
def profile():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        profile_picture = request.files.get(
            "profile_picture"
        )

        # ------------------------------------------
        # Validate username and email
        # ------------------------------------------

        if not username or not email:

            flash(
                "Username and email are required.",
                "danger"
            )

            return redirect(
                url_for("main.profile")
            )

        # ------------------------------------------
        # Check duplicate username
        # ------------------------------------------

        existing_username = User.query.filter(
            User.username == username,
            User.id != current_user.id
        ).first()

        if existing_username:

            flash(
                "That username is already taken.",
                "danger"
            )

            return redirect(
                url_for("main.profile")
            )

        # ------------------------------------------
        # Check duplicate email
        # ------------------------------------------

        existing_email = User.query.filter(
            User.email == email,
            User.id != current_user.id
        ).first()

        if existing_email:

            flash(
                "That email is already registered.",
                "danger"
            )

            return redirect(
                url_for("main.profile")
            )

        # ------------------------------------------
        # Update username and email
        # ------------------------------------------

        current_user.username = username
        current_user.email = email

        # ------------------------------------------
        # Handle profile picture
        # ------------------------------------------

        if profile_picture and profile_picture.filename:

            if not allowed_profile_picture(
                profile_picture.filename
            ):

                flash(
                    "Invalid image type. "
                    "Use PNG, JPG, JPEG, GIF, or WEBP.",
                    "danger"
                )

                return redirect(
                    url_for("main.profile")
                )

            # Create profile picture directory
            profile_folder = os.path.join(
                current_app.root_path,
                current_app.config["UPLOAD_FOLDER"],
                "profile_pics"
            )

            os.makedirs(
                profile_folder,
                exist_ok=True
            )

            # Delete old picture if it exists
            if (
                current_user.profile_picture
                and current_user.profile_picture != "default.png"
            ):

                old_picture = os.path.join(
                    profile_folder,
                    current_user.profile_picture
                )

                if os.path.exists(old_picture):

                    os.remove(old_picture)

            # Create secure unique filename
            original_name = secure_filename(
                profile_picture.filename
            )

            extension = original_name.rsplit(
                ".",
                1
            )[1].lower()

            new_filename = (
                f"user_{current_user.id}_"
                f"{uuid.uuid4().hex}.{extension}"
            )

            profile_picture.save(
                os.path.join(
                    profile_folder,
                    new_filename
                )
            )

            current_user.profile_picture = (
                new_filename
            )

        # ------------------------------------------
        # Save everything
        # ------------------------------------------

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(
            url_for("main.profile")
        )

    return render_template(
        "profile.html"
    )


# ============================================================
# PROFILE PICTURE FILE
# ============================================================

@main.route("/profile-picture/<filename>")
@login_required
def profile_picture(filename):

    profile_folder = os.path.join(
        current_app.root_path,
        current_app.config["UPLOAD_FOLDER"],
        "profile_pics"
    )

    return send_from_directory(
        profile_folder,
        filename
    )


# ============================================================
# LOGOUT
# ============================================================

@main.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(
        url_for("main.login")
    )


# ============================================================
# 404
# ============================================================

@main.app_errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


# ============================================================
# CONTACT
# ============================================================

@main.route("/contact")
def contact():

    return render_template(
        "contact.html"
    )


# ============================================================
# FORBIDDEN
# ============================================================

@main.route("/forbidden")
def forbidden():

    abort(403)


# ============================================================
# SERVER ERROR TEST
# ============================================================

@main.route("/server-error")
def server_error_test():

    abort(500)


# ============================================================
# REVIEWS
# ============================================================

@main.route("/reviews", methods=["GET", "POST"])
def reviews():

    form = ReviewForm()

    if form.validate_on_submit():

        if not current_user.is_authenticated:
            flash(
                "Please login to submit a review.",
                "warning"
            )

            return redirect(
                url_for("main.login")
            )

        review = Review(
            rating=form.rating.data,
            title=form.title.data,
            comment=form.comment.data,
            user_id=current_user.id
        )

        db.session.add(review)
        db.session.commit()

        flash(
            "Your review has been submitted!",
            "success"
        )

        return redirect(
            url_for("main.reviews")
        )


    all_reviews = Review.query.order_by(
        Review.created_at.desc()
    ).all()


    average_rating = 0

    if all_reviews:

        average_rating = round(
            sum(
                r.rating for r in all_reviews
            )
            /
            len(all_reviews),
            1
        )


    return render_template(
        "reviews.html",
        form=form,
        reviews=all_reviews,
        average_rating=average_rating
    )
