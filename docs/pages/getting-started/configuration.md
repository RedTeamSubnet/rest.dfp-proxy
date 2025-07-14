# ⚙️ Configuration

## 🌎 Environment Variables

[**`.env.example`**](https://github.com/RedTeam/rest.device-fp-gate/blob/main/.env.example):

```sh
## --- Environment variable --- ##
ENV=LOCAL
DEBUG=false
# TZ=UTC


## -- API configs -- ##
DFG_API_PORT=8000
# DFG_API_LOGS_DIR="/var/log/rest.device-fp-gate"
# DFG_API_DATA_DIR="/var/lib/rest.device-fp-gate"

# DFG_API_VERSION="1"
# DFG_API_PREFIX="/api/v{api_version}"
# DFG_API_DOCS_ENABLED=true
# DFG_API_DOCS_OPENAPI_URL="{api_prefix}/openapi.json"
# DFG_API_DOCS_DOCS_URL="{api_prefix}/docs"
# DFG_API_DOCS_REDOC_URL="{api_prefix}/redoc"
```

## 🔧 Command arguments

You can customize the command arguments to debug or run the service with different commands.

[**`compose.override.yml`**](https://github.com/RedTeam/rest.device-fp-gate/blob/main/templates/compose/compose.override.dev.yml):

```yml
    command: ["/bin/bash"]
    command: ["-b", "pwd && ls -al && /bin/bash"]
    command: ["-b", "python -u -m api"]
    command: ["-b", "uvicorn main:app --host=0.0.0.0 --port=${DFG_API_PORT:-8000} --no-access-log --no-server-header --proxy-headers --forwarded-allow-ips='*'"]
```
