

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