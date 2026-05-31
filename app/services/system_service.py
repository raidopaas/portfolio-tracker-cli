import db.account_repo as account_repo
import db.stock_repo as stock_repo
import db.transaction_repo as transaction_repo
import db.goal_repo as goal_repo

def reset(conn):
    try:
        conn.start_transaction()

        stock_repo.delete_stocks_table(conn)
        transaction_repo.delete_transactions_table(conn)           
        account_repo.delete_accounts_table(conn)
        goal_repo.delete_goals_table(conn)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError("Reset failed.") from e