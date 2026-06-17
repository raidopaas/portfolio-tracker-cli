

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

def get_monthly_goal(conn, account_id, year, month):
    cursor = conn.cursor()
    query = """
        SELECT * FROM goals WHERE 
        account_id = %s 
        AND period = 'monthly' 
        AND YEAR(deadline) = %s
        AND MONTH(deadline) = %s
    """
    values = (account_id, year, month)
    try:
        cursor.execute(query, values)
        return cursor.fetchone()
    finally:
        cursor.close()

def get_annual_goal(conn, account_id, year):
    cursor = conn.cursor()
    query = """
        SELECT * FROM goals WHERE
        account_id = %s 
        AND period = 'annual' 
        AND YEAR(deadline) = %s
    """
    values = (account_id, year)
    try:
        cursor.execute(query, values)
        return cursor.fetchone()
    finally:
        cursor.close()

def get_total_goal(conn, account_id):
    cursor = conn.cursor()
    query = """
        SELECT * FROM goals WHERE
        account_id = %s 
        AND period = 'total'
    """
    values = (account_id,)
    try:
        cursor.execute(query, values)
        return cursor.fetchone()
    finally:
        cursor.close()

def get_monthly_portfolio_goal(conn, year, month):
    cursor = conn.cursor()
    query = """
        SELECT * FROM goals WHERE 
        scope = 'portfolio' 
        AND period = 'monthly' 
        AND YEAR(deadline) = %s
        AND MONTH(deadline) = %s
    """
    values = (year, month)
    try:
        cursor.execute(query, values)
        return cursor.fetchone()
    finally:
        cursor.close()

def get_annual_portfolio_goal(conn, year):
    cursor = conn.cursor()
    query = """
        SELECT * FROM goals WHERE
        scope = 'portfolio'
        AND period = 'annual' 
        AND YEAR(deadline) = %s
    """
    values = (year,)
    try:
        cursor.execute(query, values)
        return cursor.fetchone()
    finally:
        cursor.close()

def get_total_portfolio_goal(conn):
    cursor = conn.cursor()
    query = """
        SELECT * FROM goals WHERE
        scope = 'portfolio' 
        AND period = 'total'
    """
    try:
        cursor.execute(query)
        return cursor.fetchone()
    finally:
        cursor.close()

def delete_goals_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM goals")
    finally:
        cursor.close()
