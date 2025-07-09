# -*- coding:utf-8 -*-
import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
from .config import config

class DatabaseManager:
    """数据库管理器，使用SQLite作为默认数据库"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        # 使用配置文件中的默认值或传入的参数
        database_config = config.get_database_config()
        self.db_path = db_path or database_config['path']
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建股票基本信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_info (
                    symbol TEXT PRIMARY KEY,
                    name TEXT,
                    industry TEXT,
                    market TEXT,
                    list_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建历史行情表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    date TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    amount REAL,
                    amplitude REAL,
                    change_percent REAL,
                    change_amount REAL,
                    turnover_rate REAL,
                    UNIQUE(symbol, date)
                )
            ''')
            
            # 创建分钟行情表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_minute (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    datetime TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    amount REAL,
                    average REAL,
                    UNIQUE(symbol, datetime)
                )
            ''')
            
            # 创建技术指标表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    date TEXT,
                    indicator_name TEXT,
                    indicator_value REAL,
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date, indicator_name)
                )
            ''')
            
            # 创建板块行情表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS board_quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    board_code TEXT,
                    board_name TEXT,
                    price REAL,
                    change_amount REAL,
                    change_percent REAL,
                    market_value REAL,
                    turnover_rate REAL,
                    listed_companies INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(board_code)
                )
            ''')
            
            # 创建热门股票表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hot_stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rank INTEGER,
                    symbol TEXT,
                    name TEXT,
                    price REAL,
                    change_amount REAL,
                    change_percent REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol)
                )
            ''')
            
            # 创建索引以提高查询性能
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_stock_history_symbol_date 
                ON stock_history (symbol, date)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_stock_minute_symbol_datetime 
                ON stock_minute (symbol, datetime)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_stock_indicators_symbol_date 
                ON stock_indicators (symbol, date)
            ''')
            
            conn.commit()
    
    def save_stock_info(self, symbol: str, info_data: List[Dict[str, Any]]) -> bool:
        """
        保存股票基本信息
        
        Args:
            symbol: 股票代码
            info_data: 股票信息数据列表
            
        Returns:
            bool: 是否保存成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 转换数据格式
                info_dict = {item['item']: item['value'] for item in info_data}
                
                # 确定市场类型
                market = 'SH' if symbol.startswith('6') else 'SZ'
                
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_info 
                    (symbol, name, industry, market, list_date, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    info_dict.get('股票简称'),
                    info_dict.get('行业'),
                    market,
                    info_dict.get('上市时间'),
                    datetime.now()
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"保存股票信息时出错: {e}")
            return False
    
    def save_history_data(self, symbol: str, history_data: List[Dict[str, Any]], 
                         period: str = 'daily') -> int:
        """
        保存历史行情数据
        
        Args:
            symbol: 股票代码
            history_data: 历史行情数据列表
            period: 时间周期 ('daily', 'weekly', 'monthly', 'minute')
            
        Returns:
            int: 成功保存的记录数
        """
        try:
            saved_count = 0
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if period == 'minute':
                    table_name = 'stock_minute'
                    columns = ['symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'average']
                else:
                    table_name = 'stock_history'
                    columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'amount', 
                              'amplitude', 'change_percent', 'change_amount', 'turnover_rate']
                
                for row in history_data:
                    try:
                        if period == 'minute':
                            values = (
                                symbol,
                                row['时间'],
                                float(row['开盘']),
                                float(row['最高']),
                                float(row['最低']),
                                float(row['收盘']),
                                int(row['成交量']),
                                float(row['成交额']),
                                float(row.get('均价', 0))
                            )
                        else:
                            values = (
                                symbol,
                                row['时间'],
                                float(row['开盘']),
                                float(row['最高']),
                                float(row['最低']),
                                float(row['收盘']),
                                int(row['成交量']),
                                float(row['成交额']),
                                float(row.get('振幅', 0)),
                                float(row.get('涨跌幅', 0)),
                                float(row.get('涨跌额', 0)),
                                float(row.get('换手率', 0))
                            )
                        
                        # 构建插入语句
                        placeholders = ', '.join(['?' for _ in columns])
                        insert_sql = f'''
                            INSERT OR REPLACE INTO {table_name} 
                            ({', '.join(columns)})
                            VALUES ({placeholders})
                        '''
                        
                        cursor.execute(insert_sql, values)
                        saved_count += 1
                    except (ValueError, KeyError) as e:
                        print(f"跳过无效数据行: {row}, 错误: {e}")
                        continue
                
                conn.commit()
                return saved_count
        except Exception as e:
            print(f"保存历史行情数据时出错: {e}")
            return 0
    
    def save_indicators(self, symbol: str, date: str, indicators: List[Dict[str, Any]]) -> int:
        """
        保存技术指标数据
        
        Args:
            symbol: 股票代码
            date: 日期
            indicators: 技术指标数据列表
            
        Returns:
            int: 成功保存的记录数
        """
        try:
            saved_count = 0
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for indicator in indicators:
                    try:
                        # 解析指标值
                        value_str = indicator['值']
                        # 处理可能包含多个值的情况（如KDJ）
                        if ':' in value_str and ',' in value_str:
                            # 对于复杂值，存储原始字符串
                            indicator_value = value_str
                        else:
                            # 尝试转换为数值
                            try:
                                indicator_value = float(value_str)
                            except ValueError:
                                indicator_value = value_str
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO stock_indicators 
                            (symbol, date, indicator_name, indicator_value)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            symbol,
                            date,
                            indicator['指标名称'],
                            indicator_value
                        ))
                        saved_count += 1
                    except (ValueError, KeyError) as e:
                        print(f"跳过无效指标数据: {indicator}, 错误: {e}")
                        continue
                
                conn.commit()
                return saved_count
        except Exception as e:
            print(f"保存技术指标数据时出错: {e}")
            return 0
    
    def get_stock_info(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取股票基本信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            股票信息数据列表或None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT symbol, name, industry, market, list_date 
                    FROM stock_info 
                    WHERE symbol = ?
                ''', (symbol,))
                
                row = cursor.fetchone()
                if row:
                    return [
                        {'item': '股票代码', 'value': row[0]},
                        {'item': '股票简称', 'value': row[1]},
                        {'item': '行业', 'value': row[2]},
                        {'item': '市场', 'value': row[3]},
                        {'item': '上市时间', 'value': row[4]}
                    ]
                return None
        except Exception as e:
            print(f"获取股票信息时出错: {e}")
            return None
    
    def get_history_data(self, symbol: str, start_date: str = None, 
                        end_date: str = None, period: str = 'daily') -> Optional[pd.DataFrame]:
        """
        获取历史行情数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 时间周期 ('daily', 'weekly', 'monthly', 'minute')
            
        Returns:
            历史行情数据DataFrame或None
        """
        try:
            with self.get_connection() as conn:
                if period == 'minute':
                    table_name = 'stock_minute'
                    columns = ['datetime as 时间', 'open as 开盘', 'high as 最高', 'low as 最低', 
                              'close as 收盘', 'volume as 成交量', 'amount as 成交额', 'average as 均价']
                    date_column = 'datetime'
                else:
                    table_name = 'stock_history'
                    columns = ['date as 时间', 'open as 开盘', 'high as 最高', 'low as 最低', 
                              'close as 收盘', 'volume as 成交量', 'amount as 成交额', 
                              'amplitude as 振幅', 'change_percent as 涨跌幅', 
                              'change_amount as 涨跌额', 'turnover_rate as 换手率']
                    date_column = 'date'
                
                # 构建查询条件
                query = f"SELECT {', '.join(columns)} FROM {table_name} WHERE symbol = ?"
                params = [symbol]
                
                if start_date:
                    query += f" AND {date_column} >= ?"
                    params.append(start_date)
                
                if end_date:
                    query += f" AND {date_column} <= ?"
                    params.append(end_date)
                
                query += f" ORDER BY {date_column}"
                
                # 执行查询
                df = pd.read_sql_query(query, conn, params=params)
                return df if not df.empty else None
        except Exception as e:
            print(f"获取历史行情数据时出错: {e}")
            return None

# 全局数据库管理器实例
db_manager = DatabaseManager()