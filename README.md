## Loyal Permissionless LLM Inquiry Backend

### Description
- `grpc` folder contains protobuff autogen.
- `src` contains the main code for the backend.
- `.env.example` contains required .env variables, the rest are fetched through 1Password Connect Server

### Running
- Running the service:
```
uv run main.py
```
- Using betterproto2 to generate files:
```bash
protoc -I . --python_betterproto2_out=grpc src/query/query_schemas.proto --python_betterproto2_opt=client_generation=async --python_betterproto2_opt=server_generation=async
```

