import db.account_repo as account_repo

def reset(conn):
    try:
        conn.start_transaction()

        #stocks_repo.delete_stocks_table(conn)
        #transactions_repo.delete_transactions_table(conn)           
        account_repo.delete_accounts_table(conn)
        #goals_repo.delete_goals_table(conn)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError("Reset failed.") from e