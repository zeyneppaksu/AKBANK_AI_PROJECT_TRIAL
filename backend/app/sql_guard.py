# backend/app/sql_guard.py
import sqlparse
from sqlparse import tokens as T

# only these top-level statements are allowed
ALLOWED_FIRST = {"select", "with"}

# disallowed SQL keywords (checked as real tokens, not substrings)
DISALLOWED_KEYWORDS = {
    "insert", "update", "delete", "drop", "alter", "truncate",
    "create", "grant", "revoke", "vacuum", "analyze", "call", "do",
}

def _iter_words(stmt):
    """
    Yield lowercase keyword-like tokens from a parsed statement.
    We only treat actual SQL keywords as meaningful, not identifiers.
    """
    for tok in stmt.flatten():
        if tok.is_whitespace or tok.ttype in (T.Comment, T.Comment.Single, T.Comment.Multiline):
            continue
        # sqlparse marks keywords with token types under T.Keyword
        if tok.ttype in T.Keyword or tok.ttype in T.DDL or tok.ttype in T.DML:
            yield tok.value.lower()

def assert_read_only(sql: str) -> None:
    sql = (sql or "").strip()
    if not sql:
        raise ValueError("Empty SQL")

    # block multiple statements like "SELECT ...; DROP TABLE ..."
    statements = [s for s in sqlparse.split(sql) if s.strip()]
    if len(statements) != 1:
        raise ValueError("Blocked: multiple SQL statements are not allowed")

    stmt = sqlparse.parse(sql)[0]

    # find first keyword (SELECT/WITH)
    first_kw = None
    for tok in stmt.flatten():
        if tok.is_whitespace:
            continue
        if tok.ttype in T.Keyword or tok.ttype in T.DML:
            first_kw = tok.value.lower()
            break
        # if the first meaningful token is not a keyword (rare), keep scanning
    if first_kw is None:
        raise ValueError("Blocked: could not determine SQL type")

    if first_kw not in ALLOWED_FIRST:
        raise ValueError(f"Blocked: only SELECT/WITH allowed (got: {first_kw})")

    # block any dangerous keyword appearing anywhere as a real keyword token
    for w in _iter_words(stmt):
        if w in DISALLOWED_KEYWORDS:
            raise ValueError(f"Blocked: non read-only SQL keyword detected ({w})")
