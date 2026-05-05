from typing import Any, NamedTuple, Optional, TypedDict, Union, ContextManager, Protocol, runtime_checkable

class SignedCredential:
    """Signed credential used for authenticating e.g. Azure SAS, Google URL.
    The credential may be updated without needs to recreate the client.

    :param str signature: Signature used to authenticate
    :raises TypeError: If the signature is not a string.
    """

    def __init__(self, signature: str) -> None:
        if not isinstance(signature, str):
            raise TypeError("signature must be a string.")
        self._signature = signature

    @property
    def signature(self) -> str:
        """Value of the signature.

        :rtype: str
        :return: The value of the signature.
        """
        return self._signature
    
    def update(self, signature: str) -> None:
        """Update the signature.

        This can be used when you've regenerated your signature and want
        to update long-lived clients.

        :param str signature: The signature used to authenticate
        :raises ValueError: If the signature is None or empty.
        :raises TypeError: If the signature is not a string.
        """
        if not signature:
            raise ValueError("The signature used for updating can not be None or empty")
        if not isinstance(signature, str):
            raise TypeError("The signature used for updating must be a string.")
        self._signature = signature

class NamedSignature(NamedTuple):
    """Represents a name and signature tuple."""

    name: str
    signature: str

class NamedSignedCredential:
    """Named signed credential used for authenticating.
    The named credential may be updated without needs to recreate the client.

    :param str name: The name of the signed credential used to authenticate.
    :param str signature: Signature used to authenticate
    :raises TypeError: If the signature is not a string.
    """

    def __init__(self, name: str, signature: str) -> None:
        if not isinstance(name, str) or not isinstance(signature, str):
            raise TypeError("Both name and signature must be strings.")
        self._credential = NamedSignature(name, signature)

class UntypedToken(NamedTuple):
    """Represents a token either authentication or authorization."""

    value: str
    """The token string."""
    expires_on: int
    """The token's expiration time."""

class TypedToken:
    """Typed token extending `Token`.

    :param str value: The token string.
    :param int expires_on: The token's expiration time.
    :keyword str token_type: The type of token. Defaults to 'Bearer'.
    :keyword int refresh_on: Specifies the time when the cached token should be proactively refreshed. Optional.
    """

    value: str
    """The token string."""
    expires_on: int
    """The token's expiration time"""
    token_type: str
    """The type of token."""
    refresh_on: Optional[int]
    """Specifies the time when the cached token should be proactively refreshed. Optional."""

    def __init__(
        self,
        value: str,
        expires_on: int,
        *,
        token_type: str = "Bearer",
        refresh_on: Optional[int] = None,
    ) -> None:
        self.value = value
        self.expires_on = expires_on
        self.token_type = token_type
        self.refresh_on = refresh_on

    def __repr__(self) -> str:
        return "TypedToken(value='{}', expires_on={}, token_type='{}', refresh_on={})".format(
            self.value, self.expires_on, self.token_type, self.refresh_on
        )

class TokenRequestOptions(TypedDict, total=False):
    """Options for token requests. All parameters are optional."""

    space_id: str
    """Space id is like Azure's tenant, Google's project or AWS's account."""

@runtime_checkable
class UntypedTokenProvider(Protocol):
    """Protocol for classes able to provide tokens."""

    def get_token(
        self,
        *scopes: str,
        space_id: Optional[str] = None,
        **kwargs: Any,
    ) -> UntypedToken:
        """Request an token for `scopes`.

        :param str scopes: OAuth || OpenID scopes.

        :keyword str space_id: Optional space to include in the token request.

        :rtype: Token
        :return: A Token instance containing the token string and its expiration time.
        """
        ...

@runtime_checkable
class TypedTokenProvider(Protocol, ContextManager["TypedTokenProvider"]):
    """Protocol for classes able to provide tokens with additional properties."""

    def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> TypedToken:
        """Request an access token for `scopes`.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token.

        :param str scopes: OAuth || OpenID scopes.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: TokenRequestOptions

        :rtype: TypedToken
        :return: An TypedToken instance containing information about the token.
        """
        ...

    def close(self) -> None:
        """Close the credential, releasing any resources it holds.

        :return: None
        :rtype: None
        """


TokenProvider = Union[UntypedTokenProvider, TypedTokenProvider]


__all__ = [
    "SignedCredential",
    "NamedSignedCredential",
    "Token",
    "TokenDimensions",
    "TypedToken",
    "TokenRequestOptions",
    "UntypedTokenProvider",
    "TypedTokenProvider",
    "TokenProvider"
]