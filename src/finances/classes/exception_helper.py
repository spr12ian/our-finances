class ExceptionHelper(Exception):
    """Base exception for all helper-related errors."""

    def __init__(self, message: str, *, cause: BaseException | None = None) -> None:
        super().__init__(message)
        # Optional: manually store cause (makes it accessible in all Python versions)
        self.__cause__ = cause
