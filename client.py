import sys
import time
import threading
import curses
import threading

import argparse

from copy import deepcopy
from components import OrderBookGenerator, MarketDataManager, MarketMaker

# Variable to track if curses is active
CURSES_ACTIVE = True

# Debug lines for threading 
# curses.endwin()  # Remove curses windows from the terminal
# import pdb; pdb.set_trace()

ORDER_BOOK_START = None
MARKET_MAKER = None
CARRY_TRADE_QUOTES = None
CARRY_TRADE_TABLE = None
LOG_HISTORY = None

# Create a lock object for synchronizing access to window updates
LOCK = threading.Lock()

def display_log(win):
    
    while CURSES_ACTIVE:
        time.sleep(0.1)
        with LOCK:  # Ensure only one thread updates at a time
            win.clear()
            win.border('|', '|', '-', '-', '+', '+', '+', '+') # Use ASCII characters for border: '|' for vertical, '-' for horizontal
            # height, width = win.getmaxyx()
            log_history = LOG_HISTORY  # Get the last 10 log entries
            for i, log_entry in enumerate(log_history):
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log_entry['timestamp']))
                win.addstr(i + 1, 2, timestamp, curses.color_pair(0))
                win.addstr(i + 1, 2 + len(timestamp) + 1, log_entry['data'])
            win.refresh()

def display_ct_results(win):
    
    global MARKET_MAKER
    global CARRY_TRADE_TABLE
    while CURSES_ACTIVE:
        time.sleep(0.1)
        with LOCK:  # Ensure only one thread updates at a time
            win.clear()
            
            output = CARRY_TRADE_TABLE
            
            max_y, max_x = win.getmaxyx()
            start_x, start_y = 0, 0

            # Split the output into lines and ensure it fits within the window width
            lines = str(output).split('\n')
            for i, line in enumerate(lines):
                if i < max_y - start_y:  # Ensure we don't exceed the window height
                    x_pos = start_x
                    win.addstr(i + start_y, x_pos, line[:max_x - x_pos - 4])

            win.border('|', '|', '-', '-', '+', '+', '+', '+')
            win.refresh()

