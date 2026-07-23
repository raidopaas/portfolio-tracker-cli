from models.goal import Goal, GoalScope, GoalPeriod
import db.goal_repo as goal_repo
from datetime import datetime, date
import calendar
from decimal import Decimal
import services.account_service as account_service
import services.transaction_service as transaction_service

def add_goal(conn, target_amount, scope, period, account_id=None, deadline=None, start_date=None):
    goal = Goal(
        id=None, 
        target_amount=target_amount,
        start_date=start_date,
        deadline=deadline, 
        scope=scope, 
        period=period, 
        account_id=account_id
    )

    try:
        goal_repo.add_goal(conn, goal)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError("Adding goal failed") from e
    
def add_account_goal(conn, target_amount, period, account_id, deadline=None):
    add_goal(conn, target_amount, GoalScope.ACCOUNT, period, account_id, deadline)

def add_portfolio_goal(conn, target_amount, period, deadline=None):
    today = date.today()
    add_goal(conn, target_amount, GoalScope.PORTFOLIO, period, account_id=None, deadline=deadline, start_date=today)

def has_portfolio_goal(conn):
    return goal_repo.has_portfolio_goal(conn)

def get_portfolio_deadline(conn):
    return goal_repo.get_portfolio_deadline(conn)

def get_portfolio_start_date(conn):
    return goal_repo.get_portfolio_start_date(conn)

def validate_deadline(month, year):
    month = int(month)
    year = int(year)

    if month < 1 or month > 12:
        raise ValueError("Invalid month input (must be between 1 and 12).")
    
    today = date.today()

    if year == today.year and month == today.month:
        raise ValueError("Deadline must be at least one 1 month in the future.")

    last_day = calendar.monthrange(year, month)[1]
    deadline = date(year, month, last_day)

    if deadline < today:
        raise ValueError("Deadline must be in the future.")
    
    return deadline

def calculate_total_months(start_date, end_date):
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1

def get_adjusted_monthly_proxy(conn, account=None):
    today = date.today()

    if account:
        goal = get_goal(conn, account.id, GoalPeriod.TOTAL)
    else:
        goal = get_portfolio_goal(conn, GoalPeriod.TOTAL)

    if not goal:
        return None

    if account:
        actual = account.balance
    else:
        accounts = account_service.get_cash_accounts(conn)
        actual = Decimal("0.00")
        for acc in accounts:
            actual += acc.balance

    months_remaining = calculate_total_months(today, goal.deadline)

    if months_remaining <= 0:
        return 0
    
    remaining = max(goal.target_amount - actual, Decimal("0.00"))

    return remaining / months_remaining

def get_adjusted_monthly(conn, yearly_goal_amount, account=None):
    today = date.today()
    start_date = today
    deadline = get_portfolio_deadline(conn)

    if account:
        yearly_actual = transaction_service.get_account_total(conn, account.id, today.year)
    else:
        accounts = account_service.get_cash_accounts(conn)
        totals = transaction_service.get_totals(conn, accounts, today.year)
        yearly_actual = totals["Grand Total"]

    remaining = max(yearly_goal_amount - yearly_actual, Decimal("0.00"))

    if deadline.year == today.year:
        months = deadline.month
    elif start_date.year == today.year:
        months = 12 - start_date.month + 1
    else:
        months = 12

    return remaining / months

def get_adjusted_yearly(conn, account=None):
    today = date.today()
    adjusted_monthly = get_adjusted_monthly_proxy(conn, account)
    start_date = get_portfolio_start_date(conn)
    deadline = get_portfolio_deadline(conn)

    if deadline.year == today.year:
        months = deadline.month
    elif start_date.year == today.year:
        months = 12 - start_date.month + 1
    else:
        months = 12

    if adjusted_monthly is None:
        return None

    return months * adjusted_monthly

def get_goal(conn, account_id, period):
    today = date.today()

    if period == GoalPeriod.MONTHLY:
        row = goal_repo.get_account_monthly_goal(conn, account_id)
        return Goal.from_row(row) if row else None
    elif period == GoalPeriod.ANNUAL:
        row = goal_repo.get_annual_goal(conn, account_id, today.year)
        return Goal.from_row(row) if row else None
    elif period == GoalPeriod.TOTAL:
        row = goal_repo.get_total_goal(conn, account_id)
        return Goal.from_row(row) if row else None
    
def get_portfolio_goal(conn, period):
    today = date.today()

    if period == GoalPeriod.MONTHLY:
        row = goal_repo.get_portfolio_monthly_goal(conn)
        return Goal.from_row(row) if row else None
    elif period == GoalPeriod.ANNUAL:
        row = goal_repo.get_annual_portfolio_goal(conn, today.year)
        return Goal.from_row(row) if row else None
    elif period == GoalPeriod.TOTAL:
        row = goal_repo.get_total_portfolio_goal(conn)
        return Goal.from_row(row) if row else None
    
def update_portfolio_goal(conn, end_target):
    try:
        goal_repo.update_portfolio_goal(conn, end_target)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    
def calculate_progress(actual, target):
    if target == Decimal("0.00"):
        return Decimal("0.00")
    
    return (actual / target) * Decimal("100")

def get_account_goals(conn, account_id):
    return {
        "monthly": get_goal(conn, account_id, GoalPeriod.MONTHLY),
        "yearly": get_goal(conn, account_id, GoalPeriod.ANNUAL),
        "total": get_goal(conn, account_id, GoalPeriod.TOTAL)
    }

def get_portfolio_goals(conn):
    return {
        "monthly": get_portfolio_goal(conn, GoalPeriod.MONTHLY),
        "yearly": get_portfolio_goal(conn, GoalPeriod.ANNUAL),
        "total": get_portfolio_goal(conn, GoalPeriod.TOTAL)
    }

def reset_goals(conn):
    try:
        goal_repo.delete_goals_table(conn)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError("Reseting goals failed") from e