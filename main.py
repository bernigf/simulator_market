import os
from components import MarketDataManager, MarketMaker, OrderBookGenerator
from copy import deepcopy

VERBOSE = True

base_rate = float(input("\nPlease enter the base rate for the MarketMaker instance (e.g., 0.03 for 3%): ") or 0.03)
visual_mode = input("Do you want to run the simulator in visual mode? (y/n): ").strip().lower()

if visual_mode == 'n':

    # Initialize components
    order_book_generator = OrderBookGenerator(asset_name="SYMBOL")
    market_data_manager = MarketDataManager(order_book_generator=order_book_generator)
    market_maker = MarketMaker(market_data_manager=market_data_manager, base_rate=base_rate)

    # Simulate the market
    market_data_manager.update_order_book()  # Generate a new order book

    # Generate new order_book and display it
    order_book = market_maker.market_data_manager.current_order_book
    market_maker.market_data_manager.order_book_generator.display_order_book_table(order_book)

    # Calculate the trades and display the results
    carry_trade_quotes = market_maker.carry_trade_strategy(N=5)
    trades_table = market_maker.display_strategy_quotes(carry_trade_quotes)
    print(trades_table)

else:
    
    os.system(f"python client.py --base_rate {base_rate}")