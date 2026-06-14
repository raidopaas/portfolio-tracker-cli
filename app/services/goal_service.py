from models.goal import Goal, GoalScope, GoalPeriod
import db.goal_repo as goal_repo
from datetime import datetime, date
import calendar
from decimal import Decimal

def add_goal(conn, target_amount, deadline, scope, period, account_id=None):
    goal = Goal(
        id=None, 
        target_amount=target_amount, 
        deadline=deadline, 
        scope=scope, 
        period=period, 
        account_id=account_id
    )

    try:
        validate_goal(conn, goal)
        goal_repo.add_goal(conn, goal)
        conn.commit()
    except ValueError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise
    
def validate_goal(conn, goal):
    if goal.deadline <= datetime.today().date():
        raise ValueError("Goal deadline cannot be today or less.")

def has_portfolio_goal(conn):
    return goal_repo.has_portfolio_goal(conn)

def get_portfolio_deadline(conn):
    return goal_repo.get_portfolio_deadline(conn)

def add_account_mid_goals(conn, target_amount, deadline, account_id):
    today = datetime.today().date()
    full_years = deadline.year - today.year
    full_months = 12 - today.month + 12 * full_years
    monthly_contribution = target_amount / full_months
    yearly_contribution = monthly_contribution * 12
    annual_contribution = monthly_contribution * (12 - today.month)
    annual_deadline = date(today.year, 12, 31)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_of_month = date(today.year, today.month, last_day)
    add_goal(conn, annual_contribution, annual_deadline, GoalScope.ACCOUNT, GoalPeriod.ANNUAL, account_id)
    add_goal(conn, monthly_contribution, end_of_month, GoalScope.ACCOUNT, GoalPeriod.MONTHLY, account_id)
    for index in range(0, full_years):
        annual_deadline = date(today.year + index + 1, 12, 31)
        add_goal(conn, yearly_contribution, annual_deadline, GoalScope.ACCOUNT, GoalPeriod.ANNUAL, account_id)

def add_mid_goals(conn, end_target, deadline):
    today = datetime.today().date()
    full_years = deadline.year - today.year
    full_months = 12 - today.month + 12 * full_years
    monthly_contribution = end_target / full_months
    yearly_contribution = monthly_contribution * 12
    annual_contribution = monthly_contribution * (12 - today.month)
    annual_deadline = date(today.year, 12, 31)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_of_month = date(today.year, today.month, last_day)
    add_goal(conn, annual_contribution, annual_deadline, GoalScope.PORTFOLIO, GoalPeriod.ANNUAL)
    add_goal(conn, monthly_contribution, end_of_month, GoalScope.PORTFOLIO, GoalPeriod.MONTHLY)
    for index in range(0, full_years):
        annual_deadline = date(today.year + index + 1, 12, 31)
        add_goal(conn, yearly_contribution, annual_deadline, GoalScope.PORTFOLIO, GoalPeriod.ANNUAL)

def get_goal(conn, account_id, period):
    today = date.today()

    if period == GoalPeriod.MONTHLY:
        row = goal_repo.get_monthly_goal(conn, account_id, today.year, today.month)
        return Goal.from_row(row) if row else None
    elif period == GoalPeriod.ANNUAL:
        row = goal_repo.get_annual_goal(conn, account_id, today.year)
        return Goal.from_row(row) if row else None
    elif period == GoalPeriod.TOTAL:
        row = goal_repo.get_total_goal(conn, account_id)
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

def reset_goals(conn):
    try:
        goal_repo.delete_goals_table(conn)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError("Reseting goals failed") from e