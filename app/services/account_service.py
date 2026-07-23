from models.account import Account
from decimal import Decimal
import db.account_repo as account_repo
import db.transaction_repo as transaction_repo
import utils.validation as validation
from models.transaction import Transaction
import api.fx_api as fx_api
import services.fx_service as fx_service
import services.stock_service as stock_service
import services.goal_service as goal_service
from models.goal import Goal, GoalScope, GoalPeriod
from utils import constants, formatting

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

def get_accounts(conn, exclude_account=None):
    raw_data = account_repo.get_all_accounts(conn)
    accounts = [Account.from_row(row) for row in raw_data]

    if exclude_account:
        accounts = [
            acc for acc in accounts if acc.id not in exclude_account
        ]

    return accounts

def get_cash_accounts(conn):
    try:
        eur_broker_account = get_broker_account(conn, "EUR").id
    except Exception:
        eur_broker_account = None
    try:
        usd_broker_account = get_broker_account(conn, "USD").id
    except Exception:
        usd_broker_account = None

    accounts = get_accounts(conn, [eur_broker_account, usd_broker_account])
    return accounts

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
    
def transfer(conn, account_from, account_to, amount, description_from, description_to):
    currency_from = account_from.currency
    currency_to = account_to.currency

    if currency_from == currency_to:
        withdraw(conn, account_from, amount, description_from)
        deposit(conn, account_to, amount, description_to)
        return
    
    rate = fx_service.get_usd_to_eur_rate()

    if rate is None:
        raise RuntimeError("Failed to convert currencies. Transaction cancelled.")
    
    converted_amount = (
        fx_service.usd_to_eur(amount, rate)
        if currency_from == "USD"
        else fx_service.eur_to_usd(amount, rate)
    )
    
    withdraw(conn, account_from, amount, description_from)
    deposit(conn, account_to, converted_amount, description_to)

    return converted_amount

def get_eur_value(amount):
    try:
        rate = fx_service.get_usd_to_eur_rate()
    except Exception:
        return None

    return fx_service.usd_to_eur(amount, rate)
    
def get_totals(accounts, us_stocks_value, eu_stocks_value):
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
        total_eur_broker = eu_broker_account.balance + eu_stocks_value
    else:
        total_eur_broker = Decimal("0.00")

    if us_broker_account:
        total_usd_broker = us_broker_account.balance + us_stocks_value
    else:
        total_usd_broker = Decimal("0.00")

    total_eur += total_eur_broker
    total_usd += total_usd_broker

    total_usd_eur = get_eur_value(total_usd)
    if total_usd_eur:
        grand_total = total_eur + total_usd_eur
    else:
        grand_total = Decimal("0.00")

    totals = {
        "total_eur": total_eur,
        "total_usd": total_usd,
        "total_usd_eur": total_usd_eur,
        "grand_total": grand_total
    }

    return totals

def get_deposit_goal_impact(conn, account, amount):
    account_total_goal = goal_service.get_goal(conn, account.id, GoalPeriod.TOTAL)
    portfolio_total_goal = goal_service.get_portfolio_goal(conn, GoalPeriod.TOTAL)
    if account_total_goal is None or portfolio_total_goal is None:
        return None
    account_total_increase = amount / account_total_goal.target_amount * Decimal("100")
    portfolio_total_increase = amount / portfolio_total_goal.target_amount * Decimal("100")
    return account_total_increase, portfolio_total_increase

def format_account(account):
    currency = constants.CURRENCIES[account.currency]

    if currency == "€":
        return (
                f"{(account.name + ':'):<20} {formatting.format_currency(account.balance, currency):>15}"
            )

    balance_in_eur = get_eur_value(account.balance)

    if balance_in_eur is None:
        return (
            f"{(account.name + ':'):<20} {formatting.format_currency(account.balance, currency):>15}"
        )

    return (
        f"{(account.name + ':'):<20} {formatting.format_currency(account.balance, currency):>15} ({formatting.format_currency(balance_in_eur, "€"):>10})"
    )
    

def validate_account_removal(conn, account):
    if account.balance > Decimal("0.00"):
        return False
    elif account.account_type == 'broker':
        listed = "US" if account.currency == "USD" else "EU"
        if stock_service.get_stocks(conn, listed):
            return False
    return True

def remove_account(conn, account_id):
    try:
        account_repo.delete_account(conn, account_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise