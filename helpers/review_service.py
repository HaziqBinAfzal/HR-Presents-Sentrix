from sqlalchemy import func

from database import db
from models import Review


def create_review(user_id, rating, title, comment):
    """
    Create a new review.
    """

    review = Review(
        user_id=user_id,
        rating=rating,
        title=title.strip(),
        comment=comment.strip()
    )

    db.session.add(review)
    db.session.commit()

    return review


def update_review(review, rating, title, comment):
    """
    Update an existing review.
    """

    review.rating = rating
    review.title = title.strip()
    review.comment = comment.strip()

    db.session.commit()

    return review


def delete_review(review):
    """
    Delete a review.
    """

    db.session.delete(review)
    db.session.commit()


def get_review(review_id):
    """
    Return a review by ID.
    """

    return Review.query.get_or_404(review_id)


def get_latest_reviews(limit=3):
    """
    Return latest reviews.
    """

    return (
        Review.query
        .order_by(Review.created_at.desc())
        .limit(limit)
        .all()
    )


def get_all_reviews():
    """
    Return all reviews.
    """

    return (
        Review.query
        .order_by(Review.created_at.desc())
        .all()
    )


def get_average_rating():
    """
    Return average review rating.
    """

    average = (
        db.session.query(
            func.avg(Review.rating)
        ).scalar()
    )

    return round(average or 0, 1)


def get_total_reviews():
    """
    Return total number of reviews.
    """

    return Review.query.count()


def get_rating_breakdown():
    """
    Return star counts.
    """

    breakdown = {}

    for star in range(5, 0, -1):

        breakdown[star] = (
            Review.query.filter_by(
                rating=star
            ).count()
        )

    return breakdown


def get_review_statistics():
    """
    Return all review statistics.
    """

    total_reviews = get_total_reviews()

    average_rating = get_average_rating()

    breakdown = get_rating_breakdown()

    five_star = breakdown.get(5, 0)

    recommendation_percentage = (
        round((five_star / total_reviews) * 100)
        if total_reviews
        else 0
    )

    return {
        "average_rating": average_rating,
        "total_reviews": total_reviews,
        "rating_breakdown": breakdown,
        "recommendation_percentage": recommendation_percentage
    }
