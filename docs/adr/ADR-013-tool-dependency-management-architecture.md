# ADR-013: Tool Dependency Management Architecture

**Status:** Proposed
**Date:** 2025-12-04
**Author:** Platform Engineer
**Context:** task-249 - Tool installation, version management, and caching
**Supersedes:** None
**Amended by:** None

---

## Strategic Context (Penthouse View)

### Business Problem

JP Spec Kit integrates multiple external security and development tools (Semgrep, CodeQL, act, etc.) that require:
- **Installation** - Different methods (pip, npm, binary download, container)
- **Version Management** - Pinning for reproducibility and SLSA compliance
- **Caching** - Avoiding repeated downloads (bandwidth, performance)
- **Offline Support** - Air-gapped environments and CI environments with network restrictions
- **Size Monitoring** - Tool caches can grow unbounded (500MB+ alert threshold)

**The Core Tension:** Developers want tools to "just work" without manual installation, but we must balance:
1. **Automatic installation** vs **explicit control**
2. **Latest versions** vs **version pinning** (reproducibility)
3. **Performance** (cache everything) vs **disk usage** (minimal footprint)

### Business Value

**Primary Value Streams:**

1. **Developer Productivity** - One-time setup, tools auto-install on first use
2. **Reproducibility** - Version pinning ensures consistent results across environments
3. **Compliance** - SLSA Level 2 requires version tracking for all dependencies
4. **Operational Excellence** - Offline mode enables air-gapped deployments

**Success Metrics:**

- Tool installation success rate >95% (first-run experience)
- Cache hit rate >80% (avoid redundant downloads)
- Zero manual intervention for standard tool installations
- Support for offline/air-gapped environments

---

## Decision

### Chosen Architecture: Layered Tool Resolution with Smart Caching

Implement a **Tool Dependency Manager** that:
1. Discovers tools across multiple sources (PATH → venv → cache → download)
2. Manages tool lifecycle (install, upgrade, version pinning, cleanup)
3. Implements intelligent caching with size monitoring
4. Supports offline mode (use cached tools only, no network)
5. Tracks tool versions for SLSA attestation

**Key Pattern:** **Chain of Responsibility (Discovery)** + **Strategy Pattern (Installation)** + **Cache-Aside Pattern (Caching)**

```
┌─────────────────────────────────────────────────────────────────┐
│                 TOOL DEPENDENCY MANAGER                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │ 1. Tool Discovery (PATH → venv → cache)           │         │
│  │ 2. Version Resolution (pinned → latest)           │         │
│  │ 3. Installation Strategy (pip/npm/binary)         │         │
│  │ 4. Cache Management (size monitoring, eviction)   │         │
│  │ 5. Offline Mode Support                           │         │
│  └────────────────────────────────────────────────────┘         │
│                          │                                       │
│              ┌───────────┼───────────┬───────────┐              │
│              │           │           │           │              │
│         ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌───▼────┐         │
│         │  Pip    │ │  Npm    │ │ Binary  │ │ Custom │         │
│         │Installer│ │Installer│ │Downloader│ │Installer│        │
│         └────┬────┘ └────┬────┘ └────┬────┘ └───┬────┘         │
│              │           │           │           │              │
└──────────────┼───────────┼───────────┼───────────┼──────────────┘
               │           │           │           │
         ┌─────▼─────┐┌────▼─────┐┌───▼──────┐┌───▼──────┐
         │~/.specify/││~/.specify/││~/.specify/││~/.specify/│
         │ tools/    ││ cache/   ││ versions/││ metadata/│
         │ semgrep   ││ codeql   ││ lock.json││ stats    │
         └───────────┘└──────────┘└──────────┘└──────────┘
```

---

## Engine Room View: Technical Architecture

### Component Design

#### 1. ToolDependencyManager (Core Component)

**Responsibilities:**
- Coordinate tool discovery, installation, and lifecycle management
- Manage tool cache (storage, eviction, size monitoring)
- Track tool versions for SLSA compliance
- Support offline mode

