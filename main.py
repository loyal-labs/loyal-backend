import asyncio
import logging

import uvloop
from dotenv import load_dotenv
from grpclib._typing import IServable
from grpclib.server import Server

from src.query.query_service import QueryService
from src.shared.logging_utils import configure_logging
from src.shared.secrets import SecretsFactory

load_dotenv()

logger = logging.getLogger("loyal-web-backend.main")


async def start_server():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    configure_logging()
    logger.debug("Logger configured")

    secrets = await SecretsFactory.get_instance()
    logger.debug("Secrets Manager created")
    assert secrets.grpc_host is not None, "GRPC_HOST is required"
    assert secrets.grpc_port is not None, "GRPC_PORT is required"

    services: list[IServable] = [QueryService()]
    server = Server(services)
    logger.debug("Server created")

    host = secrets.grpc_host
    port = int(secrets.grpc_port)

    logger.info("Starting server on %s:%s", host, port)
    await server.start(host, port)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(start_server())
