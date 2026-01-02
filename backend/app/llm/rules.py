# backend/app/llm/rules.py
import re

BASE_RULES = (
    "You are an expert NL-to-SQL assistant for PostgreSQL.\n"
    "Output ONLY one SQL query. No explanation.\n"
    "The SQL MUST start with SELECT or WITH.\n"
    "Read-only only: SELECT/WITH. Never use INSERT/UPDATE/DELETE/CREATE/DROP/ALTER/TRUNCATE.\n"
    "Use ONLY tables and columns from the provided schema. Do NOT invent names.\n"
    "If multiple statements are generated, keep ONLY the first.\n"
    "End the query with a semicolon.\n"
    "- If the user specifies 'top N', use LIMIT N.\n"
    "- If no limit is specified, use LIMIT 50.\n"
)

CUSTOMER_RULES = (
    "CUSTOMER/ACCOUNT RULES:\n"
    "- 'Customer' refers to rows in customers.\n"
    "- Customers may have multiple accounts.\n"
    "- Balances come from accounts.\n"
    "- Join: accounts.customer_no = customers.customer_no.\n"
    "- Total customer balance: SUM(accounts.balance_*).\n"
)

TX_RULES = (
    "TRANSACTION RULES:\n"
    "- Transactions are in islemler.\n"
    "- Join to accounts via islemler.hesap_no = accounts.account_no (or hesap_no, use schema).\n"
    "- Amount: islemler.tutar. Currency: islemler.para_birimi.\n"
    "- Fraud flag: islemler.dolandiricilik_suphesi.\n"
)

CREDIT_RULES = (
    "CREDIT RULES:\n"
    "- Credit applications are in kredi_basvurulari.\n"
    "- Join to customers via kredi_basvurulari.musteri_no = customers.customer_no (use schema).\n"
    "- Decision: kredi_karari. Score: kredi_notu.\n"
)

BRANCH_RULES = (
    "BRANCH RULES:\n"
    "- Branches are in subeler.\n"
    "- Branch code: sube_kodu.\n"
    "- Accounts belong to branches via accounts.branch_code = subeler.sube_kodu (use schema).\n"
)

# Simple keyword router (good enough for a demo)
_PATTERNS = {
    "customer": re.compile(r"\b(customer|customers|musteri|müşteri|balance|bakiye|account|hesap)\b", re.I),
    "tx": re.compile(r"\b(transaction|transactions|islem|işlem|harcama|transfer|tutar|fraud|dolandir)\b", re.I),
    "credit": re.compile(r"\b(credit|loan|kredi|basvuru|başvuru|vade|kredi notu)\b", re.I),
    "branch": re.compile(r"\b(branch|sube|şube|region|bolge|bölge)\b", re.I),
}

def build_domain_rules(question: str) -> str:
    q = (question or "").strip()
    blocks = []

    if _PATTERNS["customer"].search(q):
        blocks.append(CUSTOMER_RULES)
    if _PATTERNS["tx"].search(q):
        blocks.append(TX_RULES)
    if _PATTERNS["credit"].search(q):
        blocks.append(CREDIT_RULES)
    if _PATTERNS["branch"].search(q):
        blocks.append(BRANCH_RULES)

    return "\n".join(blocks).strip()