**Interface:**
```python
from pathlib import Path
from typing import Protocol
from dataclasses import dataclass
from enum import Enum

class ToolSource(Enum):
    """Where a tool was found."""
    SYSTEM_PATH = "system_path"
    PROJECT_VENV = "project_venv"
    SPECIFY_CACHE = "specify_cache"
    DOWNLOADED = "downloaded"
    NOT_FOUND = "not_found"

@dataclass
class ToolInfo:
    """Information about an installed tool."""
    name: str
    version: str
    path: Path
    source: ToolSource
    size_bytes: int
    installed_at: str  # ISO timestamp
    last_used: str     # ISO timestamp

@dataclass
class ToolConfig:
    """Configuration for tool management."""
    cache_dir: Path = Path.home() / ".specify" / "tools"
    max_cache_size_mb: int = 500
    allow_downloads: bool = True
    version_pinning: dict[str, str] = None  # tool_name -> version
    offline_mode: bool = False

class ToolDependencyManager:
    """Manages tool dependencies with smart caching."""

    def __init__(self, config: ToolConfig):
        self.config = config
        self.metadata = self._load_metadata()
        self._ensure_cache_dir()

    def get_tool(self, name: str, required_version: str = None) -> ToolInfo:
        """Get tool path, installing if necessary.

        Args:
            name: Tool name (e.g., "semgrep", "act")
            required_version: Optional version constraint (e.g., "1.45.0")

        Returns:
            ToolInfo with path and metadata.

        Raises:
            ToolNotFoundError: If tool unavailable and downloads disabled.
            VersionMismatchError: If installed version doesn't match requirement.
            OfflineModeError: If offline mode enabled and tool not cached.
        """
        # 1. Discover tool
        tool_info = self._discover_tool(name)

        if tool_info.source == ToolSource.NOT_FOUND:
            if self.config.offline_mode:
                raise OfflineModeError(f"{name} not available in offline mode")

            if not self.config.allow_downloads:
                raise ToolNotFoundError(f"{name} not found and downloads disabled")

            # Download and install
            tool_info = self._install_tool(name, required_version)

        # 2. Validate version
        if required_version and tool_info.version != required_version:
            if self.config.offline_mode:
                raise VersionMismatchError(
                    f"{name} version {tool_info.version} != {required_version}"
                )
            # Try to install correct version
            tool_info = self._install_tool(name, required_version)

        # 3. Update metadata
        self._update_last_used(name)

        return tool_info

    def _discover_tool(self, name: str) -> ToolInfo:
        """Discover tool using fallback chain.

        1. System PATH
        2. Project venv
        3. Specify cache (~/.specify/tools/)
        4. NOT_FOUND
        """
        # 1. System PATH
        system_path = shutil.which(name)
        if system_path:
            return ToolInfo(
                name=name,
                version=self._get_version(system_path),
                path=Path(system_path),
                source=ToolSource.SYSTEM_PATH,
                size_bytes=Path(system_path).stat().st_size,
                installed_at=self._get_install_time(system_path),
                last_used=datetime.now().isoformat(),
            )

        # 2. Project venv
        venv_path = Path.cwd() / ".venv" / "bin" / name
        if venv_path.exists():
            return ToolInfo(
                name=name,
                version=self._get_version(venv_path),
                path=venv_path,
                source=ToolSource.PROJECT_VENV,
                size_bytes=venv_path.stat().st_size,
                installed_at=self._get_install_time(venv_path),
                last_used=datetime.now().isoformat(),
            )

        # 3. Specify cache
        cache_path = self.config.cache_dir / name / "bin" / name
        if cache_path.exists():
            return ToolInfo(
                name=name,
                version=self._get_version(cache_path),
                path=cache_path,
                source=ToolSource.SPECIFY_CACHE,
                size_bytes=self._get_dir_size(cache_path.parent.parent),
                installed_at=self._get_install_time(cache_path),
                last_used=datetime.now().isoformat(),
            )

        # 4. Not found
        return ToolInfo(
            name=name,
            version="",
            path=None,
            source=ToolSource.NOT_FOUND,
            size_bytes=0,
            installed_at="",
            last_used="",
        )

    def _install_tool(self, name: str, version: str = None) -> ToolInfo:
        """Install tool using appropriate strategy.

        Strategies:
        - semgrep: pip install semgrep==<version>
        - act: binary download from GitHub releases
        - codeql: binary download + license check
        """
        strategy = self._get_install_strategy(name)

        # Check cache size before installation
        cache_size_mb = self._get_cache_size_mb()
        if cache_size_mb > self.config.max_cache_size_mb:
            logger.warning(
                f"Cache size ({cache_size_mb}MB) exceeds threshold "
                f"({self.config.max_cache_size_mb}MB)"
            )
            self._evict_oldest_tools()

        # Install tool
        install_path = strategy.install(name, version, self.config.cache_dir)

        return ToolInfo(
            name=name,
            version=version or self._get_version(install_path),
            path=install_path,
            source=ToolSource.DOWNLOADED,
            size_bytes=self._get_dir_size(install_path.parent.parent),
            installed_at=datetime.now().isoformat(),
            last_used=datetime.now().isoformat(),
        )

    def check_cache_size(self) -> dict:
        """Check cache size and return statistics.

        Returns:
            {
                "total_size_mb": 350,
                "tool_count": 5,
                "tools": [{"name": "semgrep", "size_mb": 120}, ...],
                "exceeds_threshold": False
            }
        """
        tools = []
        total_size = 0

        for tool_dir in self.config.cache_dir.iterdir():
            if tool_dir.is_dir():
                size = self._get_dir_size(tool_dir)
                total_size += size
                tools.append({
                    "name": tool_dir.name,
                    "size_mb": round(size / 1024 / 1024, 2),
                })

        total_size_mb = round(total_size / 1024 / 1024, 2)

        return {
            "total_size_mb": total_size_mb,
            "tool_count": len(tools),
            "tools": sorted(tools, key=lambda x: x["size_mb"], reverse=True),
            "exceeds_threshold": total_size_mb > self.config.max_cache_size_mb,
        }

    def _evict_oldest_tools(self) -> None:
        """Evict least recently used tools until under threshold.

        Uses LRU eviction policy based on last_used timestamp.
        """
        tools_by_last_used = sorted(
            self.metadata["tools"].items(),
            key=lambda x: x[1]["last_used"]
        )

        cache_size_mb = self._get_cache_size_mb()

        for tool_name, tool_meta in tools_by_last_used:
            if cache_size_mb <= self.config.max_cache_size_mb:
                break

            # Evict tool
            tool_dir = self.config.cache_dir / tool_name
            if tool_dir.exists():
                logger.info(f"Evicting {tool_name} (LRU policy)")
                shutil.rmtree(tool_dir)
                cache_size_mb -= tool_meta["size_mb"]
                del self.metadata["tools"][tool_name]

        self._save_metadata()
```

