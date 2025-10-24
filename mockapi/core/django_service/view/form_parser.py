import json
import re
from typing import Any


def _parse_form_key_to_parts(key: str) -> list[str]:
    """Turn 'a[b][0][c]' or 'a.b.0' into ['a','b','0','c']"""
    k = key.replace("]", "").replace("[", ".")
    return [p for p in re.split(r"\.", k) if p != ""]


def _set_in(obj: list, parts: list[str], value: Any) -> None:
    """
    Set value into nested structure `obj` according to `parts`.
    Supports dicts and lists (numeric parts -> list indices).
    This implementation favors predictable behavior:
    - If current context is dict -> use dict keys.
    - If list is encountered -> use first element as dict container for named keys.
    - Numeric indices in dict are stored as string keys.
    """
    cur = obj
    for i, part in enumerate(parts):
        is_last = i == len(parts) - 1

        if part.isdigit():
            idx = int(part)
            if isinstance(cur, list):
                # ensure length
                while len(cur) <= idx:
                    cur.append({})
                if is_last:
                    cur[idx] = value
                else:
                    if not isinstance(cur[idx], (dict, list)):
                        cur[idx] = {}
                    cur = cur[idx]
            elif isinstance(cur, dict):
                # store numeric index as string key in dict
                key = str(idx)
                if is_last:
                    cur[key] = value
                else:
                    if key not in cur or not isinstance(cur[key], (dict, list)):
                        cur[key] = {}
                    cur = cur[key]
            else:
                # unknown container: replace/stop
                if is_last:
                    # can't assign back to parent reliably, so skip
                    return
                else:
                    cur = {}
        else:
            # non-numeric part
            if isinstance(cur, dict):
                if is_last:
                    cur[part] = value
                else:
                    if part not in cur or not isinstance(cur[part], (dict, list)):
                        cur[part] = {}
                    cur = cur[part]
            elif isinstance(cur, list):
                # use first element as dict container
                if len(cur) == 0 or not isinstance(cur[0], dict):
                    cur.insert(0, {})
                if is_last:
                    cur[0][part] = value
                else:
                    if part not in cur[0] or not isinstance(cur[0][part], (dict, list)):
                        cur[0][part] = {}
                    cur = cur[0][part]
            else:
                # unknown container: create a dict and continue
                if is_last:
                    return
                cur = {part: {}}


def parse_form_to_obj(post, files) -> dict:
    """
    Converts Django POST/FILES (with getlist interface) into nested python object.
    Attempts to json.loads single-string values when possible.
    """
    out: dict = {}
    for key in post:
        vals = post.getlist(key)
        parts = _parse_form_key_to_parts(key)
        value = vals if len(vals) > 1 else vals[0]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                value = parsed
            except Exception:
                pass
        _set_in(out, parts, value)

    for key in files:
        fvals = files.getlist(key)
        parts = _parse_form_key_to_parts(key)
        value = fvals if len(fvals) > 1 else fvals[0]
        _set_in(out, parts, value)

    return out