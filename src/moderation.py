from src.constants import (
    SERVER_TO_MODERATION_CHANNEL,
)
from typing import Optional, Tuple
import discord
from src.utils import logger

# Simple local content filter (no API costs)
BLOCKED_KEYWORDS = {
    # Extremely severe content only
    "bomb", "kill yourself", "terrorism", "rape", "child porn", "bestiality", "gore", "illegal weapons", "transphobia", "incest", "suicide", "extremist content", "terrorist recruitment"
}

FLAGGED_KEYWORDS = {
    # Potentially concerning but not blocked
    "hate", "abuse", "spam",
}


def moderate_message(
    message: str, user: str
) -> Tuple[str, str]:  # [flagged_str, blocked_str]
    """
    Local moderation using keyword filtering.
    Returns (flagged_str, blocked_str) - both empty if content is OK.
    """
    message_lower = message.lower()
    blocked_str = ""
    flagged_str = ""
    
    # Check blocked keywords
    for keyword in BLOCKED_KEYWORDS:
        if keyword in message_lower:
            blocked_str = f"(blocked_keyword: {keyword})"
            logger.info(f"blocked {user} - keyword: {keyword}")
            break
    
    # Check flagged keywords (only if not already blocked)
    if not blocked_str:
        for keyword in FLAGGED_KEYWORDS:
            if keyword in message_lower:
                flagged_str = f"(flagged_keyword: {keyword})"
                logger.info(f"flagged {user} - keyword: {keyword}")
                # Don't break - could have multiple flags
    
    return (flagged_str, blocked_str)


async def fetch_moderation_channel(
    guild: Optional[discord.Guild],
) -> Optional[discord.abc.GuildChannel]:
    if not guild or not guild.id:
        return None
    moderation_channel = SERVER_TO_MODERATION_CHANNEL.get(guild.id, None)
    if moderation_channel:
        channel = await guild.fetch_channel(moderation_channel)
        return channel
    return None


async def send_moderation_flagged_message(
    guild: Optional[discord.Guild],
    user: str,
    flagged_str: Optional[str],
    message: Optional[str],
    url: Optional[str],
):
    if guild and flagged_str and len(flagged_str) > 0:
        moderation_channel = await fetch_moderation_channel(guild=guild)
        if moderation_channel:
            message = message[:100] if message else None
            await moderation_channel.send(
                f"⚠️ {user} - {flagged_str} - {message} - {url}"
            )


async def send_moderation_blocked_message(
    guild: Optional[discord.Guild],
    user: str,
    blocked_str: Optional[str],
    message: Optional[str],
):
    if guild and blocked_str and len(blocked_str) > 0:
        moderation_channel = await fetch_moderation_channel(guild=guild)
        if moderation_channel:
            message = message[:500] if message else None
            await moderation_channel.send(f"❌ {user} - {blocked_str} - {message}")
