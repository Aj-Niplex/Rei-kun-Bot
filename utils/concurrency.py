"""
Concurrency management for AI requests
"""

import asyncio
import time
from typing import Dict, Optional
import aiohttp

# Semaphore to limit concurrent AI requests (max 5 at once)
AI_SEMAPHORE = asyncio.Semaphore(5)

# Global aiohttp session
_session: Optional[aiohttp.ClientSession] = None

# Active request tracking
_active_count = 0
_active_lock = asyncio.Lock()

# User cooldown tracking: {user_id: last_request_timestamp}
_user_cooldowns: Dict[int, float] = {}
_cooldown_seconds = 3  # 3 second cooldown per user


def get_session() -> aiohttp.ClientSession:
    """Get or create the global aiohttp session"""
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
    return _session


async def close_session():
    """Close the global aiohttp session"""
    global _session
    if _session and not _session.closed:
        await _session.close()
        _session = None


async def inc_active():
    """Increment active request counter"""
    global _active_count
    async with _active_lock:
        _active_count += 1


async def dec_active():
    """Decrement active request counter"""
    global _active_count
    async with _active_lock:
        _active_count = max(0, _active_count - 1)


def get_active_count() -> int:
    """Get current active request count"""
    return _active_count


def get_queue_size() -> int:
    """Get number of requests waiting in the semaphore queue"""
    # Calculate queue size based on semaphore's locked count
    if hasattr(AI_SEMAPHORE, '_waiters'):
        return len(AI_SEMAPHORE._waiters)
    return 0


def check_user_cooldown(user_id: int):
    """
    Check if a user is on cooldown.
    
    Args:
        user_id: Discord user ID
        
    Returns:
        None if not on cooldown, otherwise seconds remaining
    """
    now = time.time()
    
    if user_id in _user_cooldowns:
        elapsed = now - _user_cooldowns[user_id]
        remaining = _cooldown_seconds - elapsed
        
        if remaining > 0:
            return remaining
    
    # Update cooldown timestamp
    _user_cooldowns[user_id] = now
    
    # Clean up old cooldowns (older than 60 seconds)
    to_remove = [uid for uid, ts in _user_cooldowns.items() if now - ts > 60]
    for uid in to_remove:
        del _user_cooldowns[uid]
    
    return None


def set_cooldown_duration(seconds: int):
    """Set the cooldown duration in seconds"""
    global _cooldown_seconds
    _cooldown_seconds = max(0, seconds)


def get_cooldown_duration() -> int:
    """Get the current cooldown duration"""
    return _cooldown_seconds
