"""Response formatting utilities."""

from typing import Any, Optional, Dict
from datetime import datetime
from config.constants import RESPONSE_TEMPLATE, ERROR_RESPONSE_TEMPLATE

def format_success_response(data: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Format successful response."""
    response = RESPONSE_TEMPLATE.copy()
    response["data"] = data
    response["meta"]["timestamp"] = datetime.utcnow().isoformat()
    if meta:
        response["meta"].update(meta)
    return response

def format_error_response(error_code: str, message: str, details: Optional[Any] = None) -> Dict[str, Any]:
    """Format error response."""
    response = ERROR_RESPONSE_TEMPLATE.copy()
    response["error"]["code"] = error_code
    response["error"]["message"] = message
    response["error"]["details"] = details
    return response

def format_paginated_response(items: list, total: int, limit: int, offset: int) -> Dict[str, Any]:
    """Format paginated response."""
    return {
        "items": items,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }
