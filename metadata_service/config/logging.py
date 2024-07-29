import re
import sys
import uuid
import json
import logging
import datetime as dt

import tomlkit
from flask import request, g

from metadata_service.config import environment


def _get_project_meta():
    with open("pyproject.toml", encoding="utf-8") as pyproject:
        file_contents = pyproject.read()

    return tomlkit.parse(file_contents)["tool"]["poetry"]


class RequestInfoFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Make sure string only contains alphanumeric characters,
        # underscores and/or dashes
        record.correlation_id = re.sub(
            r"[^\w\-]", "", request.headers.get("X-Request-ID", "")
        )
        record.method = request.method
        record.url = request.url
        record.remote_host = request.remote_addr
        record.response_status = getattr(g, "response_status")
        record.response_time_ms = getattr(g, "response_time_ms")
        return True


class MicrodataJSONFormatter(logging.Formatter):
    def __init__(self):
        self.pkg_meta = _get_project_meta()
        self.host = environment.get("DOCKER_HOST_NAME")
        self.command = json.dumps(sys.argv)

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "@timestamp": dt.datetime.fromtimestamp(
                    record.created,
                    tz=dt.timezone.utc,
                ).isoformat(),
                "command": self.command,
                "error.stack": record.__dict__.get("exc_info"),
                "host": self.host,
                "message": record.getMessage(),
                "level": record.levelno,
                "levelName": record.levelname,
                "loggerName": record.name,
                "method": record.__dict__.get("method"),
                "responseTime": record.__dict__.get("response_time_ms"),
                "schemaVersion": "v3",
                "serviceName": "metadata-service",
                "serviceVersion": str(self.pkg_meta["version"]),
                "source_host": record.__dict__.get("remote_host"),
                "statusCode": record.__dict__.get("response_status"),
                "thread": record.threadName,
                "url": record.__dict__.get("request"),
                "xRequestId": record.__dict__.get("correlation_id"),
            }
        )


def setup_logging(app, log_level: int = logging.INFO) -> None:
    """Set up logging configuration."""
    logger = logging.getLogger()
    logger.setLevel(log_level)

    formatter = MicrodataJSONFormatter()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    request_info_filter = RequestInfoFilter()
    logger.addFilter(request_info_filter)
    logger.addHandler(stream_handler)

    @app.before_request
    def before_request():
        g.start_time = dt.datetime.now()
        correlation_id = request.headers.get("X-Request-ID", None)
        if correlation_id is None:
            g.correlation_id = "metadata-service-" + str(uuid.uuid1())
        else:
            g.correlation_id = correlation_id
        g.method = request.method
        g.url = request.url
        g.remote_host = request.remote_addr

    @app.after_request
    def after_request(response):
        g.response_time_ms = int(
            (dt.datetime.now() - g.start_time).total_seconds() * 1000
        )
        g.response_status = response.status_code
        response.headers["X-Request-ID"] = g.correlation_id
        return response
