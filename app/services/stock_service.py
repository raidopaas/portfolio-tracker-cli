from models.stock import Stock
import services.account_service as account_service
import db.stock_repo as stock_repo
import api.stocks_api as stocks_api
import time

def buy_stock(conn, market, symbol, qty, price=None, dividend=None):
    currency = "USD" if market == "US" else "EUR"
    account = account_service.get_broker_account(conn, currency)

    if qty <= 0:
        raise ValueError("Quantity must be positive. Transaction cancelled.")
    
    stock = Stock(symbol, quantity=qty, listed=market)

    """ try:
        previous_price = stocks_repo.get_stock_price(conn, symbol)
    except Exception as e:
        raise RuntimeError("Failed to access the database.") from e """

    try:
        populate_stock_data(stock, price, dividend)
        stock_repo.save_stock(conn, stock)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError("Failed to buy stock. Transaction cancelled.") from e

"""     try:
        conn.rollback()
        conn.start_transaction()

        transaction_cost = qty * stock.price
        balance = accounts_repo.get_account_balance(conn, account_id)

        if transaction_cost > balance:
            raise ValueError("Insufficient funds. Transaction cancelled.") #this also prompts the below runtime error message
            
        previous_qty = stocks_repo.get_stock_qty(conn, stock.symbol)
        new_qty = previous_qty + qty

        stock.quantity = new_qty
        stocks_repo.save_stock(conn, stock)
        
        description = f"Bought {qty} share(s) of {stock.symbol}"
        transactions_repo.add_transaction(conn, account_id, -transaction_cost, description)
        
        new_balance = balance - transaction_cost
        stocks_balance_change = stock.price * new_qty - previous_price * previous_qty
        accounts_repo.update_balance(conn, account_id, new_balance)
        accounts_repo.add_stocks_balance(conn, account_id, stocks_balance_change)

        conn.commit()

    except ValueError:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        raise RuntimeError("Failed to execute stocks purchase. Transaction cancelled.") from e """
    
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