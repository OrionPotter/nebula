import requests
import pandas as pd
import json

def get_stock_board_quote() -> str:
    """
    东方财富网-行情中心-沪深京板块-概念板块-名称
    https://quote.eastmoney.com/center/boardlist.html#concept_board
    :return: 概念板块-名称（JSON 格式）
    :rtype: str
    """
    url = "https://79.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "50000",
        "po": "1",
        "np": "2",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:90 t:3 f:!50",
        "fields": "f2,f3,f4,f8,f12,f14,f15,f16,f17,f18,f20,f21,f24,f25,f22,f33,f11,f62,f128,f124,f107,f104,f105,f136",
        "_": "1626075887768",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data_json = response.json()

        if not data_json.get("data", {}).get("diff"):
            return json.dumps({"error": "No data found"}, ensure_ascii=False)

        temp_df = pd.DataFrame(data_json["data"]["diff"]).T
        temp_df.reset_index(inplace=True)
        temp_df["index"] = range(1, len(temp_df) + 1)
        
        columns = [
            "排名", "最新价", "涨跌幅", "涨跌额", "换手率", "_", "板块代码", "板块名称",
            "_", "_", "_", "_", "总市值", "_", "_", "_", "_", "_", "_",
            "上涨家数", "下跌家数", "_", "_", "领涨股票", "_", "_", "领涨股票-涨跌幅"
        ]
        temp_df.columns = columns

        selected_columns = [
            "排名", "板块名称", "板块代码", "最新价", "涨跌额", "涨跌幅", "总市值",
            "换手率", "上涨家数", "下跌家数", "领涨股票", "领涨股票-涨跌幅"
        ]
        temp_df = temp_df[selected_columns]

        numeric_columns = ["最新价", "涨跌额", "涨跌幅", "总市值", "换手率", "上涨家数", "下跌家数", "领涨股票-涨跌幅"]
        for col in numeric_columns:
            temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")

        # 将 DataFrame 转换为 JSON 字符串
        json_result = temp_df.to_json(orient='records', force_ascii=False, indent=2)
        return json_result

    except requests.RequestException as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"}, ensure_ascii=False)

if __name__ == "__main__":
    result = get_stock_board_quote()
    print(result)