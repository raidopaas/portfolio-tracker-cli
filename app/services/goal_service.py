from models.goal import Goal, GoalScope, GoalPeriod
import db.goal_repo as goal_repo

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
        raise RuntimeError(f"Adding goal {goal.name} failed.") from e
    
def validate_goal(conn, goal):
    pass