# -*- coding:utf-8 -*-
import json
import pandas as pd
from ta.trend import EMAIndicator, SMAIndicator
from ta.momentum import StochasticOscillator, RSIIndicator
from ta.trend import MACD
from .history_quote import get_stock_history_quote
from datetime import datetime, timedelta
from ..utils.cache import cache_manager
from ..utils.database import db_manager
from ..utils.logger import logger

def get_last_50_trading_days(end_date=None):
    if end_date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # 往前推100个自然日，以确保能获取到50个交易日
    start_date = end_date - timedelta(days=100)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def calculate_indicators(json_data):
    df = pd.DataFrame(json_data)
    df['时间'] = pd.to_datetime(df['时间'])
    df.set_index('时间', inplace=True)
    df.sort_index(inplace=True)
    df.rename(columns={
        '开盘': 'open', '最高': 'high', '最低': 'low', '收盘': 'close', '成交量': 'volume'
    }, inplace=True)
    
    # 只保留最近50个交易日的数据
    df = df.tail(50)
    
    for period in [5, 10, 20, 30, 40, 50]:
        ema = EMAIndicator(close=df['close'], window=period)
        sma = SMAIndicator(close=df['close'], window=period)
        df[f'EMA{period}'] = ema.ema_indicator()
        df[f'SMA{period}'] = sma.sma_indicator()
    
    stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
    df['K'] = stoch.stoch()
    df['D'] = stoch.stoch_signal()
    df['J'] = 3 * df['K'] - 2 * df['D']
    
    rsi = RSIIndicator(close=df['close'])
    df['RSI'] = rsi.rsi()
    
    macd = MACD(close=df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_histogram'] = macd.macd_diff()
    
    return df

def find_support_resistance(df, window=5):
    supports = []
    resistances = []
    
    for i in range(window, len(df) - window):
        if df['low'].iloc[i] == min(df['low'].iloc[i-window:i+window+1]):
            supports.append(df['low'].iloc[i])
        if df['high'].iloc[i] == max(df['high'].iloc[i-window:i+window+1]):
            resistances.append(df['high'].iloc[i])
    
    current_price = df['close'].iloc[-1]
    
    # 筛选出低于当前价格的支撑位
    supports = [s for s in supports if s < current_price]
    # 筛选出高于当前价格的阻力位
    resistances = [r for r in resistances if r > current_price]
    
    # 取最近的3个支撑位和阻力位
    supports = sorted(supports, reverse=True)[:3]
    resistances = sorted(resistances)[:3]
    
    return supports, resistances

def interpret_indicators(df):
    latest = df.iloc[-1]
    result = []

    # EMA 和 SMA 解释
    for period in [5, 10, 20, 30, 40, 50]:
        ema_value = latest[f'EMA{period}']
        sma_value = latest[f'SMA{period}']
        close = latest['close']
        
        result.append({
            "指标名称": f"EMA{period}",
            "值": f"{ema_value:.2f}",
            "操作": "买入" if close > ema_value else "卖出" if close < ema_value else "中立"
        })
        result.append({
            "指标名称": f"SMA{period}",
            "值": f"{sma_value:.2f}",
            "操作": "买入" if close > sma_value else "卖出" if close < sma_value else "中立"
        })

    # KDJ 解释
    result.append({
        "指标名称": "KDJ",
        "值": f"K:{latest['K']:.2f}, D:{latest['D']:.2f}, J:{latest['J']:.2f}",
        "操作": "买入" if latest['K'] > latest['D'] else "卖出" if latest['K'] < latest['D'] else "中立"
    })

    # RSI 解释
    rsi_value = latest['RSI']
    result.append({
        "指标名称": "RSI",
        "值": f"{rsi_value:.2f}",
        "操作": "卖出" if rsi_value > 70 else "买入" if rsi_value < 30 else "中立"
    })

    # MACD 解释
    result.append({
        "指标名称": "MACD",
        "值": f"MACD:{latest['MACD']:.2f}, Signal:{latest['MACD_signal']:.2f}, Histogram:{latest['MACD_histogram']:.2f}",
        "操作": "买入" if latest['MACD'] > latest['MACD_signal'] else "卖出"
    })

    # 支撑位和阻力位
    supports, resistances = find_support_resistance(df)
    if supports:
        result.append({
            "指标名称": "支撑位",
            "值": ", ".join([f"{s:.2f}" for s in supports]),
            "操作": "在接近支撑位时考虑买入"
        })
    else:
        result.append({
            "指标名称": "支撑位",
            "值": "未找到有效支撑位",
            "操作": "需要进一步观察"
        })
    
    if resistances:
        result.append({
            "指标名称": "阻力位",
            "值": ", ".join([f"{r:.2f}" for r in resistances]),
            "操作": "在接近阻力位时考虑卖出"
        })
    else:
        result.append({
            "指标名称": "阻力位",
            "值": "未找到有效阻力位",
            "操作": "需要进一步观察"
        })

    return result

def get_stock_indicators(symbol: str = "600900", period: str = 'daily', use_cache: bool = True, save_to_db: bool = True) -> str:
    # 尝试从缓存获取数据
    if use_cache:
        cache_key = f"stock_indicators_{symbol}_{period}"
        cached_data = cache_manager.get(cache_key)
        if cached_data:
            logger.info(f"从缓存获取技术指标数据: {symbol}")
            return json.dumps(cached_data, ensure_ascii=False, indent=2)
    
    start_date, end_date = get_last_50_trading_days()
    data = get_stock_history_quote(symbol=symbol, period=period, start_date=start_date, end_date=end_date)
    json_data = json.loads(data)
    indicators_df = calculate_indicators(json_data)
    advice = interpret_indicators(indicators_df)
    
    # 缓存数据
    if use_cache:
        cache_manager.set(cache_key, advice, 300)  # 缓存5分钟
        logger.info(f"技术指标数据已缓存: {symbol}")
    
    # 保存到数据库
    if save_to_db:
        saved_count = db_manager.save_indicators(symbol, end_date, advice)
        logger.info(f"技术指标数据已保存到数据库: {symbol}, 保存了 {saved_count} 条记录")
    
    return json.dumps(advice, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    result = get_stock_indicators("600900", "daily")
    print(result)