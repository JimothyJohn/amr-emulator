"""A client library for accessing 3.8.1 MIR250 REST API"""

from .client import AuthenticatedClient, Client

__all__ = (
    "AuthenticatedClient",
    "Client",
)
