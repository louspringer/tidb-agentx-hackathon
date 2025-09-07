#!/usr/bin/env python3
"""
Redis Foundation Demo

This script demonstrates the basic functionality of the Redis Foundation
module including connection management, message publishing, and health monitoring.

Requirements:
- Redis server running on localhost:6379 (or configure REDIS_URL)
- redis-py package installed

Usage:
    python examples/redis_foundation_demo.py
"""

import asyncio
import logging
import os
from typing import Optional

from src.beast_mode_network.redis_foundation import (
    RedisConnectionManager,
    ConnectionConfig,
    verify_redis_connectivity,
    create_redis_manager,
)
from src.beast_mode_network.message_models import (
    create_simple_message,
    MessageSerializer,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_basic_connection():
    """Demonstrate basic Redis connection and health checking."""
    logger.info("=== Basic Connection Demo ===")
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # First, verify connectivity
    logger.info(f"Verifying Redis connectivity to {redis_url}...")
    is_available = await verify_redis_connectivity(redis_url)
    
    if not is_available:
        logger.error("Redis is not available. Please start Redis server.")
        return False
    
    logger.info("✓ Redis is available!")
    
    # Create connection manager with custom config
    config = ConnectionConfig(
        redis_url=redis_url,
        max_retries=3,
        retry_delay=1.0,
        health_check_interval=10.0
    )
    
    manager = RedisConnectionManager(config)
    
    try:
        # Connect to Redis
        logger.info("Connecting to Redis...")
        success = await manager.connect()
        
        if success:
            logger.info("✓ Connected successfully!")
            logger.info(f"Connection status: {manager.status}")
            
            # Perform health check
            is_healthy = await manager.is_healthy()
            logger.info(f"Health check result: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
            
        else:
            logger.error("✗ Failed to connect to Redis")
            return False
            
    finally:
        await manager.disconnect()
        logger.info("Disconnected from Redis")
    
    return True


async def demo_message_publishing():
    """Demonstrate message publishing with BeastModeMessage."""
    logger.info("=== Message Publishing Demo ===")
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    try:
        async with create_redis_manager(redis_url) as manager:
            logger.info("Connected to Redis for message publishing")
            
            # Create some test messages
            messages = [
                create_simple_message("demo_agent", "Hello, Beast Mode Network!", target="all_agents"),
                create_simple_message("demo_agent", "This is a broadcast message"),
                create_simple_message("demo_agent", "Testing message serialization", target="test_agent"),
            ]
            
            # Publish messages
            channel = "beast_mode_network"
            for i, message in enumerate(messages, 1):
                serialized = MessageSerializer.serialize(message)
                
                logger.info(f"Publishing message {i}: {message.payload.get('message', 'N/A')}")
                logger.info(f"  Source: {message.source}")
                logger.info(f"  Target: {message.target or 'broadcast'}")
                logger.info(f"  Message ID: {message.id}")
                
                success = await manager.publish(channel, serialized)
                if success:
                    logger.info(f"  ✓ Message {i} published successfully")
                else:
                    logger.error(f"  ✗ Failed to publish message {i}")
                
                # Small delay between messages
                await asyncio.sleep(0.5)
            
            logger.info(f"Published {len(messages)} messages to channel '{channel}'")
            
    except Exception as e:
        logger.error(f"Error during message publishing demo: {e}")
        return False
    
    return True


async def demo_message_subscription():
    """Demonstrate message subscription and handling."""
    logger.info("=== Message Subscription Demo ===")
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    received_messages = []
    
    async def message_handler(channel: str, message_data: str):
        """Handle incoming messages."""
        try:
            message = MessageSerializer.deserialize(message_data)
            received_messages.append(message)
            
            logger.info(f"Received message on channel '{channel}':")
            logger.info(f"  From: {message.source}")
            logger.info(f"  To: {message.target or 'broadcast'}")
            logger.info(f"  Content: {message.payload.get('message', 'N/A')}")
            logger.info(f"  Timestamp: {message.timestamp}")
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    try:
        manager = await create_redis_manager(redis_url)
        
        # Subscribe to channel
        channel = "beast_mode_demo"
        logger.info(f"Subscribing to channel '{channel}'...")
        
        success = await manager.subscribe_to_channel(channel, message_handler)
        if not success:
            logger.error("Failed to subscribe to channel")
            return False
        
        logger.info("✓ Subscribed successfully!")
        
        # Publish some test messages to the same channel
        logger.info("Publishing test messages...")
        test_messages = [
            create_simple_message("publisher_agent", "Test message 1"),
            create_simple_message("publisher_agent", "Test message 2", target="subscriber"),
            create_simple_message("publisher_agent", "Final test message"),
        ]
        
        for message in test_messages:
            serialized = MessageSerializer.serialize(message)
            await manager.publish(channel, serialized)
            await asyncio.sleep(0.2)  # Small delay
        
        # Wait a bit for messages to be processed
        logger.info("Waiting for messages to be processed...")
        await asyncio.sleep(2)
        
        logger.info(f"Received {len(received_messages)} messages total")
        
        await manager.disconnect()
        
    except Exception as e:
        logger.error(f"Error during subscription demo: {e}")
        return False
    
    return True


async def demo_error_handling():
    """Demonstrate error handling and reconnection."""
    logger.info("=== Error Handling Demo ===")
    
    # Try to connect to a non-existent Redis server
    bad_url = "redis://nonexistent:6379"
    
    config = ConnectionConfig(
        redis_url=bad_url,
        max_retries=2,
        retry_delay=0.5
    )
    
    manager = RedisConnectionManager(config)
    
    logger.info(f"Attempting to connect to non-existent Redis at {bad_url}...")
    success = await manager.connect()
    
    if success:
        logger.error("Unexpected success - this should have failed!")
        return False
    else:
        logger.info("✓ Connection failed as expected")
        logger.info(f"Final status: {manager.status}")
    
    # Test connectivity verification with bad URL
    logger.info("Testing connectivity verification with bad URL...")
    is_available = await verify_redis_connectivity(bad_url)
    logger.info(f"Connectivity check result: {'Available' if is_available else '✗ Not available'}")
    
    return True


async def main():
    """Run all demos."""
    logger.info("Starting Redis Foundation Demo")
    logger.info("=" * 50)
    
    demos = [
        ("Basic Connection", demo_basic_connection),
        ("Message Publishing", demo_message_publishing),
        ("Message Subscription", demo_message_subscription),
        ("Error Handling", demo_error_handling),
    ]
    
    results = []
    
    for name, demo_func in demos:
        logger.info(f"\nRunning {name} demo...")
        try:
            result = await demo_func()
            results.append((name, result))
            if result:
                logger.info(f"✓ {name} demo completed successfully")
            else:
                logger.error(f"✗ {name} demo failed")
        except Exception as e:
            logger.error(f"✗ {name} demo crashed: {e}")
            results.append((name, False))
        
        logger.info("-" * 30)
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("DEMO SUMMARY")
    logger.info("=" * 50)
    
    successful = 0
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{name}: {status}")
        if result:
            successful += 1
    
    logger.info(f"\nOverall: {successful}/{len(results)} demos passed")
    
    if successful == len(results):
        logger.info("🎉 All demos completed successfully!")
    else:
        logger.warning("⚠️  Some demos failed. Check Redis server availability.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")