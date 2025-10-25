import json
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError

from ...core.utils import logger
from ...core.io.io import load_mocks
from ...core.django_service.view.http_helpers import apply_delay, default_mock_response, find_matching_mock, maybe_handle_unstable, on_fail_response, on_pass_response, req_path_generate, get_request_data
from ...core.django_service.view.validator import validate
from ...core.django_service.view.constants import SIDE_EFFECT_METHODS


class DynamicViewHandler:
    """
    A handler class for dynamic HTTP mock processing.
    Splits logic into smaller methods for readability and scalability.
    """

    def __init__(self, request: HttpRequest, path: str | None = None):
        self.request = request
        self.path = path
        self.method = request.method.upper()
        self.mocks = None
        self.mock = None

    # ---------- Entry point ----------
    def handle(self) -> HttpResponse:
        """Main entry point (replaces the dynamic_view function)."""
        if not self._load_mocks():
            return self._error_response("failed to load mocks", HttpResponseServerError)

        self._prepare_request_path()

        if not self._find_mock():
            return self._error_response("No mock defined", HttpResponseNotFound)

        self._apply_delay_safe()
        unstable_response = self._handle_unstable()
        if unstable_response:
            return unstable_response

        if self.method in SIDE_EFFECT_METHODS:
            return self._handle_side_effect_method()

        return self._default_response()

    # ---------- Processing steps ----------

    def _load_mocks(self) -> bool:
        """Load mocks safely with error handling."""
        try:
            self.mocks = load_mocks()
            return True
        except Exception:
            logger.exception("Failed to load mocks")
            return False

    def _prepare_request_path(self):
        """Prepare and normalize the request path."""
        self.req_path = req_path_generate(self.path)

    def _find_mock(self) -> bool:
        """Find the matching mock."""
        self.mock = find_matching_mock(self.mocks, self.req_path, self.method)
        return self.mock is not None

    def _apply_delay_safe(self):
        """Apply delay safely (non-critical if it fails)."""
        try:
            apply_delay(self.mock)
        except Exception:
            logger.exception("Error while applying delay, continuing without failing")

    def _handle_unstable(self) -> HttpResponse | None:
        """Handle unstable responses (if mock defines one)."""
        return maybe_handle_unstable(self.mock)

    # ---------- Side-effect methods ----------
    def _handle_side_effect_method(self) -> HttpResponse:
        """Handle methods that modify state (POST, PUT, DELETE, etc.)."""
        data = self._get_request_data_safe()
        if isinstance(data, HttpResponse):
            return data

        errs = self._validate_data_safe(data)
        if isinstance(errs, HttpResponse):
            return errs

        if errs:
            return on_fail_response(self.mock, errs, data)

        return on_pass_response(self.mock, data)

    def _get_request_data_safe(self):
        """Safely extract data from the request body."""
        try:
            return get_request_data(self.request)
        except ValueError:
            return self._error_response("invalid json body", HttpResponseBadRequest)
        except Exception:
            logger.exception("Unexpected error while reading request body")
            return self._error_response("failed to read request body", HttpResponseServerError)

    def _validate_data_safe(self, data):
        """Validate request data with safety wrappers."""
        try:
            return validate(data, self.mock.get("data", []))
        except Exception:
            logger.exception("Validator raised an exception")
            return self._error_response("validation failed unexpectedly", HttpResponseServerError)

    def _default_response(self) -> HttpResponse:
        """Return default response for non-side-effect methods."""
        return default_mock_response(self.mock)

    # ---------- Helpers ----------
    def _error_response(self, message: str, response_class) -> HttpResponse:
        """Generate a standardized JSON error response."""
        return response_class(
            json.dumps({"error": message}, ensure_ascii=False),
            content_type="application/json",
        )


# -------------------------------
# Example usage:
# -------------------------------
def dynamic_view(request: HttpRequest, path: str | None = None) -> HttpResponse:
    return DynamicViewHandler(request, path).handle()