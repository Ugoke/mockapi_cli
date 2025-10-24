import re


TYPE_MAP = {
    "int": int,
    "float": (float, int),
    "str": str,
    "bool": bool,
    "list": list,
    "dict": dict,
    "any": object,
}
OP_RE = re.compile(r'^(>=|<=|==|!=|>|<)\s*(.+)$')
SIDE_EFFECT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}