def nl_to_sql(question: str) -> str:
    q = question.strip().lower()

    # very small rule set (enough to demo end-to-end)
    if "top" in q and "balance" in q:
        return """
        SELECT c.full_name, a.balance
        FROM customers c
        JOIN accounts a ON a.customer_id = c.customer_id
        ORDER BY a.balance DESC
        LIMIT 5;
        """

    if "transactions" in q and ("last" in q or "recent" in q):
        return """
        SELECT tx_id, account_id, tx_type, amount, created_at
        FROM transactions
        ORDER BY created_at DESC
        LIMIT 20;
        """

    if "accounts" in q and "istanbul" in q:
        return """
        SELECT a.account_id, c.full_name, a.account_type, a.balance
        FROM accounts a
        JOIN customers c ON c.customer_id = a.customer_id
        WHERE c.city = 'Istanbul'
        ORDER BY a.balance DESC;
        """

    # default safe query
    return "SELECT customer_id, full_name, city FROM customers ORDER BY customer_id LIMIT 10;"
