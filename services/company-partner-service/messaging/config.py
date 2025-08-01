"""
Configuration for M-ERP messaging system.
"""
import os
from typing import Dict, List


class MessagingConfig:
    """Configuration for Redis messaging."""
    
    # Redis connection
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # Connection settings
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))
    REDIS_CONNECTION_TIMEOUT: int = int(os.getenv("REDIS_CONNECTION_TIMEOUT", "5"))
    REDIS_SOCKET_TIMEOUT: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
    
    # Stream settings
    STREAM_MAX_LENGTH: int = int(os.getenv("STREAM_MAX_LENGTH", "10000"))
    STREAM_BLOCK_TIME: int = int(os.getenv("STREAM_BLOCK_TIME", "1000"))  # milliseconds
    CONSUMER_GROUP_SUFFIX: str = os.getenv("CONSUMER_GROUP_SUFFIX", "workers")
    
    # Message settings
    MESSAGE_TTL: int = int(os.getenv("MESSAGE_TTL", "86400"))  # 24 hours in seconds
    MAX_RETRIES: int = int(os.getenv("MESSAGE_MAX_RETRIES", "3"))
    RETRY_DELAY: int = int(os.getenv("MESSAGE_RETRY_DELAY", "60"))  # seconds
    
    # Service settings
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "unknown-service")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @classmethod
    def get_redis_url(cls) -> str:
        """Get Redis connection URL."""
        if cls.REDIS_PASSWORD:
            return f"redis://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
    
    @classmethod
    def get_stream_names(cls) -> Dict[str, str]:
        """Get Redis stream names for different message types."""
        env_prefix = f"{cls.ENVIRONMENT}:" if cls.ENVIRONMENT != "development" else ""
        return {
            "events": f"{env_prefix}events",
            "commands": f"{env_prefix}commands", 
            "notifications": f"{env_prefix}notifications",
            "health": f"{env_prefix}health"
        }
    
    @classmethod
    def get_pubsub_channels(cls) -> Dict[str, str]:
        """Get Redis pub/sub channel names."""
        env_prefix = f"{cls.ENVIRONMENT}:" if cls.ENVIRONMENT != "development" else ""
        return {
            "notifications": f"{env_prefix}notifications:*",
            "system_alerts": f"{env_prefix}system:alerts",
            "user_activity": f"{env_prefix}user:activity:*"
        }
    
    @classmethod
    def get_consumer_group_name(cls, service_name: str) -> str:
        """Get consumer group name for a service."""
        return f"{service_name}-{cls.CONSUMER_GROUP_SUFFIX}"