def init_msg(stdscr):
    """Displays an initial message with action keys for 3 seconds."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Define the message text
    instructions = [
        "",
        "Starting in 5 seconds..",
        "",
        "Key Bindings:",
        "",
        "- 'r' to refresh the orderbook and re-calculate trades ",
        "- 'd' to enter debug mode",
        "- 'q' to quit the simulator client",
    ]

    # Calculate window dimensions to center the message
    win_height = len(instructions) + 4
    win_width = max(len(line) for line in instructions) + 4
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2

    # Create the centered window
    msg_win = curses.newwin(win_height, win_width, start_y, start_x)
    msg_win.border('|', '|', '-', '-', '+', '+', '+', '+')

    # Display the message in the window
    for idx, line in enumerate(instructions, start=1):
        msg_win.addstr(idx, 3, line)

    msg_win.refresh()
    time.sleep(5)  # Display the message for 5 seconds
    stdscr.clear()
    stdscr.refresh()

def create_windows(stdscr):
    
    global MARKET_MAKER
    global CARRY_TRADE_TABLE
    global LOG_HISTORY

    # Call the init_msg function to display the initial instructions
    init_msg(stdscr)

    CARRY_TRADE_QUOTES = MARKET_MAKER.carry_trade_strategy()
    CARRY_TRADE_TABLE = MARKET_MAKER.display_strategy_quotes(CARRY_TRADE_QUOTES)
    LOG_HISTORY = MARKET_MAKER.logger.get_logs()[-8:]

    curses.curs_set(0)  # Hide the cursor
    curses.start_color()  # Enable color functionality

    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # Color pair 1: Red text
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Color pair 2: Green text

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Calculate the dimensions for the windows based on the specification
    window1_height = height - 10
    # window1_width = width // 4
    window1_width = 32
    window1_start_y = 0
    window1_start_x = 0

    window2_height = height - 10
    window2_width = 3 * (width // 4)
    window2_start_y = 0
    window2_start_x = 33 # width // 4

    window3_height = 10
    window3_width = width
    window3_start_y = height - 10
    window3_start_x = 0

    # Create windows
    window1 = curses.newwin(window1_height, window1_width, window1_start_y, window1_start_x)
    window2 = curses.newwin(window2_height, window2_width, window2_start_y, window2_start_x)
    window3 = curses.newwin(window3_height, window3_width, window3_start_y, window3_start_x)

    # Start threads for each window
    thread1 = threading.Thread(target=display_order_book, args=(window1,), daemon=True)
    thread2 = threading.Thread(target=display_ct_results, args=(window2,), daemon=True)
    thread3 = threading.Thread(target=display_log, args=(window3,), daemon=True)
    
    thread1.start()
    thread2.start()
    thread3.start()

    # Keep the main loop running to maintain the window display
    while True:
        key = stdscr.getch()
        if key == ord('q'):  # Press 'q' to exit the program
            break
        elif key == ord('d'):  # Press 'd' to toggle debugging
            
            global CURSES_ACTIVE
            CURSES_ACTIVE = not CURSES_ACTIVE
            if CURSES_ACTIVE:
                # Re-enter curses mode
                curses.wrapper(create_windows)
            else:
                # Exit curses mode, print debug information
                curses.endwin()
                stdscr.clear()
                print("Debugging mode activated. Press 'c' to continue in curses.")
                import ipdb; ipdb.set_trace()
                # Once done debugging, you can return to curses mode by restarting it
                curses.wrapper(create_windows)
        
        elif key == ord('r'):
            
            with LOCK:

                MARKET_MAKER.logger.log_history = []
                MARKET_MAKER.market_data_manager.update_order_book()
                CARRY_TRADE_QUOTES = MARKET_MAKER.carry_trade_strategy()
                CARRY_TRADE_TABLE = MARKET_MAKER.display_strategy_quotes(CARRY_TRADE_QUOTES)
                LOG_HISTORY = MARKET_MAKER.logger.get_logs()[-8:]

                stdscr.clear()

def display_order_book(win):

    while CURSES_ACTIVE:
        time.sleep(0.1)
        with LOCK:  # Ensure only one thread updates at a time
            
            order_book = MARKET_MAKER.market_data_manager.current_order_book

            win.clear()
            win.border('|', '|', '-', '-', '+', '+', '+', '+')
            win.addstr(1, 5, "Asks", curses.color_pair(1))
            win.addstr(1, 10, "Bids", curses.color_pair(2))
            win.addstr(1, 15, "Order Book", curses.A_BOLD)

            win.addstr(3, 5, "Prices", curses.A_ITALIC)
            win.addstr(3, 18, "Amounts", curses.A_ITALIC)

            asks = 'ask'
            bids = 'bid'

            row = 5
            for ask in sorted(order_book[asks], key=lambda x: x['price'], reverse=True):
                win.addstr(row, 1, f"{ask['price']:>10}", curses.color_pair(1))  # Red color for asks
                win.addstr(row, 15, f"{ask['amount']:>10}")
                row += 1

            row += 1
            for bid in order_book[bids]:
                win.addstr(row, 1, f"{bid['price']:>10}", curses.color_pair(2))  # Green color for bids
                win.addstr(row, 15, f"{bid['amount']:>10}")
                row += 1

            # Calculating and displaying total amounts
            total_buy_amount = sum(order["amount"] for order in order_book[bids])
            total_sell_amount = sum(order["amount"] for order in order_book[asks])

            height, width = win.getmaxyx()
            win.addstr(height - 2, 2, "Total ", curses.color_pair(0))
            win.addstr(height - 2, 8, "Bids", curses.color_pair(2))
            win.addstr(height - 2, 12, f" amounts {total_buy_amount} units", curses.color_pair(0))
            win.addstr(height - 3, 2, "Total ", curses.color_pair(0))
            win.addstr(height - 3, 8, "Asks", curses.color_pair(1))
            win.addstr(height - 3, 12, f" amounts {total_sell_amount} units", curses.color_pair(0))

            win.refresh()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Market Simulator')
    parser.add_argument('--base_rate', type=float, default=0.03, help='Base rate for the MarketMaker instance (default: 0.03)')
    parser.add_argument('--debug', action='store_true', help='Run the simulator in debug mode')
    args = parser.parse_args()

    if args.debug:
        CURSES_ACTIVE = False
        import ipdb; ipdb.set_trace()

    if args.base_rate:
        base_rate = args.base_rate
    else:
        base_rate = 0.03

    # Initialize components
    order_book_generator = OrderBookGenerator(asset_name="SYMBOL")
    market_data_manager = MarketDataManager(order_book_generator=order_book_generator)
    MARKET_MAKER = MarketMaker(market_data_manager=market_data_manager, base_rate=base_rate)

    # Create first orderbook
    MARKET_MAKER.market_data_manager.update_order_book(max_ask_items=15, max_bid_items=15)
    # Save a copy of initial orderbook values for later use
    ORDER_BOOK_START = deepcopy(market_data_manager.current_order_book)

    height, width = curses.initscr().getmaxyx()
    curses.endwin()  # End the window to avoid issues with terminal state

    if height < 50 or width < 150:
        print(f"\nDISPLAY ERROR: The terminal size is {width}x{height}.\nIt must be at least 125x50 to run the simulator in visual mode.\n")
    else:
        curses.wrapper(create_windows)
    