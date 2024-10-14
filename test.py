import pytest
from components import OrderBookGenerator, MarketDataManager, MarketMaker

# Helper function to create a mock order book
def create_mock_order_book():
    return {
        "bid": [
            {"price": 101, "amount": 50},
            {"price": 100.5, "amount": 30},
        ],
        "ask": [
            {"price": 99, "amount": 40},
            {"price": 98.5, "amount": 20},
        ]
    }

@pytest.fixture
def market_maker():
    # Setup for MarketMaker object with a mock order book
    order_book_generator = OrderBookGenerator("Test Asset")
    market_data_manager = MarketDataManager(order_book_generator)
    market_maker = MarketMaker(market_data_manager, base_rate=0.05)  # 5% interest rate

    # Set the mock order book
    market_data_manager.current_order_book = create_mock_order_book()
    
    return market_maker

# Tests for calculate_future_price method
def test_calculate_future_price_valid_data(market_maker):
    future_price = market_maker.calculate_future_price(maturity_days=90)  # 90 days to maturity
    expected_spot_price = 99  # Using the lowest ask price from mock order book
    expected_future_price = expected_spot_price * (2.718 ** (0.05 * (90 / 365)))  # exp(rate * time)

    assert future_price == pytest.approx(expected_future_price, rel=1e-2), "Future price calculation is incorrect"

def test_calculate_future_price_no_order_book():
    # Create a market maker without an order book to simulate missing data scenario
    order_book_generator = OrderBookGenerator("Test Asset")
    market_data_manager = MarketDataManager(order_book_generator)
    market_maker = MarketMaker(market_data_manager, base_rate=0.05)

    future_price = market_maker.calculate_future_price(maturity_days=90)
    assert future_price is None, "Future price should be None if no order book is available"

# Tests for carry_trade_strategy method
def test_carry_trade_strategy_valid_data(market_maker):
    strategy_quotes = market_maker.carry_trade_strategy(N=3)
    
    # Verify that the strategy generated quotes for the 3 maturity dates
    assert len(strategy_quotes) > 0, "Strategy should generate at least one quote"
    for quote in strategy_quotes:
        assert quote["sell_price"] > 0, "Sell price should be greater than zero"
        assert quote["future_price"] > 0, "Future price should be greater than zero"
        assert quote["expected_earnings"] >= 0, "Expected earnings should be non-negative"

def test_carry_trade_strategy_no_order_book():
    # Create a market maker without an order book to test the empty scenario
    order_book_generator = OrderBookGenerator("Test Asset")
    market_data_manager = MarketDataManager(order_book_generator)
    market_maker = MarketMaker(market_data_manager, base_rate=0.05)

    strategy_quotes = market_maker.carry_trade_strategy(N=3)
    
    assert len(strategy_quotes) == 0, "Strategy quotes should be empty if no order book data is available"
