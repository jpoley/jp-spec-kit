"""Tests for multi-agent installation support."""

from flowspec_cli import parse_agent_list, AGENT_CONFIG


class TestParseAgentList:
    """Test suite for parse_agent_list() function."""

    def test_single_agent(self):
        """Test parsing single agent."""
        result = parse_agent_list("claude")
        assert result == ["claude"]

    def test_multiple_agents_no_spaces(self):
        """Test parsing multiple agents without spaces."""
        result = parse_agent_list("claude,copilot,gemini")
        assert result == ["claude", "copilot", "gemini"]

    def test_multiple_agents_with_spaces(self):
        """Test parsing multiple agents with spaces around commas."""
        result = parse_agent_list("claude, copilot, gemini")
        assert result == ["claude", "copilot", "gemini"]

    def test_multiple_agents_mixed_spacing(self):
        """Test parsing with inconsistent spacing."""
        result = parse_agent_list("claude,copilot , gemini,  cursor-agent")
        assert result == ["claude", "copilot", "gemini", "cursor-agent"]

    def test_empty_string(self):
        """Test parsing empty string."""
        result = parse_agent_list("")
        assert result == []

    def test_whitespace_only(self):
        """Test parsing whitespace-only string."""
        result = parse_agent_list("   ")
        assert result == []

    def test_trailing_comma(self):
        """Test parsing with trailing comma."""
        result = parse_agent_list("claude,copilot,")
        assert result == ["claude", "copilot"]

    def test_leading_comma(self):
        """Test parsing with leading comma."""
        result = parse_agent_list(",claude,copilot")
        assert result == ["claude", "copilot"]

    def test_multiple_consecutive_commas(self):
        """Test parsing with multiple consecutive commas."""
        result = parse_agent_list("claude,,copilot")
        assert result == ["claude", "copilot"]

    def test_all_supported_agents(self):
        """Test parsing all supported agents."""
        all_agents = ",".join(AGENT_CONFIG.keys())
        result = parse_agent_list(all_agents)
        assert result == list(AGENT_CONFIG.keys())

    def test_duplicate_agents(self):
        """Test that duplicate agents are removed while preserving order."""
        result = parse_agent_list("claude,copilot,claude")
        assert result == ["claude", "copilot"]  # Deduplicated

    def test_multiple_duplicates(self):
        """Test deduplication with multiple duplicate agents."""
        result = parse_agent_list("claude,copilot,claude,gemini,copilot")
        assert result == ["claude", "copilot", "gemini"]  # First occurrence preserved


class TestMultiAgentValidation:
    """Test validation of multi-agent combinations."""

    def test_valid_single_agent(self):
        """Test validation of single valid agent."""
        agents = ["claude"]
        invalid = [a for a in agents if a not in AGENT_CONFIG]
        assert invalid == []

    def test_valid_multiple_agents(self):
        """Test validation of multiple valid agents."""
        agents = ["claude", "copilot", "cursor-agent"]
        invalid = [a for a in agents if a not in AGENT_CONFIG]
        assert invalid == []

    def test_invalid_single_agent(self):
        """Test validation of invalid agent."""
        agents = ["invalid-agent"]
        invalid = [a for a in agents if a not in AGENT_CONFIG]
        assert invalid == ["invalid-agent"]

    def test_mixed_valid_invalid(self):
        """Test validation of mixed valid and invalid agents."""
        agents = ["claude", "invalid", "copilot"]
        invalid = [a for a in agents if a not in AGENT_CONFIG]
        assert invalid == ["invalid"]

    def test_all_agents_valid(self):
        """Test that all configured agents are recognized as valid."""
        for agent in AGENT_CONFIG.keys():
            agents = [agent]
            invalid = [a for a in agents if a not in AGENT_CONFIG]
            assert invalid == [], f"Agent {agent} should be valid"