#### 2. InstallStrategy (Interface)

**Pattern:** Strategy Pattern (different installation methods per tool)

```python
from abc import ABC, abstractmethod

class InstallStrategy(ABC):
    """Abstract base class for tool installation strategies."""

    @abstractmethod
    def install(self, tool: str, version: str, cache_dir: Path) -> Path:
        """Install tool and return path to executable.

        Args:
            tool: Tool name (e.g., "semgrep")
            version: Version to install (or None for latest)
            cache_dir: Directory for cached tools

        Returns:
            Path to installed executable.

        Raises:
            InstallationError: If installation fails.
        """
        pass

    @abstractmethod
    def get_latest_version(self, tool: str) -> str:
        """Get latest version number for tool.

        Returns:
            Version string (e.g., "1.45.0").
        """
        pass
```

#### 3. PipInstallStrategy (Semgrep Implementation)

```python
import subprocess
import sys

class PipInstallStrategy(InstallStrategy):
    """Install Python tools via pip."""

    def install(self, tool: str, version: str, cache_dir: Path) -> Path:
        """Install tool via pip to cache directory.

        Uses `pip install --target` to isolate tools.
        """
        target_dir = cache_dir / tool
        target_dir.mkdir(parents=True, exist_ok=True)

        package = f"{tool}=={version}" if version else tool

        cmd = [
            sys.executable, "-m", "pip", "install",
            "--target", str(target_dir),
            "--no-warn-script-location",
            package
        ]

        logger.info(f"Installing {package} via pip...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise InstallationError(f"pip install failed: {result.stderr}")

        # Find executable
        bin_path = target_dir / "bin" / tool
        if not bin_path.exists():
            # Try alternate locations
            bin_path = target_dir / tool

        if not bin_path.exists():
            raise InstallationError(f"Could not find {tool} executable after install")

        # Make executable
        bin_path.chmod(0o755)

        return bin_path

    def get_latest_version(self, tool: str) -> str:
        """Get latest version from PyPI."""
        import json
        import urllib.request

        url = f"https://pypi.org/pypi/{tool}/json"
        with urllib.request.urlopen(url) as response:
            data = json.load(response)
            return data["info"]["version"]
```

