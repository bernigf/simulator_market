# Market Simulator for Carry Trade Strategies in Futures Market

This project is a market simulator specifically designed for testing and implementing carry trade strategies in a futures market. It generates dynamic order books and evaluates potential carry trade opportunities using a predefined compound interest rate.

## Features

- **Order Book Generator**: Creates dynamic order books with BIDs (buy orders) and ASKs (sell orders), each containing prices and amounts. The update speed of the order book can be customized.
  
- **Earnings Calculation**: A method calculates the potential earnings from executing carry trades with a compound interest rate (hardcoded as a parameter in the script) for each ASK item in the order book. The calculation considers different maturity dates, which are by default set to `[30, 60, 90, 180, 365]` days if there are 5 maturity periods specified.

- **Trade Ranking**: The resulting list of potential earnings for each ASK item is sorted in descending order. This way, you can identify the best trades and their respective maturity dates available at that moment.

- **Real-Time Updates**: The entire calculation process is repeated whenever the order book updates, ensuring you always have up-to-date information for your trading strategy.

## Requirements

The project dependencies are listed in the `requirements.txt` file, install them using

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- **Windows Users**: If you are running the project on a Windows environment, make sure to install the `windows-curses` package to enable proper terminal functionality.

## Running the Client

To run the project, you need a terminal with at least a size of `125x50`. The main client file to execute is `client.py`, which provides the command-line interface for interacting with the market simulator.

Execute the following command to start the market simulator:

```
python client.py
```

You can also run the client in debug mode by adding the --debug parameter:

```
python client.py --debug
```

This will start the market simulator, where you can observe the order book and analyze the carry trade opportunities in real time.

## Running in Non-Visual Mode

If you encounter issues running the client due to problems with the `curses` library, you can still use the market simulator in a non-visual mode. This mode will allow you to perform all calculations and analyze the carry trade opportunities without relying on the terminal-based visual interface.

### How to Run in Non-Visual Mode

1. Open a terminal.
2. Run the following command to start the simulator in non-visual mode:
   ```bash
   python components.py
   ```

This mode bypasses the visual interface and provides the core functionality of the simulator directly through command-line outputs, ensuring compatibility on systems that do not support the `curses` library.

### How to Run
1. Open a terminal with dimensions of at least `125x50`.
2. If you're on Windows, ensure that `windows-curses` is installed.
3. Execute the following command:
   ```bash
   python client.py
   ```

This will start the market simulator, where you can observe the order book and analyze the carry trade opportunities in real time.

## License

This project is licensed under the GPLv3 License. See the `LICENSE` file for more details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or new features. 

## Contact

For any issues or questions, please open an issue on GitHub or contact the project maintainer directly at bernigf@gmail.com