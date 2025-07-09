# -*- coding:utf-8 -*-
import json
import redis
from typing import Optional, Any
from datetime import timedelta
from .config import config
from .logger import logger

class CacheManager:
    """缓存管理器，使用Redis作为缓存后端，支持Upstash Redis"""
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, db: Optional[int] = None, 
                 password: Optional[str] = None, default_ttl: Optional[int] = None, url: Optional[str] = None):
        """
        初始化缓存管理器
        
        Args:
            host: Redis服务器地址
            port: Redis服务器端口
            db: Redis数据库编号
            password: Redis密码（如果需要）
            default_ttl: 默认过期时间（秒）
            url: Redis连接URL（优先使用）
        """
        # 使用配置文件中的默认值或传入的参数
        redis_config = config.get_redis_config()
        self.url = url or redis_config['url']
        self.host = host or redis_config['host']
        self.port = port or redis_config['port']
        self.db = db or redis_config['db']
        self.password = password or redis_config['password']
        self.default_ttl = default_ttl or redis_config['default_ttl']
        
        try:
            # 优先使用URL连接（支持Upstash Redis）
            if self.url and self.url != 'redis://localhost:6379/0':
                self.redis_client = redis.from_url(self.url, decode_responses=True)
            else:
                self.redis_client = redis.Redis(
                    host=self.host, 
                    port=self.port, 
                    db=self.db, 
                    password=self.password,
                    decode_responses=True
                )
            # 测试连接
            self.redis_client.ping()
            logger.info("成功连接到Redis服务器")
        except Exception as e:
            logger.warning(f"无法连接到Redis服务器: {e}，将使用内存字典作为后备缓存")
            self.redis_client = None
            self._local_cache = {}
    
    def _get_local_cache_key(self, key: str) -> str:
        """生成本地缓存的键"""
        return f"local_cache:{key}"
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值（可序列化对象）
            ttl: 过期时间（秒），默认使用default_ttl
            
        Returns:
            bool: 是否设置成功
        """
        try:
            # 序列化值
            serialized_value = json.dumps(value, ensure_ascii=False)
            expire_time = ttl if ttl is not None else self.default_ttl
            
            if self.redis_client:
                # 使用Redis缓存
                result = self.redis_client.setex(key, expire_time, serialized_value)
                logger.debug(f"缓存设置成功: {key}")
                return result
            else:
                # 使用本地缓存
                import time
                self._local_cache[self._get_local_cache_key(key)] = {
                    'value': serialized_value,
                    'expire_at': time.time() + expire_time
                }
                logger.debug(f"本地缓存设置成功: {key}")
                return True
        except Exception as e:
            logger.error(f"设置缓存时出错: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值或None（如果不存在或过期）
        """
        try:
            if self.redis_client:
                # 使用Redis缓存
                serialized_value = self.redis_client.get(key)
                if serialized_value is None:
                    logger.debug(f"缓存键不存在: {key}")
                    return None
                logger.debug(f"从Redis获取缓存成功: {key}")
                return json.loads(serialized_value)
            else:
                # 使用本地缓存
                import time
                cache_key = self._get_local_cache_key(key)
                if cache_key not in self._local_cache:
                    logger.debug(f"本地缓存键不存在: {key}")
                    return None
                
                cache_entry = self._local_cache[cache_key]
                if time.time() > cache_entry['expire_at']:
                    # 缓存过期，删除
                    del self._local_cache[cache_key]
                    logger.debug(f"本地缓存已过期并删除: {key}")
                    return None
                
                logger.debug(f"从本地缓存获取成功: {key}")
                return json.loads(cache_entry['value'])
        except Exception as e:
            logger.error(f"获取缓存时出错: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        try:
            if self.redis_client:
                # 使用Redis缓存
                result = self.redis_client.delete(key)
                logger.debug(f"从Redis删除缓存: {key}, 结果: {result > 0}")
                return result > 0
            else:
                # 使用本地缓存
                cache_key = self._get_local_cache_key(key)
                if cache_key in self._local_cache:
                    del self._local_cache[cache_key]
                    logger.debug(f"从本地缓存删除成功: {key}")
                    return True
                logger.debug(f"本地缓存键不存在: {key}")
                return False
        except Exception as e:
            logger.error(f"删除缓存时出错: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查缓存键是否存在且未过期
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在
        """
        try:
            if self.redis_client:
                # 使用Redis缓存
                exists = self.redis_client.exists(key) > 0
                logger.debug(f"Redis缓存键存在检查: {key}, 结果: {exists}")
                return exists
            else:
                # 使用本地缓存
                import time
                cache_key = self._get_local_cache_key(key)
                if cache_key not in self._local_cache:
                    logger.debug(f"本地缓存键不存在: {key}")
                    return False
                
                if time.time() > self._local_cache[cache_key]['expire_at']:
                    # 缓存过期，删除
                    del self._local_cache[cache_key]
                    logger.debug(f"本地缓存已过期并删除: {key}")
                    return False
                
                logger.debug(f"本地缓存键存在: {key}")
                return True
        except Exception as e:
            logger.error(f"检查缓存存在时出错: {e}")
            return False

# 全局缓存管理器实例
cache_manager = CacheManager()