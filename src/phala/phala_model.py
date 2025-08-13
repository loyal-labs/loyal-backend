import logging
from typing import Any, override

from src.phala.phala_constants import COMPLETIONS_ENDPOINT, SELECTED_MODEL
from src.phala.phala_schemas import PhalaChatMessage, PhalaEnvFields
from src.shared.http import AsyncHttpClient, AsyncSingleton
from src.shared.secrets import OnePasswordManager, SecretsFactory

logger = logging.getLogger("loyal-web-backend.phala.phala_model")


class PhalaModel(AsyncSingleton):
    default_item_name = "PHALA_SERVERLESS_TEE"

    def __init__(self):
        self.http_client = AsyncHttpClient()

        # From 1Password
        self.api_key: str | None = None
        self.host: str | None = None

    @override
    @classmethod
    async def get_instance(cls) -> "PhalaModel":
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
    ) -> dict[str, Any]:
        """
        Get completions from the Phala Serverless TEE.
        """
        assert self.host is not None, "Host is not set"
        assert self.api_key is not None, "API key is not set"

        url = f"{self.host}/{COMPLETIONS_ENDPOINT}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": SELECTED_MODEL,
            "messages": [message.model_dump() for message in messages],
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
