"""Unit tests for the SecretManager and TokenRedactionFilter classes."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.satellite import ProviderType
from specify_cli.satellite.secrets import (
    ENV_VAR_NAMES,
    TOKEN_PATTERNS,
    SecretManager,
    TokenRedactionFilter,
)


class TestTokenValidation:
    """Tests for token format validation patterns."""

    def test_github_classic_token_valid(self):
        """GitHub classic PAT (40-char hex) should be valid."""
        manager = SecretManager()
        token = "a" * 40  # 40 hex chars
        assert manager.validate_token_format(ProviderType.GITHUB, token)

    def test_github_fine_grained_pat_valid(self):
        """GitHub fine-grained PAT (ghp_*) should be valid."""
        manager = SecretManager()
        token = "ghp_" + "a" * 36
        assert manager.validate_token_format(ProviderType.GITHUB, token)

    def test_github_oauth_token_valid(self):
        """GitHub OAuth token (gho_*) should be valid."""
        manager = SecretManager()
        token = "gho_" + "A" * 36
        assert manager.validate_token_format(ProviderType.GITHUB, token)

    def test_github_pat_v2_valid(self):
        """GitHub PAT v2 (github_pat_*) should be valid."""
        manager = SecretManager()
        token = "github_pat_" + "a" * 22 + "_" + "b" * 59
        assert manager.validate_token_format(ProviderType.GITHUB, token)

    def test_github_invalid_token(self):
        """Invalid GitHub token format should fail."""
        manager = SecretManager()
        assert not manager.validate_token_format(ProviderType.GITHUB, "invalid")
        assert not manager.validate_token_format(ProviderType.GITHUB, "ghp_short")
        assert not manager.validate_token_format(ProviderType.GITHUB, "")

    def test_jira_token_valid(self):
        """Jira API token (base64-like) should be valid."""
        manager = SecretManager()
        token = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh"  # 34 chars
        assert manager.validate_token_format(ProviderType.JIRA, token)

    def test_jira_token_invalid(self):
        """Invalid Jira token format should fail."""
        manager = SecretManager()
        assert not manager.validate_token_format(ProviderType.JIRA, "short")
        assert not manager.validate_token_format(ProviderType.JIRA, "")

    def test_notion_secret_token_valid(self):
        """Notion secret_* token should be valid."""
        manager = SecretManager()
        token = "secret_" + "a" * 43
        assert manager.validate_token_format(ProviderType.NOTION, token)

    def test_notion_ntn_token_valid(self):
        """Notion ntn_* token should be valid."""
        manager = SecretManager()
        token = "ntn_" + "a" * 50
        assert manager.validate_token_format(ProviderType.NOTION, token)

    def test_notion_token_invalid(self):
        """Invalid Notion token format should fail."""
        manager = SecretManager()
        assert not manager.validate_token_format(ProviderType.NOTION, "invalid")
        assert not manager.validate_token_format(ProviderType.NOTION, "secret_short")

    def test_empty_token_invalid(self):
        """Empty token should always be invalid."""
        manager = SecretManager()
        for provider in ProviderType:
            assert not manager.validate_token_format(provider, "")
            assert not manager.validate_token_format(provider, None)


class TestTokenRedactionFilter:
    """Tests for the TokenRedactionFilter class."""

    def test_redaction_filter_redacts_token(self):
        """Filter should redact registered tokens."""
        filter = TokenRedactionFilter()
        token = "ghp_secret123456789012345678901234567890"
        filter.add_token(token, ProviderType.GITHUB)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"Using token {token}",
            args=(),
            exc_info=None,
        )

        filter.filter(record)
        assert "[REDACTED:github]" in record.msg
        assert token not in record.msg

    def test_redaction_filter_handles_args(self):
        """Filter should redact tokens in log args."""
        filter = TokenRedactionFilter()
        token = "secret_abcdefghij1234567890abcdefghij1234567890abc"
        filter.add_token(token, ProviderType.NOTION)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Token: %s",
            args=(token,),
            exc_info=None,
        )

        filter.filter(record)
        assert token not in str(record.args)
        assert "[REDACTED:notion]" in str(record.args)

    def test_redaction_filter_removes_token(self):
        """Filter should stop redacting after remove_token."""
        filter = TokenRedactionFilter()
        token = "test_token_123"
        filter.add_token(token, ProviderType.GITHUB)
        filter.remove_token(token)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"Token: {token}",
            args=(),
            exc_info=None,
        )

        filter.filter(record)
        assert token in record.msg  # Should NOT be redacted

    def test_redaction_filter_no_tokens(self):
        """Filter should pass through when no tokens registered."""
        filter = TokenRedactionFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Normal message",
            args=(),
            exc_info=None,
        )

        result = filter.filter(record)
        assert result is True
        assert record.msg == "Normal message"

    def test_registered_tokens_property(self):
        """Should return set of registered tokens."""
        filter = TokenRedactionFilter()
        filter.add_token("token1", ProviderType.GITHUB)
        filter.add_token("token2", ProviderType.JIRA)

        assert "token1" in filter.registered_tokens
        assert "token2" in filter.registered_tokens
        assert len(filter.registered_tokens) == 2


class TestSecretManagerEnvVars:
    """Tests for environment variable retrieval."""

    def test_get_token_from_env_github(self, monkeypatch):
        """Should retrieve GITHUB_TOKEN from environment."""
        token = "ghp_" + "a" * 36
        monkeypatch.setenv("GITHUB_TOKEN", token)

        manager = SecretManager()
        # Force keychain to be unavailable
        manager._keychain_available = False

        result = manager.get_token(ProviderType.GITHUB)
        assert result == token

    def test_get_token_from_env_jira(self, monkeypatch):
        """Should retrieve JIRA_TOKEN from environment."""
        token = "jira_api_token_12345678901234567890"
        monkeypatch.setenv("JIRA_TOKEN", token)

        manager = SecretManager()
        manager._keychain_available = False

        result = manager.get_token(ProviderType.JIRA)
        assert result == token

    def test_get_token_from_env_notion(self, monkeypatch):
        """Should retrieve NOTION_TOKEN from environment."""
        token = "secret_" + "a" * 43
        monkeypatch.setenv("NOTION_TOKEN", token)

        manager = SecretManager()
        manager._keychain_available = False

        result = manager.get_token(ProviderType.NOTION)
        assert result == token

    def test_get_token_env_not_set(self, monkeypatch):
        """Should return None when env var not set."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

        manager = SecretManager()
        manager._keychain_available = False

        result = manager._get_from_env(ProviderType.GITHUB)
        assert result is None


