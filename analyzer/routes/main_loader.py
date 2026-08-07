"""Load the main route blueprint without runtime source-file access.

The Windows standalone build is compiled with Nuitka, so route modules must be
imported normally rather than read from .py files at runtime.
"""

from analyzer.routes.main import main
from helpers.community_routes import install_community_routes

install_community_routes(main)

__all__ = ["main"]
