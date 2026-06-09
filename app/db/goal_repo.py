

def add_goal(conn, goal):
    cursor = conn.cursor()

    query = """
    INSERT INTO goals (target_amount, deadline, scope, period, account_id)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        goal.target_amount,
        goal.deadline,
        goal.scope.value,
        goal.period.value,
        goal.account_id
    )

    try:
        cursor.execute(query, values)
    finally:
        cursor.close()

def has_portfolio_goal(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM goals WHERE scope = 'portfolio' LIMIT 1")
        return cursor.fetchone() is not None
    finally:
        cursor.close()

def get_portfolio_deadline(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT deadline FROM goals WHERE scope = 'portfolio' AND period = 'total'")
        return cursor.fetchone()[0]
    finally:
        cursor.close()

def get_goals_for_account(conn, account_id):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM goals WHERE account_id = %s", (account_id,))
        return cursor.fetchall()
    finally:
        cursor.close()

def delete_goals_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM goals")
    finally:
        cursor.close()
