# -*- coding:utf-8 -*-
import time
import requests
from typing import Optional, Callable, Any
from functools import wraps
from .config import config
from .logger import logger

def retry_on_failure(max_retries: Optional[int] = None, delay: float = 1.0, 
                    backoff: float = 2.0, exceptions: tuple = (requests.RequestException,)):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数，默认使用配置文件中的值
        delay: 初始延迟时间（秒）
        backoff: 延迟时间增长倍数
        exceptions: 需要重试的异常类型
    """
    if max_retries is None:
        max_retries = config.get_api_config()['retries']
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            current_delay = delay
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        raise e
                    
                    logger.warning(f"请求失败 (尝试 {retries}/{max_retries + 1}): {str(e)}")
                    logger.info(f"等待 {current_delay} 秒后重试...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # 这行代码不应该被执行到
            raise Exception("重试逻辑异常")
        
        return wrapper
    return decorator

class StockAnalyzerError(Exception):
    """Stock Analyzer基础异常类"""
    pass

class NetworkError(StockAnalyzerError):
    """网络错误异常"""
    pass

class DataParseError(StockAnalyzerError):
    """数据解析错误异常"""
    pass

class APIError(StockAnalyzerError):
    """API错误异常"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

def handle_api_response(response: requests.Response) -> dict:
    """
    处理API响应
    
    Args:
        response: requests响应对象
        
    Returns:
        解析后的JSON数据
        
    Raises:
        APIError: API返回错误
        DataParseError: 数据解析错误
    """
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        logger.error(f"HTTP错误: {response.status_code} - {response.reason}")
        raise APIError(f"HTTP错误: {response.status_code} - {response.reason}", 
                      response.status_code) from e
    
    try:
        data = response.json()
        return data
    except ValueError as e:
        logger.error(f"JSON解析失败: {str(e)}")
        raise DataParseError(f"JSON解析失败: {str(e)}") from e

@retry_on_failure()
def make_request(url: str, params: Optional[dict] = None, 
                timeout: Optional[float] = None) -> requests.Response:
    """
    发送HTTP请求
    
    Args:
        url: 请求URL
        params: 请求参数
        timeout: 超时时间，默认使用配置文件中的值
        
    Returns:
        requests响应对象
        
    Raises:
        NetworkError: 网络错误
        APIError: API错误
    """
    if timeout is None:
        timeout = config.get_api_config()['timeout']
    
    try:
        logger.debug(f"发送HTTP请求: {url}, 参数: {params}, 超时: {timeout}")
        response = requests.get(url, params=params, timeout=timeout)
        logger.debug(f"HTTP请求成功: {response.status_code}")
        return response
    except requests.Timeout as e:
        logger.error(f"请求超时 ({timeout}秒): {str(e)}")
        raise NetworkError(f"请求超时 ({timeout}秒)") from e
    except requests.ConnectionError as e:
        logger.error(f"连接错误: {str(e)}")
        raise NetworkError(f"连接错误: {str(e)}") from e
    except requests.RequestException as e:
        logger.error(f"请求错误: {str(e)}")
        raise NetworkError(f"请求错误: {str(e)}") from e