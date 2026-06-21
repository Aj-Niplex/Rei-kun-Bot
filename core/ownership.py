"""
🔒 HARDCODED OWNERSHIP SYSTEM
This file is CRITICAL - do not modify unless you know what you're doing.

FOUNDER rights are LOCKED to the original creator.
Even if someone downloads this bot from GitHub, the FOUNDER role stays with the ID below.
"""

# ═══════════════════════════════════════════════════════════════════
# 🏛️ FOUNDER (LOCKED - DO NOT CHANGE)
# This Discord user ID has PERMANENT, IRREVOCABLE founder rights.
# Even bot admins/owners cannot override this.
# ═══════════════════════════════════════════════════════════════════
FOUNDER_ID = 1489553674287054848  # @dora_aj - Original creator
FOUNDER_EMAIL = "aj.jin.japan.2006@gmail.com"  # Error reports go here

# ═══════════════════════════════════════════════════════════════════
# 📧 SYSTEM EMAIL (LOCKED)
# This email receives ALL error reports, regardless of .env settings.
# Hardcoded to prevent others from hijacking error notifications.
# ═══════════════════════════════════════════════════════════════════
SYSTEM_ERROR_EMAIL = "aj.jin.japan.2006@gmail.com"

# ═══════════════════════════════════════════════════════════════════
# 🎭 PERMISSION LEVELS
# ═══════════════════════════════════════════════════════════════════
class PermissionLevel:
    """Permission hierarchy for bot users"""
    
    FOUNDER = 100    # Original creator (LOCKED above)
    OWNER = 50       # Bot owners (can manage bot settings, NOT personality)
    ADMIN = 25       # Server admins (can use admin commands)
    MODERATOR = 10   # Moderators (limited admin access)
    USER = 0         # Regular users


def get_permission_level(user_id: int, owner_ids: list = None, admin_ids: list = None) -> int:
    """
    Get permission level for a Discord user.
    
    Args:
        user_id: Discord user ID
        owner_ids: List of owner IDs from .env (BOT_OWNER_USER_IDS)
        admin_ids: List of admin IDs from .env (BOT_ADMIN_USER_IDS)
    
    Returns:
        Permission level (0-100)
    """
    # FOUNDER check (hardcoded, can't be overridden)
    if user_id == FOUNDER_ID:
        return PermissionLevel.FOUNDER
    
    # OWNER check (from .env)
    if owner_ids and user_id in owner_ids:
        return PermissionLevel.OWNER
    
    # ADMIN check (from .env)
    if admin_ids and user_id in admin_ids:
        return PermissionLevel.ADMIN
    
    return PermissionLevel.USER


def is_founder(user_id: int) -> bool:
    """Check if user is the bot founder (hardcoded)"""
    return user_id == FOUNDER_ID


def is_owner_or_above(user_id: int, owner_ids: list = None) -> bool:
    """Check if user is owner or founder"""
    return get_permission_level(user_id, owner_ids) >= PermissionLevel.OWNER


def is_admin_or_above(user_id: int, owner_ids: list = None, admin_ids: list = None) -> bool:
    """Check if user is admin, owner, or founder"""
    return get_permission_level(user_id, owner_ids, admin_ids) >= PermissionLevel.ADMIN


def get_role_name(user_id: int, owner_ids: list = None, admin_ids: list = None) -> str:
    """Get human-readable role name"""
    level = get_permission_level(user_id, owner_ids, admin_ids)
    
    if level == PermissionLevel.FOUNDER:
        return "🏛️ Founder"
    elif level == PermissionLevel.OWNER:
        return "👑 Owner"
    elif level == PermissionLevel.ADMIN:
        return "🛡️ Admin"
    elif level == PermissionLevel.MODERATOR:
        return "⚔️ Moderator"
    else:
        return "👤 User"
 
