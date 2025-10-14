"""
BMAD v6 MCP Server Agent Registry Tests
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import tempfile
import os

from app.services.agent_registry import AgentRegistry, BMadAgent
from app.models.bmad_models import AgentType

@pytest.fixture
def agent_registry():
    """Create agent registry instance."""
    return AgentRegistry()

@pytest.fixture
def sample_agents():
    """Create sample agents for testing."""
    return [
        BMadAgent(
            name="test-analyst",
            description="Test business analyst agent",
            persona="Strategic analyst with testing expertise",
            communication_language="English",
            agent_type=AgentType.SPECIALIST,
            capabilities=["analysis", "research", "reporting"],
            temperature=0.7,
            max_tokens=4000
        ),
        BMadAgent(
            name="test-pm",
            description="Test project manager agent",
            persona="Experienced project manager for testing",
            communication_language="English",
            agent_type=AgentType.SPECIALIST,
            capabilities=["planning", "coordination", "management"],
            temperature=0.6,
            max_tokens=3000
        ),
        BMadAgent(
            name="test-orchestrator",
            description="Test orchestrator agent",
            persona="Master orchestrator for test workflows",
            communication_language="English",
            agent_type=AgentType.ORCHESTRATOR,
            capabilities=["orchestration", "coordination", "routing"],
            temperature=0.5,
            max_tokens=5000
        )
    ]

class TestAgentRegistration:
    """Test agent registration and retrieval."""
    
    @pytest.mark.asyncio
    async def test_register_agent(self, agent_registry, sample_agents):
        """Test agent registration."""
        agent = sample_agents[0]
        
        result = await agent_registry.register_agent(agent)
        assert result is True
        
        retrieved = await agent_registry.get_agent(agent.name)
        assert retrieved is not None
        assert retrieved.name == agent.name
        assert retrieved.description == agent.description
        assert retrieved.agent_type == agent.agent_type
    
    @pytest.mark.asyncio
    async def test_register_multiple_agents(self, agent_registry, sample_agents):
        """Test registering multiple agents."""
        for agent in sample_agents:
            result = await agent_registry.register_agent(agent)
            assert result is True
        
        agents = await agent_registry.list_agents()
        assert len(agents) >= len(sample_agents)
        
        agent_names = [a.name for a in agents]
        for sample_agent in sample_agents:
            assert sample_agent.name in agent_names
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_agent(self, agent_registry):
        """Test retrieving non-existent agent."""
        result = await agent_registry.get_agent("nonexistent-agent")
        assert result is None

class TestAgentInvocation:
    """Test agent invocation."""
    
    @pytest.mark.asyncio
    async def test_invoke_analyst_agent(self, agent_registry, sample_agents):
        """Test invoking analyst agent."""
        agent = sample_agents[0]  # test-analyst
        await agent_registry.register_agent(agent)
        
        response = await agent.invoke(
            prompt="Analyze the market opportunity for this M&A deal",
            context={"industry": "fintech", "deal_size": "50M"}
        )
        
        assert response is not None
        assert "type" in response
        assert "agent" in response
        assert response["agent"] == agent.name
    
    @pytest.mark.asyncio
    async def test_invoke_pm_agent(self, agent_registry, sample_agents):
        """Test invoking project manager agent."""
        agent = sample_agents[1]  # test-pm
        await agent_registry.register_agent(agent)
        
        response = await agent.invoke(
            prompt="Create a project plan for this integration",
            context={"complexity": "high", "timeline": "6 months"}
        )
        
        assert response is not None
        assert "type" in response
        assert response["agent"] == agent.name
    
    @pytest.mark.asyncio
    async def test_invoke_orchestrator_agent(self, agent_registry, sample_agents):
        """Test invoking orchestrator agent."""
        agent = sample_agents[2]  # test-orchestrator
        await agent_registry.register_agent(agent)
        
        response = await agent.invoke(
            prompt="Orchestrate the workflow for this project",
            context={"project_type": "M&A", "scale": "large"}
        )
        
        assert response is not None
        assert "type" in response
        assert response["agent"] == agent.name

class TestAgentCapabilities:
    """Test agent capabilities and behavior."""
    
    @pytest.mark.asyncio
    async def test_agent_workflow_handling(self, sample_agents):
        """Test agent workflow request handling."""
        agent = sample_agents[0]
        
        response = await agent.invoke(
            prompt="Execute the workflow-status workflow",
            context={"project_id": "test-project"}
        )
        
        assert response["type"] == "workflow_guidance"
        assert "next_actions" in response
        assert "bmad_context" in response
    
    @pytest.mark.asyncio
    async def test_agent_analysis_handling(self, sample_agents):
        """Test agent analysis request handling."""
        agent = sample_agents[0]
        
        response = await agent.invoke(
            prompt="Analyze the competitive landscape",
            context={"industry": "fintech"}
        )
        
        assert response["type"] == "analysis_guidance"
        assert "analysis_framework" in response
        assert "next_steps" in response
    
    @pytest.mark.asyncio
    async def test_agent_planning_handling(self, sample_agents):
        """Test agent planning request handling."""
        agent = sample_agents[1]  # PM agent
        
        response = await agent.invoke(
            prompt="Plan the project implementation",
            context={"scope": "large", "team_size": 8}
        )
        
        assert response["type"] == "planning_guidance"
        assert "planning_framework" in response
        assert "scale_assessment" in response["planning_framework"]
    
    @pytest.mark.asyncio
    async def test_agent_general_handling(self, sample_agents):
        """Test agent general request handling."""
        agent = sample_agents[0]
        
        response = await agent.invoke(
            prompt="Help me understand BMAD methodology",
            context={}
        )
        
        assert response["type"] == "general_guidance"
        assert "bmad_approach" in response
        assert "available_capabilities" in response

class TestAgentConfiguration:
    """Test agent configuration management."""
    
    @pytest.mark.asyncio
    async def test_agent_to_dict(self, sample_agents):
        """Test agent dictionary conversion."""
        agent = sample_agents[0]
        
        agent_dict = agent.to_dict()
        
        assert agent_dict["name"] == agent.name
        assert agent_dict["description"] == agent.description
        assert agent_dict["persona"] == agent.persona
        assert agent_dict["agent_type"] == agent.agent_type.value
        assert agent_dict["capabilities"] == agent.capabilities
        assert agent_dict["temperature"] == agent.temperature
        assert agent_dict["max_tokens"] == agent.max_tokens
    
    @pytest.mark.asyncio
    async def test_update_agent_configuration(self, agent_registry, sample_agents):
        """Test updating agent configuration."""
        agent = sample_agents[0]
        await agent_registry.register_agent(agent)
        
        updates = {
            "temperature": 0.8,
            "max_tokens": 5000,
            "capabilities": ["analysis", "research", "reporting", "validation"]
        }
        
        result = await agent_registry.update_agent_configuration(agent.name, updates)
        assert result is True
        
        updated_agent = await agent_registry.get_agent(agent.name)
        assert updated_agent.temperature == 0.8
        assert updated_agent.max_tokens == 5000
        assert "validation" in updated_agent.capabilities

class TestAgentAsCode:
    """Test agent-as-code pattern."""
    
    @pytest.mark.asyncio
    async def test_save_agent_to_file(self, agent_registry, sample_agents):
        """Test saving agent to markdown file."""
        agent = sample_agents[0]
        await agent_registry.register_agent(agent)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            file_path = f.name
        
        try:
            result = await agent_registry.save_agent_to_file(agent.name, file_path)
            assert result is True
            
            # Verify file was created and contains expected content
            assert os.path.exists(file_path)
            with open(file_path, 'r') as f:
                content = f.read()
                assert agent.name in content
                assert agent.description in content
                assert agent.persona in content
        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    @pytest.mark.asyncio
    async def test_load_agent_from_file(self, agent_registry):
        """Test loading agent from markdown file."""
        # Create a test agent file
        agent_content = """---
