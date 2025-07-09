import pytest

def test_imports():
    """测试所有模块导入"""
    # 测试核心模块导入
    from nebula.core import realtime_quote, history_quote, board_quote
    from nebula.core import hot_rank, indicators, stock_info
    
    # 测试工具模块导入
    from nebula.utils import cache, database, config, errors
    
    # 测试根包导入
    from nebula import get_stock_realtime_quote, get_stock_history_quote
    from nebula import get_stock_board_quote, get_stock_hot_rank
    from nebula import get_stock_indicators, get_stock_info

def test_cache_imports():
    """测试缓存模块导入"""
    from nebula.utils.cache import CacheManager, cache_manager
    assert CacheManager is not None
    assert cache_manager is not None

def test_database_imports():
    """测试数据库模块导入"""
    from nebula.utils.database import DatabaseManager, db_manager
    assert DatabaseManager is not None
    assert db_manager is not None

def test_config_imports():
    """测试配置模块导入"""
    from nebula.utils.config import Config, config
    assert Config is not None
    assert config is not None

def test_error_imports():
    """测试错误处理模块导入"""
    from nebula.utils.errors import (
        retry_on_failure, StockAnalyzerError, 
        NetworkError, DataParseError, APIError
    )
    assert retry_on_failure is not None
    assert StockAnalyzerError is not None
    assert NetworkError is not None
    assert DataParseError is not None
    assert APIError is not None

if __name__ == '__main__':
    pytest.main([__file__, "-v"])