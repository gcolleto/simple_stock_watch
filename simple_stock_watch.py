import yfinance as yf
import csv
import sys

def load_config(config_file):
    """
    Load the stock configuration from a CSV file.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        tuple: A tuple containing a list of stock symbols, a dictionary of shares owned,
               and a dictionary of purchase prices.
    """
    stock_symbols = []
    shares_owned = {}
    purchase_prices = {}

    try:
        with open(config_file, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) != 3:
                    print(f"Skipping invalid row: {row}")
                    continue
                symbol, shares, price = row
                stock_symbols.append(symbol.strip())
                shares_owned[symbol.strip()] = int(shares.strip())
                purchase_prices[symbol.strip()] = float(price.strip())
    except Exception as e:
        print(f"Error reading the config file: {e}")
        return [], {}, {}

    return stock_symbols, shares_owned, purchase_prices


def get_stock_prices(symbols):
    """
    Fetch the current prices of multiple stocks using yfinance.

    Args:
        symbols (list): List of stock symbols (e.g., ["AAPL", "MSFT"]).

    Returns:
        dict: A dictionary with stock symbols as keys and their prices as values.
    """
    prices = {}
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            price = stock.info["regularMarketPrice"]
            prices[symbol] = price
        except Exception as e:
            prices[symbol] = None
            print(f"Error: Unable to fetch stock price for {symbol}.\n{e}")
    return prices


def calculate_portfolio_value_and_variation(prices, shares, purchase_prices):
    """
    Calculate the portfolio value, profit/loss (benefits), and percentage variation for each stock.

    Args:
        prices (dict): Dictionary of stock prices with symbols as keys.
        shares (dict): Dictionary of shares owned with symbols as keys.
        purchase_prices (dict): Dictionary of purchase prices with symbols as keys.

    Returns:
        dict: A dictionary with stock symbols as keys and their total value, benefits, and percentage variation,
              and totals for the entire portfolio.
    """
    portfolio_values = {}
    total_portfolio_value = 0
    total_benefits = 0
    total_invested = 0

    for symbol, price in prices.items():
        if price is not None and symbol in shares and symbol in purchase_prices:
            # Calculate total value, benefits, and percentage variation
            total_value = price * shares[symbol]
            benefit = (price - purchase_prices[symbol]) * shares[symbol]
            percentage_variation = ((price - purchase_prices[symbol]) / purchase_prices[symbol]) * 100

            # Store data for the stock
            portfolio_values[symbol] = {
                "price": f'{price:.2f}',
                "invested": f'{purchase_prices[symbol]*shares[symbol]:.2f}',
                "total_value": f'{total_value:.2f}',
                "benefit": f'{benefit:.2f}',
                "percentage_variation": f'{percentage_variation:.2f}'
            }

            # Accumulate totals
            total_portfolio_value += total_value
            total_benefits += benefit
            total_invested += purchase_prices[symbol] * shares[symbol]
        else:
            portfolio_values[symbol] = None

    # Calculate total percentage variation for the portfolio
    total_percentage_variation = ((total_portfolio_value - total_invested) / total_invested) * 100 if total_invested else 0

    portfolio_values["Total"] = {
        "total_value": total_portfolio_value,
        "benefit": total_benefits,
        "percentage_variation": total_percentage_variation
    }
    return portfolio_values


if __name__ == "__main__":
    # Check if the config file is provided as an argument
    if len(sys.argv) != 2:
        print("Usage: python get_portfolio_from_config.py <config_file>")
        sys.exit(1)

    # Get the config file from the command-line argument
    config_file = sys.argv[1]

    # Load the configuration from the file
    stock_symbols, shares_owned, purchase_prices = load_config(config_file)

    if not stock_symbols:
        print("No valid stock data found in the configuration file.")
        exit(1)

    # Fetch stock prices
    stock_prices = get_stock_prices(stock_symbols)

    # Calculate portfolio values and variation
    portfolio_values = calculate_portfolio_value_and_variation(stock_prices, shares_owned, purchase_prices)

    # Display the stock prices, portfolio values, benefits, and percentage variation
    print("Stock Prices, Portfolio Values, Benefits, and Percentage Variation:")
    for symbol in stock_symbols:
        price = stock_prices.get(symbol)
        portfolio_data = portfolio_values.get(symbol)
        if price is not None and portfolio_data is not None:
            print(f"{symbol}: Price = ${price:.2f}, Value = ${portfolio_data['total_value']}, "
                  f"Benefit = ${portfolio_data['benefit']}, Variation = {portfolio_data['percentage_variation']}%")
        else:
            print(f"{symbol}: Failed to fetch price or data")

    # Display total portfolio value, benefits, and percentage variation
    print(f"\nTotal Portfolio Value: ${portfolio_values['Total']['total_value']:.2f}")
    print(f"Total Portfolio Benefits: ${portfolio_values['Total']['benefit']:.2f}")
    print(f"Total Portfolio Percentage Variation: {portfolio_values['Total']['percentage_variation']:.2f}%")
