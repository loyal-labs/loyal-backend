import asyncio
import logging
from typing import Any

from src.phala.phala_constants import (
    COMPLETIONS_ENDPOINT,
    PHALA_BASE_URL,
    SELECTED_MODEL,
)
from src.phala.phala_schemas import PhalaChatMessage, PhalaEnvFields
from src.shared.http import AsyncHttpClient
from src.shared.secrets import OnePasswordManager, SecretsFactory

logger = logging.getLogger("loyal-web-backend.phala.phala_model")


class PhalaModel:
    default_item_name = "PHALA_SERVERLESS_TEE"

    def __init__(self):
        self.http_client = AsyncHttpClient()

        # From 1Password
        self.api_key: str | None = None
        self.host: str | None = None

    @classmethod
    async def create(cls) -> "PhalaModel":
        logger.debug("Creating PhalaModel")
        secrets_manager = await SecretsFactory.get_instance()
        self = cls()

        await self.__init_class(secrets_manager)
        logger.info("PhalaModel initialized")
        return self

    async def __init_class(self, secrets_manager: OnePasswordManager) -> None:
        assert secrets_manager is not None, "Secrets manager is not set"
        assert isinstance(secrets_manager, OnePasswordManager), (
            "Secrets manager is not an instance of OnePasswordManager"
        )

        fetched_secrets = await secrets_manager.get_secret_item(self.default_item_name)

        self.api_key = fetched_secrets.get(PhalaEnvFields.API_KEY.value)
        self.host = fetched_secrets.get(PhalaEnvFields.HOST.value)

    async def get_completions(
        self,
        messages: list[PhalaChatMessage],
        max_tokens: int = 1024,
        stream: bool = False,
    ) -> dict[str, Any]:
        """
        Get completions from the Phala Serverless TEE.
        """
        url = f"{PHALA_BASE_URL}/{COMPLETIONS_ENDPOINT}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": SELECTED_MODEL,
            "messages": [message.model_dump() for message in messages],
            "max_tokens": max_tokens,
            "stream": stream,
        }

        try:
            response = await self.http_client.request(
                url=url,
                headers=headers,
                data=data,
                method="POST",
            )
        except Exception as e:
            logger.error("Error getting completions: %s", e)
            raise e

        assert isinstance(response, dict), (
            "Phala completion response is not a dictionary"
        )
        return response


class PhalaFactory:
    """Global singleton factory for PhalaModel."""

    _instance: PhalaModel | None = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls) -> PhalaModel:
        """Get or create singleton instance of PhalaModel."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    logger.info("Creating PhalaModel singleton")
                    cls._instance = await PhalaModel.create()
                    logger.info("PhalaModel singleton created")
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
