import unittest

from app import create_app
from database import db
from helpers.review_service import get_review_statistics
from models import Review, User


class TestConfig:
    TESTING = True
    SECRET_KEY = "review-test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    UPLOAD_FOLDER = "uploads"
    PROJECT_FOLDER = "uploads/projects"


class ReviewFlowTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.context = self.app.app_context()
        self.context.push()

        db.drop_all()
        db.create_all()

        self.owner = User(username="owner", email="owner@example.com")
        self.owner.set_password("Password123!")
        self.other = User(username="other", email="other@example.com")
        self.other.set_password("Password123!")
        db.session.add_all([self.owner, self.other])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def login_as(self, user):
        with self.client.session_transaction() as session:
            session["_user_id"] = str(user.id)
            session["_fresh"] = True

    def test_reviews_page_loads_and_contains_star_control(self):
        response = self.client.get("/reviews")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="rating"', response.data)
        self.assertIn(b'data-rating="5"', response.data)

    def test_anonymous_user_cannot_create_review(self):
        response = self.client.post(
            "/reviews",
            data={
                "rating": "5",
                "title": "Excellent platform",
                "comment": "The review workflow works very well.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])
        self.assertEqual(Review.query.count(), 0)

    def test_owner_can_create_edit_and_delete_review(self):
        self.login_as(self.owner)

        create_response = self.client.post(
            "/reviews",
            data={
                "rating": "5",
                "title": "Excellent platform",
                "comment": "The dynamic star rating works correctly.",
            },
        )
        self.assertEqual(create_response.status_code, 302)

        review = Review.query.one()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.title, "Excellent platform")
        self.assertEqual(review.user_id, self.owner.id)

        edit_response = self.client.post(
            f"/reviews/edit/{review.id}",
            data={
                "rating": "4",
                "title": "Updated review",
                "comment": "Editing and saving this review also works.",
            },
        )
        self.assertEqual(edit_response.status_code, 302)

        db.session.refresh(review)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.title, "Updated review")

        delete_response = self.client.post(f"/reviews/delete/{review.id}")
        self.assertEqual(delete_response.status_code, 302)
        self.assertEqual(Review.query.count(), 0)

    def test_user_cannot_edit_or_delete_another_users_review(self):
        review = Review(
            user_id=self.owner.id,
            rating=5,
            title="Owner review",
            comment="Only the owner should be able to change this review.",
        )
        db.session.add(review)
        db.session.commit()

        self.login_as(self.other)

        edit_response = self.client.post(
            f"/reviews/edit/{review.id}",
            data={
                "rating": "1",
                "title": "Unauthorized edit",
                "comment": "This edit must never be stored in the database.",
            },
        )
        self.assertEqual(edit_response.status_code, 403)

        delete_response = self.client.post(f"/reviews/delete/{review.id}")
        self.assertEqual(delete_response.status_code, 403)

        stored_review = db.session.get(Review, review.id)
        self.assertIsNotNone(stored_review)
        self.assertEqual(stored_review.rating, 5)
        self.assertEqual(stored_review.title, "Owner review")

    def test_statistics_update_from_database(self):
        db.session.add_all(
            [
                Review(
                    user_id=self.owner.id,
                    rating=5,
                    title="Five stars",
                    comment="A complete five-star review for statistics.",
                ),
                Review(
                    user_id=self.other.id,
                    rating=3,
                    title="Three stars",
                    comment="A complete three-star review for statistics.",
                ),
            ]
        )
        db.session.commit()

        stats = get_review_statistics()

        self.assertEqual(stats["total_reviews"], 2)
        self.assertEqual(stats["average_rating"], 4.0)
        self.assertEqual(stats["rating_breakdown"][5], 1)
        self.assertEqual(stats["rating_breakdown"][3], 1)
        self.assertEqual(stats["recommendation_percentage"], 50)


if __name__ == "__main__":
    unittest.main()
