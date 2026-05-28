class EmbeddingServiceError(Exception):
    """Raised when the embedding provider is unavailable."""

    def __init__(self, message: str, *, status_code: int = 503, retryable: bool = True):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
