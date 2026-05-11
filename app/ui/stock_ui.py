import utils.console as console
import utils.formatting as formatting
import services.stock_service as stock_service
from decimal import Decimal

def view_stocks(conn):
    console.clear_screen()

    print(
                f"{'Symbol':<8} "
                f"{'Qty':>6} "
                f"{'Price':>12} "
                f"{'Value':>14} "
                f"{'Dividend':>10} "
                f"{'Income':>10} "
                f"{'(Net)':>10}"
                f"{'Next Date':>10}"
            )
    
    total_value_usd, total_gross_usd, total_net_usd = print_stocks(conn, listed="US")

    print("---------------------------------------------------------------------------------------")

    total_value_eur, total_gross_eur, total_net_eur = print_stocks(conn, listed="EU")

    print("---------------------------------------------------------------------------------------")

    try:
        totals = stock_service.calculate_portfolio_totals(total_value_usd, total_value_eur, total_gross_usd, total_gross_eur, total_net_eur)
        print_totals(totals["portfolio_value_eur"], totals["dividend_gross_eur"], totals["dividend_net_eur"])
    except Exception as e:
        print(e)

    input("Press enter to continue...")
    console.clear_screen()

def print_stocks(conn, listed):
    stocks = stock_service.get_stocks(conn, listed)
    currency = "$" if listed == "US" else "€"

    total_value = total_gross = total_net = Decimal("0.00")

    if stocks:
        for stock in stocks:
            print(stock)
        total_value = stock_service.get_total_value(stocks)
        total_gross, total_net = stock_service.get_total_dividend(stocks)

        print(
        f"{'Subtotal':<8} "
        f"{' ':>6} "
        f"{' ':>12} "
        f"{total_value:>12.2f} {currency} "
        f"{' ':>10} "
        f"{total_gross:>8.2f} {currency} "
        f"{f'({formatting.format_currency(total_net, currency)})':>10}"
          )
    else:
        print(f"No {listed} stocks found.")
    
    return total_value, total_gross, total_net 
    
def print_totals(portfolio_value_eur, dividend_gross_eur, dividend_net_eur):
    print(
            f"{'Total':<8} "
            f"{' ':>6} "
            f"{' ':>12} "
            f"{portfolio_value_eur:>12.2f} € "
            f"{' ':>10} "
            f"{dividend_gross_eur:>8.2f} € "
            f"{f'({formatting.format_currency(dividend_net_eur, "€")})':>10}"
            )