class TestSecretManagerGhCli:
    """Tests for gh CLI integration."""

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_get_token_from_gh_cli(self, mock_run, mock_which):
        """Should retrieve token from gh CLI."""
        mock_which.return_value = "/usr/bin/gh"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="ghp_testtoken123456789012345678901234\n",
        )

        manager = SecretManager()
        result = manager._get_from_gh_cli()

        assert result == "ghp_testtoken123456789012345678901234"
        mock_run.assert_called_once()

    @patch("shutil.which")
    def test_get_token_gh_cli_not_installed(self, mock_which):
        """Should return None when gh CLI not installed."""
        mock_which.return_value = None

        manager = SecretManager()
        result = manager._get_from_gh_cli()

        assert result is None

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_get_token_gh_cli_not_authenticated(self, mock_run, mock_which):
        """Should return None when gh CLI not authenticated."""
        mock_which.return_value = "/usr/bin/gh"
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
        )

        manager = SecretManager()
        result = manager._get_from_gh_cli()

        assert result is None


class TestSecretManagerKeychain:
    """Tests for keychain operations."""

    @patch("specify_cli.satellite.secrets.KEYRING_AVAILABLE", True)
    @patch("specify_cli.satellite.secrets.keyring")
    def test_get_token_from_keychain(self, mock_keyring):
        """Should retrieve token from keychain."""
        mock_keyring.get_keyring.return_value = MagicMock()
        mock_keyring.get_password.return_value = "stored_token"

        manager = SecretManager()
        manager._keychain_available = True

        result = manager._get_from_keychain(ProviderType.GITHUB)
        assert result == "stored_token"
        mock_keyring.get_password.assert_called_once_with(
            "backlog-satellite", "github-token"
        )

    @patch("specify_cli.satellite.secrets.KEYRING_AVAILABLE", True)
    @patch("specify_cli.satellite.secrets.keyring")
    def test_store_token_in_keychain(self, mock_keyring):
        """Should store token in keychain."""
        mock_keyring.get_keyring.return_value = MagicMock()

        manager = SecretManager()
        manager._keychain_available = True

        result = manager.store_token(ProviderType.GITHUB, "new_token")
        assert result is True
        mock_keyring.set_password.assert_called_once_with(
            "backlog-satellite", "github-token", "new_token"
        )

    @patch("specify_cli.satellite.secrets.KEYRING_AVAILABLE", True)
    @patch("specify_cli.satellite.secrets.keyring")
    def test_delete_token_from_keychain(self, mock_keyring):
        """Should delete token from keychain."""
        mock_keyring.get_keyring.return_value = MagicMock()
        mock_keyring.get_password.return_value = "existing_token"

        manager = SecretManager()
        manager._keychain_available = True

        result = manager.delete_token(ProviderType.GITHUB)
        assert result is True
        mock_keyring.delete_password.assert_called_once_with(
            "backlog-satellite", "github-token"
        )

    def test_store_token_keychain_unavailable(self):
        """Should raise error when keychain unavailable."""
        manager = SecretManager()
        manager._keychain_available = False

        from specify_cli.satellite.errors import SecretStorageUnavailableError

        with pytest.raises(SecretStorageUnavailableError):
            manager.store_token(ProviderType.GITHUB, "token")


