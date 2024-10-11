import random
import math
import time

from tabulate import tabulate

VERBOSE = False

class Logger:
    def __init__(self):
        self.log_history = []

    def log(self, message, verbose=False):
        timestamp = time.time()
        log_entry = {
            'timestamp': timestamp,
            'data': message,
        }
        self.log_history.append(log_entry)
        
        if verbose:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))}] {log_entry['data']}")

    def get_logs(self):
        return self.log_history

class OrderBookGenerator:
    
    def __init__(self, asset_name="Generic Asset"):
        self.asset_name = asset_name

    #def generate_order_book(self, num_orders=10):
    def generate_order_book(self, max_ask_items=10, max_bid_items=10, market_price=100, max_ask_spread=5, max_bid_spread=5):
        """
        Generates a simulated order book with given number of buy and sell orders.
        """

        order_book = {
            "bid": [],
            "ask": []
        }

        for _ in range(max_bid_items):
            price = round(market_price * (1 + random.uniform(0, max_ask_spread / 100)), 2)
            amount = round(random.randint(1, 100))  # Random amount between 1 and 100
            order_book["bid"].append({"price": price, "amount": amount})
        
        for _ in range(max_ask_items):
            price = round(market_price * (1 - random.uniform(0, max_bid_spread / 100)), 2)
            amount = round(random.randint(1, 100))  # Random amount between 1 and 100
            order_book["ask"].append({"price": price, "amount": amount})

        # Sort the orders
        order_book["bid"].sort(key=lambda x: x["price"], reverse=True)  # Highest price first
        order_book["ask"].sort(key=lambda x: x["price"])  # Lowest price first
        
        return order_book
    
    def display_order_book_table(self, order_book):
        """
        Displays the order book in a tabulated table for easier readability
        """
        print(tabulate(order_book, headers="keys", tablefmt="pretty"))

class MarketDataManager:
    
    def __init__(self, order_book_generator, verbose=False):
        self.order_book_generator = order_book_generator
        self.current_order_book = None
        self.verbose = VERBOSE
        self.logger = Logger()

    def update_order_book(self, max_ask_items=15, max_bid_items=15, market_price=100, max_ask_spread=5, max_bid_spread=5):
        """
        Updates the current order book by generating a new one.
        """
        self.current_order_book = self.order_book_generator.generate_order_book(max_ask_items, max_bid_items, market_price, max_ask_spread, max_bid_spread)
        asset = self.order_book_generator.asset_name
        self.logger.log(f"Order book updated for asset {asset}", verbose=self.verbose)

class MarketMaker:
    
    def __init__(self, market_data_manager, base_rate=0.02, verbose=False):
        self.market_data_manager = market_data_manager
        self.base_rate = base_rate  # Base interest rate for carry trade calculations
        self.verbose = VERBOSE
        self.logger = market_data_manager.logger

        self.logger.log(f"MarketMaker initialized with base rate: {self.base_rate * 100}%", verbose=self.verbose)

    def carry_trade_strategy(self, N=5, maturity_dates=None):
        """
        Implements the carry trade strategy for each sell order in the order book across N future contracts.
        Quote amounts are calculated based on all available liquidity, and the potential earnings are evaluated.
        """

        if maturity_dates is None:
            maturity_dates = [30, 60, 90, 180, 365]  # Default maturity dates in days

        self.logger.log("Starting carry trade strategy...", verbose=self.verbose)
        self.logger.log(f"Using the following maturity dates: {maturity_dates[:N]} days", verbose=self.verbose)

        order_book = self.market_data_manager.current_order_book
        if not order_book:
            self.logger.log("No order book data available. Exiting strategy.", verbose=self.verbose)
            return []

        sell_orders = order_book["ask"]
        all_strategy_quotes = []

        for sell_order in sell_orders:
            sell_price = sell_order["price"]
            amount = sell_order["amount"]

            for maturity in maturity_dates[:N]:
                future_price = self.calculate_future_price(maturity)

                if future_price is not None:
                    expected_earnings = (future_price - sell_price) * amount
                    all_strategy_quotes.append({
                        "sell_price": sell_price,
                        "maturity_days": maturity,
                        "future_price": round(future_price, 2),
                        "amount": amount,
                        "expected_earnings": round(expected_earnings, 2)
                    })

        return all_strategy_quotes

    def calculate_future_price(self, maturity_days):
        """
        Calculates the future price of the asset using the compound interest formula.
        """
        order_book = self.market_data_manager.current_order_book

        if not order_book:
            self.logger.log("Order book data is missing. Cannot calculate future price", verbose=self.verbose)
            return None

        # Use spot price from the lowest sell order
        spot_price = order_book["ask"][0]["price"]
        future_price = spot_price * math.exp(self.base_rate * (maturity_days / 365))
        return future_price

    def display_strategy_quotes(self, strategy_quotes):
        """
        Display the generated strategy quotes in a tabulated format for easier reading and comparison.
        """

        # Create a table with the details of each strategy quote
        table_data = []
        highest_earnings = float('-inf')

        for quote in strategy_quotes:
            if quote["expected_earnings"] > highest_earnings:
                highest_earnings = quote["expected_earnings"]

            table_data.append([
                quote["sell_price"],
                quote["maturity_days"],
                quote["future_price"],
                quote["amount"],
                quote["expected_earnings"]
            ])

        # Sort the table data by expected earnings in descending order
        table_data = sorted(table_data, key=lambda x: x[4], reverse=True)

        # Build the table using tabulate for better readability
        headers = ["Sell Price", "Maturity (Days)", "Future Price", "Amount", "Expected Earnings"]
        output = tabulate(table_data, headers=headers, tablefmt="pretty")

        self.logger.log("Summary of Strategy Quotes:", verbose=True)
        best_quote = max(strategy_quotes, key=lambda x: x["expected_earnings"], default=None)
        if best_quote:
            self.logger.log(f"Best potential trade: Sell at {best_quote['sell_price']} with maturity in {best_quote['maturity_days']} days", verbose=True)
            self.logger.log(f"Expected earnings: {best_quote['expected_earnings']} units", verbose=True)
        else:
            self.logger.log("No profitable trades found", verbose=True)

        return output

if __name__ == "__main__":
    
    VERBOSE = True
    
    # Initialize components
    order_book_generator = OrderBookGenerator(asset_name="SYMBOL")
    market_data_manager = MarketDataManager(order_book_generator=order_book_generator)
    market_maker = MarketMaker(market_data_manager=market_data_manager, base_rate=0.03)

    # Simulate the market
    market_data_manager.update_order_book()  # Generate a new order book

    # Generate new order_book and display it
    order_book = market_maker.market_data_manager.current_order_book
    market_maker.market_data_manager.order_book_generator.display_order_book_table(order_book)
    
    # Calculate the thrades and display the results
    carry_trade_quotes = market_maker.carry_trade_strategy(N=3)
    trades_table = market_maker.display_strategy_quotes(carry_trade_quotes)
    print(trades_table)
