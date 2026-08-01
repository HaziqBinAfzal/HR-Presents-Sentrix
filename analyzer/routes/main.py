import os
import uuid
import tempfile
import time
from flask import send_file
from flask_login import login_required, current_user
from flask_mail import Message
from extensions import mail
from helpers.analysis_service import run_project_analysis
from analyzer.extractor import extract_project
from analyzer.formatter import run_black
from analyzer.lint import run_pylint
from analyzer.security import run_bandit
from analyzer.complexity import run_radon
from analyzer.ai import generate_ai_summary
from forms import ContactForm
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
from models import User, Project, Review, Analysis


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
# ABOUT
# ============================================================

@main.route("/about")
def about():

    return render_template(
        "about.html"
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

    total_projects = Project.query.filter_by(
        user_id=current_user.id
    ).count()

    total_analyses = Analysis.query.filter_by(
        user_id=current_user.id
    ).count()

    total_reports = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.report_path.isnot(None)
    ).count()

    security_issues = (
        db.session.query(
            db.func.sum(Analysis.security_count)
        )
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0
    )

    latest_analysis = (
        Analysis.query
        .filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .first()
    )

    average_score = (
        db.session.query(db.func.avg(Analysis.overall_score))
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0
    )

    overall_score = round(average_score, 1)

    average_quality = (
        db.session.query(db.func.avg(Analysis.pylint_score))
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0
    )

    quality_score = round(average_quality, 1)

    total_size = (
         db.session.query(db.func.sum(Project.file_size))
         .filter_by(user_id=current_user.id)
         .scalar()
         or 0
    )

    storage_used = f"{round(total_size / (1024 * 1024), 2)} MB"

    recent_analyses = (
        Analysis.query
        .filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(5)
        .all()
    )

    recent_activities = []

    for analysis in recent_analyses:

        recent_activities.append(
            {
                "title": analysis.filename,
                "status": analysis.status,
                "score": analysis.overall_score,
                "date": analysis.created_at.strftime("%d %b %Y")
            }
        )
    

    chart_analyses = list(reversed(recent_analyses))

    quality_chart = {
        "labels": [
            analysis.created_at.strftime("%d %b")
            for analysis in chart_analyses
        ],
        "datasets": [
            {
                "label": "Overall Score",
                "data": [
                    analysis.overall_score
                    for analysis in chart_analyses
                ],
                "fill": False
            }
        ]
    }

    latest_stats = latest_analysis

    secure_projects = (
        Analysis.query
        .filter(
            Analysis.user_id == current_user.id,
            Analysis.security_count == 0
        )
        .count()
    )

    projects_with_issues = (
        Analysis.query
        .filter(
            Analysis.user_id == current_user.id,
            Analysis.security_count > 0
        )
        .count()
    )

    security_chart = {
        "labels": [
            "Secure Projects",
            "Projects with Issues"
        ],
        "datasets": [
            {
               "data": [
                   secure_projects,
                   projects_with_issues
               ]
            }
        ]
    }

    return render_template(
        "dashboard.html",

        total_projects=total_projects,
        total_analyses=total_analyses,
        total_reports=total_reports,
        latest_stats=latest_stats,
        security_issues=security_issues,

        overall_score=overall_score,
        quality_score=quality_score,

        storage_used=storage_used,

        recent_analyses=recent_analyses,

        security_score=100,
        maintainability_score=100,
        ai_score=100,

        quality_chart=quality_chart,
        security_chart=security_chart,

        recent_activities=recent_activities,

        ai_insight=(
            latest_analysis.ai_summary
            if latest_analysis and latest_analysis.ai_summary
            else "Upload a project to receive AI insights."

        )
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

        print(
            "Project Name:",
            metadata["project_name"]
        )

        print(
            "Original File:",
            metadata["original_filename"]
        )

        print(
            "Stored File:",
            stored_filename
        )

        print(
            "Project Path:",
            workspace["root"]
        )

        # --------------------------------------------------
        # Success
        # --------------------------------------------------

        analysis_result = run_project_analysis(
            project,
            current_user,
        )


        flash(
            "Project uploaded successfully. Analysis is starting...",
            "success"
        )

        return redirect(
            url_for(
                "main.results",
        analysis_id=analysis_result["analysis_id"]
            )
        )

    except Exception as e:

        db.session.rollback()

        import traceback
        traceback.print_exc()

        raise
# ============================================================
# RESULTS
# ============================================================

@main.route("/results/<int:analysis_id>")
@login_required
def results(analysis_id):

    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=current_user.id
    ).first()

    if not analysis:

        flash(
            "Analysis not found.",
            "error"
        )

        return redirect(
            url_for("main.dashboard")
        )

    project = Project.query.filter_by(
        id=analysis.project_id,
        user_id=current_user.id
    ).first()

    if not project:

        flash(
            "Project not found.",
            "error"
        )

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "results.html",

        project=project,

        analysis=analysis
    )

