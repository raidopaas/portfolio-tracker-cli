from models.goal import Goal, GoalScope, GoalPeriod

def add_goal(conn, goal):
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO goals
            (target_amount, start_date, deadline, scope, period, account_id)
            VALUES(%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            goal.target_amount,
            goal.start_date,
            goal.deadline,
            goal.scope.value,
            goal.period.value,
            goal.account_id
        ))

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

def delete_goals_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM goals")
    finally:
        cursor.close()

def get_goal(conn, period, account_id=None):
    cursor = conn.cursor()

    query = """
        SELECT * FROM goals
        WHERE period = %s
        AND start_date <= CURDATE()
        AND deadline >= CURDATE()
    """

    values = [period]

    if account_id is not None:
        query += "AND account_id = %s"
        values.append(account_id)
    else:
        query += "AND scope = 'portfolio'"

    try:
        cursor.execute(query, values)
        return cursor.fetchone()
    finally:
        cursor.close()