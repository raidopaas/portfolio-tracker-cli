from models.account import Account
from decimal import Decimal
import db.account_repo as account_repo
import db.transaction_repo as transaction_repo
import utils.validation as validation
from models.transaction import Transaction
import api.fx_api as fx_api
import services.fx_service as fx_service

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

def deposit(conn, account, amount, description):
    if not validation.is_positive_number(amount):
        raise ValueError("Deposit amount must be positive. Transaction cancelled.")
    
    if not description.strip():
        raise ValueError("Description cannot be empty. Transaction cancelled.")
    
    transaction = Transaction(account.id, amount, description)

    try:
        rows = account_repo.change_balance(conn, account.id, amount)

        if rows == 0:
            raise ValueError("Account not found")
        
        transaction_repo.add_transaction(conn, transaction)
        
        conn.commit()
    
    except ValueError:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        raise RuntimeError("Deposit failed.") from e
    
def withdraw(conn, account, amount, description):
    
    if not validation.is_positive_number(amount):
        raise ValueError("Withdrawal amount must be positive. Transaction cancelled.")

    if not description.strip():
        raise ValueError("Description cannot be empty. Transaction cancelled.")
    
    balance = account.balance

    if balance < amount:
        raise ValueError("Insufficient funds. Transaction cancelled.")
    
    transaction = Transaction(account.id, -amount, description)
    
    try:
        rows = account_repo.change_balance(conn, account.id, -amount)

        if rows == 0:
            raise ValueError("Account not found.")
        
        transaction_repo.add_transaction(conn, transaction)
        
        conn.commit()

    except ValueError:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        raise RuntimeError("Withdrawal failed.") from e
    
def get_totals(accounts, us_stocks, eu_stocks):
    totals = []

    us_broker_account = next((acc for acc in accounts if acc.account_type == "broker" and acc.currency == "USD"), None)
    eu_broker_account = next((acc for acc in accounts if acc.account_type == "broker" and acc.currency == "EUR"), None)

    total_eur = Decimal("0.00")
    total_usd = Decimal("0.00")

    for account in accounts:
        if account.account_type == 'cash' and account.currency == 'EUR':
            total_eur += account.balance
        elif account.account_type == 'cash' and account.currency == 'USD':
            total_usd += account.balance

    if eu_broker_account:
        total_eur_broker = eu_broker_account.balance + eu_stocks
    else:
        total_eur_broker = Decimal("0.00")

    if us_broker_account:
        total_usd_broker = us_broker_account.balance + us_stocks
    else:
        total_usd_broker = Decimal("0.00")

    total_eur += total_eur_broker
    total_usd += total_usd_broker

    rate = fx_api.get_usdeur()

    if rate is None:
        total_usd_eur = None
        grand_total = None
    else:
        total_usd_eur = fx_service.usd_to_eur(total_usd, rate)
        grand_total = total_eur + total_usd_eur

    totals = {
        "total_eur": total_eur,
        "total_usd": total_usd,
        "total_usd_eur": total_usd_eur,
        "grand_total": grand_total
    }

    return totals

def remove_account(conn, account_id):
    try:
        account_repo.delete_account(conn, account_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise