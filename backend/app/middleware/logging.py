import json
import time
import logging
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("argus_api")
logger.setLevel(logging.INFO)

# Stream handler for console logs
handler = logging.StreamHandler()
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        return json.dumps(log_entry)

handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.time()

        # Log Request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={"extra_fields": {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else None
            }}
        )

        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            # Log Response
            logger.info(
                f"Completed request: {request.method} {request.url.path} with status {response.status_code}",
                extra={"extra_fields": {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(process_time, 2)
                }}
            )
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Failed request: {request.method} {request.url.path} due to error {str(e)}",
                exc_info=True,
                extra={"extra_fields": {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "duration_ms": round(process_time, 2)
                }}
            )
            raise e
