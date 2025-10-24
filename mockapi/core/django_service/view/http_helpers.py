import time
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from typing import Any
import json
from faker import Faker
import random

from .form_parser import parse_form_to_obj
from ...utils import logger


def _get_method(mock, method) -> bool:
    method_value = mock.get("method", "GET")

    if isinstance(method_value, str):
        return method_value == method
    elif isinstance(method_value, list):
        return method in [m for m in method_value]
    return False


def _get_or_generate_response(data: dict, user_response = None, errs: list[str]|None = None) -> dict:
    if data.get("generate_response"):   
        response_to_gen: dict = data["generate_response"]
        locale: str = response_to_gen["locale"]
        count: int|list[int, int] = response_to_gen["count"]
        template = response_to_gen.get("response", {})
        response: list[dict] = []

        if isinstance(count, list):
            min_count, max_count = count
            count: int = random.randint(min_count, max_count)

        templates: list[dict[str, Any]]
        if isinstance(template, dict):
            templates = [template]
        elif isinstance(template, list):
            templates = [t if isinstance(t, dict) else {"value": t} for t in template]
        else:
            templates = [{"value": template}]

        for _ in range(count):
            tpl = templates[0] if len(templates) == 1 else random.choice(templates)
            item: dict[str, Any] = {}
            for field_name, tmpl_val in tpl.items():
                try:
                    item[field_name] = _generate_fake_data(tmpl_val, locale)
                except:
                    item[field_name] = tmpl_val
            response.append(item)
        return response
    else:
        shuffle_flag = data.get("shuffle")
        
        if errs:
            response = data.get("response", {"errors": errs})
        response = data.get("response")

        if not response and data.get("fallback_data"):
            response = user_response

        if shuffle_flag:
            random.shuffle(response)

        return response


def req_path_generate(path: str|None) -> str:
    """Generate canonical request path, honoring APPEND_SLASH setting."""
    path = (path or "").lstrip("/")
    if getattr(settings, "APPEND_SLASH", False) and path and not path.endswith("/"):
        path = path + "/"
    return "/" + path


def _make_response(data: Any, status: int = 200):
    """Return JsonResponse for dict/list, otherwise raw JSON HttpResponse."""
    if isinstance(data, (dict, list)):
        return JsonResponse(data, safe=not isinstance(data, list), status=status)
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json", status=status)


def get_request_data(request) -> Any:
    """Return parsed request body: JSON when content-type is application/json else parsed form/files."""
    if request.content_type and "application/json" in request.content_type:
        try:
            body = request.body.decode() if hasattr(request, "body") else ""
            return json.loads(body or "{}")
        except Exception:
            raise ValueError("invalid json")
    return parse_form_to_obj(request.POST, request.FILES)


def _generate_fake_data(field_name: str | list[int, int], locale: str = "en_US") -> str | int:
    fake = Faker(locale)

    if isinstance(field_name, str) and ".unGen" in field_name:
        return field_name.replace(".unGen", "")

    if isinstance(field_name, str) and hasattr(fake, field_name):
        faker_function = getattr(fake, field_name)
        if callable(faker_function):
            return faker_function()

    if isinstance(field_name, list):
        if len(field_name) == 3:
            return round(random.uniform(field_name[0], field_name[1]), field_name[2])
        return random.randint(field_name[0], field_name[1])

    return field_name


def find_matching_mock(mocks: list[dict[str, Any]], req_path: str, method: str) -> dict[str, Any]|None:
    for m in mocks:
        try:
            if m.get("path") == req_path and _get_method(m, method):
                return m
        except Exception:
            logger.exception("Error while checking mock entry, skipping it")
    return None


def apply_delay(mock: dict[str, Any]) -> None:
    delay = mock.get("delay")
    if delay is None:
        return

    if isinstance(delay, (int, float)):
        if delay < 0:
            logger.warning("Negative delay ignored: %s", delay)
            return
        time.sleep(delay)
        return

    if isinstance(delay, list):
        if len(delay) == 2:
            a, b = delay
            if not (isinstance(a, int) and isinstance(b, int)):
                logger.warning("Expected ints for 2-element delay list, got: %r", delay)
                return
            time.sleep(random.randint(a, b))
            return
        if len(delay) == 3:
            a, b, prec = delay
            if not (isinstance(a, (int, float)) and isinstance(b, (int, float)) and isinstance(prec, int)):
                logger.warning("Bad types for 3-element delay list, got: %r", delay)
                return
            if prec < 0:
                logger.warning("Negative precision for delay ignored: %r", delay)
                return
            value = round(random.uniform(a, b), prec)
            time.sleep(value)
            return

    logger.warning("Unsupported delay format: %r", delay)


def maybe_handle_unstable(mock: dict[str, Any]) -> HttpResponse|None:
    unstable = mock.get("unstable")
    if not unstable:
        return None

    fail_rate = unstable.get("fail_rate", 0)
    try:
        fail_rate = float(fail_rate)
    except Exception:
        logger.warning("Invalid fail_rate in unstable: %r, defaulting to 0", unstable.get("fail_rate"))
        fail_rate = 0.0

    if not (0.0 <= fail_rate <= 1.0):
        logger.warning("fail_rate out of range [0,1]: %r, clamping", fail_rate)
        fail_rate = max(0.0, min(1.0, fail_rate))

    rnd = random.random()
    if rnd < fail_rate:
        status = unstable.get("status", 400)
        try:
            return _make_response(_get_or_generate_response(unstable), status)
        except Exception:
            logger.exception("Error while generating unstable response")
            return HttpResponseServerError(
                json.dumps({"error": "failed to generate unstable response"}, ensure_ascii=False),
                content_type="application/json",
            )
    return None


def on_fail_response(mock: dict[str, Any], errs: Any, data) -> HttpResponse:
    of = mock.get("on_fail")
    if not of:
        return HttpResponseBadRequest(
            json.dumps({"errors": errs}, ensure_ascii=False),
            content_type="application/json",
        )
    try:
        payload = _get_or_generate_response(of, errs, user_response=data)
        status = of.get("status", 400)
        return _make_response(payload, status)
    except Exception:
        logger.exception("Error while generating on_fail response")
        return HttpResponseServerError(
            json.dumps({"error": "failed to generate on_fail response"}, ensure_ascii=False),
            content_type="application/json",
        )
    

def on_pass_response(mock: dict[str, Any], data) -> HttpResponse:
    op = mock.get("on_pass")
    if op:
        try:
            payload = _get_or_generate_response(op, user_response=data)
            status = op.get("status", mock.get("status", 200))
            return _make_response(payload, status)
        except Exception:
            logger.exception("Error while generating on_pass response")
            return HttpResponseServerError(
                json.dumps({"error": "failed to generate on_pass response"}, ensure_ascii=False),
                content_type="application/json",
            )
    return default_mock_response(mock, data)


def default_mock_response(mock: dict[str, Any], data = None) -> HttpResponse:
    try:
        payload = _get_or_generate_response(mock, user_response=data)
        status = mock.get("status", 200)
        return _make_response(payload, status)
    except Exception:
        logger.exception("Error while generating default mock response")
        return HttpResponseServerError(
            json.dumps({"error": "failed to generate response"}, ensure_ascii=False),
            content_type="application/json",
        )