

def add_transaction(conn, transaction):
    cursor = conn.cursor()

    query = "INSERT INTO transactions(account_id, amount, description) VALUES(%s, %s, %s)"

    values = (
        transaction.account_id,
        transaction.amount,
        transaction.description
    )

    try:
        cursor.execute(query, values)
    finally:
        cursor.close()


def delete_transactions_table(conn):
    cursor = conn.cursor() 
    try:
        cursor.execute("DELETE FROM transactions")
    finally:
        cursor.close()

def get_transactions_for_account(conn, account_id, year, month):
    cursor = conn.cursor()

    query = """
        SELECT t.*, a.currency
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE account_id = %s
    """
    params = [account_id]

    if year is not None:
        query += " AND YEAR(txn_date) = %s"
        params.append(year)

    if month is not None:
        query += " AND MONTH(txn_date) = %s"
        params.append(month)

    query += " ORDER BY txn_date"

    try:
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()