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
