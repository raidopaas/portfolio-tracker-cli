import utils.constants as constants
import utils.formatting as formatting
import services.account_service as account_service

class Account:
    def __init__(self, id, name, account_type, balance, currency):
        self.id = id
        self.name = name
        self.account_type = account_type
        self.balance = balance
        self.currency = currency

    @classmethod
    def from_row(cls, row):
        # Converts a database row (tuple) into an Account object
        return cls(
            id = row[0],
            name = row[1],
            account_type = row[2],
            balance = row[3],
            currency = row[4]
        )