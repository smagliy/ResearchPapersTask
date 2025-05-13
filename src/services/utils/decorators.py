from functools import wraps
from aiohttp import ClientSession
from typing import Callable, Awaitable

from src.services.logger.logging import LoggerConfig

logger = LoggerConfig.set_up_logger()


def handle_response(func: Callable[[ClientSession, str, bytes], Awaitable[None]]):
    @wraps(func)
    async def wrapper(self, bucket_name: str, session: ClientSession, url: str, *args, **kwargs):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.read()
                return await func(self, bucket_name, url, content, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error downloading or uploading {url}: {e}")
            return None
    return wrapper
