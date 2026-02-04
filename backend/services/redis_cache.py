"""
Redis Cache Service for FAQ answers
Handles caching of FAQ Q&A pairs with TTL (Time To Live)
"""

import redis
import json
import logging
from typing import Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis caching service for FAQ answers"""
    
    def __init__(self, 
                 host: str = settings.REDIS_HOST,
                 port: int = settings.REDIS_PORT,
                 db: int = settings.REDIS_DB,
                 decode_responses: bool = True):
        """
        Initialize Redis cache client
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            decode_responses: Whether to decode responses as strings
        """
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Redis connected: {host}:{port}")
            self.connected = True
        except Exception as e:
            logger.warning(f"⚠️  Redis connection failed: {str(e)}")
            self.connected = False
            self.redis_client = None
    
    def _get_cache_key(self, question: str) -> str:
        """Generate cache key from question"""
        # Normalize question for consistent caching
        normalized = question.strip().lower()
        return f"faq:{normalized}"
    
    def get(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Get FAQ answer from cache
        
        Args:
            question: User's question
            
        Returns:
            Cached FAQ data or None if not found
        """
        if not self.connected or not self.redis_client:
            logger.debug("Redis not connected, skipping cache get")
            return None
        
        try:
            cache_key = self._get_cache_key(question)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"✅ Cache HIT for: {question[:50]}...")
                return json.loads(cached_data)
            else:
                logger.info(f"❌ Cache MISS for: {question[:50]}...")
                return None
                
        except Exception as e:
            logger.warning(f"Error retrieving from cache: {str(e)}")
            return None
    
    def set(self, question: str, answer_data: Dict[str, Any], ttl_minutes: int = 20) -> bool:
        """
        Cache FAQ answer with TTL
        
        Args:
            question: User's question
            answer_data: FAQ answer data to cache (should contain at least 'answer' key)
            ttl_minutes: Time to live in minutes (default: 20)
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.connected or not self.redis_client:
            logger.debug("Redis not connected, skipping cache set")
            return False
        
        try:
            cache_key = self._get_cache_key(question)
            ttl_seconds = ttl_minutes * 60
            
            # Store as JSON
            cached_json = json.dumps(answer_data)
            self.redis_client.setex(cache_key, ttl_seconds, cached_json)
            
            logger.info(f"✅ Cached answer for: {question[:50]}... (TTL: {ttl_minutes}min)")
            return True
            
        except Exception as e:
            logger.warning(f"Error caching to Redis: {str(e)}")
            return False
    
    def delete(self, question: str) -> bool:
        """
        Delete FAQ answer from cache
        
        Args:
            question: User's question
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.connected or not self.redis_client:
            return False
        
        try:
            cache_key = self._get_cache_key(question)
            result = self.redis_client.delete(cache_key)
            logger.info(f"Deleted cache for: {question[:50]}...")
            return result > 0
            
        except Exception as e:
            logger.warning(f"Error deleting from cache: {str(e)}")
            return False
    
    def clear_all(self) -> bool:
        """
        Clear all FAQ cache (use with caution)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.redis_client:
            return False
        
        try:
            # Clear only FAQ keys (pattern: faq:*)
            keys = self.redis_client.keys("faq:*")
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} FAQ cache entries")
            return True
            
        except Exception as e:
            logger.warning(f"Error clearing cache: {str(e)}")
            return False
    
    def get_cache_info(self) -> Optional[Dict[str, Any]]:
        """
        Get cache statistics
        
        Returns:
            Cache info or None if not connected
        """
        if not self.connected or not self.redis_client:
            return None
        
        try:
            info = self.redis_client.info()
            faq_keys = self.redis_client.keys("faq:*")
            
            return {
                "connected": True,
                "faq_cached_items": len(faq_keys),
                "redis_memory_used": info.get("used_memory_human", "N/A"),
                "redis_version": info.get("redis_version", "N/A"),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            logger.warning(f"Error getting cache info: {str(e)}")
            return None


# Global cache instance
redis_cache = None


def get_redis_cache() -> RedisCache:
    """Get or create Redis cache instance"""
    global redis_cache
    if redis_cache is None:
        redis_cache = RedisCache()
    return redis_cache
