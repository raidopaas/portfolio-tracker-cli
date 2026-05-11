from models.stock import Stock
import services.account_service as account_service
import db.stock_repo as stock_repo
import db.account_repo as account_repo
import db.transaction_repo as transaction_repo
import api.stocks_api as stocks_api
import services.fx_service as fx_service
import time
from decimal import Decimal
from models.transaction import Transaction

def buy_stock(conn, market, symbol, qty, price=None, dividend=None):
    currency = "USD" if market == "US" else "EUR"
    account = account_service.get_broker_account(conn, currency)

    if qty <= 0:
        raise ValueError("Quantity must be positive. Transaction cancelled.")
    
    stock = Stock(symbol, quantity=qty, listed=market)

    populate_stock_data(stock, price, dividend)
        
    transaction_cost = qty * stock.price

    if transaction_cost > account.balance:
        raise ValueError("Insufficient funds. Transaction cancelled.")
    
    description = f"Bought {qty} shares of {stock.symbol}"
    transaction = Transaction(account.id, -transaction_cost, description)
    
    try:
        account_repo.change_balance(conn, account.id, -transaction_cost)
        stock_repo.save_stock(conn, stock)
        transaction_repo.add_transaction(conn, transaction)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError("Failed to buy stock. Transaction cancelled.") from e
    
def sell_stock(conn, market, symbol, qty, stock_qty, price, dividend=None):
    currency = "USD" if market == "US" else "EUR"
    account = account_service.get_broker_account(conn, currency)

    if qty <= 0:
        raise ValueError("Quantity must be positive. Transaction cancelled.")
    
    if qty > stock_qty:
        raise ValueError("Not enough stock to complete transaction. Transaction cancelled.")
    
    stock = Stock(symbol, quantity=qty, listed=market)
    update_price(stock, price)
    time.sleep(1.1)
    transaction_cost = qty * stock.price
    description = f"Sold {qty} share(s) of {symbol}"
    transaction = Transaction(account.id, transaction_cost, description)

    new_qty = stock_qty - qty

    try:
        if new_qty == 0:
            stock_repo.delete_stock(conn, symbol)
        else:
            stock.quantity = new_qty
            update_dividend(stock, dividend)
            time.sleep(1.1)
            stock_repo.save_stock(conn, stock)

        account_repo.change_balance(conn, account.id, transaction_cost)
        transaction_repo.add_transaction(conn, transaction)

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise RuntimeError("Failed to sell stock. Transaction cancelled.") from e
    
def populate_stock_data(stock, price, dividend):
    if stock.listed=="US":
        update_price(stock)
        time.sleep(1.1)
        update_dividend(stock)
        time.sleep(1.1)
    else:
        update_price(stock, price)
        update_dividend(stock, dividend)

def update_price(stock, manual_price=None):
    if stock.listed == 'US':
        stock.price = stocks_api.get_latest_us_stock_price(stock.symbol)
    """ else:
        if manual_price is None: #code actually would never reach here
            raise ValueError("Manual price required for non-US stocks.")
        if manual_price < 0:
            raise ValueError("Stock price cannot be negative.")
        stock.price = manual_price """

def update_dividend(stock, manual_dividend=None):
    if stock.listed == 'US':
        dividend, date = stocks_api.get_latest_us_stock_dividend(stock.symbol)
        stock.dividend = dividend
        stock.dividend_date = date
    """ else:
        if manual_dividend is None: #code actually would never reach here
            raise ValueError("Manual dividend required for non-US stocks.")
        if manual_dividend < 0:
            raise ValueError("Dividend cannot be negative.")
        stock.dividend = manual_dividend """
    
def get_stocks(conn, listed):
    raw_data = stock_repo.get_stocks_by_listing(conn, listed)
    return [Stock.from_row(row) for row in raw_data]

def get_stock_qty(conn, symbol):
    qty = stock_repo.get_stock_qty(conn, symbol)
    if qty == 0:
        raise ValueError("Stock not found.")
    return qty

def get_total_value(stocks):
    total_value = Decimal("0.00")
    for stock in stocks:
        total_value += stock.value()
    return total_value

def get_total_dividend(stocks):
    total_gross = Decimal("0.00")
    total_net = Decimal("0.00")
    for stock in stocks:
        bruto_dividend = stock.dividend_income()
        net_divident = bruto_dividend * Decimal("0.85") if stock.listed == "US" else bruto_dividend
        total_gross += bruto_dividend
        total_net += net_divident
    return total_gross, total_net

def calculate_portfolio_totals(
    total_value_usd,
    total_value_eur,
    total_dividend_usd,
    total_dividend_eur,
    total_net_eur
):
    rate = fx_service.get_usd_to_eur_rate()

    if rate is None:
        raise RuntimeError("Could not retrieve USD data.")

    usd_value_eur = fx_service.usd_to_eur(total_value_usd, rate)

    usd_dividend_gross_eur = fx_service.usd_to_eur(
        total_dividend_usd,
        rate
    )

    usd_dividend_net_eur = fx_service.usd_to_eur(
        total_dividend_usd * Decimal("0.85"),
        rate
    )

    return {
        "portfolio_value_eur":
            total_value_eur + usd_value_eur,

        "dividend_gross_eur":
            total_dividend_eur + usd_dividend_gross_eur,

        "dividend_net_eur":
            total_net_eur + usd_dividend_net_eur
    }