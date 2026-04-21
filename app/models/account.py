from decimal import Decimal
import utils.formatting as formatting

class Account:
    def __init__(self, id, name, account_type, balance, currency, stock_value=Decimal("0.00")):
        self.id = id
        self.name = name
        self.account_type = account_type
        self.balance = balance
        self.stock_value = stock_value
        self.currency = currency

    def total_value(self):
        return self.balance + self.stock_value

    def __str__(self):
        symbols = {"USD": "$", "EUR": "€"}
        currency = symbols.get(self.currency, self.currency)
        if self.account_type == 'broker':
            amount = self.total_value()
            details = (
                f"(cash: {formatting.format_currency(self.balance, currency)}, "
                f"stocks: {formatting.format_currency(self.stock_value, currency)})"
            )
        else:
            amount = self.balance
            details = ""

        return (
                f"{(self.name + ':'):<20} {amount:>12.2f} {currency} {details}".strip()
            )

    @classmethod
    def from_row(cls, row):
        return cls(
            id = row[0],
            name = row[1],
            account_type = row[2],
            balance = row[3],
            stock_value = row[4],
            currency = row[5]
        )