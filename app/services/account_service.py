from models.account import Account
from decimal import Decimal
import db.account_repo as account_repo
import utils.validation as validation

def add_account(conn, name, account_type, currency):
    account = Account(
        id=None,
        name=name,
        account_type=account_type,
        balance=Decimal("0.00"),
        currency=currency
    )

    try:
        validate_account(conn, account)
        account_repo.add_account(conn, account)
        conn.commit()
    except ValueError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Adding account {name} failed.") from e
    
def validate_account(conn, account):

    if account_repo.account_exists(conn, account.name, account.currency):
        raise ValueError(f"Account with name {account.name} already exists.")

    if account.account_type == "broker":
        broker_accounts = account_repo.count_broker_accounts(conn, account.currency)
        if broker_accounts > 0:
            raise ValueError(f"Broker account with currency {account.currency} already exists.")
        
def get_broker_account(conn, currency):
    row = account_repo.get_broker_account(conn, currency)

    if not row:
        raise ValueError(f"No broker account for {currency}.")
    
    return Account.from_row(row)

def get_accounts(conn):
    raw_data = account_repo.get_all_accounts(conn)
    return [Account.from_row(row) for row in raw_data]

def deposit(conn, account_id, amount, description):
    if not validation.is_positive_number(amount):
        raise ValueError("Deposit amount must be positive. Transaction cancelled.")
    
    if not description.strip():
        raise ValueError("Description cannot be empty. Transaction cancelled.")

    try:
        account_repo.change_balance(conn, account_id, amount)
        #transactions_repo.add_transaction(conn, account_id, amount, description)

        conn.commit()
    
    except ValueError:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        raise RuntimeError("Deposit failed.") from e