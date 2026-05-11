

def save_stock(conn, stock):
    cursor = conn.cursor()
    
    query = """
    INSERT INTO stocks (symbol, quantity, stock_price, dividend, listed, dividend_date)
    VALUES(%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    quantity = VALUES(quantity),
    stock_price = VALUES(stock_price),
    dividend = VALUES(dividend),
    dividend_date = VALUES(dividend_date)
    """

    values = (
        stock.symbol, 
        stock.quantity, 
        stock.price, 
        stock.dividend, 
        stock.listed, 
        stock.dividend_date
    )

    try:
        cursor.execute(query, values)
    finally:
        cursor.close()

def delete_stock(conn, symbol):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM stocks WHERE symbol = %s", (symbol,))
    finally:
        cursor.close()

def get_stocks_by_listing(conn, listed):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM stocks WHERE listed = %s ORDER BY symbol ASC", (listed,))
        return cursor.fetchall()
    finally:
        cursor.close()

def get_stock_qty(conn, symbol):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT quantity FROM stocks WHERE symbol = %s", (symbol,))
        qty = cursor.fetchone()
        return qty[0] if qty else 0
    finally:
        cursor.close()

def delete_stocks_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM stocks")
    finally:
        cursor.close()