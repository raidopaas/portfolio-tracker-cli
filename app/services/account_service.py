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
        account_repo.add_account(conn, account)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Adding account {name} failed.") from e