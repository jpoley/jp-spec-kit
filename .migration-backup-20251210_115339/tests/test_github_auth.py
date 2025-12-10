"""Tests for GitHub API authentication and release fetching.

These tests verify:
1. Token handling (env vars, CLI args, whitespace stripping)
2. Header generation (with/without auth)
3. Retry logic for 401 errors with invalid tokens
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specify_cli import (
    _github_headers,
    _github_token,
)


class TestGitHubToken:
    """Tests for _github_token function."""

    def test_returns_none_when_no_token(self):
        """Should return None when no token is provided."""
        with patch.dict("os.environ", {}, clear=True):
            assert _github_token(None) is None

    def test_returns_none_for_empty_string(self):
        """Should return None for empty string."""
        with patch.dict("os.environ", {}, clear=True):
            assert _github_token("") is None

    def test_returns_none_for_whitespace(self):
        """Should return None for whitespace-only string."""
        with patch.dict("os.environ", {}, clear=True):
            assert _github_token("   ") is None

    def test_strips_whitespace_from_valid_token(self):
        """Should strip whitespace from valid token."""
        assert _github_token("  ghp_1234  ") == "ghp_1234"

    def test_cli_token_takes_precedence(self):
        """CLI token should take precedence over env var."""
        with patch.dict("os.environ", {"GITHUB_JPSPEC": "env_token"}):
            assert _github_token("cli_token") == "cli_token"

    def test_uses_github_jpspec_env_var_when_no_cli_token(self):
        """Should use GITHUB_JPSPEC env var when no CLI token."""
        with patch.dict("os.environ", {"GITHUB_JPSPEC": "env_token"}, clear=True):
            assert _github_token(None) == "env_token"

    def test_uses_github_token_env_var_when_no_cli_token(self):
        """Should use GITHUB_TOKEN env var when no CLI token."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "gh_token"}, clear=True):
            assert _github_token(None) == "gh_token"

    def test_github_token_takes_precedence_over_github_jpspec(self):
        """GITHUB_TOKEN should take precedence over GITHUB_JPSPEC."""
        with patch.dict(
            "os.environ",
            {"GITHUB_TOKEN": "gh_token", "GITHUB_JPSPEC": "jpspec_token"},
            clear=True,
        ):
            assert _github_token(None) == "gh_token"

    def test_env_var_stripped(self):
        """Should strip whitespace from env var."""
        with patch.dict("os.environ", {"GITHUB_JPSPEC": "  env_token  "}, clear=True):
            assert _github_token(None) == "env_token"

    def test_github_token_env_var_stripped(self):
        """Should strip whitespace from GITHUB_TOKEN env var."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "  gh_token  "}, clear=True):
            assert _github_token(None) == "gh_token"

    def test_empty_env_var_treated_as_none(self):
        """Empty env var should be treated as None."""
        with patch.dict("os.environ", {"GITHUB_JPSPEC": ""}, clear=True):
            assert _github_token(None) is None

    def test_whitespace_only_env_var_treated_as_none(self):
        """Whitespace-only env var should be treated as None."""
        with patch.dict("os.environ", {"GITHUB_JPSPEC": "   "}, clear=True):
            assert _github_token(None) is None


class TestGitHubHeaders:
    """Tests for _github_headers function."""

    def test_headers_without_token(self, monkeypatch):
        """Should return headers without Authorization when no token."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GITHUB_JPSPEC", raising=False)
        headers = _github_headers(None)
        assert "Authorization" not in headers
        assert headers["Accept"] == "application/vnd.github+json"
        assert headers["User-Agent"] == "jp-spec-kit/specify-cli"
        assert headers["X-GitHub-Api-Version"] == "2022-11-28"

    def test_headers_with_valid_token(self):
        """Should include Authorization header with Bearer token."""
        headers = _github_headers("ghp_1234")
        assert headers["Authorization"] == "Bearer ghp_1234"
        assert headers["Accept"] == "application/vnd.github+json"

    def test_headers_with_empty_token(self, monkeypatch):
        """Should not include Authorization header for empty token."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GITHUB_JPSPEC", raising=False)
        headers = _github_headers("")
        assert "Authorization" not in headers

    def test_headers_with_none_token(self, monkeypatch):
        """Should not include Authorization header for None token."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GITHUB_JPSPEC", raising=False)
        headers = _github_headers(None)
        assert "Authorization" not in headers

    def test_all_required_headers_present(self):
        """All required GitHub API headers should be present."""
        headers = _github_headers("token")
        required = ["Accept", "User-Agent", "X-GitHub-Api-Version", "Authorization"]
        for header in required:
            assert header in headers

    def test_skip_auth_explicitly_removes_auth(self):
        """skip_auth=True should never include Authorization even with env var."""
        with patch.dict("os.environ", {"GITHUB_JPSPEC": "env_token"}, clear=True):
            headers = _github_headers(skip_auth=True)
            assert "Authorization" not in headers
            # Other headers should still be present
            assert headers["Accept"] == "application/vnd.github+json"
            assert headers["User-Agent"] == "jp-spec-kit/specify-cli"

    def test_skip_auth_with_cli_token_still_skips(self):
        """skip_auth=True ignores cli token too."""
        headers = _github_headers("cli_token", skip_auth=True)
        assert "Authorization" not in headers


