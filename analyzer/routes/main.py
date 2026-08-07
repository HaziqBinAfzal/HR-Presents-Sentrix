import os
import uuid

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from werkzeug.utils import secure_filename

from database import db
from extensions import mail
from forms import ContactForm, LoginForm, RegisterForm, ReviewForm, UploadForm
from helpers.analysis_service import run_project_analysis
from helpers.review_service import (
    create_review,
    delete_review as delete_review_record,
    get_all_reviews,
    get_latest_reviews,
    get_review,
    get_review_statistics,
    update_review,
)
from helpers.upload_service import (
    build_metadata,
    create_project_workspace,
    generate_project_id,
    generate_unique_filename,
    validate_upload,
)
from models import Analysis, Project, Review, User


main = Blueprint("main", __name__)

ALLOWED_PROFILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_profile_picture(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_PROFILE_EXTENSIONS
    )


def _average(values):
    numbers = [float(value) for value in values if value is not None]
    return round(sum(numbers) / len(numbers), 1) if numbers else 0.0


@main.route("/")
def home():
    return render_template(
        "home.html",
        latest_reviews=get_latest_reviews(3),
        review_stats=get_review_statistics(),
    )


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("main.dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)


@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        username = form.username.data.strip()
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("main.register"))
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("main.register"))

        user = User(username=username, email=email)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)


@main.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        if email:
            flash(
                "If an account exists with this email, password reset instructions will be sent.",
                "success",
            )
            return redirect(url_for("main.login"))
        flash("Please enter your email address.", "error")
    return render_template("forgot_password.html")


@main.route("/dashboard")
@login_required
def dashboard():
    user_analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )
    recent_analyses = user_analyses[:5]
    latest_analysis = user_analyses[0] if user_analyses else None
    scorecards = [analysis.scorecard for analysis in user_analyses]

    total_projects = Project.query.filter_by(user_id=current_user.id).count()
    total_reports = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.report_path.isnot(None),
    ).count()
    security_issues = sum(int(analysis.security_count or 0) for analysis in user_analyses)
    total_size = (
        db.session.query(db.func.sum(Project.file_size))
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0
    )

    overall_score = _average(card["overall_score"] for card in scorecards)
    quality_score = _average(card["quality_score"] for card in scorecards)
    security_score = _average(card["security_score"] for card in scorecards)
    maintainability_score = _average(
        card["maintainability_score"] for card in scorecards
    )

    chart_analyses = list(reversed(recent_analyses))
    quality_chart = {
        "labels": [a.created_at.strftime("%d %b") for a in chart_analyses],
        "datasets": [
            {
                "label": "Overall Score",
                "data": [a.scorecard["overall_score"] for a in chart_analyses],
                "fill": False,
            }
        ],
    }

    secure_projects = sum(1 for a in user_analyses if int(a.security_count or 0) == 0)
    projects_with_issues = len(user_analyses) - secure_projects
    security_chart = {
        "labels": ["Secure Projects", "Projects with Issues"],
        "datasets": [{"data": [secure_projects, projects_with_issues]}],
    }

    recent_activities = [
        {
            "title": analysis.filename,
            "status": analysis.status,
            "score": analysis.scorecard["overall_score"],
            "date": analysis.created_at.strftime("%d %b %Y"),
        }
        for analysis in recent_analyses
    ]

    return render_template(
        "dashboard.html",
        total_projects=total_projects,
        total_analyses=len(user_analyses),
        total_reports=total_reports,
        latest_stats=latest_analysis,
        security_issues=security_issues,
        overall_score=overall_score,
        quality_score=quality_score,
        security_score=security_score,
        maintainability_score=maintainability_score,
        storage_used=f"{round(total_size / (1024 * 1024), 2)} MB",
        recent_analyses=recent_analyses,
        quality_chart=quality_chart,
        security_chart=security_chart,
        language_chart=None,
        recent_activities=recent_activities,
        ai_insight=(
            latest_analysis.ai_summary
            if latest_analysis and latest_analysis.ai_summary
            else "Upload a project to receive AI insights."
        ),
    )


