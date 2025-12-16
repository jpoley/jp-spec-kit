"""Provider registry with factory pattern and auto-detection."""

import re
from threading import Lock
from typing import Dict, Optional, Type

from .enums import ProviderType
from .errors import ProviderNotFoundError
from .provider import RemoteProvider


# Provider ID patterns for auto-detection
PROVIDER_PATTERNS = {
    ProviderType.GITHUB: r"^(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)#(?P<number>\d+)$",
    ProviderType.JIRA: r"^(?P<project>[A-Z][A-Z0-9]*)-(?P<number>\d+)$",
    ProviderType.NOTION: r"^(?P<id>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})$",
}


class ProviderRegistry:
    """
    Thread-safe registry for remote providers.

    Implements factory pattern with:
    - Decorator-based provider registration
    - Auto-detection from task ID patterns
    - Lazy initialization with singleton pattern
    - Thread-safe instance caching

    Example:
        @ProviderRegistry.register(ProviderType.GITHUB)
        class GitHubProvider(RemoteProvider):
            ...

        # Auto-detect and get provider
        provider_type = ProviderRegistry.detect_provider("owner/repo#123")
        provider = ProviderRegistry.get(provider_type, config)
    """

    # Registry state (class-level)
    _providers: Dict[ProviderType, Type[RemoteProvider]] = {}
    _instances: Dict[str, RemoteProvider] = {}
    _lock = Lock()

    @classmethod
    def register(cls, provider_type: ProviderType):
        """
        Decorator to register a provider class.

        The decorated class must be a subclass of RemoteProvider.

        Args:
            provider_type: The ProviderType enum value for this provider

        Returns:
            Decorator function that registers the provider

        Raises:
            TypeError: If decorated class doesn't subclass RemoteProvider

        Example:
            @ProviderRegistry.register(ProviderType.GITHUB)
            class GitHubProvider(RemoteProvider):
                @property
                def provider_type(self) -> ProviderType:
                    return ProviderType.GITHUB
                # ... implement other abstract methods
        """

        def decorator(provider_class: Type[RemoteProvider]):
            if not issubclass(provider_class, RemoteProvider):
                raise TypeError(
                    f"{provider_class.__name__} must subclass RemoteProvider"
                )
            cls._providers[provider_type] = provider_class
            return provider_class

        return decorator

    @classmethod
    def get(
        cls, provider_type: ProviderType, config: Optional[Dict] = None
    ) -> RemoteProvider:
        """
        Get or create a provider instance.

        Instances are cached per provider type + config hash combination.
        Thread-safe via locking.

        Args:
            provider_type: The type of provider to get
            config: Configuration dictionary for the provider

        Returns:
            Provider instance (cached or newly created)

        Raises:
            ProviderNotFoundError: If provider type not registered
        """
        config = config or {}
        # Create cache key from provider type + config hash
        config_hash = hash(frozenset(config.items()))
        key = f"{provider_type.value}:{config_hash}"

        with cls._lock:
            # Return cached instance if exists
            if key not in cls._instances:
                # Get registered provider class
                provider_class = cls._providers.get(provider_type)
                if not provider_class:
                    raise ProviderNotFoundError(provider_type.value)

                # Create and cache new instance
                cls._instances[key] = provider_class(config)

            return cls._instances[key]

    @classmethod
    def detect_provider(cls, task_id: str) -> Optional[ProviderType]:
        """
        Auto-detect provider from task ID format.

        Matches task_id against known provider patterns:
        - GitHub: "owner/repo#123"
        - Jira: "PROJ-123"
        - Notion: "abc12345-1234-1234-1234-123456789abc"

        Args:
            task_id: Task identifier string to analyze

        Returns:
            ProviderType if matched, None if no pattern matches

        Example:
            >>> ProviderRegistry.detect_provider("myorg/myrepo#42")
            ProviderType.GITHUB
            >>> ProviderRegistry.detect_provider("ENG-123")
            ProviderType.JIRA
            >>> ProviderRegistry.detect_provider("unknown-format")
            None
        """
        for provider_type, pattern in PROVIDER_PATTERNS.items():
            if re.match(pattern, task_id):
                return provider_type
        return None

    @classmethod
    def parse_task_id(cls, task_id: str) -> Optional[Dict[str, str]]:
        """
        Parse task ID into components.

        Extracts named groups from the matching pattern and includes
        the provider type.

        Args:
            task_id: Task identifier string to parse

        Returns:
            Dictionary with 'provider' key and pattern-specific fields,
            or None if no pattern matches

        Example:
            >>> ProviderRegistry.parse_task_id("owner/repo#123")
            {
                'provider': ProviderType.GITHUB,
                'owner': 'owner',
                'repo': 'repo',
                'number': '123'
            }
            >>> ProviderRegistry.parse_task_id("PROJ-456")
            {
                'provider': ProviderType.JIRA,
                'project': 'PROJ',
                'number': '456'
            }
        """
        for provider_type, pattern in PROVIDER_PATTERNS.items():
            match = re.match(pattern, task_id)
            if match:
                return {"provider": provider_type, **match.groupdict()}
        return None

    @classmethod
    def list_available(cls) -> Dict[ProviderType, Type[RemoteProvider]]:
        """
        Get all registered providers.

        Returns:
            Dictionary mapping ProviderType to provider class

        Example:
            >>> providers = ProviderRegistry.list_available()
            >>> ProviderType.GITHUB in providers
            True
        """
        return cls._providers.copy()

    @classmethod
    def unregister(cls, provider_type: ProviderType) -> None:
        """
        Remove a provider registration.

        Also removes all cached instances for that provider type.
        Useful for testing or dynamic provider management.

        Args:
            provider_type: The provider type to unregister
        """
        with cls._lock:
            # Remove from registry
            cls._providers.pop(provider_type, None)

            # Remove cached instances
            prefix = f"{provider_type.value}:"
            to_remove = [k for k in cls._instances if k.startswith(prefix)]
            for key in to_remove:
                del cls._instances[key]

    @classmethod
    def clear_instances(cls) -> None:
        """
        Clear all cached provider instances.

        Useful for testing or to force reconnection.
        Does not clear provider registrations.
        """
        with cls._lock:
            cls._instances.clear()


class LazyProvider:
    """
    Proxy that defers provider initialization until first use.

    Useful for:
    - Startup performance when not all providers are needed
    - Delaying authentication until actually required
    - Testing scenarios with mocked providers

    Example:
        lazy = LazyProvider(ProviderType.GITHUB, {"token": "..."})
        # Provider not created yet

        task = lazy.get_task("owner/repo#123")
        # Provider created on first method call
    """

    def __init__(self, provider_type: ProviderType, config: Optional[Dict] = None):
        """
        Initialize lazy provider proxy.

        Args:
            provider_type: Type of provider to create on demand
            config: Configuration to pass when creating provider
        """
        self._provider_type = provider_type
        self._config = config or {}
        self._instance: Optional[RemoteProvider] = None

    def _get_instance(self) -> RemoteProvider:
        """
        Get or create the provider instance.

        Returns:
            The actual provider instance
        """
        if self._instance is None:
            self._instance = ProviderRegistry.get(self._provider_type, self._config)
        return self._instance

    def __getattr__(self, name: str):
        """
        Proxy attribute access to the provider instance.

        Args:
            name: Attribute or method name

        Returns:
            The attribute from the provider instance
        """
        return getattr(self._get_instance(), name)

    def __repr__(self) -> str:
        """String representation showing lazy status."""
        if self._instance is None:
            return f"LazyProvider({self._provider_type.value}, not initialized)"
        return f"LazyProvider({self._provider_type.value}, initialized)"