name: test-file-agent
description: Agent loaded from file
author: Test Author
communication_language: English
persona: Test persona for file loading
agent_type: specialist
capabilities:
  - file_loading
  - testing
temperature: 0.7
max_tokens: 4000
created_at: 2024-01-01T00:00:00
updated_at: 2024-01-01T00:00:00
---

# test-file-agent

Agent loaded from file

## Persona
Test persona for file loading

## Capabilities
- file_loading
- testing

## System Prompt
Generated system prompt for test-file-agent
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(agent_content)
            file_path = f.name
        
        try:
            agent = await agent_registry.load_agent_from_file(file_path)
            assert agent is not None
            assert agent.name == "test-file-agent"
            assert agent.description == "Agent loaded from file"
            assert "file_loading" in agent.capabilities
            
            # Verify agent was registered
            retrieved = await agent_registry.get_agent("test-file-agent")
            assert retrieved is not None
        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    @pytest.mark.asyncio
    async def test_load_agents_from_directory(self, agent_registry):
        """Test loading multiple agents from directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple agent files
            for i in range(3):
                agent_content = f"""---
name: test-dir-agent-{i}
description: Agent {i} from directory
author: Test Author
communication_language: English
persona: Test persona {i}
agent_type: specialist
capabilities:
  - testing
