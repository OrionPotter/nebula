# stock_analyzer

[![Python](https://img.shields.io/badge/Python-3.13.3-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

This toolkit provides a comprehensive set of modules for retrieving and analyzing Chinese stock market data from East Money (东方财富网). It offers real-time quotes, historical data, technical indicators, board information, and more.

## Features

- **Real-time Stock Quotes**: Get up-to-the-minute stock prices and market data
- **Historical Data**: Retrieve daily, weekly, monthly, and minute-level historical prices
- **Technical Analysis**: Calculate EMA, SMA, KDJ, RSI, MACD indicators with trading signals
- **Board Information**: Access sector and concept board performance
- **Hot Stock Rankings**: Discover trending stocks based on popularity
- **Stock Fundamentals**: Retrieve company information and financial metrics
- **Data Persistence**: Store data in SQLite database for analysis and backtesting
- **Caching**: Built-in Redis caching for improved performance

## Modules Overview

| Module | Description |
|--------|-------------|
| `nebula.core.realtime_quote` | Retrieves real-time tick data (五档报价) |
| `nebula.core.history_quote` | Fetches historical price data (daily/weekly/monthly/minute) |
| `nebula.core.board_quote` | Gets sector and concept board performance data |
| `nebula.core.hot_rank` | Retrieves popular stock rankings |
| `nebula.core.indicators` | Calculates technical indicators and provides trading signals |
| `nebula.core.stock_info` | Retrieves company information and fundamentals |

## Installation

1. Clone the repository:
```bash
git clone https://github.com/OrionPotter/nebula.git
cd nebula
```

2. Install required dependencies:
```bash
# Using pip
pip install pandas requests ta redis python-dotenv

# Or using uv (recommended)
uv sync
```

## Usage Examples

### Get Real-time Quote
```python
from stock_analyzer.core.realtime_quote import get_stock_realtime_quote

quote = get_stock_realtime_quote(symbol="600900")
print(quote)
```

### Retrieve Historical Data
```python
from stock_analyzer.core.history_quote import get_stock_history_quote

# Daily data
daily_data = get_stock_history_quote(symbol="600900", period='daily', 
                                    start_date='2023-07-01', end_date='2023-07-10')

# Minute-level data
minute_data = get_stock_history_quote(symbol="600900", period='15', 
                                     start_date='2023-07-09 13:00:00', 
                                     end_date='2023-07-09 15:00:00')
```

### Analyze Technical Indicators
```python
from stock_analyzer.core.indicators import get_stock_indicators

analysis = get_stock_indicators(symbol="600900", period='daily')
print(analysis)
```

### Get Board Information
```python
from stock_analyzer.core.board_quote import get_stock_board_quote

board_data = get_stock_board_quote()
```

### Access Hot Stock Rankings
```python
from stock_analyzer.core.hot_rank import get_stock_hot_rank

hot_stocks = get_stock_hot_rank()
```

### Retrieve Stock Fundamentals
```python
from stock_analyzer.core.stock_info import get_stock_info

info = get_stock_info(symbol="600900")
```

## Technical Indicators Supported

The `get_stock_indicators` module calculates the following technical indicators:

- **Moving Averages**:
  - EMA (5, 10, 20, 30, 40, 50)
  - SMA (5, 10, 20, 30, 40, 50)
  
- **Oscillators**:
  - KDJ (Stochastic Oscillator)
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  
- **Support & Resistance Levels**:
  - Identifies key support and resistance levels
  
- **Trading Signals**:
  - Provides buy/sell/hold recommendations based on indicator analysis

## Data Persistence

The toolkit uses SQLite for data persistence. Database file is created automatically on first run and can be configured via environment variables.

## Caching

Redis caching is supported to improve performance. If Redis is not available, the system will automatically fall back to in-memory caching.

## Data Sources

All data is retrieved from East Money (东方财富网) public APIs:
- https://push2.eastmoney.com
- https://push2his.eastmoney.com
- https://emappdata.eastmoney.com

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This toolkit is for educational and research purposes only. The data and analysis provided should not be considered as financial advice. Always conduct your own research before making any investment decisions.