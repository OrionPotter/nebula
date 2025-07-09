# -*- coding:utf-8 -*-
import pandas as pd
import requests
import json

BASE_URL = "https://push2.eastmoney.com/api/qt/stock/get"
PARAMS = {
    "ut": "fa5fd1943c7b386f172d6893dbfba10b",
    "fltt": "2",
    "invt": "2",
    "fields": "f57,f58,f84,f85,f127,f116,f117,f189",
    "_": "1640157544804",
}

CODE_NAME_MAP = {
    "f57": "股票代码",
    "f58": "股票简称",
    "f84": "总股本",
    "f85": "流通股",
    "f127": "行业",
    "f116": "总市值",
    "f117": "流通市值",
    "f189": "上市时间",
}

def get_stock_info(symbol: str = "600900", timeout: float = None) -> str:
    """
    东方财富-个股-股票信息
    :param symbol: 股票代码
    :param timeout: 请求超时时间
    :return: 股票信息的JSON字符串
    """
    try:
        market_code = 1 if symbol.startswith("6") else 0
        params = {**PARAMS, "secid": f"{market_code}.{symbol}"}
        
        with requests.Session() as session:
            response = session.get(BASE_URL, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
        
        if 'data' not in data:
            return json.dumps({"error": "No data found"}, ensure_ascii=False, indent=2)
        
        stock_data = {CODE_NAME_MAP[k]: v for k, v in data['data'].items() if k in CODE_NAME_MAP}
        df = pd.DataFrame(list(stock_data.items()), columns=['item', 'value'])
        
        return df.to_json(orient='records', force_ascii=False, indent=2)
    
    except requests.RequestException as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"}, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    result = get_stock_info(symbol="600900")
    print(result)