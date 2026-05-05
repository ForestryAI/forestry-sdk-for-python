from typing import Final

class Turn:
    """Turn constants when constructing a pipeline"""
    TRANSITION_NAME: Final[str] = "transition"
    RETRY_DIRECTIVE_NAME: Final[str] = "retry_directive"