"""Production-safe contact and community review route handlers."""

from flask import abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_mail import Message

from extensions import mail
from forms import ContactForm, ReviewForm
from helpers.review_service import (
    create_review,
    delete_review,
    get_all_reviews,
    get_review,
    get_review_statistics,
    update_review,
)


def install_community_routes(blueprint):
    """Replace legacy contact/review handlers with validated implementations."""

    def contact():
        form = ContactForm()

        if form.validate_on_submit():
            recipient = current_app.config.get(
                "SUPPORT_EMAIL", "supportsentrix@gmail.com"
            )

            message = Message(
                subject=f"Sentrix contact: {form.subject.data.strip()}",
                recipients=[recipient],
                reply_to=form.email.data.strip(),
            )
            message.body = (
                f"Name: {form.name.data.strip()}\n"
                f"Email: {form.email.data.strip()}\n"
                f"Subject: {form.subject.data.strip()}\n\n"
                f"Message:\n{form.message.data.strip()}\n"
            )

            try:
                mail.send(message)
            except Exception:
                current_app.logger.exception("Contact message delivery failed")
                flash(
                    "We could not deliver your message right now. "
                    "Please email supportsentrix@gmail.com directly.",
                    "danger",
                )
            else:
                flash("Your message has been sent successfully.", "success")
                return redirect(url_for("main.contact"))

        return render_template(
            "contact.html",
            form=form,
            support_email=current_app.config.get(
                "SUPPORT_EMAIL", "supportsentrix@gmail.com"
            ),
        )

    def reviews():
        form = ReviewForm()

        if form.validate_on_submit():
            if not current_user.is_authenticated:
                flash("Please log in to submit a review.", "warning")
                return redirect(url_for("main.login"))

            create_review(
                user_id=current_user.id,
                rating=form.rating.data,
                title=form.title.data,
                comment=form.comment.data,
            )
            flash("Your review has been published.", "success")
            return redirect(url_for("main.reviews"))

        return render_template(
            "reviews.html",
            form=form,
            reviews=get_all_reviews(),
            review_stats=get_review_statistics(),
        )

    @login_required
    def edit_review(review_id):
        review = get_review(review_id)
        if review.user_id != current_user.id:
            abort(403)

        form = ReviewForm(obj=review)
        if form.validate_on_submit():
            update_review(
                review,
                form.rating.data,
                form.title.data,
                form.comment.data,
            )
            flash("Review updated successfully.", "success")
            return redirect(url_for("main.reviews"))

        return render_template("edit_review.html", form=form, review=review)

    @login_required
    def remove_review(review_id):
        review = get_review(review_id)
        if review.user_id != current_user.id:
            abort(403)

        delete_review(review)
        flash("Review deleted successfully.", "success")
        return redirect(url_for("main.reviews"))

    # Flask blueprints defer URL-rule registration. Replacing the endpoint's
    # view function directly preserves the existing rule without registering
    # a duplicate endpoint during app.register_blueprint().
    blueprint.view_functions["contact"] = contact
    blueprint.view_functions["reviews"] = reviews
    blueprint.view_functions["edit_review"] = edit_review
    blueprint.view_functions["remove_review"] = remove_review
