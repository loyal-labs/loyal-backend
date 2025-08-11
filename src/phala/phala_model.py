import asyncio
import logging

from src.phala.phala_schemas import PhalaEnvFields
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
