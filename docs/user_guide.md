# 用户指南

## 目录
- [安装](#安装)
- [快速开始](#快速开始)
- [核心功能](#核心功能)
  - [实时行情](#实时行情)
  - [历史数据](#历史数据)
  - [技术指标](#技术指标)
  - [板块信息](#板块信息)
  - [热门股票](#热门股票)
  - [股票信息](#股票信息)
- [配置](#配置)
- [缓存](#缓存)
- [数据库](#数据库)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)

## 安装

### 环境要求
- Python 3.13.3
- pip 或 uv

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/OrionPotter/nebula.git
cd nebula
```

2. 安装依赖：
```bash
# 使用pip
pip install -e .

# 或使用uv（推荐）
uv sync
```

3. 安装开发依赖（可选）：
```bash
pip install -e .[dev]
```

## 快速开始

```python
# 导入模块
from stock_analyzer.core.realtime_quote import get_stock_realtime_quote
from stock_analyzer.core.history_quote import get_stock_history_quote
from stock_analyzer.core.indicators import get_stock_indicators

# 获取实时行情
realtime_data = get_stock_realtime_quote("600028")
print(realtime_data)

# 获取历史数据
history_data = get_stock_history_quote(
    symbol="600028",
    period="daily",
    start_date="2023-01-01",
    end_date="2023-12-31"
)
print(history_data)

# 获取技术指标
indicators = get_stock_indicators("600028", "daily")
print(indicators)
```

## 核心功能

### 实时行情

获取股票的五档报价和实时数据：

```python
from stock_analyzer.core.realtime_quote import get_stock_realtime_quote

# 获取中国石化的实时行情
quote = get_stock_realtime_quote("600028")
print(quote)
```

返回的数据包含：
- 买卖五档价格和数量
- 最新价、均价、涨幅、涨跌
- 总手、金额、换手、量比
- 最高、最低、今开、昨收等

### 历史数据

获取股票的历史价格数据：

```python
from stock_analyzer.core.history_quote import get_stock_history_quote

# 获取日线数据
daily_data = get_stock_history_quote(
    symbol="600028",
    period="daily",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# 获取周线数据
weekly_data = get_stock_history_quote(
    symbol="600028",
    period="weekly",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# 获取分钟线数据
minute_data = get_stock_history_quote(
    symbol="600028",
    period="5",  # 5分钟线
    start_date="2023-12-01 09:30:00",
    end_date="2023-12-01 15:00:00"
)
```

支持的时间周期：
- 日线：`daily`, `weekly`, `monthly`
- 分钟线：`1`, `5`, `15`, `30`, `60`

### 技术指标

计算技术指标并提供交易信号：

```python
from stock_analyzer.core.indicators import get_stock_indicators

# 获取技术指标
indicators = get_stock_indicators("600028", "daily")
print(indicators)
```

支持的技术指标：
- 移动平均线：EMA (5, 10, 20, 30, 40, 50), SMA (5, 10, 20, 30, 40, 50)
- 震荡指标：KDJ, RSI, MACD
- 支撑位和阻力位识别
- 交易信号建议

### 板块信息

获取行业和概念板块的表现数据：

```python
from stock_analyzer.core.board_quote import get_stock_board_quote

# 获取板块行情
board_data = get_stock_board_quote()
print(board_data)
```

### 热门股票

获取基于人气的股票排名：

```python
from stock_analyzer.core.hot_rank import get_stock_hot_rank

# 获取热门股票排名
hot_stocks = get_stock_hot_rank()
print(hot_stocks)
```

### 股票信息

获取股票的基本信息和财务数据：

```python
from stock_analyzer.core.stock_info import get_stock_info

# 获取股票基本信息
info = get_stock_info("600028")
print(info)
```

## 配置

### 环境变量配置

可以通过环境变量配置以下参数：

```bash
# Redis配置
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0
export REDIS_PASSWORD=your_password
export REDIS_DEFAULT_TTL=300

# 数据库配置
export DATABASE_PATH=stock_data.db

# API配置
export REQUEST_TIMEOUT=30
export REQUEST_RETRIES=3

# 日志配置
export LOG_LEVEL=INFO
export LOG_FILE=logs/stock_analyzer.log
```

### 配置文件

也可以通过代码配置：

```python
from stock_analyzer.utils.config import config

# 修改配置
config.REDIS_HOST = "your.redis.host"
config.REQUEST_TIMEOUT = 60
```

## 缓存

stock_analyzer支持Redis缓存和内存缓存：

```python
from stock_analyzer.utils.cache import cache_manager

# 设置缓存
cache_manager.set("stock_600028", stock_data, ttl=600)  # 10分钟过期

# 获取缓存
data = cache_manager.get("stock_600028")

# 检查缓存是否存在
if cache_manager.exists("stock_600028"):
    print("缓存存在")

# 删除缓存
cache_manager.delete("stock_600028")
```

当Redis不可用时，系统会自动降级到内存缓存。

## 数据库

stock_analyzer使用SQLite存储数据。数据库文件会在首次运行时自动创建：

```python
from stock_analyzer.utils.database import db_manager

# 保存数据
db_manager.save_stock_info("600028", stock_info_data)
db_manager.save_history_data("600028", history_data, "daily")
db_manager.save_indicators("600028", "2023-12-01", indicators_data)

# 查询数据
stock_info = db_manager.get_stock_info("600028")
history_data = db_manager.get_history_data(
    "600028", 
    start_date="2023-01-01", 
    end_date="2023-12-31", 
    period="daily"
)
```

数据库包含以下表：
- `stock_info`: 股票基本信息
- `stock_history`: 历史行情数据（日线、周线、月线）
- `stock_minute`: 分钟行情数据
- `stock_indicators`: 技术指标数据
- `board_quotes`: 板块行情数据
- `hot_stocks`: 热门股票排名数据

## 错误处理

stock_analyzer提供了完善的错误处理机制：

```python
from stock_analyzer.utils.errors import retry_on_failure, NetworkError, APIError

# 使用重试装饰器
@retry_on_failure(max_retries=3, delay=1.0)
def get_data():
    # 可能失败的API调用
    pass

# 处理特定异常
try:
    data = get_data()
except NetworkError as e:
    print(f"网络错误: {e}")
except APIError as e:
    print(f"API错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 最佳实践

### 1. 合理使用缓存

```python
from stock_analyzer.utils.cache import cache_manager

# 对于频繁请求的数据使用缓存
def get_cached_stock_info(symbol):
    cache_key = f"stock_info_{symbol}"
    
    # 尝试从缓存获取
    cached_data = cache_manager.get(cache_key)
    if cached_data:
        return cached_data
    
    # 缓存未命中，获取新数据
    from stock_analyzer.core.stock_info import get_stock_info
    data = get_stock_info(symbol)
    
    # 存入缓存
    cache_manager.set(cache_key, data, ttl=300)  # 5分钟过期
    
    return data
```

### 2. 批量处理数据

```python
# 批量获取多只股票的数据
def get_multiple_stocks(symbols):
    results = {}
    for symbol in symbols:
        try:
            results[symbol] = get_cached_stock_info(symbol)
        except Exception as e:
            print(f"获取{symbol}数据失败: {e}")
            results[symbol] = None
    return results
```

### 3. 异常处理和日志记录

```python
import logging
from stock_analyzer.utils.errors import retry_on_failure

logger = logging.getLogger(__name__)

@retry_on_failure(max_retries=3)
def safe_get_stock_data(symbol):
    try:
        from stock_analyzer.core.realtime_quote import get_stock_realtime_quote
        return get_stock_realtime_quote(symbol)
    except Exception as e:
        logger.error(f"获取股票{symbol}数据失败: {e}")
        raise
```

### 4. 数据库使用

```python
from stock_analyzer.utils.database import db_manager

# 定期保存数据到数据库
def save_stock_data(symbol):
    # 获取数据
    realtime_data = get_stock_realtime_quote(symbol)
    history_data = get_stock_history_quote(symbol, "daily")
    indicators_data = get_stock_indicators(symbol, "daily")
    
    # 保存到数据库
    try:
        db_manager.save_stock_info(symbol, realtime_data)
        db_manager.save_history_data(symbol, history_data, "daily")
        db_manager.save_indicators(symbol, "2023-12-01", indicators_data)
        print(f"股票{symbol}数据保存成功")
    except Exception as e:
        print(f"保存股票{symbol}数据失败: {e}")
```