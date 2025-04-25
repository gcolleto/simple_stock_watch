from flask import Flask, render_template_string
import sys
from simple_stock_watch import load_config, get_stock_prices, calculate_portfolio_value_and_variation

app = Flask(__name__)

# Global variable to store the configuration file path
CONFIG_FILE = None

# Flask route to display the portfolio
@app.route("/")
def display_portfolio():
    # Use the global CONFIG_FILE passed during server startup
    if not CONFIG_FILE:
        return "Error: No configuration file provided. Please pass the config file when starting the server."

    # Load the portfolio data
    symbols, shares_owned, purchase_prices = load_config(CONFIG_FILE)
    prices = get_stock_prices(symbols)
    portfolio = calculate_portfolio_value_and_variation(
        prices, shares_owned, purchase_prices
    )

    total_value, total_benefit, overall_variation = [f'{x:.2f}' for x in portfolio["Total"].values()]
    print(total_value, total_benefit, overall_variation, portfolio)
    
    del portfolio["Total"]
    
    # HTML template for the webpage
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Portfolio Overview</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { border-collapse: collapse; width: 80%; margin: auto; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            th { background-color: #f4f4f4; }
        </style>
    </head>
    <body>
        <h1 style="text-align: center;">Portfolio Overview</h1>
        <table>
            <tr>
                <th>Symbol</th>
                <th>Current Price</th>
                <th>Invested Amount</th>
                <th>Total Value</th>
                <th>Benefit</th>
                <th>Variation (%)</th>
            </tr>
            {% for stock in portfolio %}
            <tr>
                <td>{{  stock }}</td>
                <td>${{ portfolio[stock].price }}</td>
                <td>${{ portfolio[stock].invested }}</td>
                <td>${{ portfolio[stock].total_value }}</td>
                <td>${{ portfolio[stock].benefit }}</td>
                <td>{{  portfolio[stock].percentage_variation }}%</td>
            </tr>
            {% endfor %}
            <tr>
                <th colspan="3">Total</th>
                <th>${{ total_value }}</th>
                <th>${{ total_benefit }}</th>
                <th>{{ overall_variation }}%</th>
            </tr>
        </table>
    </body>
    </html>
    """
    # Render the HTML template with data
    return render_template_string(
        html_template,
        portfolio=portfolio,
        total_value=total_value,
        total_benefit=total_benefit,
        overall_variation=overall_variation,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python app.py <config.file>")
        sys.exit(1)

    CONFIG_FILE = sys.argv[1]

    try:
        open(CONFIG_FILE, "r").close()
    except FileNotFoundError:
        print(f"Error: File '{CONFIG_FILE}' does not exist.")
        sys.exit(1)

    app.run(host="0.0.0.0", port=5000, debug=True)
