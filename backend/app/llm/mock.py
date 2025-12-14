# backend/app/llm/mock.py

def generate_sql(question: str) -> str:
    q = question.strip().lower()

    if "top" in q and ("balance" in q or "bakiye" in q):
        return """
        SELECT c.first_name, c.last_name, a.balance_try
        FROM accounts a
        JOIN customers c ON c.customer_no = a.customer_no
        ORDER BY a.balance_try DESC
        LIMIT 5;
        """

    if ("recent" in q or "son" in q) and ("transactions" in q or "işlemler" in q):
        return """
        SELECT transaction_no, account_no, transaction_type, amount, currency, transaction_time
        FROM transactions
        ORDER BY transaction_time DESC
        LIMIT 20;
        """

    if "istanbul" in q and ("accounts" in q or "hesap" in q):
        return """
        SELECT a.account_no, c.first_name, c.last_name, a.account_type, a.balance_try
        FROM accounts a
        JOIN customers c ON c.customer_no = a.customer_no
        JOIN branches b ON b.branch_code = a.branch_code
        WHERE b.city = 'İstanbul' OR b.city = 'Istanbul'
        ORDER BY a.balance_try DESC
        LIMIT 50;
        """

    if "kredi" in q and ("redded" in q or "rejected" in q):
        return """
        SELECT decision, COUNT(*) AS cnt
        FROM credit_applications
        GROUP BY decision
        ORDER BY cnt DESC;
        """

    return "SELECT customer_no, first_name, last_name, residence_city FROM customers ORDER BY customer_no LIMIT 10;"