@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = UploadForm()
    recent_analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(5)
        .all()
    )
    if not form.validate_on_submit():
        return render_template("upload.html", form=form, recent_analyses=recent_analyses)

    uploaded_file = form.file.data
    is_valid, message = validate_upload(uploaded_file)
    if not is_valid:
        flash(message, "danger")
        return render_template("upload.html", form=form, recent_analyses=recent_analyses)

    project_id = generate_project_id()
    workspace = create_project_workspace(current_app.config["PROJECT_FOLDER"], project_id)
    stored_filename = generate_unique_filename(uploaded_file.filename)
    source_path = os.path.join(workspace["source"], stored_filename)

    try:
        uploaded_file.save(source_path)
        metadata = build_metadata(uploaded_file, stored_filename=stored_filename)
        submitted_name = (getattr(form, "project_name", None).data or "").strip() if getattr(form, "project_name", None) else ""
        project = Project(
            project_id=project_id,
            project_name=submitted_name or metadata["project_name"],
            original_filename=metadata["original_filename"],
            stored_filename=stored_filename,
            file_type=metadata["extension"],
            file_size=metadata["size"],
            project_path=workspace["root"],
            user_id=current_user.id,
        )
        db.session.add(project)
        db.session.commit()
        analysis_result = run_project_analysis(project, current_user)
        flash("Project uploaded and analyzed successfully.", "success")
        return redirect(
            url_for("main.results", analysis_id=analysis_result["analysis_id"])
        )
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Sentrix project upload or analysis failed.")
        flash(
            "Sentrix could not complete the analysis. The scan was not saved with fake scores.",
            "danger",
        )
        return redirect(url_for("main.upload"))


@main.route("/results/<int:analysis_id>")
@login_required
def results(analysis_id):
    analysis = Analysis.query.filter_by(
        id=analysis_id, user_id=current_user.id
    ).first()
    if not analysis:
        flash("Analysis not found.", "error")
        return redirect(url_for("main.dashboard"))

    project = Project.query.filter_by(
        id=analysis.project_id, user_id=current_user.id
    ).first()
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("main.dashboard"))
    return render_template(
        "results.html", project=project, analysis=analysis, scorecard=analysis.scorecard
    )


@main.route("/history")
@login_required
def history():
    search = request.args.get("search", "").strip()
    complexity = request.args.get("complexity", "").strip()
    sort = request.args.get("sort", "latest").strip()
    query = Analysis.query.filter_by(user_id=current_user.id)
    if search:
        query = query.filter(
            db.or_(
                Analysis.filename.ilike(f"%{search}%"),
                Analysis.language.ilike(f"%{search}%"),
            )
        )
    if complexity:
        query = query.filter(Analysis.complexity.ilike(complexity))
    if sort == "oldest":
        query = query.order_by(Analysis.created_at.asc())
    elif sort == "score_desc":
        query = query.order_by(Analysis.overall_score.desc())
    elif sort == "score_asc":
        query = query.order_by(Analysis.overall_score.asc())
    else:
        query = query.order_by(Analysis.created_at.desc())

    analyses = query.all()
    average_score = _average(analysis.scorecard["overall_score"] for analysis in analyses)
    return render_template(
        "history.html",
        analyses=analyses,
        total_projects=Project.query.filter_by(user_id=current_user.id).count(),
        total_analyses=len(analyses),
        total_security=sum(int(a.security_count or 0) for a in analyses),
        average_score=average_score,
        search=search,
        complexity=complexity,
        sort=sort,
    )


@main.route("/delete_analysis/<int:analysis_id>", methods=["POST"])
@login_required
def delete_analysis(analysis_id):
    analysis = Analysis.query.filter_by(
        id=analysis_id, user_id=current_user.id
    ).first_or_404()
    if analysis.report_path and os.path.exists(analysis.report_path):
        os.remove(analysis.report_path)
    db.session.delete(analysis)
    db.session.commit()
    flash("Analysis deleted successfully.", "success")
    return redirect(url_for("main.history"))


@main.route("/settings")
@login_required
def settings():
    storage_size = (
        db.session.query(db.func.sum(Project.file_size))
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0
    )
    return render_template(
        "settings.html",
        total_projects=Project.query.filter_by(user_id=current_user.id).count(),
        total_analyses=Analysis.query.filter_by(user_id=current_user.id).count(),
        total_reports=Analysis.query.filter(
            Analysis.user_id == current_user.id,
            Analysis.report_path.isnot(None),
        ).count(),
        storage_used=f"{round(storage_size / (1024 * 1024), 2)} MB",
    )


