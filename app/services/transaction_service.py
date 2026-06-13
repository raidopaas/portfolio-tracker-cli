import db.transaction_repo as transaction_repo
from models.transaction import Transaction
from decimal import Decimal
import services.fx_service as fx_service

def get_transactions_for_account(conn, account_id, year, month):
    raw_data = transaction_repo.get_transactions_for_account(conn, account_id, year, month)
    return [Transaction.from_row(row) for row in raw_data]

def get_totals(conn, accounts, year=None, month=None):
    totals = {}
    grand_total = Decimal("0.00")
    rate = fx_service.get_usd_to_eur_rate() or Decimal("0.00")

    for account in accounts:
        transactions = get_transactions_for_account(conn, account.id, year, month)
        account_total = Decimal("0.00")

        for transaction in transactions:
            account_total += transaction.amount

        totals[account.name] = account_total
        grand_total += account_total if account.currency == "EUR" else fx_service.usd_to_eur(account_total, rate)
    
    totals["Grand Total"] = grand_total

    return totals
