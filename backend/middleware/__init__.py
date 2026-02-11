"""Middleware for logging, error handling, and validation."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import time
from logger.setup import get_logger

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response."""
        start_time = time.time()
        request_id = f"{datetime.now().timestamp()}"
        
        # Log request
        logger.info(f"[{request_id}] {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(f"[{request_id}] Status: {response.status_code} | Time: {process_time:.3f}s")
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"[{request_id}] Exception: {str(e)} | Time: {process_time:.3f}s")
            raise

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""
    
    async def dispatch(self, request: Request, call_next):
        """Handle exceptions and format responses."""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": str(e) if logger.level == "DEBUG" else None
                    }
                }
            )

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware (simple in-memory implementation)."""
    
    def __init__(self, app, requests: int = 100, period: int = 3600):
        super().__init__(app)
        self.requests = requests
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limits."""
        # Get client IP
        client_ip = request.client.host
        current_time = time.time()
        
        # Initialize client if new
        if client_ip not in self.clients:
            self.clients[client_ip] = {"requests": 0, "reset_time": current_time + self.period}
        
        client_data = self.clients[client_ip]
        
        # Reset if period expired
        if current_time > client_data["reset_time"]:
            client_data["requests"] = 0
            client_data["reset_time"] = current_time + self.period
        
        # Check limit
        if client_data["requests"] >= self.requests:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later."
                    }
                }
            )
        
        # Increment request counter
        client_data["requests"] += 1
        
        response = await call_next(request)
        return response
