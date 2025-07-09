# -*- coding:utf-8 -*-
import requests
import pandas as pd
from datetime import datetime
from typing import Optional
from ..utils.cache import cache_manager
from ..utils.database import db_manager
from ..utils.logger import logger

# 常量定义
BASE_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
MINUTE_URL = "https://push2his.eastmoney.com/api/qt/stock/trends2/get"
ADJUST_MAP = {"": "0", "qfq": "1", "hfq": "2"}
PERIOD_MAP = {"daily": "101", "weekly": "102", "monthly": "103"}
MINUTE_PERIODS = {'1', '5', '15', '30', '60'}

def _to_date(dt_str: Optional[str]) -> str:
    """转为 'YYYYMMDD' 格式字符串"""
    if not dt_str:
        return ""
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d").strftime("%Y%m%d")
    except ValueError:
        return datetime.strptime(dt_str, "%Y%m%d").strftime("%Y%m%d")

def _to_datetime(dt_str: Optional[str], default_time: str = "00:00:00") -> str:
    """输入'YYYY-MM-DD'或'YYYY-MM-DD HH:MM:SS'，输出'YYYY-MM-DD HH:MM:SS'"""
    if not dt_str:
        return ""
    dt_str = dt_str.strip()
    if len(dt_str) == 10:
        return f"{dt_str} {default_time}"
    if len(dt_str) == 8:
        return f"{datetime.strptime(dt_str, '%Y%m%d').strftime('%Y-%m-%d')} {default_time}"
    return dt_str

def get_stock_history_quote(
    symbol: str = "600900",
    period: str = "5",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    adjust: str = "",
    timeout: Optional[float] = None,
    use_cache: bool = True,
    save_to_db: bool = True
) -> str:
    """获取股票历史行情数据"""
    # 尝试从缓存获取数据
    if use_cache:
        cache_key = f"history_quote_{symbol}_{period}_{start_date}_{end_date}_{adjust}"
        cached_data = cache_manager.get(cache_key)
        if cached_data:
            logger.info(f"从缓存获取历史行情数据: {symbol}, period={period}")
            return cached_data
    
    market_code = 1 if symbol.startswith("6") else 0
    is_minute = period in MINUTE_PERIODS

    start_date = start_date or "1970-01-01"
    end_date = end_date or "2099-12-31"

    session = requests.Session()

    try:
        if is_minute:
            sdt = _to_datetime(start_date, "00:00:00")
            edt = _to_datetime(end_date, "23:59:59")
            
            if period == "1":
                url = MINUTE_URL
                params = {
                    "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
                    "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
                    "ut": "7eea3edcaed734bea9cbfc24409ed989",
                    "ndays": "10",
                    "iscr": "0",
                    "secid": f"{market_code}.{symbol}",
                    "_": "1623766962675",
                }
                columns = ["时间", "开盘", "收盘", "最高", "最低", "成交量", "成交额", "均价"]
            else:
                url = BASE_URL
                params = {
                    "fields1": "f1,f2,f3,f4,f5,f6",
                    "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                    "ut": "7eea3edcaed734bea9cbfc24409ed989",
                    "klt": period,
                    "fqt": ADJUST_MAP[adjust],
                    "secid": f"{market_code}.{symbol}",
                    "beg": "0",
                    "end": "20500000",
                    "_": "1630930917857",
                }
                columns = ["时间", "开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率"]

            response = session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            data_json = response.json()

            if not (data_json.get("data") and data_json["data"].get("trends" if period == "1" else "klines")):
                return "[]"

            temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["trends" if period == "1" else "klines"]])
            temp_df.columns = columns
            
            temp_df.index = pd.to_datetime(temp_df["时间"])
            temp_df = temp_df[(temp_df.index >= pd.to_datetime(sdt)) & (temp_df.index <= pd.to_datetime(edt))]
            temp_df.reset_index(drop=True, inplace=True)
            
            num_cols = [col for col in columns if col != "时间"]
            temp_df[num_cols] = temp_df[num_cols].apply(pd.to_numeric, errors="coerce")
            temp_df["时间"] = pd.to_datetime(temp_df["时间"]).astype(str)

        else:
            sdt = _to_date(start_date)
            edt = _to_date(end_date)
            params = {
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
                "ut": "7eea3edcaed734bea9cbfc24409ed989",
                "klt": PERIOD_MAP[period],
                "fqt": ADJUST_MAP[adjust],
                "secid": f"{market_code}.{symbol}",
                "beg": sdt,
                "end": edt,
                "_": "1623766962675",
            }
            response = session.get(BASE_URL, params=params, timeout=timeout)
            response.raise_for_status()
            data_json = response.json()

            if not (data_json["data"] and data_json["data"]["klines"]):
                return "[]"

            temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
            temp_df.columns = ["时间", "开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率"]
            temp_df["时间"] = pd.to_datetime(temp_df["时间"]).astype(str)
            num_cols = ["开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率"]
            temp_df[num_cols] = temp_df[num_cols].apply(pd.to_numeric, errors="coerce")

        result = temp_df.to_json(orient='records', force_ascii=False, indent=2)
        
        # 缓存数据
        if use_cache:
            cache_manager.set(cache_key, result, 300)  # 缓存5分钟
            logger.info(f"历史行情数据已缓存: {symbol}, period={period}")
        
        # 保存到数据库
        if save_to_db:
            data_list = temp_df.to_dict(orient='records')
            saved_count = db_manager.save_history_data(symbol, data_list, 'minute' if is_minute else 'daily')
            logger.info(f"历史行情数据已保存到数据库: {symbol}, 保存了 {saved_count} 条记录")
        
        return result

    except requests.RequestException as e:
        logger.error(f"请求历史行情数据时出错: {str(e)}")
        return f"请求错误: {str(e)}"
    except Exception as e:
        logger.error(f"获取历史行情数据时出错: {str(e)}")
        return f"发生错误: {str(e)}"
    finally:
        session.close()

if __name__ == "__main__":
    print(get_stock_history_quote(symbol="600900", period='15', start_date='2025-07-09 13:00:00', end_date='2025-07-09 15:00:00'))
    print(get_stock_history_quote(symbol="600900", period='daily', start_date='2023-07-01', end_date='2023-07-10'))