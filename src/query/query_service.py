from grpc.query import QueryRequest, QueryResponse, QueryServiceBase
from src.phala.phala_schemas import PhalaChatMessage
from src.phala.phala_service import PhalaService


class QueryService(QueryServiceBase):
    async def query(self, message: QueryRequest) -> QueryResponse:
        assert message.query is not None, "Query is required"
        assert len(message.query) > 0 and len(message.query) < 1000, (
            "Query must be between 1 and 1000 characters"
        )

        phala_service = await PhalaService.get_instance()

        response = await phala_service.get_completions(
            messages=[PhalaChatMessage(role="user", content=message.query)]
        )

        return QueryResponse(response=response)
