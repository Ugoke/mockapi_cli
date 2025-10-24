from typing import Any
import json
import re

from .constants import TYPE_MAP, OP_RE


def _get_by_dotted(obj: Any, dotted: str) -> tuple[bool, Any]:
    """Get nested value by dotted path. Returns (found, value)."""
    if not dotted:
        return False, None
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict):
            if part in cur:
                cur = cur[part]
            else:
                return False, None
        elif isinstance(cur, list):
            try:
                i = int(part)
            except Exception:
                return False, None
            if 0 <= i < len(cur):
                cur = cur[i]
            else:
                return False, None
        else:
            return False, None
    return True, cur


def _matches_type(val: Any, expected: str) -> bool:
    """Type checking according to _TYPE_MAP (case-insensitive)."""
    if not expected or expected.lower() == "any":
        return True
    t = TYPE_MAP.get(expected.lower())
    if t is None:
        # allow custom class names from globals if present
        return isinstance(val, globals().get(expected, object))
    if isinstance(t, tuple):
        # avoid bool being treated as int
        if int in t and isinstance(val, bool):
            return False
        return isinstance(val, t)
    return isinstance(val, t)


def _safe_parse(s: str) -> Any:
    """Try json.loads, then int, then float, otherwise return raw string."""
    try:
        return json.loads(s)
    except Exception:
        try:
            return int(s)
        except Exception:
            try:
                return float(s)
            except Exception:
                return s


class ConditionEvaluator:
    def evaluate(self, val: Any, cond) -> tuple[bool, str]:
        if cond is None:
            return True, ""

        if isinstance(cond, dict):
            op = str(cond.get("op", "")).lower()
            cmp = cond.get("value")
            return self._dispatch(val, op, cmp)

        s = str(cond).strip()

        if s.startswith("regex:"):
            op, cmp = "regex", s[len("regex:"):]
            return self._dispatch(val, op, cmp)

        if s.startswith("in "):
            op, cmp = "in", _safe_parse(s[3:].strip())
            return self._dispatch(val, op, cmp)

        if s.startswith("not_in "):
            op, cmp = "not_in", _safe_parse(s[7:].strip())
            return self._dispatch(val, op, cmp)

        if s.startswith("min_length"):
            num = int(re.sub(r"\D", "", s) or 0)
            return self._dispatch(val, "min_length", num)

        if s.startswith("max_length"):
            num = int(re.sub(r"\D", "", s) or 0)
            return self._dispatch(val, "max_length", num)

        if s.startswith("between"):
            parts = s.split()
            if len(parts) == 3:
                try:
                    low, high = float(parts[1]), float(parts[2])
                    try:
                        ok = low <= float(val) <= high
                        return ok, "" if ok else f"{val} not between {low} and {high}"
                    except Exception:
                        return False, f"{val} not between {low} and {high}"
                except Exception:
                    return False, f"invalid numbers in between: {s}"
            return False, f"invalid between format: {s}"

        m = OP_RE.match(s)
        if m:
            op, cmp = m.group(1), _safe_parse(m.group(2))
        else:
            op, cmp = "==", _safe_parse(s)

        return self._dispatch(val, op, cmp)

    def _dispatch(self, val: Any, op: str, cmp: Any) -> tuple[bool, str]:
        """
        Dispatch operation to specific handler and catch exceptions uniformly.
        """
        try:
            if op in (">", ">=", "<", "<=", "==", "!="):
                return self._handle_comparison(val, op, cmp)

            if op == "in":
                return self._handle_in(val, cmp)

            if op == "not_in":
                return self._handle_not_in(val, cmp)

            if op == "regex":
                return self._handle_regex(val, cmp)

            if op == "min_length":
                return self._handle_min_length(val, cmp)

            if op == "max_length":
                return self._handle_max_length(val, cmp)
        except Exception as e:
            return False, f"eval error {e}"

        return False, f"unknown op {op}"

    # ---------------- handlers ----------------

    def _handle_comparison(self, val: Any, op: str, cmp: Any) -> tuple[bool, str]:
        left, right = val, cmp
        if op == "==":
            ok = left == right
        elif op == "!=":
            ok = left != right
        elif op == ">":
            ok = left > right
        elif op == ">=":
            ok = left >= right
        elif op == "<":
            ok = left < right
        else:  # "<="
            ok = left <= right
        return ok, "" if ok else f"{left} {op} {right}"

    def _handle_in(self, val: Any, cmp: Any) -> tuple[bool, str]:
        ok = (val in cmp) if isinstance(cmp, (list, tuple, set)) else (str(val) in str(cmp))
        return ok, "" if ok else f"{val} not in {cmp}"

    def _handle_not_in(self, val: Any, cmp: Any) -> tuple[bool, str]:
        ok = not ((val in cmp) if isinstance(cmp, (list, tuple, set)) else (str(val) in str(cmp)))
        return ok, "" if ok else f"{val} in {cmp}"

    def _handle_regex(self, val: Any, pattern: Any) -> tuple[bool, str]:
        if not isinstance(val, str):
            return False, "regex requires string"
        ok = re.search(str(pattern), val) is not None
        return ok, "" if ok else f"does not match {pattern}"

    def _handle_min_length(self, val: Any, min_len: int) -> tuple[bool, str]:
        try:
            ok = len(val) >= int(min_len)
        except Exception:
            return False, "no length"
        return ok, "" if ok else f"len {len(val)} < {min_len}"

    def _handle_max_length(self, val: Any, max_len: int) -> tuple[bool, str]:
        try:
            ok = len(val) <= int(max_len)
        except Exception:
            return False, "no length"
        return ok, "" if ok else f"len {len(val)} > {max_len}"


def _eval_condition(val: Any, cond) -> tuple[bool, str]:
    return ConditionEvaluator().evaluate(val, cond)


def validate(target: Any, rules: list[dict]) -> list[str]:
    """
    Validate `target` (dict or list) against list of rule dicts.
    Each rule: { name: 'a.b', type: 'int', if: condition, ... }
    Returns list of error messages.
    """
    errs: list[str] = []
    targets = [(f"[{i}]", it) for i, it in enumerate(target)] if isinstance(target, list) else [("", target)]
    for pref, targ in targets:
        for r in (rules or []):
            name = r.get("name")
            if not name:
                errs.append(f"{pref}: rule without name")
                continue
            ok, val = _get_by_dotted(targ, name)
            if not ok:
                errs.append(f"{pref}.{name}: missing")
                continue
            if not _matches_type(val, r.get("type", "any")):
                errs.append(f"{pref}.{name}: type {r.get('type')} != {type(val).__name__}")
                continue
            if "if" in r:
                ok2, msg = _eval_condition(val, r["if"])
                if not ok2:
                    errs.append(f"{pref}.{name}: {msg}")
    return errs