"""Load the Sentrix main blueprint and install production route extensions."""

from analyzer.routes.main import main
from helpers.community_routes import install_community_routes
from helpers.email_verification import install_email_verification_routes
from helpers.password_reset import install_password_reset_routes


install_email_verification_routes(main)
install_password_reset_routes(main)
install_community_routes(main)
