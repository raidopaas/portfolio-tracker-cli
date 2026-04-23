import utils.formatting as formatting

class Transaction:
    def __init__(self, id, account_id, amount, txn_date, description="", currency=None):
        self.id = id
        self.account_id = account_id
        self.amount = amount
        self.txn_date = txn_date
        self.description = description
        self.currency = currency

    def __str__(self):
        currency = self.currency or ""
        amount_str = formatting.format_currency(self.amount, currency)
        txn_date_str = str(self.txn_date)

        return(
            f"{amount_str:>14}   "
            f"{txn_date_str:<12}   "
            f"{self.description}"
        )