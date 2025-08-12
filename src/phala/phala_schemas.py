from enum import Enum

from pydantic import BaseModel


class PhalaEnvFields(Enum):
    """
    Fields for the Phala Serverless TEE.
    """

    API_KEY = "credential"
    HOST = "hostname"


class PhalaChatMessage(BaseModel):
    role: str
    content: str
