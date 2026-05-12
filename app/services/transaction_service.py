import db.transaction_repo as transaction_repo
from models.transaction import Transaction 

def get_transactions_for_account(conn, account_id, year, month):
    raw_data = transaction_repo.get_transactions_for_account(conn, account_id, year, month)
    return [Transaction.from_row(row) for row in raw_data]
