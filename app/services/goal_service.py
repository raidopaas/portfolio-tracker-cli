import db.goal_repo as goal_repo
from datetime import date
from decimal import Decimal
import calendar
from models.goal import Goal, GoalScope, GoalPeriod
import services.account_service as account_service

def has_portfolio_goal(conn):
    return goal_repo.has_portfolio_goal(conn)

def get_portfolio_deadline(conn):
    return goal_repo.get_portfolio_deadline(conn)

def validate_deadline(month, year, start_date):
    month = int(month)
    year = int(year)

    if month < 1 or month > 12:
        raise ValueError("Invalid month input (must be between 1 and 12).")

    if year == start_date.year and month == start_date.month:
        raise ValueError("Deadline must be at least one 1 month in the future.")

    last_day = calendar.monthrange(year, month)[1]
    deadline = date(year, month, last_day)

    if deadline < start_date:
        raise ValueError("Deadline must be in the future.")
    
    return deadline

def get_goal(conn, period, account_id=None):
    if account_id:
        row = goal_repo.get_goal(conn, period.value, account_id)
    else:
        row = goal_repo.get_goal(conn, period.value)

    if row is None:
        return None
    
    return Goal.from_row(row)

def calculate_progress(actual, target):
    if target == Decimal("0.00"):
        return Decimal("0.00")
    
    return (actual / target) * Decimal("100")

def get_month_periods(start_date, deadline):
    periods = []

    current = start_date

    while current <= deadline:
        year = current.year
        month = current.month

        month_start = current
        month_end = date(year, month, calendar.monthrange(year, month)[1])

        if month_end > deadline:
            month_end = deadline

        periods.append((month_start, month_end))

        current = month_end.replace(day=1)

        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    return periods

def get_year_periods(start_date, deadline):
    periods = []

    current = start_date

    while current <= deadline:
        year = current.year

        year_start = current
        year_end = date(year, 12, 31)

        if year_end > deadline:
            year_end = deadline

        periods.append((year_start, year_end))

        current = date(year + 1, 12, 31)

    return periods

def add_period_goals(conn, target, start_date, deadline, scope, account_id=None):
    total_days = (deadline - start_date).days + 1
    accounts = account_service.get_cash_accounts(conn)

    if scope == GoalScope.ACCOUNT:
        collected = next(
            account.balance
            for account in accounts
            if account.id == account_id
        )
    else:
        collected = sum(account.balance for account in accounts)

    remaining_target = max(target - collected, Decimal("0.00"))
    
    daily_goal = remaining_target / total_days

    remaining = remaining_target

    for month_start, month_end in get_month_periods(start_date, deadline):
        days = (month_end - month_start).days + 1

        if month_end == deadline:
            monthly_target = remaining
        else:
            monthly_target = (daily_goal * days).quantize(Decimal("0.01"))
            remaining -= monthly_target

        monthly_goal = Goal(
            id=None,
            target_amount=monthly_target,
            start_date=month_start,
            deadline=month_end,
            scope=scope,
            period=GoalPeriod.MONTHLY,
            account_id=account_id
        )

        goal_repo.add_goal(conn, monthly_goal)

    remaining = remaining_target

    for year_start, year_end in get_year_periods(start_date, deadline):
        days = (year_end - year_start).days + 1

        if year_end == deadline:
            annual_target = remaining
        else:
            annual_target = (daily_goal * days).quantize(Decimal("0.01"))
            remaining -= annual_target

        annual_goal = Goal(
            id=None,
            target_amount=annual_target,
            start_date=year_start,
            deadline=year_end,
            scope=scope,
            period=GoalPeriod.ANNUAL,
            account_id=account_id
        )

        goal_repo.add_goal(conn, annual_goal)

def add_goals(conn, account_goals, start_date, deadline):

    try:
        goal_repo.delete_goals_table(conn)

        portfolio_target = sum(goal["target"] for goal in account_goals)
        portfolio_goal = Goal(
            id=None,
            target_amount=portfolio_target,
            start_date=start_date,
            deadline=deadline,
            scope=GoalScope.PORTFOLIO,
            period=GoalPeriod.TOTAL,
            account_id=None
        )

        goal_repo.add_goal(conn, portfolio_goal)
        add_period_goals(conn, portfolio_target, start_date, deadline, GoalScope.PORTFOLIO)

        for goal in account_goals:
            account_id = goal["account_id"]
            target = goal["target"]

            total_goal = Goal(
                id=None,
                target_amount=target,
                start_date=start_date,
                deadline=deadline,
                scope=GoalScope.ACCOUNT,
                period=GoalPeriod.TOTAL,
                account_id=account_id
            )

            goal_repo.add_goal(conn, total_goal)

            add_period_goals(conn, target, start_date, deadline, GoalScope.ACCOUNT, account_id)

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise RuntimeError("Adding goals failed") from e

def reset_goals(conn):
    try:
        goal_repo.delete_goals_table(conn)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError("Reseting goals failed") from e