class TestAgentCombinations:
    """Test common multi-agent combinations."""

    def test_claude_copilot_combination(self):
        """Test Claude + Copilot combination."""
        agents = parse_agent_list("claude,copilot")
        assert "claude" in agents
        assert "copilot" in agents
        assert len(agents) == 2

    def test_claude_cursor_copilot_combination(self):
        """Test Claude + Cursor + Copilot combination."""
        agents = parse_agent_list("claude,cursor-agent,copilot")
        assert "claude" in agents
        assert "cursor-agent" in agents
        assert "copilot" in agents
        assert len(agents) == 3

    def test_all_cli_agents(self):
        """Test combination of all CLI-based agents."""
        cli_agents = [
            agent
            for agent, config in AGENT_CONFIG.items()
            if config.get("requires_cli")
        ]
        agent_str = ",".join(cli_agents)
        result = parse_agent_list(agent_str)
        assert result == cli_agents

    def test_all_ide_agents(self):
        """Test combination of all IDE-based agents."""
        ide_agents = [
            agent
            for agent, config in AGENT_CONFIG.items()
            if not config.get("requires_cli")
        ]
        agent_str = ",".join(ide_agents)
        result = parse_agent_list(agent_str)
        assert result == ide_agents


class TestBackwardCompatibility:
    """Test backward compatibility with single-agent usage."""

    def test_single_agent_string_normalized_to_list(self):
        """Test that single agent string is normalized to list internally."""
        # This simulates the normalization logic in download functions
        ai_assistants = "claude"
        if isinstance(ai_assistants, str):
            ai_assistants = [ai_assistants]
        assert isinstance(ai_assistants, list)
        assert ai_assistants == ["claude"]

    def test_list_with_single_agent(self):
        """Test list containing single agent."""
        ai_assistants = ["claude"]
        assert isinstance(ai_assistants, list)
        assert len(ai_assistants) == 1
        assert ai_assistants[0] == "claude"

    def test_multiple_agents_list(self):
        """Test list containing multiple agents."""
        ai_assistants = ["claude", "copilot"]
        assert isinstance(ai_assistants, list)
        assert len(ai_assistants) == 2


class TestAgentFolders:
    """Test agent folder handling for multiple agents."""

    def test_single_agent_folder(self):
        """Test getting folder for single agent."""
        agent = "claude"
        config = AGENT_CONFIG.get(agent)
        assert config is not None
        assert "folder" in config
        assert config["folder"] == ".claude/"

    def test_multiple_agent_folders_unique(self):
        """Test that multiple agents have unique folders."""
        agents = ["claude", "copilot", "cursor-agent"]
        folders = []
        for agent in agents:
            config = AGENT_CONFIG.get(agent)
            assert config is not None
            folder = config["folder"]
            assert folder not in folders, f"Duplicate folder {folder}"
            folders.append(folder)

    def test_all_agent_folders_unique(self):
        """Test that all agents have unique folders (no conflicts)."""
        all_folders = set()
        for agent, config in AGENT_CONFIG.items():
            folder = config["folder"]
            assert folder not in all_folders, (
                f"Agent {agent} has duplicate folder {folder}"
            )
            all_folders.add(folder)


class TestToolChecks:
    """Test CLI tool checking for multiple agents."""

    def test_identify_cli_agents(self):
        """Test identification of CLI-based agents."""
        agents = ["claude", "gemini", "copilot"]
        cli_agents = [
            agent for agent in agents if AGENT_CONFIG.get(agent, {}).get("requires_cli")
        ]
        # Claude and Gemini require CLI, Copilot does not
        assert "claude" in cli_agents
        assert "gemini" in cli_agents
        assert "copilot" not in cli_agents

    def test_identify_ide_agents(self):
        """Test identification of IDE-based agents."""
        agents = ["claude", "copilot", "cursor-agent"]
        ide_agents = [
            agent
            for agent in agents
            if not AGENT_CONFIG.get(agent, {}).get("requires_cli")
        ]
        # Copilot and Cursor are IDE-based
        assert "copilot" in ide_agents
        assert "cursor-agent" in ide_agents
        assert "claude" not in ide_agents

    def test_all_agents_have_cli_flag(self):
        """Test that all agents have requires_cli defined."""
        for agent, config in AGENT_CONFIG.items():
            assert "requires_cli" in config, f"Agent {agent} missing requires_cli flag"
            assert isinstance(config["requires_cli"], bool), (
                f"Agent {agent} requires_cli should be boolean"
            )


