import utils.formatting as formatting
import utils.constants as constants

class Transaction:
    def __init__(self, account_id, amount, description="", id=None, txn_date=None, currency=None):
        self.id = id
        self.account_id = account_id
        self.amount = amount
        self.txn_date = txn_date
        self.description = description
        self.currency = currency

    def __str__(self):
        currency = constants.CURRENCIES.get(self.currency, "")
        amount_str = formatting.format_currency(self.amount, currency)
        txn_date_str = str(self.txn_date)

        return(
            f"{amount_str:>14}   "
            f"{txn_date_str:<12}   "
            f"{self.description}"
        )
    
    @classmethod
    def from_row(cls, row):
        # Converts a database row (tuple) into a Transaction object
        return cls(
            id = row[0],
            account_id = row[1],
            amount = row[2],
            txn_date = row[3],
            description = row[4],
            currency = row[5]
        )