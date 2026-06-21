"""
Interaction Tracker - Wrapper for logging command responses
"""
import discord
from functools import wraps

# Global reference to activity logger (will be set by app.py)
_activity_logger = None

def set_activity_logger(logger):
    """Set the global activity logger instance."""
    global _activity_logger
    _activity_logger = logger


def track_response(interaction: discord.Interaction, response_content: str, animation_shown: bool = False):
    """Track a command response in the activity logger."""
    global _activity_logger
    if _activity_logger:
        _activity_logger.log_command_response(interaction, response_content, animation_shown)


def track_interaction_response(original_method):
    """
    Decorator to automatically track interaction responses.
    Wraps interaction.response.send_message and interaction.followup.send
    """
    @wraps(original_method)
    async def wrapper(self, *args, **kwargs):
        result = await original_method(self, *args, **kwargs)
        
        # Try to extract response content
        response_content = ""
        if args:
            if isinstance(args[0], str):
                response_content = args[0]
            elif isinstance(args[0], discord.Embed):
                response_content = args[0].description or args[0].title or "Embed"
        
        # Log the response
        if hasattr(self, '_parent') and isinstance(self._parent, discord.Interaction):
            track_response(self._parent, response_content)
        
        return result
    
    return wrapper
