"""Middleware used to create metrics on requests and response
"""

import time
from typing import Tuple
import datetime
import uuid
from prometheus_client import Counter, Gauge, Histogram, Info , Summary
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match
from starlette.types import ASGIApp

from .logging import logger

RELEASE_DATE = Info("release_date","Date of last server update")
RELEASE_DATE.info({'last_release': datetime.datetime.now().strftime("%m/%d/%Y"),})

REQUESTS = Counter(
    "server_requests_total",
    "Total count of requests by path.",
    ["path"]
)
RESPONSES = Counter(
    "server_responses_total",
    "Total count of responses by path and status codes.",
    ["path", "status_code"],
)

TIME_BUCKETS = [0.05, 0.1, 0.5, 1, 5, 10, 50, 100, 500, 1000]

REQUESTS_PROCESSING_TIME = Histogram(
    "server_requests_processing_time_milliseconds",
    "Histogram of requests processing time by path",
    ["path"],
    buckets=TIME_BUCKETS
)
EXCEPTIONS = Counter(
    "server_exceptions_total",
    "Total count of exceptions raised by path and exception type",
    ["path", "exception_type"],
)
REQUESTS_IN_PROGRESS = Gauge(
    "server_requests_in_progress",
    "Gauge of requests by path currently being processed",
    ["path"],
)

PATH_TO_BE_IGNORED = [
    "/auth",
    "/metrics",
    "/programmers/verify",
    "/users/verify"
]

class MonitoringMiddleware(BaseHTTPMiddleware):
    """MonitoringMiddleware deals with request based metrics
    """
    def __init__(self, app: ASGIApp, filter_unhandled_paths: bool = False) -> None:
        super().__init__(app)
        self.filter_unhandled_paths = filter_unhandled_paths

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path_template, is_handled_path = self.get_path_template(request)

        if self._is_path_filtered(is_handled_path) or path_template in PATH_TO_BE_IGNORED:
            return await call_next(request)

        idem = uuid.uuid4()
        logger.debug(f"rid={idem} start request path={path_template}")
        start_time = time.time()
        REQUESTS_IN_PROGRESS.labels(path=path_template).inc()
        REQUESTS.labels(path=path_template).inc()
        try:
            before_time = time.perf_counter()
            response = await call_next(request)
            after_time = time.perf_counter()
        except Exception as e:
            EXCEPTIONS.labels(path=path_template, exception_type=type(e).__name__).inc()
            raise e from None
        else:
            REQUESTS_PROCESSING_TIME.labels(path=path_template).observe(
                (after_time - before_time)*1000
            )
            RESPONSES.labels(path=path_template, status_code=response.status_code).inc()
        finally:
            REQUESTS_IN_PROGRESS.labels(path=path_template).dec()

            process_time = (time.time() - start_time) * 1000
            formatted_process_time = '{0:.2f}'.format(process_time)
            logger.debug(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
        return response

    @staticmethod
    def get_path_template(request: Request) -> Tuple[str, bool]:
        for route in request.app.routes:
            match, child_scope = route.matches(request.scope)
            if match == Match.FULL:
                return route.path, True

        return request.url.path, False

    def _is_path_filtered(self, is_handled_path: bool) -> bool:
        return self.filter_unhandled_paths and not is_handled_path