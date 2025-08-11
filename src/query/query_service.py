from collections.abc import AsyncIterator

from grpc.query import (
    QueryRequest,
    QueryResponse,
    QueryServiceBase,
    QueryStreamResponse,
)


class QueryService(QueryServiceBase):
    async def query(self, message: QueryRequest) -> QueryResponse:
        return QueryResponse(response="Hello, world!")

    async def query_stream(
        self, message: QueryRequest
    ) -> AsyncIterator[QueryStreamResponse]:
        yield QueryStreamResponse(response="Hello, world!")
