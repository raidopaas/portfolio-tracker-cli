from models.goal import Goal, GoalScope, GoalPeriod
import db.goal_repo as goal_repo
from datetime import datetime, date
import calendar
from decimal import Decimal

def add_goal(conn, target_amount, scope, period, account_id=None, deadline=None):
    goal = Goal(
        id=None, 
        target_amount=target_amount, 
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
    add_goal(conn, target_amount, GoalScope.PORTFOLIO, period, account_id=None, deadline=deadline)

def has_portfolio_goal(conn):
    return goal_repo.has_portfolio_goal(conn)

def get_portfolio_deadline(conn):
    return goal_repo.get_portfolio_deadline(conn)

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

def add_mid_goals(conn, end_target, deadline, scope, account_id=None):
    if scope == GoalScope.ACCOUNT and not account_id:
        raise ValueError("Account id is required for account goals.")
    today = datetime.today().date()
    months = calculate_total_months(today, deadline)

    monthly_amount = end_target / months

    if scope == GoalScope.PORTFOLIO:
        add_portfolio_goal(conn, monthly_amount, GoalPeriod.MONTHLY)
    else:
        add_account_goal(conn, monthly_amount, GoalPeriod.MONTHLY, account_id)

    current_year = today.year
    end_year = deadline.year

    for year in range(current_year, end_year + 1):
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)

        if year == current_year:
            start = today
        else:
            start = year_start

        if year == end_year:
            end = deadline
        else:
            end = year_end

        months_in_year = calculate_total_months(start, end)

        yearly_amount = monthly_amount * months_in_year

        if scope == GoalScope.PORTFOLIO:
            add_portfolio_goal(conn, yearly_amount, GoalPeriod.ANNUAL, deadline=end)
        else:
            add_account_goal(conn, yearly_amount, GoalPeriod.ANNUAL, account_id, deadline=end)

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