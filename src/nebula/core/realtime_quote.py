# -*- coding:utf-8 -*-
import pandas as pd
import requests
import json
from ..utils.errors import retry_on_failure, make_request, handle_api_response
from ..utils.config import config
from ..utils.cache import cache_manager
from ..utils.database import db_manager
from ..utils.logger import logger

# 常量定义
BASE_URL = "https://push2.eastmoney.com/api/qt/stock/get"
FIELDS = (
    "f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,"
    "f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,"
    "f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,"
    "f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,"
    "f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,"
    "f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,"
    "f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,"
    "f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20"
)

TICK_MAP = {
    "卖五价": "f31", "卖五量": "f32", "卖四价": "f33", "卖四量": "f34",
    "卖三价": "f35", "卖三量": "f36", "卖二价": "f37", "卖二量": "f38",
    "卖一价": "f39", "卖一量": "f40", "买一价": "f19", "买一量": "f20",
    "买二价": "f17", "买二量": "f18", "买三价": "f15", "买三量": "f16",
    "买四价": "f13", "买四量": "f14", "买五价": "f11", "买五量": "f12",
    "最新": "f43", "均价": "f71", "涨幅": "f170", "涨跌": "f169",
    "总手": "f47", "金额": "f48", "换手": "f168", "量比": "f50",
    "最高": "f44", "最低": "f45", "今开": "f46", "昨收": "f60",
    "涨停": "f51", "跌停": "f52", "外盘": "f49", "内盘": "f161"
}

@retry_on_failure()
def get_stock_realtime_quote(symbol: str = "600900", use_cache: bool = True, save_to_db: bool = True) -> str:
    """
    东方财富-行情报价
    :param symbol: 股票代码
    :param use_cache: 是否使用缓存
    :param save_to_db: 是否保存到数据库
    :return: 行情报价的JSON字符串
    """
    # 尝试从缓存获取数据
    if use_cache:
        cache_key = f"realtime_quote_{symbol}"
        cached_data = cache_manager.get(cache_key)
        if cached_data:
            logger.info(f"从缓存获取实时行情数据: {symbol}")
            return json.dumps(cached_data, ensure_ascii=False, indent=2)
    
    market_code = 1 if symbol.startswith("6") else 0
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": FIELDS,
        "secid": f"{market_code}.{symbol}",
    }

    try:
        response = make_request(BASE_URL, params=params, timeout=config.get_api_config()['timeout'])
        data_json = handle_api_response(response)

        if "data" not in data_json:
            return '{"error": "No data found"}'

        tick_dict = {}
        for key, field in TICK_MAP.items():
            value = data_json["data"].get(field)
            if field in ["f32", "f34", "f36", "f38", "f40", "f20", "f18", "f16", "f14", "f12"]:
                value = value * 100 if value is not None else None
            tick_dict[key] = value

        temp_df = pd.DataFrame(list(tick_dict.items()), columns=["item", "value"])
        result = temp_df.to_dict(orient='records')
        
        # 缓存数据
        if use_cache:
            cache_manager.set(cache_key, result, config.get_redis_config()['default_ttl'])
            logger.info(f"实时行情数据已缓存: {symbol}")
        
        # 保存到数据库
        if save_to_db:
            db_manager.save_stock_info(symbol, result)
            logger.info(f"实时行情数据已保存到数据库: {symbol}")
        
        return temp_df.to_json(orient='records', force_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"获取实时行情数据时出错: {str(e)}")
        return f'{{"error": "An unexpected error occurred: {str(e)}"}}'

if __name__ == "__main__":
    stock_realtime_quote = get_stock_realtime_quote(symbol="600900")
    print(stock_realtime_quote)