#### 4. BinaryDownloadStrategy (CodeQL, act Implementation)

```python
import platform
import tarfile
import zipfile
import urllib.request

class BinaryDownloadStrategy(InstallStrategy):
    """Download pre-built binaries from GitHub releases."""

    def __init__(self, github_repo: str):
        """Initialize with GitHub repository.

        Args:
            github_repo: Format "owner/repo" (e.g., "github/codeql-cli-binaries")
        """
        self.github_repo = github_repo

    def install(self, tool: str, version: str, cache_dir: Path) -> Path:
        """Download and extract binary from GitHub release."""
        target_dir = cache_dir / tool / version
        target_dir.mkdir(parents=True, exist_ok=True)

        # Get download URL for platform
        download_url = self._get_download_url(version)

        logger.info(f"Downloading {tool} {version} from {download_url}...")

        # Download
        archive_path = target_dir / "download.tar.gz"
        urllib.request.urlretrieve(download_url, archive_path)

        # Extract
        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path) as zf:
                zf.extractall(target_dir)
        else:
            with tarfile.open(archive_path) as tf:
                tf.extractall(target_dir)

        # Find executable
        bin_path = self._find_executable(target_dir, tool)
        if not bin_path:
            raise InstallationError(f"Could not find {tool} executable in archive")

        # Make executable
        bin_path.chmod(0o755)

        # Cleanup archive
        archive_path.unlink()

        return bin_path

    def _get_download_url(self, version: str) -> str:
        """Get download URL for current platform."""
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Map to GitHub release naming conventions
        os_name = {"darwin": "macos", "linux": "linux", "windows": "win64"}[system]
        arch = {"x86_64": "x64", "amd64": "x64", "arm64": "arm64"}[machine]

        # Construct URL (varies by tool)
        if self.github_repo == "github/codeql-cli-binaries":
            return (
                f"https://github.com/{self.github_repo}/releases/download/"
                f"v{version}/codeql-{os_name}-{arch}.tar.gz"
            )
        elif self.github_repo == "nektos/act":
            return (
                f"https://github.com/{self.github_repo}/releases/download/"
                f"v{version}/act_{os_name}_{arch}.tar.gz"
            )

        raise ValueError(f"Unknown binary source: {self.github_repo}")

    def get_latest_version(self, tool: str) -> str:
        """Get latest version from GitHub API."""
        import json
        import urllib.request

        url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")

        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            # Remove 'v' prefix if present
            return data["tag_name"].lstrip("v")
```

### Tool Registry

**Registry Pattern** for tool-to-strategy mapping:

```python
class ToolRegistry:
    """Registry of available tools and their installation strategies."""

    TOOLS = {
        "semgrep": {
            "strategy": PipInstallStrategy(),
            "default_version": "1.95.0",
            "license": "LGPL-2.1",
            "required_for": ["security scanning"],
        },
        "codeql": {
            "strategy": BinaryDownloadStrategy("github/codeql-cli-binaries"),
            "default_version": "2.15.5",
            "license": "Proprietary (free for research/OSS)",
            "license_check": True,  # Require license acceptance
            "required_for": ["security scanning"],
        },
        "act": {
            "strategy": BinaryDownloadStrategy("nektos/act"),
            "default_version": "0.2.68",
            "license": "MIT",
            "required_for": ["local CI simulation"],
        },
    }

    @classmethod
    def get_strategy(cls, tool: str) -> InstallStrategy:
        """Get installation strategy for tool."""
        if tool not in cls.TOOLS:
            raise ValueError(f"Unknown tool: {tool}")
        return cls.TOOLS[tool]["strategy"]

    @classmethod
    def get_default_version(cls, tool: str) -> str:
        """Get default/recommended version for tool."""
        if tool not in cls.TOOLS:
            raise ValueError(f"Unknown tool: {tool}")
        return cls.TOOLS[tool]["default_version"]

    @classmethod
    def requires_license_check(cls, tool: str) -> bool:
        """Check if tool requires license acceptance."""
        if tool not in cls.TOOLS:
            return False
        return cls.TOOLS[tool].get("license_check", False)
```

