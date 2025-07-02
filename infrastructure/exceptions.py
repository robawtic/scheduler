class RepositoryError(Exception):
    """Base exception for repository errors."""
    
    def __init__(self, message: str, code: str = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            code: Error code for more specific error handling
        """
        self.message = message
        self.code = code
        super().__init__(message)