# ============================================================
# HISTORY
# ============================================================

@main.route("/history")
@login_required
def history():

    search = request.args.get("search", "").strip()
    complexity = request.args.get("complexity", "").strip()
    sort = request.args.get("sort", "latest").strip()

    query = Analysis.query.filter_by(
        user_id=current_user.id
    )

    # -----------------------------
    # Search
    # -----------------------------

    if search:
        query = query.filter(
            db.or_(
                Analysis.filename.ilike(f"%{search}%"),
                Analysis.language.ilike(f"%{search}%")
            )
        )


    # -----------------------------
    # Complexity
    # -----------------------------

    if complexity:
        query = query.filter(
            Analysis.complexity.ilike(complexity)
        )

    # -----------------------------
    # Sorting
    # -----------------------------

    if sort == "oldest":
        query = query.order_by(
            Analysis.created_at.asc()
        )

    elif sort == "score_desc":
        query = query.order_by(
            Analysis.overall_score.desc()
        )

    elif sort == "score_asc":
        query = query.order_by(
            Analysis.overall_score.asc()
        )

    else:
        query = query.order_by(
            Analysis.created_at.desc()
        )

    analyses = query.all()

    total_projects = Project.query.filter_by(
        user_id=current_user.id
    ).count()

    total_analyses = len(analyses)

    total_security = sum(
        analysis.security_count
        for analysis in analyses
    )

    average_score = round(
        db.session.query(
            db.func.avg(
                Analysis.overall_score
            )
        ).filter_by(
            user_id=current_user.id
        ).scalar() or 0,
        2
    )

    return render_template(
        "history.html",
        analyses=analyses,
        total_projects=total_projects,
        total_analyses=total_analyses,
        total_security=total_security,
        average_score=average_score,
        search=search,
        complexity=complexity,
        sort=sort
    )
# DELETE ANALYSIS# 


@main.route("/delete_analysis/<int:analysis_id>", methods=["POST"])
@login_required
def delete_analysis(analysis_id):

    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=current_user.id
    ).first_or_404()

    # Delete report file if it exists
    if analysis.report_path and os.path.exists(analysis.report_path):
        os.remove(analysis.report_path)

    db.session.delete(analysis)
    db.session.commit()

    flash(
        "Analysis deleted successfully.",
        "success"
    )

    return redirect(
        url_for("main.history")
    )


# ============================================================
# SETTINGS
# ============================================================

