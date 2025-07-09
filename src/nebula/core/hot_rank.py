# -*- coding:utf-8 -*-
import pandas as pd
import requests
import json

def to_json(df: pd.DataFrame) -> str:
    """Convert DataFrame to JSON string"""
    return df.to_json(orient='records', force_ascii=False, indent=2)

def get_stock_hot_rank() -> str:
    """东方财富-个股人气榜-人气榜"""
    url = "https://emappdata.eastmoney.com/stockrank/getAllCurrentList"
    payload = {
        "appId": "appId01",
        "globalId": "786e4c21-70dc-435a-93bb-38",
        "marketType": "",
        "pageNo": 1,
        "pageSize": 100,
    }
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        data_json = r.json()
        temp_rank_df = pd.DataFrame(data_json["data"])

        temp_rank_df["mark"] = ["0" + "." + item[2:] if "SZ" in item else "1" + "." + item[2:] for item in temp_rank_df["sc"]]
        params = {
            "ut": "f057cbcbce2a86e2866ab8877db1d059",
            "fltt": "2",
            "invt": "2",
            "fields": "f14,f3,f12,f2",
            "secids": ",".join(temp_rank_df["mark"]) + ",?v=08926209912590994",
        }
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        r = requests.get(url, params=params)
        r.raise_for_status()
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["data"]["diff"])
        temp_df.columns = ["最新价", "涨跌幅", "代码", "股票名称"]
        temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
        temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
        temp_df["涨跌额"] = temp_df["最新价"] * temp_df["涨跌幅"] / 100
        temp_df["当前排名"] = temp_rank_df["rk"]
        temp_df["代码"] = temp_rank_df["sc"]
        temp_df = temp_df[["当前排名", "代码", "股票名称", "最新价", "涨跌额", "涨跌幅"]]
        temp_df["当前排名"] = pd.to_numeric(temp_df["当前排名"], errors="coerce")
        return to_json(temp_df)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(get_stock_hot_rank())