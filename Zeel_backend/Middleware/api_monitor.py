import time
from fastapi import Request
import logging

logger = logging.getLogger("api")


class APIMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def __call__(self, request: Request, call_next):
        start_time = time.time()

        # Get client info
        client_host = request.client.host if request.client else "unknown"

        # Log request
        self.logger.info(
            f"API Request - Method: {request.method}, "
            f"URL: {request.url}, "
            f"Client: {client_host}, "
            f"User-Agent: {request.headers.get('user-agent', 'Unknown')}"
        )

        try:
            response = await call_next(request)
        except Exception as e:
            # Log errors
            self.logger.error(f"API Error - {str(e)}")
            raise

        process_time = time.time() - start_time

        # Log response
        self.logger.info(
            f"API Response - Status: {response.status_code}, Time: {process_time:.4f}s"
        )

        return response


# Create instance
api_monitor = APIMonitor()