@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        profile_picture = request.files.get("profile_picture")
        if not username or not email:
            flash("Username and email are required.", "danger")
            return redirect(url_for("main.profile"))
        if User.query.filter(User.username == username, User.id != current_user.id).first():
            flash("That username is already taken.", "danger")
            return redirect(url_for("main.profile"))
        if User.query.filter(User.email == email, User.id != current_user.id).first():
            flash("That email is already registered.", "danger")
            return redirect(url_for("main.profile"))

        current_user.username = username
        current_user.email = email
        current_user.full_name = request.form.get("full_name", "").strip()
        current_user.organization = request.form.get("organization", "").strip()
        current_user.bio = request.form.get("bio", "").strip()

        if profile_picture and profile_picture.filename:
            if not allowed_profile_picture(profile_picture.filename):
                flash("Invalid image type. Use PNG, JPG, JPEG, GIF, or WEBP.", "danger")
                return redirect(url_for("main.profile"))
            profile_folder = os.path.join(
                current_app.root_path,
                current_app.config["UPLOAD_FOLDER"],
                "profile_pics",
            )
            os.makedirs(profile_folder, exist_ok=True)
            if current_user.profile_picture and current_user.profile_picture != "default.png":
                old_picture = os.path.join(profile_folder, current_user.profile_picture)
                if os.path.exists(old_picture):
                    os.remove(old_picture)
            original_name = secure_filename(profile_picture.filename)
            extension = original_name.rsplit(".", 1)[1].lower()
            new_filename = f"user_{current_user.id}_{uuid.uuid4().hex}.{extension}"
            profile_picture.save(os.path.join(profile_folder, new_filename))
            current_user.profile_picture = new_filename

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Failed to update user profile.")
            flash("Unable to update your profile.", "danger")
            return redirect(url_for("main.profile"))
        flash("Profile updated successfully!", "success")
        return redirect(url_for("main.profile"))

    return render_template(
        "profile.html",
        total_projects=Project.query.filter_by(user_id=current_user.id).count(),
        total_analyses=Analysis.query.filter_by(user_id=current_user.id).count(),
        total_reviews=Review.query.filter_by(user_id=current_user.id).count(),
        recent_projects=(
            Project.query.filter_by(user_id=current_user.id)
            .order_by(Project.upload_date.desc())
            .limit(5)
            .all()
        ),
    )


@main.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    flash("Change Password feature is coming soon.", "info")
    return redirect(url_for("main.profile"))


@main.route("/profile-picture/<filename>")
@login_required
def profile_picture(filename):
    profile_folder = os.path.join(
        current_app.root_path,
        current_app.config["UPLOAD_FOLDER"],
        "profile_pics",
    )
    return send_from_directory(profile_folder, filename)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


@main.app_errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@main.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            msg = Message(
                subject="New Contact Form Message",
                recipients=[current_app.config.get("SUPPORT_EMAIL", "supportsentrix@gmail.com")],
            )
            msg.body = (
                f"Name: {form.name.data}\n\nEmail: {form.email.data}\n\n"
                f"Message:\n\n{form.message.data}"
            )
            mail.send(msg)
            flash("Your message has been sent successfully.", "success")
            return redirect(url_for("main.contact"))
        except Exception:
            current_app.logger.exception("Contact email delivery failed.")
            flash("Unable to send your message right now.", "danger")
    return render_template("contact.html", form=form)


@main.route("/forbidden")
def forbidden():
    abort(403)


@main.route("/server-error")
def server_error_test():
    abort(500)


@main.route("/reviews", methods=["GET", "POST"])
def reviews():
    form = ReviewForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please login to submit a review.", "warning")
            return redirect(url_for("main.login"))
        create_review(
            user_id=current_user.id,
            rating=form.rating.data,
            title=form.title.data,
            comment=form.comment.data,
        )
        flash("Your review has been submitted!", "success")
        return redirect(url_for("main.reviews"))
    return render_template(
        "reviews.html",
        reviews=get_all_reviews(),
        review_stats=get_review_statistics(),
        form=form,
    )


@main.route("/reviews/edit/<int:review_id>", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    review = get_review(review_id)
    if review.user_id != current_user.id:
        abort(403)
    form = ReviewForm(obj=review)
    if form.validate_on_submit():
        update_review(review, form.rating.data, form.title.data, form.comment.data)
        flash("Review updated successfully!", "success")
        return redirect(url_for("main.reviews"))
    return render_template("edit_review.html", form=form, review=review)


@main.route("/reviews/delete/<int:review_id>", methods=["POST"])
@login_required
def remove_review(review_id):
    review = get_review(review_id)
    if review.user_id != current_user.id:
        abort(403)
    delete_review_record(review)
    flash("Review deleted successfully!", "success")
    return redirect(url_for("main.reviews"))


@main.route("/download_report/<int:analysis_id>")
@login_required
def download_report(analysis_id):
    analysis = Analysis.query.filter_by(
        id=analysis_id, user_id=current_user.id
    ).first_or_404()
    if not analysis.report_path:
        flash("Report has not been generated yet.", "warning")
        return redirect(url_for("main.results", analysis_id=analysis.id))

    report_path = os.path.abspath(analysis.report_path)
    if not os.path.isfile(report_path):
        flash("Report file was not found.", "danger")
        return redirect(url_for("main.results", analysis_id=analysis.id))

    return send_file(
        report_path,
        as_attachment=True,
        download_name=f"{secure_filename(analysis.filename)}_report.html",
        mimetype="text/html",
    )