### Version Pinning File

**Format:** `~/.specify/versions.lock.json`

```json
{
  "version": "1",
  "generated": "2025-12-04T10:00:00Z",
  "tools": {
    "semgrep": {
      "version": "1.95.0",
      "source": "pypi",
      "integrity": "sha256:abc123...",
      "installed_at": "2025-12-04T09:00:00Z"
    },
    "codeql": {
      "version": "2.15.5",
      "source": "github/codeql-cli-binaries",
      "integrity": "sha256:def456...",
      "installed_at": "2025-12-04T09:05:00Z"
    },
    "act": {
      "version": "0.2.68",
      "source": "github/nektos/act",
      "integrity": "sha256:ghi789...",
      "installed_at": "2025-12-04T09:10:00Z"
    }
  }
}
```

---

## Platform Quality Assessment (7 C's)

### 1. Clarity - 9/10

**Strengths:**
- Clear separation: Manager coordinates, Strategies install, Registry maps
- Discovery chain is explicit and predictable
- Offline mode is first-class (not an afterthought)

**Improvement:**
- Document tool-specific quirks (CodeQL license, etc.)

### 2. Consistency - 10/10

**Strengths:**
- All tools use same discovery chain (PATH → venv → cache)
- All strategies implement same interface (InstallStrategy)
- Version pinning works identically for all tools

### 3. Composability - 10/10

**Strengths:**
- Add new tool = implement InstallStrategy + register
- Strategies are independent (no cross-tool dependencies)
- Cache management is tool-agnostic

**Example:**
```python
# Adding new tool
class NpmInstallStrategy(InstallStrategy):
    # Implement interface methods
    pass

# Register
ToolRegistry.TOOLS["prettier"] = {
    "strategy": NpmInstallStrategy(),
    "default_version": "3.1.0",
    "license": "MIT",
}
```

### 4. Consumption (Developer Experience) - 9/10

**Strengths:**
- Zero-config for standard tools (auto-install on first use)
- Clear error messages when tools unavailable
- Offline mode prevents surprise downloads

**Needs Work:**
- First-run download notifications could be more prominent
- Cache size warnings need actionable guidance (which tools to remove)

### 5. Correctness (Validation) - 9/10

**Strengths:**
- Version pinning ensures reproducibility
- Integrity hashes prevent tampering (SLSA Level 2)
- Timeout prevents hanging downloads

**Risks:**
- Network failures during installation (mitigated by retry + fallback)
- Disk space exhaustion (mitigated by size monitoring + eviction)

### 6. Completeness - 8/10

**Covers:**
- Discovery, installation, version management, caching
- Offline mode, size monitoring, eviction
- SLSA compliance (version tracking, integrity)

**Missing (Future):**
- Automatic version updates with testing
- Tool usage analytics (which tools are actually used?)
- Cross-platform testing automation

### 7. Changeability - 10/10

**Strengths:**
- New installation methods: implement InstallStrategy, no core changes
- Change discovery order: modify _discover_tool, strategies unaffected
- Change cache eviction policy: modify _evict_oldest_tools, no tool impact

---

## Alternatives Considered and Rejected

### Option A: System-Only Tools (No Auto-Install)

**Approach:** Require users to install all tools manually via package managers.

**Pros:**
- Simplest implementation
- No download/caching complexity
- Users have full control

**Cons:**
- Poor developer experience (manual setup for 5+ tools)
- Version mismatches across environments
- No offline support (users must download individually)

**Rejected:** Violates "tools just work" principle

---

### Option B: Container-Based Tools (DevContainer)

**Approach:** Package all tools in Docker container.

**Pros:**
- Guaranteed tool availability
- Consistent environment
- Version pinning built-in

**Cons:**
- Requires Docker (not available in all CI environments)
- Large download (multi-GB container)
- Poor performance (container overhead)

**Rejected:** Over-engineered for CLI tool

---

### Option C: Lazy Download with No Caching (RECOMMENDED)

**Approach:** Download tools on first use, cache locally, smart eviction.