class TestMultiAgentDownloadAndExtract:
    """Integration tests for multi-agent download and extraction."""

    def test_extract_zip_to_project_single_agent(self, tmp_path):
        """Test ZIP extraction for single agent."""
        import zipfile
        from flowspec_cli import _extract_zip_to_project

        # Create a mock ZIP with agent-specific directory
        zip_path = tmp_path / "claude.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr(".claude/commands/flow/assess.md", "# Assess")
            zf.writestr(".claude/skills/architect.md", "# Architect")

        # Extract to project
        project_path = tmp_path / "project"
        project_path.mkdir()
        _extract_zip_to_project(zip_path, project_path)

        # Verify extraction
        assert (project_path / ".claude" / "commands" / "flow" / "assess.md").exists()
        assert (project_path / ".claude" / "skills" / "architect.md").exists()

    def test_extract_zip_to_project_with_shared_directories(self, tmp_path):
        """Test ZIP extraction handles shared directories correctly."""
        import zipfile
        from flowspec_cli import _extract_zip_to_project

        # Create first agent's ZIP with shared .flowspec/
        zip1 = tmp_path / "claude.zip"
        with zipfile.ZipFile(zip1, "w") as zf:
            zf.writestr(".claude/commands/flow/assess.md", "# Assess")
            zf.writestr(".flowspec/config.yml", "agent: claude")

        # Create second agent's ZIP with shared .flowspec/
        zip2 = tmp_path / "copilot.zip"
        with zipfile.ZipFile(zip2, "w") as zf:
            zf.writestr(".github/prompts/assess.md", "# Assess")
            zf.writestr(".flowspec/workflow.yml", "version: 1.0")

        # Extract both
        project_path = tmp_path / "project"
        project_path.mkdir()
        _extract_zip_to_project(zip1, project_path)
        _extract_zip_to_project(zip2, project_path)

        # Verify both agents' files exist
        assert (project_path / ".claude" / "commands" / "flow" / "assess.md").exists()
        assert (project_path / ".github" / "prompts" / "assess.md").exists()

        # Verify shared directory has both files (merged)
        assert (project_path / ".flowspec" / "config.yml").exists()
        assert (project_path / ".flowspec" / "workflow.yml").exists()

    def test_extract_zip_with_nested_directory(self, tmp_path):
        """Test ZIP extraction handles nested directory structure."""
        import zipfile
        from flowspec_cli import _extract_zip_to_project

        # Create ZIP with nested directory (github/spec-kit style)
        zip_path = tmp_path / "spec-kit.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            # Nested: spec-kit-v0.0.90/.claude/...
            zf.writestr(
                "spec-kit-v0.0.90/.claude/commands/spec/specify.md", "# Specify"
            )
            zf.writestr("spec-kit-v0.0.90/.flowspec/base.yml", "base: true")

        # Extract
        project_path = tmp_path / "project"
        project_path.mkdir()
        _extract_zip_to_project(zip_path, project_path)

        # Verify nested structure is flattened correctly
        assert (project_path / ".claude" / "commands" / "spec" / "specify.md").exists()
        assert (project_path / ".flowspec" / "base.yml").exists()

    def test_multi_agent_installation_creates_all_directories(
        self, tmp_path, monkeypatch
    ):
        """Test that multi-agent installation creates directories for all agents."""
        import zipfile
        from flowspec_cli import download_and_extract_two_stage

        # Create mock ZIPs for base and extension (2 agents)
        def create_mock_zip(agent):
            """Helper to create mock ZIPs."""
            base_zip = tmp_path / f"{agent}_base.zip"
            ext_zip = tmp_path / f"{agent}_ext.zip"

            if agent == "claude":
                folder = ".claude/"
                subfolder = "commands"
            else:  # copilot
                folder = ".github/"
                subfolder = "prompts"

            with zipfile.ZipFile(base_zip, "w") as zf:
                zf.writestr(
                    f"{folder}{subfolder}/spec/specify.md", f"# {agent} Specify"
                )

            with zipfile.ZipFile(ext_zip, "w") as zf:
                zf.writestr(f"{folder}{subfolder}/flow/assess.md", f"# {agent} Assess")
                zf.writestr(".flowspec/workflow.yml", f"agent: {agent}")

            return base_zip, ext_zip

        # Mock download_template_from_github to return our mock ZIPs
        # In standalone mode, both base and extension use the same repo,
        # so we track calls by order (base first, then extension for each agent)
        call_count = {"base": 0, "ext": 0}
        agents_processed = []
        agent_call_tracker = {}  # Track calls per agent

        def mock_download(
            ai_assistant,
            download_dir,
            *,
            repo_owner=None,
            repo_name=None,
            version=None,
            **kwargs,
        ):
            # Track which call this is for this agent (first=base, second=ext)
            if ai_assistant not in agent_call_tracker:
                agent_call_tracker[ai_assistant] = 0
            agent_call_tracker[ai_assistant] += 1
            call_num = agent_call_tracker[ai_assistant]

            if call_num == 1:
                # First call for this agent = base download
                call_count["base"] += 1
                base_zip, _ = create_mock_zip(ai_assistant)
                metadata = {
                    "release": version or "test",
                    "size": base_zip.stat().st_size,
                }
                return base_zip, metadata
            else:
                # Second call for this agent = extension download
                call_count["ext"] += 1
                _, ext_zip = create_mock_zip(ai_assistant)
                agents_processed.append(ai_assistant)
                metadata = {
                    "release": version or "test",
                    "size": ext_zip.stat().st_size,
                }
                return ext_zip, metadata

        monkeypatch.setattr("flowspec_cli.download_template_from_github", mock_download)

        # Run multi-agent installation
        project_path = tmp_path / "project"
        project_path.mkdir()

        download_and_extract_two_stage(
            project_path=project_path,
            ai_assistants=["claude", "copilot"],
            script_type="sh",
            verbose=False,
            tracker=None,
        )

        # Verify both agents called download twice (base + extension)
        assert call_count["base"] == 2  # Once per agent
        assert call_count["ext"] == 2  # Once per agent

        # Verify both agent directories exist
        assert (project_path / ".claude" / "commands" / "flow" / "assess.md").exists()
        assert (project_path / ".github" / "prompts" / "flow" / "assess.md").exists()

        # Verify shared directory merged correctly (last agent wins)
        assert (project_path / ".flowspec" / "workflow.yml").exists()
        content = (project_path / ".flowspec" / "workflow.yml").read_text()
        assert "copilot" in content  # Last agent's version

    def test_multi_agent_installation_handles_failure_gracefully(
        self, tmp_path, monkeypatch
    ):
        """Test that failure during second agent installation leaves first agent intact."""
        import zipfile
        from flowspec_cli import download_and_extract_two_stage

        # Create mock ZIP for first agent
        claude_base = tmp_path / "claude_base.zip"
        claude_ext = tmp_path / "claude_ext.zip"

        with zipfile.ZipFile(claude_base, "w") as zf:
            zf.writestr(".claude/commands/spec/specify.md", "# Claude Specify")

        with zipfile.ZipFile(claude_ext, "w") as zf:
            zf.writestr(".claude/commands/flow/assess.md", "# Claude Assess")

        # Mock download that succeeds for first agent, fails for second
        # In standalone mode, each agent gets 2 calls (base + ext)
        call_count = [0]
        agent_call_tracker = {}

        def mock_download(
            ai_assistant,
            download_dir,
            *,
            repo_owner=None,
            repo_name=None,
            version=None,
            **kwargs,
        ):
            call_count[0] += 1
            # Track which call this is for this agent (first=base, second=ext)
            if ai_assistant not in agent_call_tracker:
                agent_call_tracker[ai_assistant] = 0
            agent_call_tracker[ai_assistant] += 1
            call_num = agent_call_tracker[ai_assistant]

            if call_count[0] <= 2:  # First agent (base + ext)
                # First call = base, second call = ext
                zip_path = claude_base if call_num == 1 else claude_ext
                metadata = {
                    "release": version or "test",
                    "size": zip_path.stat().st_size,
                }
                return zip_path, metadata
            else:  # Second agent fails
                raise Exception("Download failed for second agent")

        monkeypatch.setattr("flowspec_cli.download_template_from_github", mock_download)

        # Run multi-agent installation (should fail on second agent)
        project_path = tmp_path / "project"
        project_path.mkdir()

        try:
            download_and_extract_two_stage(
                project_path=project_path,
                ai_assistants=["claude", "copilot"],
                script_type="sh",
                verbose=False,
                tracker=None,
            )
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Download failed" in str(e)

        # Verify first agent still installed correctly
        assert (project_path / ".claude" / "commands" / "flow" / "assess.md").exists()
        # Second agent should not exist
        assert not (project_path / ".github").exists()
