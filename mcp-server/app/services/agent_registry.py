"""
BMAD v6 Agent Registry Service
Implements agent-as-code pattern with dynamic loading from markdown files
"""

import os
import yaml
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.models.bmad_models import AgentConfiguration, AgentType

logger = logging.getLogger(__name__)

class BMadAgent:
    """BMAD v6 Agent implementation following agent-as-code pattern."""
    
    def __init__(
        self,
        name: str,
        description: str,
        persona: str,
        communication_language: str = "English",
        agent_type: AgentType = AgentType.SPECIALIST,
        capabilities: List[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system_prompt: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.persona = persona
        self.communication_language = communication_language
        self.agent_type = agent_type
        self.capabilities = capabilities or []
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt or self._generate_system_prompt()
        
        # Runtime state
        self.context_history: List[Dict[str, Any]] = []
        self.active_workflows: List[str] = []
        
        logger.info(f"Initialized BMAD v6 agent: {self.name}")
    
    def _generate_system_prompt(self) -> str:
        """Generate system prompt based on agent configuration."""
        prompt = f"""You are {self.name}, a {self.description}.

PERSONA: {self.persona}

COMMUNICATION LANGUAGE: {self.communication_language}

AGENT TYPE: {self.agent_type.value}

CAPABILITIES: {', '.join(self.capabilities)}

BMAD v6 METHODOLOGY:
You follow the BMAD-method v6 specifications:
- Collaboration Optimized Reflection Engine (C.O.R.E.)
- Scale-Adaptive Workflow Engine (Levels 0-4)
- Four-Phase Methodology (Analysis, Planning, Solutioning, Implementation)
- Agent-as-Code pattern with markdown-based configuration

INSTRUCTIONS:
1. Always maintain your persona and communication style
2. Follow BMAD v6 workflow patterns and state machines
3. Provide guidance that amplifies human thinking rather than replacing it
4. Use structured approaches for complex problems
5. Maintain context awareness across interactions
6. Collaborate effectively with other BMAD agents

Remember: Your role is to enhance human capabilities through guided collaboration and reflection, not to simply execute tasks."""
        
        return prompt
    
    async def invoke(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Invoke the agent with a prompt and context."""
        context = context or {}
        
        # Add to context history
        interaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "prompt": prompt,
            "context": context
        }
        self.context_history.append(interaction)
        
        # Process the request based on agent capabilities
        response = await self._process_request(prompt, context)
        
        # Add response to history
        interaction["response"] = response
        
        return response
    
    async def _process_request(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the agent request based on capabilities."""
        
        # Determine the type of request and route accordingly
        if "workflow" in prompt.lower():
            return await self._handle_workflow_request(prompt, context)
        elif "analyze" in prompt.lower():
            return await self._handle_analysis_request(prompt, context)
        elif "plan" in prompt.lower():
            return await self._handle_planning_request(prompt, context)
        else:
            return await self._handle_general_request(prompt, context)
    
    async def _handle_workflow_request(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow-related requests."""
        return {
            "type": "workflow_guidance",
            "agent": self.name,
            "response": f"As {self.name}, I recommend following the BMAD v6 workflow patterns. Based on your request, I suggest starting with the workflow-status workflow to assess your current project state.",
            "next_actions": [
                "Run workflow-status to check current state",
                "Determine appropriate phase and scale level",
                "Route to specific workflow based on assessment"
            ],
            "bmad_context": {
                "methodology": "BMAD v6",
                "phase_guidance": "Always start with workflow-status as universal entry point"
            }
        }
    
    async def _handle_analysis_request(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analysis requests."""
        return {
            "type": "analysis_guidance",
            "agent": self.name,
            "response": f"As {self.name}, I'll guide you through a structured analysis approach following BMAD v6 methodology.",
            "analysis_framework": {
                "phase_1_analysis": [
                    "Define scope and objectives",
                    "Gather relevant data and context",
                    "Conduct systematic evaluation"
                ],
                "bmad_principles": [
                    "Human amplification over replacement",
                    "Guided collaboration and reflection",
                    "Structured problem-solving approach"
                ]
            },
            "next_steps": [
                "Clarify analysis objectives",
                "Identify key stakeholders and constraints",
                "Determine appropriate analysis methodology"
            ]
        }
    
    async def _handle_planning_request(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle planning requests."""
        return {
            "type": "planning_guidance",
            "agent": self.name,
            "response": f"As {self.name}, I'll help you create a scale-adaptive plan following BMAD v6 methodology.",
            "planning_framework": {
                "scale_assessment": {
                    "level_0": "Single atomic change",
                    "level_1": "1-10 stories, 1 epic",
                    "level_2": "5-15 stories, 1-2 epics",
                    "level_3": "12-40 stories, 2-5 epics",
                    "level_4": "40+ stories, 5+ epics"
                },
                "phase_routing": {
                    "levels_0_2": "Direct to Implementation",
                    "levels_3_4": "Requires Solutioning Phase"
                }
            },
            "next_steps": [
                "Assess project complexity and scope",
                "Determine appropriate scale level",
                "Route to phase-specific planning workflow"
            ]
        }
    
    async def _handle_general_request(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general requests."""
        return {
            "type": "general_guidance",
            "agent": self.name,
            "response": f"As {self.name}, I'm here to help you following BMAD v6 principles of guided collaboration and human amplification.",
            "guidance": "I focus on enhancing your thinking through structured approaches rather than simply providing answers.",
            "bmad_approach": [
                "Collaborative reflection and discovery",
                "Structured problem-solving frameworks", 
                "Context-aware guidance and support"
            ],
            "available_capabilities": self.capabilities
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "persona": self.persona,
            "communication_language": self.communication_language,
            "agent_type": self.agent_type.value,
            "capabilities": self.capabilities,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "context_history_count": len(self.context_history),
            "active_workflows": self.active_workflows
        }

class AgentRegistry:
    """Registry for managing BMAD v6 agents following agent-as-code pattern."""
    
    def __init__(self):
        self.agents: Dict[str, BMadAgent] = {}
        self.agent_configurations: Dict[str, AgentConfiguration] = {}
        self.agent_files_path = "bmad/core/agents"  # Default path for agent files
        
        logger.info("Initialized BMAD v6 Agent Registry")
    
    async def register_agent(self, agent: BMadAgent) -> bool:
        """Register a new agent in the registry."""
        try:
            self.agents[agent.name] = agent
            
            # Create configuration object
            config = AgentConfiguration(
                name=agent.name,
                description=agent.description,
                persona=agent.persona,
                communication_language=agent.communication_language,
                agent_type=agent.agent_type,
                capabilities=agent.capabilities,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
                system_prompt=agent.system_prompt
            )
            
            self.agent_configurations[agent.name] = config
            
            logger.info(f"Registered agent: {agent.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent.name}: {str(e)}")
            return False
    
    async def get_agent(self, name: str) -> Optional[BMadAgent]:
        """Get an agent by name."""
        return self.agents.get(name)
    
    async def list_agents(self) -> List[BMadAgent]:
        """List all registered agents."""
        return list(self.agents.values())
    
    async def load_agent_from_file(self, file_path: str) -> Optional[BMadAgent]:
        """Load agent from markdown file with YAML frontmatter (agent-as-code)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    markdown_content = parts[2]
                    
                    config = yaml.safe_load(yaml_content)
                    
                    # Create agent from configuration
                    agent = BMadAgent(
                        name=config.get('name'),
                        description=config.get('description'),
                        persona=config.get('persona'),
                        communication_language=config.get('communication_language', 'English'),
                        agent_type=AgentType(config.get('agent_type', 'specialist')),
                        capabilities=config.get('capabilities', []),
                        temperature=config.get('temperature', 0.7),
                        max_tokens=config.get('max_tokens', 4000),
                        system_prompt=config.get('system_prompt')
                    )
                    
                    await self.register_agent(agent)
                    logger.info(f"Loaded agent from file: {file_path}")
                    return agent
            
            logger.warning(f"Invalid agent file format: {file_path}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load agent from file {file_path}: {str(e)}")
            return None
    
    async def load_agents_from_directory(self, directory_path: str) -> int:
        """Load all agents from a directory of markdown files."""
        loaded_count = 0
        
        if not os.path.exists(directory_path):
            logger.warning(f"Agent directory not found: {directory_path}")
            return loaded_count
        
        for filename in os.listdir(directory_path):
            if filename.endswith('.md'):
                file_path = os.path.join(directory_path, filename)
                agent = await self.load_agent_from_file(file_path)
                if agent:
                    loaded_count += 1
        
        logger.info(f"Loaded {loaded_count} agents from directory: {directory_path}")
        return loaded_count
    
    async def save_agent_to_file(self, agent_name: str, file_path: str) -> bool:
        """Save agent configuration to markdown file (agent-as-code export)."""
        try:
            agent = await self.get_agent(agent_name)
            if not agent:
                logger.error(f"Agent not found: {agent_name}")
                return False
            
            config = self.agent_configurations.get(agent_name)
            if not config:
                logger.error(f"Agent configuration not found: {agent_name}")
                return False
            
            # Create YAML frontmatter
            yaml_data = {
                'name': config.name,
                'description': config.description,
                'author': config.author,
                'communication_language': config.communication_language,
                'persona': config.persona,
                'agent_type': config.agent_type.value,
                'capabilities': config.capabilities,
                'temperature': config.temperature,
                'max_tokens': config.max_tokens,
                'created_at': config.created_at.isoformat(),
                'updated_at': config.updated_at.isoformat()
            }
            
            # Create markdown content
            markdown_content = f"""
# {config.name}

{config.description}

## Persona
{config.persona}

## Capabilities
{chr(10).join(f"- {cap}" for cap in config.capabilities)}

## System Prompt
{agent.system_prompt}
"""
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('---\n')
                yaml.dump(yaml_data, f, default_flow_style=False)
                f.write('---\n')
                f.write(markdown_content)
            
            logger.info(f"Saved agent to file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save agent to file {file_path}: {str(e)}")
            return False
    
    async def update_agent_configuration(self, agent_name: str, updates: Dict[str, Any]) -> bool:
        """Update agent configuration."""
        try:
            agent = await self.get_agent(agent_name)
            if not agent:
                return False
            
            config = self.agent_configurations.get(agent_name)
            if not config:
                return False
            
            # Update configuration
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                if hasattr(agent, key):
                    setattr(agent, key, value)
            
            config.updated_at = datetime.utcnow()
            
            logger.info(f"Updated agent configuration: {agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update agent configuration {agent_name}: {str(e)}")
            return False
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        agent_types = {}
        total_capabilities = set()
        
        for agent in self.agents.values():
            agent_type = agent.agent_type.value
            agent_types[agent_type] = agent_types.get(agent_type, 0) + 1
            total_capabilities.update(agent.capabilities)
        
        return {
            "total_agents": len(self.agents),
            "agent_types": agent_types,
            "total_unique_capabilities": len(total_capabilities),
            "capabilities": list(total_capabilities)
        }
