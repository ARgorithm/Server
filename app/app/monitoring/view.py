import os

from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, CollectorRegistry, generate_latest
from prometheus_client.multiprocess import MultiProcessCollector
from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from ..main import config

def metrics(request: Request) -> Response:
    if config.METRICS_TOKEN:
        try:
            assert request.headers['authorization'] == 'Bearer ' + config.METRICS_TOKEN 
        except Exception as ae:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="invalid credentials"
            ) from ae
    if "prometheus_multiproc_dir" in os.environ:
        registry = CollectorRegistry()
        MultiProcessCollector(registry)
    else:
        registry = REGISTRY

    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)