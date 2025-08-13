import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, ClassVar, TypeVar, cast

import aiohttp
from aiohttp import ClientTimeout
from aiohttp.client_exceptions import ContentTypeError

from src.shared.exceptions import HTTPError

logger = logging.getLogger("loyal-web-backend.shared.http")

T = TypeVar("T", bound="AsyncSingleton")


class AsyncSingleton:
    _instances: ClassVar[dict[type, Any]] = {}
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    @classmethod
    async def get(cls: type[T]) -> T:
        if cls not in AsyncSingleton._instances:
            async with AsyncSingleton._lock:
                if cls not in AsyncSingleton._instances:
                    AsyncSingleton._instances[cls] = await cls.get_instance()
        return cast(T, AsyncSingleton._instances[cls])

    @classmethod
    def reset(cls: type[T]) -> None:
        if cls in AsyncSingleton._instances:
            del AsyncSingleton._instances[cls]

    @classmethod
    async def get_instance(cls: type[T]) -> T:
        """This method should be implemented by subclasses."""
        self = cls()
        return self


class AsyncHttpClient:
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[aiohttp.ClientSession, None]:
        async with aiohttp.ClientSession() as session:
            yield session

    async def request(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        method: str = "GET",
    ) -> dict[str, Any] | str:
        async with self.session() as session:
            async with session.request(
                method,
                url,
                headers=headers,
                params=params,
                json=data,
                timeout=ClientTimeout(total=20),
            ) as response:
                try:
                    return await response.json()
                except ContentTypeError:
                    return await response.text()
                except aiohttp.ClientError as e:
                    raise HTTPError(response.status, await response.text()) from e
                except Exception as e:
                    raise HTTPError(response.status, await response.text()) from e
