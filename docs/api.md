# API Documentation

## Table of Contents
- [Core Modules](#core-modules)
  - [Real-time Quote](#real-time-quote)
  - [History Quote](#history-quote)
  - [Board Quote](#board-quote)
  - [Hot Rank](#hot-rank)
  - [Indicators](#indicators)
  - [Stock Info](#stock-info)
- [Utility Modules](#utility-modules)
  - [Cache](#cache)
  - [Database](#database)
  - [Configuration](#configuration)
  - [Error Handling](#error-handling)

## Core Modules

### Real-time Quote

#### `get_stock_realtime_quote(symbol: str = "600900") -> str`

获取股票实时行情数据（五档报价）

**Parameters:**
- `symbol` (str): 股票代码，默认为"600900"

**Returns:**
- `str`: JSON格式的行情数据

**Example:**
```python
from stock_analyzer.core.realtime_quote import get_stock_realtime_quote

# 获取中国石化(600028)的实时行情
quote = get_stock_realtime_quote("600028")
print(quote)
```

### History Quote

#### `get_stock_history_quote(symbol: str = "600900", period: str = "5", start_date: Optional[str] = None, end_date: Optional[str] = None, adjust: str = "", timeout: Optional[float] = None) -> str`

获取股票历史行情数据

**Parameters:**
- `symbol` (str): 股票代码，默认为"600900"
- `period` (str): 时间周期，可选值：
  - 日线: "daily", "weekly", "monthly"
  - 分钟线: "1", "5", "15", "30", "60"
- `start_date` (str, optional): 开始日期，格式为"YYYY-MM-DD"
- `end_date` (str, optional): 结束日期，格式为"YYYY-MM-DD"
- `adjust` (str): 复权类型，""(不复权), "qfq"(前复权), "hfq"(后复权)
- `timeout` (float, optional): 请求超时时间

**Returns:**
- `str`: JSON格式的历史行情数据

**Example:**
```python
from stock_analyzer.core.history_quote import get_stock_history_quote

# 获取日线数据
daily_data = get_stock_history_quote(
    symbol="600028", 
    period="daily", 
    start_date="2023-01-01", 
    end_date="2023-12-31"
)

# 获取5分钟线数据
minute_data = get_stock_history_quote(
    symbol="600028", 
    period="5", 
    start_date="2023-12-01 09:30:00", 
    end_date="2023-12-01 15:00:00"
)
```

### Board Quote

#### `get_stock_board_quote() -> str`

获取板块行情数据

**Returns:**
- `str`: JSON格式的板块行情数据

**Example:**
```python
from stock_analyzer.core.board_quote import get_stock_board_quote

board_data = get_stock_board_quote()
print(board_data)
```

### Hot Rank

#### `get_stock_hot_rank() -> str`

获取热门股票排名

**Returns:**
- `str`: JSON格式的热门股票排名数据

**Example:**
```python
from stock_analyzer.core.hot_rank import get_stock_hot_rank

hot_stocks = get_stock_hot_rank()
print(hot_stocks)
```

### Indicators

#### `get_stock_indicators(symbol: str = "600900", period: str = 'daily') -> str`

计算技术指标并提供交易信号

**Parameters:**
- `symbol` (str): 股票代码，默认为"600900"
- `period` (str): 时间周期，可选值："daily", "weekly", "monthly"

**Returns:**
- `str`: JSON格式的技术指标和交易信号

**Example:**
```python
from stock_analyzer.core.indicators import get_stock_indicators

indicators = get_stock_indicators("600028", "daily")
print(indicators)
```

### Stock Info

#### `get_stock_info(symbol: str = "600900", timeout: float = None) -> str`

获取股票基本信息

**Parameters:**
- `symbol` (str): 股票代码，默认为"600900"
- `timeout` (float, optional): 请求超时时间

**Returns:**
- `str`: JSON格式的股票基本信息

**Example:**
```python
from stock_analyzer.core.stock_info import get_stock_info

info = get_stock_info("600028")
print(info)
```

## Utility Modules

### Cache

#### `CacheManager`

缓存管理器，支持Redis和内存缓存

**Example:**
```python
from stock_analyzer.utils.cache import cache_manager

# 设置缓存
cache_manager.set("key", {"data": "value"}, ttl=600)

# 获取缓存
data = cache_manager.get("key")

# 删除缓存
cache_manager.delete("key")
```

### Database

#### `DatabaseManager`

数据库管理器，使用SQLite存储数据

**Example:**
```python
from stock_analyzer.utils.database import db_manager

# 保存股票信息
info_data = [{"item": "股票简称", "value": "中国石化"}]
db_manager.save_stock_info("600028", info_data)

# 获取股票信息
stock_info = db_manager.get_stock_info("600028")
```

### Configuration

#### `Config`

配置管理器，支持环境变量配置

**Environment Variables:**
- `REDIS_HOST`: Redis服务器地址
- `REDIS_PORT`: Redis端口
- `REDIS_DB`: Redis数据库编号
- `REDIS_PASSWORD`: Redis密码
- `DATABASE_PATH`: 数据库文件路径
- `REQUEST_TIMEOUT`: 请求超时时间
- `REQUEST_RETRIES`: 请求重试次数

### Error Handling

#### Custom Exceptions

- `StockAnalyzerError`: 基础异常类
- `NetworkError`: 网络错误异常
- `DataParseError`: 数据解析错误异常
- `APIError`: API错误异常

#### Retry Decorator

```python
from stock_analyzer.utils.errors import retry_on_failure

@retry_on_failure(max_retries=3, delay=1.0)
def my_function():
    # 可能失败的函数
    pass
```