class TestSecretManagerFallbackChain:
    """Tests for the credential resolution fallback chain."""

    @patch("specify_cli.satellite.secrets.KEYRING_AVAILABLE", True)
    @patch("specify_cli.satellite.secrets.keyring")
    def test_fallback_chain_keychain_first(self, mock_keyring, monkeypatch):
        """Keychain should take priority over env vars."""
        mock_keyring.get_keyring.return_value = MagicMock()
        mock_keyring.get_password.return_value = "keychain_token"
        monkeypatch.setenv("GITHUB_TOKEN", "env_token")

        manager = SecretManager()
        manager._keychain_available = True

        result = manager.get_token(ProviderType.GITHUB)
        assert result == "keychain_token"

    @patch("specify_cli.satellite.secrets.KEYRING_AVAILABLE", True)
    @patch("specify_cli.satellite.secrets.keyring")
    def test_fallback_to_env_when_keychain_empty(self, mock_keyring, monkeypatch):
        """Should fall back to env var when keychain returns None."""
        mock_keyring.get_keyring.return_value = MagicMock()
        mock_keyring.get_password.return_value = None
        monkeypatch.setenv("GITHUB_TOKEN", "env_token")

        manager = SecretManager()
        manager._keychain_available = True

        result = manager.get_token(ProviderType.GITHUB)
        assert result == "env_token"

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_fallback_to_gh_cli_for_github(self, mock_run, mock_which, monkeypatch):
        """Should fall back to gh CLI for GitHub when other sources empty."""
        mock_which.return_value = "/usr/bin/gh"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="gh_cli_token\n",
        )
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

        manager = SecretManager()
        manager._keychain_available = False

        result = manager.get_token(ProviderType.GITHUB)
        assert result == "gh_cli_token"

    def test_returns_none_when_all_sources_empty(self, monkeypatch):
        """Should return None when no credential source has token."""
        monkeypatch.delenv("JIRA_TOKEN", raising=False)

        manager = SecretManager()
        manager._keychain_available = False

        result = manager.get_token(ProviderType.JIRA)
        assert result is None


class TestSecretManagerTokenSource:
    """Tests for get_token_source method."""

    @patch("specify_cli.satellite.secrets.KEYRING_AVAILABLE", True)
    @patch("specify_cli.satellite.secrets.keyring")
    def test_token_source_keychain(self, mock_keyring):
        """Should identify keychain as source."""
        mock_keyring.get_keyring.return_value = MagicMock()
        mock_keyring.get_password.return_value = "token"

        manager = SecretManager()
        manager._keychain_available = True

        assert manager.get_token_source(ProviderType.GITHUB) == "keychain"

    def test_token_source_env(self, monkeypatch):
        """Should identify env as source."""
        monkeypatch.setenv("GITHUB_TOKEN", "env_token")

        manager = SecretManager()
        manager._keychain_available = False

        assert manager.get_token_source(ProviderType.GITHUB) == "env"

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_token_source_gh_cli(self, mock_run, mock_which, monkeypatch):
        """Should identify gh_cli as source."""
        mock_which.return_value = "/usr/bin/gh"
        mock_run.return_value = MagicMock(returncode=0, stdout="token\n")
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

        manager = SecretManager()
        manager._keychain_available = False

        assert manager.get_token_source(ProviderType.GITHUB) == "gh_cli"

    def test_token_source_none(self, monkeypatch):
        """Should return None when no source has token."""
        monkeypatch.delenv("NOTION_TOKEN", raising=False)

        manager = SecretManager()
        manager._keychain_available = False

        assert manager.get_token_source(ProviderType.NOTION) is None


class TestEnvVarNames:
    """Tests for ENV_VAR_NAMES configuration."""

    def test_all_providers_have_env_var(self):
        """Every provider should have an env var name defined."""
        for provider in ProviderType:
            assert provider in ENV_VAR_NAMES

    def test_env_var_naming_convention(self):
        """Env vars should follow PROVIDER_TOKEN convention."""
        assert ENV_VAR_NAMES[ProviderType.GITHUB] == "GITHUB_TOKEN"
        assert ENV_VAR_NAMES[ProviderType.JIRA] == "JIRA_TOKEN"
        assert ENV_VAR_NAMES[ProviderType.NOTION] == "NOTION_TOKEN"


class TestTokenPatterns:
    """Tests for TOKEN_PATTERNS configuration."""

    def test_all_providers_have_pattern(self):
        """Every provider should have a token pattern defined."""
        for provider in ProviderType:
            assert provider in TOKEN_PATTERNS