temperature: 0.7
max_tokens: 4000
created_at: 2024-01-01T00:00:00
updated_at: 2024-01-01T00:00:00
---

# test-dir-agent-{i}

Agent {i} from directory
"""
                file_path = os.path.join(temp_dir, f"agent-{i}.md")
                with open(file_path, 'w') as f:
                    f.write(agent_content)
            
            # Load agents from directory
            loaded_count = await agent_registry.load_agents_from_directory(temp_dir)
            assert loaded_count == 3
            
            # Verify agents were loaded
            for i in range(3):
                agent = await agent_registry.get_agent(f"test-dir-agent-{i}")
                assert agent is not None

class TestRegistryStatistics:
    """Test agent registry statistics."""
    
    @pytest.mark.asyncio
    async def test_registry_stats(self, agent_registry, sample_agents):
        """Test agent registry statistics."""
        # Register agents
        for agent in sample_agents:
            await agent_registry.register_agent(agent)
        
        stats = agent_registry.get_registry_stats()
        
        assert "total_agents" in stats
        assert "agent_types" in stats
        assert "total_unique_capabilities" in stats
        assert "capabilities" in stats
        
        assert stats["total_agents"] >= len(sample_agents)
        assert "specialist" in stats["agent_types"]
        assert "orchestrator" in stats["agent_types"]

class TestErrorHandling:
    """Test agent registry error handling."""
    
    @pytest.mark.asyncio
    async def test_register_invalid_agent(self, agent_registry):
        """Test registering invalid agent."""
        # This would test error handling for invalid agent data
        # Implementation depends on validation requirements
        pass
    
    @pytest.mark.asyncio
    async def test_load_invalid_file(self, agent_registry):
        """Test loading invalid agent file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Invalid agent file content")
            file_path = f.name
        
        try:
            agent = await agent_registry.load_agent_from_file(file_path)
            assert agent is None
        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_agent(self, agent_registry):
        """Test updating non-existent agent."""
        result = await agent_registry.update_agent_configuration(
            "nonexistent-agent",
            {"temperature": 0.8}
        )
        assert result is False

class TestAgentTypes:
    """Test different agent types."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_agent(self, sample_agents):
        """Test orchestrator agent behavior."""
        orchestrator = sample_agents[2]
        assert orchestrator.agent_type == AgentType.ORCHESTRATOR
        assert "orchestration" in orchestrator.capabilities
    
    @pytest.mark.asyncio
    async def test_specialist_agent(self, sample_agents):
        """Test specialist agent behavior."""
        specialist = sample_agents[0]
        assert specialist.agent_type == AgentType.SPECIALIST
        assert "analysis" in specialist.capabilities
    
    @pytest.mark.asyncio
    async def test_agent_system_prompt_generation(self, sample_agents):
        """Test agent system prompt generation."""
        agent = sample_agents[0]
        
        assert agent.system_prompt is not None
        assert agent.name in agent.system_prompt
        assert agent.persona in agent.system_prompt
        assert "BMAD v6" in agent.system_prompt

if __name__ == "__main__":
    pytest.main([__file__])
