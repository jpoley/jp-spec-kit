"""Abstract base class for remote task providers."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterator, List, Optional

from .enums import ProviderType
from .entities import (
    ConnectionStatus,
    RateLimitStatus,
    RemotePullRequest,
    RemoteTask,
    RemoteUser,
    TaskCreate,
    TaskHistoryEntry,
    TaskUpdate,
)


class RemoteProvider(ABC):
    """
    Abstract base class for remote task providers.

    All providers must implement this interface to integrate
    with the Satellite Mode sync engine. Implementations include
    GitHub, Jira, and Notion providers.

    Example:
        class GitHubProvider(RemoteProvider):
            def __init__(self, config: dict):
                self._token = config.get("token")
                self._owner = config.get("owner")
                self._repo = config.get("repo")

            @property
            def provider_type(self) -> ProviderType:
                return ProviderType.GITHUB

            # ... implement other methods
    """

    # ===================
    # Provider Metadata
    # ===================

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """
        Return the provider type identifier.

        Returns:
            ProviderType enum value for this provider
        """
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Human-readable provider name.

        Returns:
            Display name like "GitHub" or "Jira Cloud"
        """
        ...

    @property
    @abstractmethod
    def id_pattern(self) -> str:
        """
        Regex pattern to match task IDs for this provider.

        Used for auto-detection of provider from task ID format.

        Returns:
            Regex pattern string

        Examples:
            GitHub: r'^[\\w.-]+/[\\w.-]+#\\d+$'  # owner/repo#123
            Jira: r'^[A-Z][A-Z0-9]*-\\d+$'       # PROJ-123
            Notion: r'^[a-f0-9-]{36}$'           # UUID format
        """
        ...

    # ===================
    # Authentication
    # ===================

    @abstractmethod
    def authenticate(self, token: str) -> bool:
        """
        Validate authentication token.

        Args:
            token: API token or credential string

        Returns:
            True if authentication succeeds

        Raises:
            AuthenticationError: If token is invalid or expired
        """
        ...

    @abstractmethod
    def get_current_user(self) -> RemoteUser:
        """
        Get the authenticated user's information.

        Returns:
            RemoteUser with current user details

        Raises:
            AuthenticationError: If not authenticated
        """
        ...

    # ===================
    # Task Operations (US-1, US-2)
    # ===================

    @abstractmethod
    def get_task(self, task_id: str) -> RemoteTask:
        """
        Fetch a single task by ID.

        Args:
            task_id: Provider-specific task identifier
                     (e.g., "owner/repo#123" for GitHub, "PROJ-123" for Jira)

        Returns:
            RemoteTask with all available fields populated

        Raises:
            TaskNotFoundError: If task doesn't exist
            PermissionDeniedError: If user lacks read access
            RateLimitError: If rate limit exceeded
        """
        ...

    @abstractmethod
    def list_tasks(
        self,
        assignee: Optional[str] = None,
        status: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        updated_since: Optional[datetime] = None,
        limit: int = 100,
    ) -> Iterator[RemoteTask]:
        """
        List tasks matching filters.

        Args:
            assignee: Filter by assignee username (None = current user)
            status: Filter by status values (provider-specific)
            labels: Filter by labels/tags
            updated_since: Only tasks updated after this timestamp
            limit: Maximum number of tasks to return

        Yields:
            RemoteTask objects matching the criteria

        Raises:
            PermissionDeniedError: If user lacks list access
            RateLimitError: If rate limit exceeded
        """
        ...

    @abstractmethod
    def update_task(
        self,
        task_id: str,
        updates: TaskUpdate,
    ) -> RemoteTask:
        """
        Update a remote task.

        Args:
            task_id: Provider-specific task identifier
            updates: TaskUpdate with fields to modify

        Returns:
            Updated RemoteTask with new values

        Raises:
            TaskNotFoundError: If task doesn't exist
            ValidationError: If updates are invalid
            ConflictError: If remote was modified since last read
            PermissionDeniedError: If user lacks write access
        """
        ...

    @abstractmethod
    def create_task(self, task: TaskCreate) -> RemoteTask:
        """
        Create a new task on remote.

        Args:
            task: TaskCreate with required fields

        Returns:
            Created RemoteTask with assigned ID and URL

        Raises:
            ValidationError: If required fields are missing
            PermissionDeniedError: If user lacks create access
        """
        ...

    # ===================
    # PR Operations (US-3)
    # ===================

    @abstractmethod
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        draft: bool = False,
    ) -> RemotePullRequest:
        """
        Create a pull request.

        Only implemented by GitHub provider. Other providers
        should raise NotImplementedError.

        Args:
            title: PR title
            body: PR body (spec content injected here)
            head_branch: Source branch name
            base_branch: Target branch name (default: main)
            draft: Create as draft PR

        Returns:
            Created RemotePullRequest with URL

        Raises:
            NotImplementedError: If provider doesn't support PRs
            ValidationError: If branches don't exist
            PermissionDeniedError: If user lacks PR create access
        """
        ...

    @abstractmethod
    def link_pr_to_task(
        self,
        task_id: str,
        pr_url: str,
    ) -> None:
        """
        Link a PR to a task.

        Creates a reference/comment on the task pointing to the PR.

        Args:
            task_id: Provider-specific task identifier
            pr_url: URL of the pull request

        Raises:
            TaskNotFoundError: If task doesn't exist
            PermissionDeniedError: If user lacks comment access
        """
        ...

    # ===================
    # History/Compliance (US-4)
    # ===================

    @abstractmethod
    def get_task_history(
        self,
        task_id: str,
        since: Optional[datetime] = None,
    ) -> List[TaskHistoryEntry]:
        """
        Get audit history for a task.

        Args:
            task_id: Provider-specific task identifier
            since: Only changes after this timestamp

        Returns:
            List of TaskHistoryEntry objects in chronological order

        Raises:
            TaskNotFoundError: If task doesn't exist
            PermissionDeniedError: If user lacks read access
        """
        ...

    # ===================
    # Connection Utilities
    # ===================

    @abstractmethod
    def test_connection(self) -> ConnectionStatus:
        """
        Test provider connectivity and authentication.

        Returns:
            ConnectionStatus with connection details and latency
        """
        ...

    @abstractmethod
    def get_rate_limit_status(self) -> RateLimitStatus:
        """
        Get current rate limit status.

        Returns:
            RateLimitStatus with remaining quota and reset time
        """
        ...