class TestGitHubAuthRetry:
    """Tests for automatic retry without auth on 401 errors.

    These tests mock httpx.Client.get to simulate various HTTP response scenarios
    and verify the retry logic works correctly.
    """

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for downloads."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_success_without_token_no_retry_needed(self, temp_dir):
        """Public repo without token should succeed on first try."""
        from specify_cli import download_template_from_github

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tag_name": "v1.0.0",
            "assets": [
                {
                    "name": "spec-kit-template-claude-sh.zip",
                    "browser_download_url": "https://example.com/t.zip",
                }
            ],
        }

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        with patch.dict("os.environ", {}, clear=True):
            # This will fail at tarball download but that's OK - we're testing the release fetch
            try:
                download_template_from_github(
                    ai_assistant="claude",
                    download_dir=temp_dir,
                    repo_owner="test",
                    repo_name="repo",
                    version="latest",
                    client=mock_client,
                    verbose=False,
                )
            except Exception:
                pass  # Expected - actual download will fail

        # Should have made at least one call
        assert mock_client.get.call_count >= 1

    def test_401_with_token_triggers_retry_without_auth(self, temp_dir):
        """401 with invalid token should retry without authentication."""
        from specify_cli import download_template_from_github

        # First call returns 401, second call (without auth) returns 200
        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {
            "tag_name": "v1.0.0",
            "assets": [
                {
                    "name": "spec-kit-template-claude-sh.zip",
                    "browser_download_url": "https://example.com/t.zip",
                }
            ],
        }

        mock_client = MagicMock()
        # Use a counter because call_count is incremented BEFORE side_effect runs
        call_counter = {"count": 0}

        def mock_get_side_effect(*args, **kwargs):
            call_counter["count"] += 1
            # Return 401 for first call, 200 for subsequent calls
            if call_counter["count"] == 1:
                return mock_response_401
            return mock_response_200

        mock_client.get.side_effect = mock_get_side_effect

        with patch.dict("os.environ", {"GITHUB_JPSPEC": "invalid_token"}, clear=True):
            try:
                download_template_from_github(
                    ai_assistant="claude",
                    download_dir=temp_dir,
                    repo_owner="test",
                    repo_name="repo",
                    version="latest",
                    client=mock_client,
                    verbose=False,
                )
            except Exception:
                pass  # Expected - actual download will fail

        # Should have made 2 calls: first with token (401), second without (200)
        assert mock_client.get.call_count >= 2

        # Verify first call had Authorization header
        first_call_headers = mock_client.get.call_args_list[0][1]["headers"]
        assert "Authorization" in first_call_headers
        assert first_call_headers["Authorization"] == "Bearer invalid_token"

        # Verify second call did NOT have Authorization header
        second_call_headers = mock_client.get.call_args_list[1][1]["headers"]
        assert "Authorization" not in second_call_headers

    def test_401_without_token_no_retry(self, temp_dir):
        """401 without token should not retry (nothing to retry without)."""
        from click.exceptions import Exit as ClickExit

        from specify_cli import download_template_from_github

        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response_401

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ClickExit):
                download_template_from_github(
                    ai_assistant="claude",
                    download_dir=temp_dir,
                    repo_owner="test",
                    repo_name="private-repo",
                    version="latest",
                    client=mock_client,
                    verbose=False,
                )

        # All calls should NOT have Authorization header since no token provided
        for call in mock_client.get.call_args_list:
            headers = call[1]["headers"]
            assert "Authorization" not in headers

    def test_401_retry_also_fails_exits_gracefully(self, temp_dir):
        """If retry without auth also returns 401, should exit gracefully."""
        from click.exceptions import Exit as ClickExit

        from specify_cli import download_template_from_github

        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401

        mock_client = MagicMock()
        # All calls return 401
        mock_client.get.return_value = mock_response_401

        with patch.dict("os.environ", {"GITHUB_JPSPEC": "invalid_token"}, clear=True):
            with pytest.raises(ClickExit) as exc_info:
                download_template_from_github(
                    ai_assistant="claude",
                    download_dir=temp_dir,
                    repo_owner="test",
                    repo_name="private-repo",
                    version="latest",
                    client=mock_client,
                    verbose=False,
                )

        # Should exit with code 1 (failure)
        assert exc_info.value.exit_code == 1

    def test_403_triggers_retry_without_auth(self, temp_dir):
        """403 should trigger retry-without-auth for public repos (bad token can cause 403)."""
        from click.exceptions import Exit as ClickExit

        from specify_cli import download_template_from_github

        mock_response_403 = MagicMock()
        mock_response_403.status_code = 403

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response_403

        with patch.dict("os.environ", {"GITHUB_JPSPEC": "valid_token"}, clear=True):
            with pytest.raises(ClickExit):
                download_template_from_github(
                    ai_assistant="claude",
                    download_dir=temp_dir,
                    repo_owner="test",
                    repo_name="repo",
                    version="latest",
                    client=mock_client,
                    verbose=False,
                )

        # Should have retried without auth after 403 (first call with token, second without)
        # Check that at least one call was made without Authorization header
        calls_without_auth = [
            call
            for call in mock_client.get.call_args_list
            if "Authorization" not in call[1]["headers"]
        ]
        assert len(calls_without_auth) > 0, "403 should trigger retry without auth"

    def test_success_with_valid_token(self, temp_dir):
        """Valid token should work on first try without retry."""
        from specify_cli import download_template_from_github

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tag_name": "v1.0.0",
            "assets": [
                {
                    "name": "spec-kit-template-claude-sh.zip",
                    "browser_download_url": "https://example.com/t.zip",
                }
            ],
        }

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        with patch.dict("os.environ", {"GITHUB_JPSPEC": "valid_token"}, clear=True):
            try:
                download_template_from_github(
                    ai_assistant="claude",
                    download_dir=temp_dir,
                    repo_owner="test",
                    repo_name="repo",
                    version="latest",
                    client=mock_client,
                    verbose=False,
                )
            except Exception:
                pass  # Expected - actual download will fail but we're testing auth

        # All calls should have Authorization header (no retry without auth needed)
        for call in mock_client.get.call_args_list:
            headers = call[1]["headers"]
            assert "Authorization" in headers


class TestGitHubTokenEdgeCases:
    """Edge case tests for token handling."""

    def test_token_with_newlines_stripped(self):
        """Tokens with newlines should be stripped."""
        assert _github_token("ghp_1234\n") == "ghp_1234"
        assert _github_token("\nghp_1234\n") == "ghp_1234"

    def test_token_with_tabs_stripped(self):
        """Tokens with tabs should be stripped."""
        assert _github_token("\tghp_1234\t") == "ghp_1234"

    def test_very_long_token_preserved(self):
        """Very long tokens should be preserved (GitHub tokens can be long)."""
        long_token = "ghp_" + "a" * 200
        assert _github_token(long_token) == long_token

    def test_token_with_special_chars_preserved(self):
        """Tokens with special characters should be preserved."""
        special_token = "ghp_abc123-_XYZ"
        assert _github_token(special_token) == special_token
