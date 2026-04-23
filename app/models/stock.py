from decimal import Decimal
import utils.constants as constants

class Stock:
    def __init__(self, symbol, quantity=0, price=Decimal("0.00"), dividend=Decimal("0.00"), listed="US", dividend_date=None):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.dividend = dividend
        self.listed = listed
        self.dividend_date = dividend_date

    def value(self):
        return self.quantity * self.price
    
    def dividend_income(self):
        return self.quantity * self.dividend
    
    def net_income(self):
        return self.dividend_income() * constants.NET_DIVIDEND_RATE.get(self.listed, Decimal("1.00"))

    def __str__(self):
        currency = constants.CURRENCIES[self.listed]
        date_str = str(self.dividend_date) if self.dividend_date else "-"
        net_str = f"({self.net_income():.2f} {currency})"

        return (
            f"{self.symbol:<8} "
            f"{self.quantity:>6} "
            f"{self.price:>10.2f} {currency} "
            f"{self.value():>12.2f} {currency} "
            f"{self.dividend:>8.2f} {currency} "
            f"{self.dividend_income():>8.2f} {currency} "
            f"{net_str:>10} "
            f"{date_str:>10}"
        )
    
    @classmethod
    def from_row(cls, row):
        # Converts a database row (tuple) into a Stock object
        return cls(
            symbol = row[0],
            quantity = row[1],
            price = row[2],
            dividend = row[4],
            dividend_date = row[5],
            listed = row[6]
        )