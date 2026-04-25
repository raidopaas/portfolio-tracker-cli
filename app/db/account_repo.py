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