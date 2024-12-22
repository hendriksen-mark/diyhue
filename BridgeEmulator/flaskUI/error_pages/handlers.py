from flask import Blueprint, render_template
from typing import Tuple

error_pages = Blueprint('error_pages', __name__)

@error_pages.app_errorhandler(404)
def error_404(error: Exception) -> Tuple[str, int]:
    """
    Handle 404 errors (Page Not Found).

    Args:
        error (Exception): The exception that was raised.

    Returns:
        Tuple[str, int]: The rendered template and the HTTP status code.
    """
    return render_template('page-404.html'), 404

@error_pages.app_errorhandler(500)
def error_500(error: Exception) -> Tuple[str, int]:
    """
    Handle 500 errors (Internal Server Error).

    Args:
        error (Exception): The exception that was raised.

    Returns:
        Tuple[str, int]: The rendered template and the HTTP status code.
    """
    return render_template('page-500.html'), 500
