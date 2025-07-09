# -*- coding:utf-8 -*-
import os
import redis
from dotenv import load_dotenv
from typing import Optional

class Config:
    """配置管理器"""
    
    # Redis配置 - 支持Upstash Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_DEFAULT_TTL = int(os.getenv('REDIS_DEFAULT_TTL', 300))
    
    # 数据库配置
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'stock_data.db')
    
    # API配置
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    REQUEST_RETRIES = int(os.getenv('REQUEST_RETRIES', 3))
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'stock_analyzer.log')
    
    @classmethod
    def get_redis_config(cls):
        """获取Redis配置"""
        return {
            'url': cls.REDIS_URL,
            'host': cls.REDIS_HOST,
            'port': cls.REDIS_PORT,
            'db': cls.REDIS_DB,
            'password': cls.REDIS_PASSWORD,
            'default_ttl': cls.REDIS_DEFAULT_TTL
        }
    
    @classmethod
    def get_database_config(cls):
        """获取数据库配置"""
        return {
            'path': cls.DATABASE_PATH
        }
    
    @classmethod
    def get_api_config(cls):
        """获取API配置"""
        return {
            'timeout': cls.REQUEST_TIMEOUT,
            'retries': cls.REQUEST_RETRIES
        }
    
load_dotenv() 
# 全局配置实例
config = Config()