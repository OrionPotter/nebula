import pytest
import os
import tempfile
from unittest.mock import patch, Mock

# 测试缓存模块
class TestCache:
    def test_cache_manager_init(self):
        """测试缓存管理器初始化"""
        from nebula.utils.cache import CacheManager
        
        # 测试默认初始化
        cache = CacheManager()
        assert cache.default_ttl == 300
        
    def test_cache_manager_memory_cache(self):
        """测试内存缓存功能"""
        from nebula.utils.cache import CacheManager
        
        # 创建不依赖Redis的缓存管理器
        cache = CacheManager()
        cache.redis_client = None  # 强制使用内存缓存
        
        # 测试设置和获取缓存
        test_data = {"key": "value", "number": 123}
        assert cache.set("test_key", test_data) == True
        assert cache.get("test_key") == test_data
        
        # 测试删除缓存
        assert cache.delete("test_key") == True
        assert cache.get("test_key") is None
        
        # 测试缓存存在检查
        cache.set("test_key2", "test_value")
        assert cache.exists("test_key2") == True
        assert cache.exists("nonexistent_key") == False

# 测试数据库模块
class TestDatabase:
    def test_database_manager_init(self):
        """测试数据库管理器初始化"""
        from nebula.utils.database import DatabaseManager
        
        # 简单测试初始化
        db = DatabaseManager(":memory:")  # 使用内存数据库避免文件权限问题
            
        # 测试初始化
        assert db.db_path == ":memory:"
            
        # 测试数据库连接
        conn = db.get_connection()
        assert conn is not None
        conn.close()

if __name__ == '__main__':
    pytest.main([__file__, "-v"])