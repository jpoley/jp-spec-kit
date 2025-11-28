"""Secure credential management for Satellite Mode providers.

This module provides secure storage and retrieval of API tokens for remote
providers (GitHub, Jira, Notion) using the system keychain as the primary
storage mechanism, with fallbacks to environment variables and CLI tools.

Security Design:
- Tokens stored in OS keychain (macOS Keychain, Windows Credential Manager,
  Linux Secret Service)
- Environment variables as fallback for CI/CD environments
- gh CLI integration for GitHub tokens
- Log redaction to prevent token leakage
- Token format validation before storage

Example:
    >>> from specify_cli.satellite import SecretManager, ProviderType
    >>> manager = SecretManager()
    >>> token = manager.get_token(ProviderType.GITHUB)
    >>> if token:
    ...     print("GitHub token found")
    ... else:
    ...     token = manager.prompt_for_token(ProviderType.GITHUB)
"""

import getpass
import logging
import os
import re
import shutil
import subprocess
from typing import Dict, Optional, Set

from .enums import ProviderType
from .errors import SecretStorageUnavailableError

# Try to import keyring, handle gracefully if unavailable
try:
    import keyring
    from keyring.errors import KeyringError, NoKeyringError

    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    KeyringError = Exception  # type: ignore
    NoKeyringError = Exception  # type: ignore


# Environment variable names for each provider
ENV_VAR_NAMES: Dict[ProviderType, str] = {
    ProviderType.GITHUB: "GITHUB_TOKEN",
    ProviderType.JIRA: "JIRA_TOKEN",
    ProviderType.NOTION: "NOTION_TOKEN",
}

# Token format validation patterns
TOKEN_PATTERNS: Dict[ProviderType, re.Pattern] = {
    # GitHub: ghp_*, gho_*, github_pat_*, or 40-char hex (classic)
    ProviderType.GITHUB: re.compile(
        r"^(ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36}|"
        r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}|"
        r"[a-f0-9]{40})$"
    ),
    # Jira: API tokens are typically 24+ chars alphanumeric
    ProviderType.JIRA: re.compile(r"^[A-Za-z0-9+/=]{20,}$"),
    # Notion: secret_* or ntn_* prefix
    ProviderType.NOTION: re.compile(r"^(secret_[a-zA-Z0-9]{43}|ntn_[a-zA-Z0-9]{50,})$"),
}