**Pros:**
- Balance of automation and control
- Offline mode supported
- Minimal disk usage (LRU eviction)
- SLSA compliance (version tracking)

**Cons:**
- More complex than Option A
- Network dependency (mitigated by offline mode)

**Accepted:** Best balance of UX and operational requirements

---

## Implementation Guidance

### Phase 1: Core Manager (Week 1)

**Scope:** Tool discovery + Semgrep pip installation

```bash
src/specify_cli/tools/
├── __init__.py
├── manager.py           # ToolDependencyManager
├── strategies/
│   ├── __init__.py
│   ├── base.py         # InstallStrategy interface
│   └── pip.py          # PipInstallStrategy
├── registry.py         # ToolRegistry
└── models.py           # ToolInfo, ToolConfig
```

**Tasks:**
- Implement ToolDependencyManager
- Implement PipInstallStrategy (Semgrep)
- Implement discovery chain
- Unit tests with mocked pip

### Phase 2: Multi-Strategy Support (Week 2)

**Scope:** Binary downloads (CodeQL, act)

```bash
src/specify_cli/tools/strategies/
├── binary.py           # BinaryDownloadStrategy
└── npm.py              # NpmInstallStrategy (future)
```

**Tasks:**
- Implement BinaryDownloadStrategy
- Add CodeQL and act to ToolRegistry
- Implement license check (CodeQL)
- Integration tests with real downloads

### Phase 3: Cache Management (Week 3)

**Scope:** Size monitoring, eviction, offline mode

**Tasks:**
- Implement cache size monitoring
- Implement LRU eviction policy
- Implement offline mode
- Implement versions.lock.json
- Documentation and examples

---

## Risks and Mitigations

### Risk 1: Network Failures During Installation

**Likelihood:** Medium
**Impact:** High (blocks tool usage)

**Mitigation:**
- Retry logic with exponential backoff (3 attempts)
- Clear error messages with manual installation instructions
- Offline mode allows pre-installed tools
- Fallback to system tools if available

### Risk 2: Disk Space Exhaustion

**Likelihood:** Low
**Impact:** Medium (installation failures)

**Mitigation:**
- Size monitoring with 500MB alert threshold
- LRU eviction policy (automatic cleanup)
- User notification before large downloads
- Manual cleanup command (`specify tools clean`)

### Risk 3: Version Incompatibilities

**Likelihood:** Medium
**Impact:** Medium (tool failures)

**Mitigation:**
- Version pinning prevents automatic upgrades
- Integrity hashes detect corrupted downloads
- Test suite validates tool compatibility
- Rollback mechanism (reinstall previous version)

---

## Success Criteria

**Objective Measures:**

1. **Installation Success Rate** - >95% (first-run installation)
2. **Cache Hit Rate** - >80% (avoid redundant downloads)
3. **Offline Mode Support** - 100% (all tools work offline if cached)
4. **Cache Size Management** - Zero uncontrolled growth incidents

**Subjective Measures:**

1. **Developer Feedback** - "Tools just work" (NPS >40)
2. **Reduced Setup Time** - <5 minutes for full tool suite

---

## Decision

**APPROVED for implementation as Option C: Lazy Download with Smart Caching**

**Next Steps:**

1. Create implementation task for Phase 1 (Semgrep pip installation)
2. Design versions.lock.json schema
3. Begin development in `src/specify_cli/tools/`

**Review Date:** 2025-12-18 (after Phase 1 complete)

---

## References

### Design Patterns Applied

1. **Chain of Responsibility (GoF)** - Tool discovery fallback chain
2. **Strategy Pattern (GoF)** - InstallStrategy for different installation methods
3. **Registry Pattern** - ToolRegistry for tool-to-strategy mapping
4. **Cache-Aside Pattern** - Local tool caching with fallback to download

### Related Documents

- **Task:** task-249 - Implement Tool Dependency Management Module
- **Related ADRs:** ADR-005 (Scanner Orchestration Pattern)

### External References

- [SLSA Framework](https://slsa.dev/)
- [Python Packaging Guide](https://packaging.python.org/en/latest/)
- [GitHub Releases API](https://docs.github.com/en/rest/releases)

---

*This ADR follows Gregor Hohpe's architectural philosophy: strategic framing (why), engine room details (how), quality assessment (verification), and alternatives considered (decision rationale).*
