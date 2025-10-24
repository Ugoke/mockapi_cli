import json
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError

from ...core.utils import logger
from ...core.io.io import load_mocks
from ...core.django_service.view.http_helpers import apply_delay, default_mock_response, find_matching_mock, maybe_handle_unstable, on_fail_response, on_pass_response, req_path_generate, get_request_data
from ...core.django_service.view.validator import validate
from ...core.django_service.view.constants import SIDE_EFFECT_METHODS


def dynamic_view(request: HttpRequest, path: str | None = None) -> HttpResponse:
    try:
        mocks = load_mocks()
    except Exception as e:
        logger.exception("Failed to load mocks")
        return HttpResponseServerError(
            json.dumps({"error": "failed to load mocks"}, ensure_ascii=False),
            content_type="application/json",
        )

    req_path = req_path_generate(path)
    method = request.method.upper()

    mock = find_matching_mock(mocks, req_path, method)
    if mock is None:
        return HttpResponseNotFound(
            json.dumps({"error": "No mock defined"}, ensure_ascii=False),
            content_type="application/json",
        )

    try:
        apply_delay(mock)
    except Exception:
        logger.exception("Error while applying delay, continuing without failing")

    unstable_resp = maybe_handle_unstable(mock)
    if unstable_resp is not None:
        return unstable_resp

    if method in SIDE_EFFECT_METHODS:
        try:
            data = get_request_data(request)
        except ValueError:
            return HttpResponseBadRequest(
                json.dumps({"error": "invalid json body"}, ensure_ascii=False),
                content_type="application/json",
            )
        except Exception:
            logger.exception("Unexpected error while reading request body")
            return HttpResponseServerError(
                json.dumps({"error": "failed to read request body"}, ensure_ascii=False),
                content_type="application/json",
            )

        try:
            errs = validate(data, mock.get("data", []))
        except Exception:
            logger.exception("Validator raised an exception")
            return HttpResponseServerError(
                json.dumps({"error": "validation failed unexpectedly"}, ensure_ascii=False),
                content_type="application/json",
            )

        if errs:
            return on_fail_response(mock, errs, data)

        return on_pass_response(mock, data)

    return default_mock_response(mock)