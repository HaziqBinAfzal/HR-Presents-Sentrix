from pathlib import Path


path = Path("analyzer/routes/main.py")
source = path.read_text(encoding="utf-8")

source = source.replace(
    "    delete_review,\n",
    "    delete_review as delete_review_record,\n",
    1,
)

reviews_marker = """# ============================================================
# REVIEWS
# ============================================================"""
report_marker = "# REPORT DOWNLOAD #"

reviews_start = source.index(reviews_marker)
report_start = source.index(report_marker, reviews_start)

clean_reviews = '''# ============================================================
# REVIEWS
# ============================================================

@main.route("/reviews", methods=["GET", "POST"])
def reviews():
    form = ReviewForm()

    if request.method == "POST" and not current_user.is_authenticated:
        flash("Please login to submit a review.", "warning")
        return redirect(url_for("main.login"))

    if form.validate_on_submit():
        create_review(
            user_id=current_user.id,
            rating=form.rating.data,
            title=form.title.data.strip(),
            comment=form.comment.data.strip(),
        )
        flash("Your review has been submitted!", "success")
        return redirect(url_for("main.reviews"))

    if request.method == "POST":
        flash("Please correct the highlighted review fields.", "danger")

    return render_template(
        "reviews.html",
        reviews=get_all_reviews(),
        review_stats=get_review_statistics(),
        form=form,
    )


# ============================================================
# EDIT REVIEW
# ============================================================

@main.route("/reviews/edit/<int:review_id>", methods=["GET", "POST"])
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
            form.title.data.strip(),
            form.comment.data.strip(),
        )
        flash("Review updated successfully!", "success")
        return redirect(url_for("main.reviews"))

    return render_template("edit_review.html", form=form, review=review)


# ============================================================
# DELETE REVIEW
# ============================================================

@main.route("/reviews/delete/<int:review_id>", methods=["POST"])
@login_required
def remove_review(review_id):
    review = get_review(review_id)

    if review.user_id != current_user.id:
        abort(403)

    delete_review_record(review)
    flash("Review deleted successfully!", "success")
    return redirect(url_for("main.reviews"))


'''

source = source[:reviews_start] + clean_reviews + source[report_start:]

# Remove the second duplicated edit/delete block after report download.
duplicate_marker = """# ============================================================
# EDIT REVIEW
# ============================================================"""
report_start = source.index(report_marker)
duplicate_start = source.find(duplicate_marker, report_start)
if duplicate_start != -1:
    source = source[:duplicate_start].rstrip() + "\n"

path.write_text(source, encoding="utf-8")
