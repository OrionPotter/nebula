import pytest
import json
from unittest.mock import patch, Mock

# 测试实时行情模块
class TestRealtimeQuote:
    def test_get_stock_realtime_quote_success(self):
        """测试成功获取实时行情"""
        from nebula.core.realtime_quote import get_stock_realtime_quote
        
        # 使用mock避免实际网络请求
        with patch('nebula.core.realtime_quote.make_request') as mock_request:
            # 模拟API响应
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "f43": 5.5,  # 最新价
                    "f19": 5.6,  # 买一价
                    "f20": 1000, # 买一量
                    "f39": 5.4,  # 卖一价
                    "f40": 1000, # 卖一量
                }
            }
            mock_request.return_value = mock_response
            
            result = get_stock_realtime_quote("600028")
            
            # 验证返回的是JSON字符串
            assert isinstance(result, str)
            data = json.loads(result)
            assert len(data) > 0
            
    def test_get_stock_realtime_quote_error(self):
        """测试获取实时行情失败"""
        from nebula.core.realtime_quote import get_stock_realtime_quote
        from nebula.utils.errors import NetworkError
        
        # 模拟网络错误，同时禁用缓存以确保触发网络请求
        with patch('nebula.core.realtime_quote.make_request', 
                  side_effect=NetworkError("网络错误")):
            result = get_stock_realtime_quote("600028", use_cache=False)
            
            # 验证返回错误信息
            assert '"error"' in result

# 测试配置模块
class TestConfig:
    def test_config_defaults(self):
        """测试配置默认值"""
        from nebula.utils.config import config
        
        # 验证默认配置
        assert config.REDIS_HOST == 'localhost'
        assert config.REDIS_PORT == 6379
        assert config.REDIS_DB == 0
        assert config.REDIS_DEFAULT_TTL == 300
        
    def test_config_methods(self):
        """测试配置方法"""
        from nebula.utils.config import config
        
        # 验证配置方法
        redis_config = config.get_redis_config()
        assert 'host' in redis_config
        assert 'port' in redis_config
        assert 'db' in redis_config
        
        db_config = config.get_database_config()
        assert 'path' in db_config
        
        api_config = config.get_api_config()
        assert 'timeout' in api_config
        assert 'retries' in api_config

# 测试错误处理模块
class TestErrors:
    def test_retry_decorator(self):
        """测试重试装饰器"""
        from nebula.utils.errors import retry_on_failure
        
        # 简单测试装饰器是否能正常导入和应用
        @retry_on_failure(max_retries=1, delay=0.01)
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"

if __name__ == '__main__':
    pytest.main([__file__, "-v"])