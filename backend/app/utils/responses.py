from fastapi import HTTPException

def format_response(status: str, message: str, data=None, errors=None, code=200, raise_exception=False):
    """Standardizes API responses and ensures correct exception handling."""
    response = {
        "status": status,
        "message": message,
        "data": data or {},
        "errors": errors or [],
        "code": code
    }
    
    if raise_exception:  
        raise HTTPException(status_code=code, detail=response)
    
    return response
