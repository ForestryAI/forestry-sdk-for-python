from __future__ import annotations
from types import TracebackType
from typing import Any, Optional, AsyncContextManager, Type, Union, TYPE_CHECKING
from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from .security import TypedToken, UntypedToken, TokenRequestOptions

@runtime_checkable
class AsyncUntypedTokenProvider(Protocol, AsyncContextManager["AsyncUntypedTokenProvider"]):
    """Protocol for classes able to provide tokens."""

    async def get_token(
        self,
        *scopes: str,
        space_id: Optional[str] = None,
        **kwargs: Any,
    ) -> UntypedToken:
        """Request an access token for `scopes`.

        :param str scopes: OAuth || OpenID scopes.

        :keyword str space_id: Optional space to include in the token request.

        :rtype: UntypedToken
        :return: An UntypedToken instance containing the token string and its expiration time.
        """
        ...

    async def close(self) -> None:
        """Close the provider, releasing any resources.

        :return: None
        :rtype: None
        """

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        pass


@runtime_checkable
class AsyncTypedTokenProvider(Protocol, AsyncContextManager["AsyncTypedTokenProvider"]):
    """Protocol for classes able to provide tokens with additional properties."""

    async def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> TypedToken:
        """Request an token for `scopes`.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token.

        :param str scopes: OAuth || OpenID scopes.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: TokenRequestOptions

        :rtype: TypedToken
        :return: An TypedToken instance containing the token string and its expiration time.
        """
        ...

    async def close(self) -> None:
        """Close the provider, releasing any resources.

        :return: None
        :rtype: None
        """

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        pass


AsyncTokenProvider = Union[AsyncUntypedTokenProvider, AsyncTypedTokenProvider]