class TokenRedactionFilter(logging.Filter):
    """Logging filter that redacts known tokens from log messages.

    This filter maintains a set of tokens that should be redacted from any
    log output. Tokens are replaced with [REDACTED:{provider}] to indicate
    sensitive data was present without exposing the actual value.

    Example:
        >>> import logging
        >>> filter = TokenRedactionFilter()
        >>> filter.add_token("ghp_abc123xyz", ProviderType.GITHUB)
        >>> logger = logging.getLogger("satellite")
        >>> logger.addFilter(filter)
        >>> logger.info("Using token ghp_abc123xyz")  # logs "[REDACTED:github]"
    """

    def __init__(self, name: str = ""):
        """Initialize the token redaction filter.

        Args:
            name: Logger name to filter (empty string = all loggers)
        """
        super().__init__(name)
        self._tokens: Dict[str, str] = {}  # token -> provider name

    def add_token(self, token: str, provider: ProviderType) -> None:
        """Register a token for redaction.

        Args:
            token: The token value to redact
            provider: The provider this token belongs to
        """
        if token:
            self._tokens[token] = provider.value

    def remove_token(self, token: str) -> None:
        """Unregister a token from redaction.

        Args:
            token: The token value to stop redacting
        """
        self._tokens.pop(token, None)

    @property
    def registered_tokens(self) -> Set[str]:
        """Return set of currently registered tokens (for testing)."""
        return set(self._tokens.keys())

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record by redacting registered tokens.

        Args:
            record: The log record to filter

        Returns:
            True (always allows the record through, but modifies message)
        """
        if not self._tokens:
            return True

        msg = str(record.msg)
        for token, provider in self._tokens.items():
            if token in msg:
                msg = msg.replace(token, f"[REDACTED:{provider}]")

        # Also check args if present
        if record.args:
            args = []
            for arg in record.args:
                arg_str = str(arg)
                for token, provider in self._tokens.items():
                    if token in arg_str:
                        arg_str = arg_str.replace(token, f"[REDACTED:{provider}]")
                args.append(arg_str)
            record.args = tuple(args)

        record.msg = msg
        return True


class SecretManager:
    """Manages secure storage and retrieval of provider credentials.

    The SecretManager provides a unified interface for handling API tokens
    across different providers, with a priority-based fallback chain:

    1. System keychain (via keyring library)
    2. Environment variables (GITHUB_TOKEN, JIRA_TOKEN, NOTION_TOKEN)
    3. gh CLI (GitHub only)
    4. Interactive prompt (with optional keychain storage)

    Attributes:
        service_name: The keychain service name for storing credentials
        redaction_filter: Logging filter for token redaction

    Example:
        >>> manager = SecretManager()
        >>> token = manager.get_token(ProviderType.GITHUB)
        >>> if manager.validate_token_format(ProviderType.GITHUB, token):
        ...     print("Valid token format")
    """

    def __init__(self, service_name: str = "backlog-satellite"):
        """Initialize the SecretManager.

        Args:
            service_name: Keychain service name for credential storage
        """
        self.service_name = service_name
        self.redaction_filter = TokenRedactionFilter()
        self._keychain_available: Optional[bool] = None

    def _get_keychain_key(self, provider: ProviderType) -> str:
        """Get the keychain username/key for a provider.

        Args:
            provider: The provider type

        Returns:
            Keychain key in format "{provider}-token"
        """
        return f"{provider.value}-token"

    def _is_keychain_available(self) -> bool:
        """Check if system keychain is available.

        Returns:
            True if keychain can be used, False otherwise
        """
        if self._keychain_available is not None:
            return self._keychain_available

        if not KEYRING_AVAILABLE:
            self._keychain_available = False
            return False

        try:
            # Try a minimal operation to test keychain availability
            keyring.get_keyring()
            self._keychain_available = True
        except (NoKeyringError, KeyringError):
            self._keychain_available = False

        return self._keychain_available

    def _get_from_keychain(self, provider: ProviderType) -> Optional[str]:
        """Retrieve token from system keychain.

        Args:
            provider: The provider type

        Returns:
            Token string if found, None otherwise
        """
        if not self._is_keychain_available():
            return None

        try:
            key = self._get_keychain_key(provider)
            token = keyring.get_password(self.service_name, key)
            if token:
                self.redaction_filter.add_token(token, provider)
            return token
        except (KeyringError, Exception):
            return None

    def _get_from_env(self, provider: ProviderType) -> Optional[str]:
        """Retrieve token from environment variable.

        Args:
            provider: The provider type

        Returns:
            Token string if found, None otherwise
        """
        env_var = ENV_VAR_NAMES.get(provider)
        if not env_var:
            return None

        token = os.environ.get(env_var)
        if token:
            self.redaction_filter.add_token(token, provider)
        return token

    def _get_from_gh_cli(self) -> Optional[str]:
        """Retrieve GitHub token from gh CLI.

        Returns:
            Token string if gh CLI is authenticated, None otherwise
        """
        # Check if gh CLI is available
        if not shutil.which("gh"):
            return None

        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                token = result.stdout.strip()
                self.redaction_filter.add_token(token, ProviderType.GITHUB)
                return token
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
            pass

        return None

    def get_token(self, provider: ProviderType) -> Optional[str]:
        """Retrieve token for a provider using the fallback chain.

        Tries sources in order:
        1. System keychain
        2. Environment variable
        3. gh CLI (GitHub only)

        Args:
            provider: The provider type to get token for

        Returns:
            Token string if found from any source, None otherwise
        """
        # 1. Try keychain
        token = self._get_from_keychain(provider)
        if token:
            return token

        # 2. Try environment variable
        token = self._get_from_env(provider)
        if token:
            return token

        # 3. Try gh CLI for GitHub
        if provider == ProviderType.GITHUB:
            token = self._get_from_gh_cli()
            if token:
                return token

        return None

    def store_token(self, provider: ProviderType, token: str) -> bool:
        """Store token in system keychain.

        Args:
            provider: The provider type
            token: The token value to store

        Returns:
            True if stored successfully, False otherwise

        Raises:
            SecretStorageUnavailableError: If keychain is not available
        """
        if not self._is_keychain_available():
            raise SecretStorageUnavailableError(
                "System keychain is not available. "
                "Please install a keyring backend or use environment variables."
            )

        try:
            key = self._get_keychain_key(provider)
            keyring.set_password(self.service_name, key, token)
            self.redaction_filter.add_token(token, provider)
            return True
        except (KeyringError, Exception) as e:
            raise SecretStorageUnavailableError(
                f"Failed to store token in keychain: {e}"
            )

    def delete_token(self, provider: ProviderType) -> bool:
        """Delete token from system keychain.

        Args:
            provider: The provider type

        Returns:
            True if deleted successfully or not found, False on error
        """
        if not self._is_keychain_available():
            return False

        try:
            key = self._get_keychain_key(provider)
            # Get the token first so we can unregister it from redaction
            token = keyring.get_password(self.service_name, key)
            if token:
                self.redaction_filter.remove_token(token)
                keyring.delete_password(self.service_name, key)
            return True
        except (KeyringError, Exception):
            return False

    def validate_token_format(self, provider: ProviderType, token: str) -> bool:
        """Validate token format matches expected pattern.

        This performs basic format validation only. It does NOT verify
        the token is valid with the remote provider.

        Args:
            provider: The provider type
            token: The token value to validate

        Returns:
            True if format matches expected pattern, False otherwise
        """
        if not token:
            return False

        pattern = TOKEN_PATTERNS.get(provider)
        if not pattern:
            # Unknown provider, accept any non-empty token
            return True

        return bool(pattern.match(token))

    def prompt_for_token(
        self,
        provider: ProviderType,
        save: bool = True,
        validate: bool = True,
    ) -> str:
        """Interactively prompt user for a token.

        Args:
            provider: The provider type to prompt for
            save: Whether to save to keychain if available
            validate: Whether to validate token format before accepting

        Returns:
            The entered token string

        Raises:
            InvalidTokenError: If validation enabled and format is invalid
        """
        provider_name = provider.value.title()
        prompt = f"Enter {provider_name} API token: "

        while True:
            token = getpass.getpass(prompt)

            if not token:
                print("Token cannot be empty. Please try again.")
                continue

            if validate and not self.validate_token_format(provider, token):
                print(f"Invalid {provider_name} token format. Please try again.")
                continue

            break

        # Register for redaction
        self.redaction_filter.add_token(token, provider)

        # Save if requested and keychain available
        if save:
            try:
                self.store_token(provider, token)
                print(f"{provider_name} token saved to system keychain.")
            except SecretStorageUnavailableError:
                print(
                    f"Note: Could not save to keychain. "
                    f"Set {ENV_VAR_NAMES[provider]} environment variable for persistence."
                )

        return token

    def get_or_prompt(
        self,
        provider: ProviderType,
        save: bool = True,
        validate: bool = True,
    ) -> str:
        """Get token from any source, prompting if not found.

        Convenience method that combines get_token() and prompt_for_token().

        Args:
            provider: The provider type
            save: Whether to save prompted token to keychain
            validate: Whether to validate token format

        Returns:
            Token string (from storage or user input)
        """
        token = self.get_token(provider)
        if token:
            return token

        return self.prompt_for_token(provider, save=save, validate=validate)

    def get_token_source(self, provider: ProviderType) -> Optional[str]:
        """Determine where a token would be retrieved from.

        Useful for debugging and user feedback.

        Args:
            provider: The provider type

        Returns:
            Source name ("keychain", "env", "gh_cli") or None if not found
        """
        if self._get_from_keychain(provider):
            return "keychain"

        if self._get_from_env(provider):
            return "env"

        if provider == ProviderType.GITHUB and self._get_from_gh_cli():
            return "gh_cli"

        return None
