import time
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class BaseResponse:
    success: bool
    message: str
    code: str
    data: Optional[Any] = None
    # time defaults to current timestamp if not provided
    timestamp: float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "code": self.code,
            "data": self.data,
            "time": self.timestamp
        }

# Factory methods for clean usage
class ResponseFactory:
    @staticmethod
    def success(data: Any = None, message: str = "Call successful"):
        return BaseResponse(success=True, message=message, code="000000", data=data)

    @staticmethod
    def error(message: str = "Call failed", code: str = "xxxxxx"):
        return BaseResponse(success=False, message=message, code=code)

# Usage
if __name__ == '__main__':
    # Success response
    resp = ResponseFactory.success(data={"id": 1, "name": "Apple"})
    print(resp.to_dict())
    
    # Error response
    err = ResponseFactory.error(message="Database connection timeout")
    print(err.to_dict())