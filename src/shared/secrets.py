import asyncio
import logging
import os
from typing import cast

from dotenv import load_dotenv
from onepasswordconnectsdk.client import AsyncClient, Item, new_client
from onepasswordconnectsdk.models.field import Field
from pydantic import BaseModel

logger = logging.getLogger("loyal-web-backend.shared.secrets")


class SecretsSchema(BaseModel):
    secrets: dict[str, str]

    def get(self, key: str) -> str:
        result = self.secrets.get(key)
        assert result is not None, f"Key {key} not found"
        return result


load_dotenv()


class OnePasswordManager:
    """
    Secrets manager. Currently supports only 1Password.
    """

    default_vault: str = "loyal-web-backend"
    secret_value = "ONEPASS_CONNECT_TOKEN"
    host_value = "ONEPASS_CONNECT_HOST"

    def __init__(self):
        self.client: AsyncClient | None = None
        self.host: str | None = None
        self.default_vault_uuid: str | None = None

        self.frontend_url: str | None = None

        self.grpc_host: str | None = None
        self.grpc_port: str | None = None

        self.deployment: str = "local"

    @classmethod
    async def create(cls):
        """
        Creates a new instance of the OnePasswordManager.

        Returns:
            OnePasswordManager: A new instance of the OnePasswordManager.
        """

        logger.info("Creating OnePasswordManager")
        service_token = os.getenv(cls.secret_value, "")
        host = os.getenv(cls.host_value, "")

        frontend_url = os.getenv("FRONTEND_URL")
        grpc_host = os.getenv("GRPC_HOST")
        grpc_port = os.getenv("GRPC_PORT")

        assert service_token is not None, f"{cls.secret_value} is not set"
        assert host is not None, f"{cls.host_value} is not set"
        logger.info("Fetched OnePassword service token")

        self = cls()
        self.deployment = os.getenv("GLOBAL_APP_ENV", "local")
        self.host = host

        if self.deployment == "local":
            self.frontend_url = "https://127.0.0.1:3000/"
            self.grpc_host = "127.0.0.1"
            self.grpc_port = "50051"
        else:
            self.frontend_url = frontend_url
            self.grpc_host = grpc_host
            self.grpc_port = grpc_port

            assert self.frontend_url is not None, "FRONTEND_URL is required"
            assert self.grpc_host is not None, "GRPC_HOST is required"
            assert self.grpc_port is not None, "GRPC_PORT is required"

        await self.__init_client(service_token)
        logger.info("OnePasswordManager initialized")
        return self

    # --- Private Methods ---
    async def __init_client(
        self,
        service_token: str,
    ) -> AsyncClient:
        assert service_token is not None, "OP_SERVICE_ACCOUNT_TOKEN is not set"
        assert self.host is not None, "ONEPASS_CONNECT_HOST is not set"

        try:
            client = new_client(self.host, service_token, is_async=True)
            vault_info = await client.get_vault_by_title(self.default_vault)  # type: ignore
            assert vault_info is not None, "Vault not found"
            vault_uuid = vault_info.id  # type: ignore
            self.default_vault_uuid = vault_uuid
        except Exception as e:
            logger.exception("Error initializing client")
            raise e

        logger.debug("Client initialized")
        self.client = cast(AsyncClient, client)
        return self.client

    async def get_secret_file(self, item_name: str, file_id: str) -> str:
        assert self.client is not None, "Client is not initialized"
        assert self.default_vault_uuid is not None, "Vault UUID is not set"
        assert item_name is not None, "Item name is not set"
        assert file_id is not None, "File ID is not set"

        item = await self.client.get_item_by_title(item_name, self.default_vault_uuid)
        assert item is not None, "Item is not set"
        assert isinstance(item, Item), "Item is not an Item"
        item_id = cast(str, item.id)  # type: ignore

        files = await self.client.get_file_content(
            file_id, item_id, self.default_vault_uuid
        )
        files = files.decode("utf-8")  # type: ignore
        return files  # type: ignore

    async def get_secret_item(self, item_name: str) -> SecretsSchema:
        assert self.client is not None, "Client is not initialized"
        assert self.default_vault_uuid is not None, "Vault UUID is not set"
        assert item_name is not None, "Item name is not set"

        response_dict: SecretsSchema = SecretsSchema(secrets={})

        try:
            logger.debug("Getting secret for %s", item_name)
            item = await self.client.get_item_by_title(
                item_name, self.default_vault_uuid
            )
            assert item is not None, "Item is not set"
            assert isinstance(item, Item), "Item is not an Item"
            fields = cast(list[Field], item.fields)  # type: ignore
            assert fields is not None, "Item has no fields"

            for field in fields:
                try:
                    assert field.label is not None, "Field label is not set"  # type: ignore
                    assert field.value is not None, "Field value is not set"  # type: ignore
                except AssertionError:
                    continue
                except Exception as e:
                    logger.exception("Error getting secret %s", item_name)
                    raise e
                response_dict.secrets[field.label] = field.value  # type: ignore

        except Exception as e:
            logger.exception("Error getting secret")
            raise e

        return response_dict


class SecretsFactory:
    """Global singleton factory for Secrets."""

    _instance: OnePasswordManager | None = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls) -> OnePasswordManager:
        """Get or create singleton instance of OnePasswordManager."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    logger.info("Creating Database singleton")
                    cls._instance = await OnePasswordManager.create()
                    logger.info("Database singleton created")
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
