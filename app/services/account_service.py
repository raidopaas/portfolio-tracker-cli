from models.account import Account
from decimal import Decimal
import db.account_repo as account_repo

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
    currency = account.currency
    name = account.name

    if account_repo.account_exists(conn, name):
        raise ValueError(f"Account with name {name} already exists.")

    if account.account_type == "broker":
        broker_accounts = account_repo.count_broker_accounts(conn, currency)
        if broker_accounts > 0:
            raise ValueError(f"Broker account with currency {currency} already exists.")