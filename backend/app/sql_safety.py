# backend/app/sql_safety.py
import re

READONLY_START = re.compile(r"^\s*(with|select)\b", re.IGNORECASE)

# Block obvious non-read-only keywords (simple but effective)
BLOCKLIST = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|vacuum|analyze|copy)\b",
    re.IGNORECASE,
)

def assert_read_only(sql: str) -> None:
    if not sql or not READONLY_START.search(sql):
        raise ValueError("Only SELECT/WITH queries are allowed.")
    if BLOCKLIST.search(sql):
        raise ValueError("Blocked: non read-only SQL detected.")

def ensure_limit(sql: str, default_limit: int = 50, max_limit: int = 200) -> str:
    """
    If query has no LIMIT, add LIMIT default_limit.
    If it has LIMIT > max_limit, clamp it to max_limit.
    Very simple parsing (works for typical single-statement queries).
    """
    s = sql.strip().rstrip(";")

    # If user runs aggregate count or single scalar, allow no limit
    if re.search(r"\bcount\s*\(", s, re.IGNORECASE):
        return s + ";"

    m = re.search(r"\blimit\s+(\d+)\b", s, re.IGNORECASE)
    if not m:
        return f"{s}\nLIMIT {default_limit};"

    lim = int(m.group(1))
    if lim > max_limit:
        s = re.sub(r"\blimit\s+\d+\b", f"LIMIT {max_limit}", s, flags=re.IGNORECASE)
    return s + ";"