@main.route("/settings")
@login_required
def settings():

    total_projects = Project.query.filter_by(
W        user_id=current_user.id
    ).count()

    total_analyses = Analysis.query.filter_by(
        user_id=current_user.id
    ).count()

    total_reports = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.report_path.isnot(None)
    ).count()

    storage_size = (
        db.session.query(
            db.func.sum(Project.file_size)
        )
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0
    )

    storage_used = round(
        storage_size / (1024 * 1024),
        2
    )

    return render_template(
        "settings.html",

        total_projects=total_projects,
        total_analyses=total_analyses,
        total_reports=total_reports,
        storage_used=f"{storage_used} MB"
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

        current_user.full_name = request.form.get("full_name", "").strip()
        current_user.organization = request.form.get("organization", "").strip()
        current_user.bio = request.form.get("bio", "").strip()

        # ------------------------------------------
        # Handle profile picture
        # ------------------------------------------

        if profile_picture and profile_picture.filename:

            if not allowed_profile_picture(
                profile_picture.filename
            ):

                flash(
                    "Invalid image type. Use PNG, JPG, JPEG, GIF, or WEBP.",
                    "danger"
                )

                return redirect(
                    url_for("main.profile")
                )

            profile_folder = os.path.join(
                current_app.root_path,
                current_app.config["UPLOAD_FOLDER"],
                "profile_pics"
            )

            os.makedirs(
                profile_folder,
                exist_ok=True
            )

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

            current_user.profile_picture = new_filename

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(
            url_for("main.profile")
        )

        total_projects = Project.query.filter_by(
           user_id=current_user.id
        ).count()

        total_analyses = Analysis.query.filter_by(
           user_id=current_user.id
        ).count()

        total_reviews = Review.query.filter_by(
           user_id=current_user.id
        ).count()

        recent_projects = (
           Project.query
           .filter_by(user_id=current_user.id)
           .order_by(Project.upload_date.desc())
           .limit(5)
           .all()
    )

    return render_template(
        "profile.html",
        total_projects=total_projects,
        total_analyses=total_analyses,
        total_reviews=total_reviews,
        recent_projects=recent_projects
    )


# CHANGE PASSWORD #

@main.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    flash(
        "Change Password feature is coming soon.",
        "info"
    )

    return redirect(
        url_for("main.profile")
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

@main.route("/contact", methods=["GET", "POST"])
def contact():

    form = ContactForm()

    if form.validate_on_submit():

        try:
            
            print("Name:", repr(form.name.data))
            print("Email:", repr(form.email.data))
            print("Message:", repr(form.message.data))
            print("Form data:", request.form)

            msg = Message(
                subject="New Contact Form Message",
                recipients=["supportcodesentinelai@gmail.com"]
            )

            msg.body = f"""
Name: {form.name.data}

Email: {form.email.data}

Message:

{form.message.data}
"""

            mail.send(msg)

            flash(
                "Your message has been sent successfully.",
                "success"
            )

            return redirect(url_for("main.contact"))

        except Exception as e:

            flash(
                f"Failed to send email: {e}",
                "danger"
            )

    return render_template(
        "contact.html",
        form=form
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

        print("FORM VALID")

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

    elif request.method == "POST":

        print("FORM ERRORS:")
        print(form.errors)

    all_reviews = get_all_reviews()

    review_stats = get_review_statistics()

    return render_template(
        "reviews.html",
        form=form,
        reviews=all_reviews,
        review_stats=review_stats,
        average_rating=review_stats["average_rating"],
        total_reviews=review_stats["total_reviews"],
        rating_breakdown=review_stats["rating_breakdown"],
        recommendation_percentage=review_stats[
            "recommendation_percentage"
        ]
    )

# REPORT DOWNLOAD #

@main.route("/download_report/<int:analysis_id>")
@login_required
def download_report(analysis_id):

    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=current_user.id
    ).first_or_404()

    if not analysis.report_path:
        flash(
            "Report has not been generated yet.",
            "warning"
        )
        return redirect(
            url_for(
                "main.results",
                analysis_id=analysis.id
            )
        )

    if not os.path.exists(analysis.report_path):
        flash(
            "Report file was not found.",
            "danger"
        )
        return redirect(
            url_for(
                "main.results",
                analysis_id=analysis.id
            )
        )

    return send_file(
        analysis.report_path,
        as_attachment=True,
        download_name=f"{analysis.filename}_report.html",
        mimetype="text/html"
    )



# ============================================================
# EDIT REVIEW
# ============================================================

@main.route("/reviews/edit/<int:review_id>", methods=["GET", "POST"])
@login_required
def edit_review(review_id):

    review = Review.query.get_or_404(review_id)

    if review.user_id != current_user.id:

        flash(
            "You can only edit your own review.",
            "danger"
        )

        return redirect(url_for("main.reviews"))

    form = ReviewForm()

    if form.validate_on_submit():

        review.rating = form.rating.data
        review.title = form.title.data
        review.comment = form.comment.data

        db.session.commit()

        flash(
            "Review updated successfully!",
            "success"
        )

        return redirect(url_for("main.reviews"))

    form.rating.data = review.rating
    form.title.data = review.title
    form.comment.data = review.comment

    return render_template(
        "edit_review.html",
        form=form,
        review=review
    )





# ============================================================
# DELETE REVIEW
# ============================================================

@main.route("/reviews/delete/<int:review_id>", methods=["POST"])
@login_required
def delete_review(review_id):

    review = Review.query.get_or_404(review_id)

    if review.user_id != current_user.id:

        flash(
            "You can only delete your own review.",
            "danger"
        )

        return redirect(url_for("main.reviews"))

    db.session.delete(review)
    db.session.commit()

    flash(
        "Review deleted successfully!",
        "success"
    )

    return redirect(url_for("main.reviews"))





o

