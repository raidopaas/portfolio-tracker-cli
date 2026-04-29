

def save_stock(conn, stock):
    cursor = conn.cursor()
    
    query = """
    INSERT INTO stocks (symbol, quantity, stock_price, dividend, listed, dividend_date)
    VALUES(%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    quantity = quantity + VALUES(quantity),
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