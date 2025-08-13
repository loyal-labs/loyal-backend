from enum import Enum

from pydantic import BaseModel

from grpc.query import DialogEntry, QueryRequest, QueryResponse


class Role(Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class DialogEntrySchema(BaseModel):
    role: Role | None = None
    content: str
    date: int

    @classmethod
    def from_grpc(cls, message: DialogEntry) -> "DialogEntrySchema":
        return cls(
            role=Role(message.role.type) if message.role else None,
            content=message.content,
            date=message.date,
        )


class QueryRequestSchema(BaseModel):
    dialog: list[DialogEntrySchema]
    query: str

    @classmethod
    def from_grpc(cls, message: QueryRequest) -> "QueryRequestSchema":
        return cls(
            dialog=[DialogEntrySchema.from_grpc(entry) for entry in message.dialog],
            query=message.query,
        )


class QueryResponseSchema(BaseModel):
    response: str

    @classmethod
    def from_grpc(cls, message: QueryResponse) -> "QueryResponseSchema":
        return cls(response=message.response)
