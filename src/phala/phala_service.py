from src.phala.phala_model import PhalaModel
from src.phala.phala_schemas import PhalaChatMessage
from src.shared.http import AsyncSingleton


class PhalaService(AsyncSingleton):
    """Global singleton"""

    async def get_completions(
        self,
        messages: list[PhalaChatMessage],
    ) -> str:
        model = await PhalaModel.get_instance()

        response = await model.get_completions(messages)

        choices = response.get("choices", [])
        assert len(choices) > 0, "Phala choices response is empty"  # type: ignore

        response = choices[0]
        response_msg = response.get("message", {})
        response_content = response_msg.get("content", None)

        assert response_content is not None, "Phala response content is empty"

        return response_content
