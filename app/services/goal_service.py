from models.goal import Goal, GoalScope, GoalPeriod
import db.goal_repo as goal_repo
from datetime import datetime
import calendar

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