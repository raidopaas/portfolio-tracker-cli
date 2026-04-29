from models.account import Account

def add_account(conn, account):
    cursor = conn.cursor()

    query = """
    INSERT INTO accounts (account_name, account_type, currency)
    VALUES (%s, %s, %s)
    """

    values = (
        account.name,
        account.account_type,
        account.currency
    )

    try:
        cursor.execute(query, values)
    finally:
        cursor.close()

def delete_accounts_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM accounts")
    finally:
        cursor.close()

def account_exists(conn, name, currency):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM accounts WHERE LOWER(account_name) = LOWER(%s) AND currency = %s LIMIT 1", (name, currency))
        return cursor.fetchone() is not None
    finally:
        cursor.close()

def count_broker_accounts(conn, currency):
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM accounts WHERE account_type = 'broker' AND currency = %s", (currency,))
        return cursor.fetchone()[0]
    finally:
        cursor.close()

def get_broker_account(conn, currency):
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM accounts WHERE account_type = 'broker' AND currency = %s", (currency,))
        return cursor.fetchone()
    finally:
        cursor.close()