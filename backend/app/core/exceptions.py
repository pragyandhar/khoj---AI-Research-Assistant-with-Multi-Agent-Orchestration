# WHAT DOES THIS FILE DO: Defines custom application exception classes to handle structured error responses.

# =========== CLASS ===========
# ROLE: Base exception class for all errors in the app.
class AppException(Exception):
    """ Base application exception. """

    def __init__(self, message: str, status_code: int, error_code: str):
        """ Initialize the exception with message, status code and error code. """
        # FLOW-1: Store the exception fields and call parent init
        self.message = message                  # USE: Human readable error message
        self.status_code = status_code          # USE: HTTP status code
        self.error_code = error_code            # USE: Unique string for client side error tracking
        super().__init__(message)               # USE: Parent class constructor call
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Custom exception raised when LLM service is unavailable or returns an error.
class LLMException(AppException):
    """ Upstream LLM service error. """

    def __init__(self, message: str, status_code: int = 502, error_code: str = "LLM_UNAVAILABLE"):
        """ Initialize LLM exception with default 502 status. """
        # FLOW-1: Call parent AppException constructor with default parameters
        super().__init__(message, status_code, error_code)
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Custom exception raised when a LangChain tool execution fails.
class ToolExecutionException(AppException):
    """ Custom tool run error. """

    def __init__(self, message: str, status_code: int = 500, error_code: str = "TOOL_EXECUTION_FAILED"):
        """ Initialize tool exception with default 500 status. """
        # FLOW-1: Pass arguments to parent constructor
        super().__init__(message, status_code, error_code)
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Custom exception raised when research session does not exist.
class SessionNotFoundException(AppException):
    """ Missing session error. """

    def __init__(self, message: str, status_code: int = 404, error_code: str = "SESSION_NOT_FOUND"):
        """ Initialize session exception with default 404 status. """
        # FLOW-1: Send data to AppException base class constructor
        super().__init__(message, status_code, error_code)
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Custom exception raised when client exceeds request rate limit.
class RateLimitException(AppException):
    """ Exceeded rate limit error. """

    def __init__(self, message: str, status_code: int = 429, error_code: str = "RATE_LIMIT_EXCEEDED"):
        """ Initialize rate limit exception with default 429 status. """
        # FLOW-1: Pass to parent init method
        super().__init__(message, status_code, error_code)
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Custom exception raised when input validation fails.
class ValidationException(AppException):
    """ Input fields validation error. """

    def __init__(self, message: str, status_code: int = 422, error_code: str = "VALIDATION_ERROR"):
        """ Initialize validation exception with default 422 status. """
        # FLOW-1: Send arguments to parent constructor
        super().__init__(message, status_code, error_code)
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Custom exception raised on database query or connection failures.
class DatabaseException(AppException):
    """ Database operation error. """

    def __init__(self, message: str, status_code: int = 500, error_code: str = "DATABASE_ERROR"):
        """ Initialize database exception with default 500 status. """
        # FLOW-1: Pass exception data to base class
        super().__init__(message, status_code, error_code)
# =========== CLASS ===========