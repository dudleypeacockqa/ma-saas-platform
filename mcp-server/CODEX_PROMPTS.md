# OpenAI Codex Prompts for BMAD v6 MCP Server

This document provides a comprehensive set of OpenAI Codex-optimized prompts for accelerating M&A SaaS platform development using the BMAD v6 MCP server. These prompts are designed to be used with the OpenAI Codex CLI or integrated into a development environment like Cursor.

## 1. Project Initialization & Setup

### **Prompt: Initialize New M&A Deal Project**

```
# BMAD v6 Project Initialization

# Goal: Initialize a new M&A deal project for the acquisition of 'TargetCorp' by 'AcquirerCorp'.

# Instructions for Codex:
# 1. Use the BMAD v6 MCP Server to initialize a new project.
# 2. Start with the 'workflow-status' workflow to check for existing state.
# 3. If no state exists, proceed to the 'plan-project' workflow.
# 4. Provide the following context for project planning:
#    - project_name: "Acquisition of TargetCorp"
#    - estimated_stories: 25
#    - estimated_epics: 4
#    - complexity: "high"
#    - team_size: 5
#    - timeline_weeks: 12
# 5. The MCP server will assess the scale level and route to the appropriate planning phase.
# 6. Capture the returned project_id and initial state for future interactions.

import requests
import json

mcp_server_url = "http://localhost:8000"  # Replace with your MCP server URL
api_token = "your_jwt_token"  # Replace with your valid JWT

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# Step 1: Check workflow status
workflow_status_payload = {
    "workflow_name": "workflow-status",
    "context": {},
    "project_id": "targetcorp-acquisition"
}

response = requests.post(f"{mcp_server_url}/api/v1/workflow/execute", headers=headers, data=json.dumps(workflow_status_payload))

if response.json().get("result", {}).get("status") == "new_project":
    # Step 2: Plan the project
    plan_project_payload = {
        "workflow_name": "plan-project",
        "context": {
            "project_name": "Acquisition of TargetCorp",
            "estimated_stories": 25,
            "estimated_epics": 4,
            "complexity": "high",
            "team_size": 5,
            "timeline_weeks": 12
        },
        "project_id": "targetcorp-acquisition"
    }
    
    plan_response = requests.post(f"{mcp_server_url}/api/v1/workflow/execute", headers=headers, data=json.dumps(plan_project_payload))
    print(plan_response.json())

```

## 2. Phase 1: Analysis

### **Prompt: Conduct Market Research for M&A Target**

```
# BMAD v6 Analysis Phase: Market Research

# Goal: Use the 'analyst' agent to conduct market research on 'TargetCorp', a company in the fintech sector.

# Instructions for Codex:
# 1. Invoke the 'analyst' agent on the BMAD v6 MCP Server.
# 2. Use the 'research' workflow to perform market analysis.
# 3. Provide the following context:
#    - research_topic: "Market analysis of TargetCorp in the fintech sector"
#    - research_scope: ["competitive_landscape", "market_trends", "growth_opportunities"]
# 4. The 'analyst' agent will guide the research process following BMAD v6 methodology.

import requests
import json

mcp_server_url = "http://localhost:8000"
api_token = "your_jwt_token"
project_id = "targetcorp-acquisition"

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

research_payload = {
    "workflow_name": "research",
    "context": {
        "research_topic": "Market analysis of TargetCorp in the fintech sector",
        "research_scope": ["competitive_landscape", "market_trends", "growth_opportunities"],
        "agent_guidance": "Invoke the analyst agent to lead this research effort."
    },
    "project_id": project_id
}

response = requests.post(f"{mcp_server_url}/api/v1/workflow/execute", headers=headers, data=json.dumps(research_payload))
print(response.json())

```

## 3. Phase 2: Planning

### **Prompt: Create Scale-Adaptive Project Plan**

```
# BMAD v6 Planning Phase: Scale-Adaptive Plan

# Goal: Use the 'pm' agent to create a scale-adaptive project plan for the 'TargetCorp' acquisition.

# Instructions for Codex:
# 1. Invoke the 'pm' agent on the BMAD v6 MCP Server.
# 2. Execute the 'plan-project' workflow.
# 3. The MCP server will use the previously assessed scale level (Level 3) to generate a full PRD and Epics list.
# 4. The 'pm' agent will guide the process of refining the plan.

# This prompt assumes the project has been initialized and scale level assessed.

import requests
import json

mcp_server_url = "http://localhost:8000"
api_token = "your_jwt_token"
project_id = "targetcorp-acquisition"

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# The 'plan-project' workflow was already called during initialization.
# This prompt is for interacting with the 'pm' agent to refine the plan.

invoke_pm_payload = {
    "agent_name": "pm",
    "prompt": "Review the generated project plan for the TargetCorp acquisition and suggest areas for refinement.",
    "context": {
        "project_id": project_id
    }
}

response = requests.post(f"{mcp_server_url}/api/v1/agent/invoke", headers=headers, data=json.dumps(invoke_pm_payload))
print(response.json())

```

## 4. Phase 3: Solutioning

### **Prompt: Design Solution Architecture for M&A Platform**

```
# BMAD v6 Solutioning Phase: Solution Architecture

# Goal: Use the 'architect' agent to design the solution architecture for the M&A platform integration.

# Instructions for Codex:
# 1. Invoke the 'architect' agent on the BMAD v6 MCP Server.
# 2. Execute the 'solution-architecture' workflow for the 'TargetCorp' acquisition project.
# 3. The project is at Level 3, so this workflow is required.
# 4. The 'architect' agent will guide the creation of the solution-architecture.md file.

import requests
import json

mcp_server_url = "http://localhost:8000"
api_token = "your_jwt_token"
project_id = "targetcorp-acquisition"

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

solution_arch_payload = {
    "workflow_name": "solution-architecture",
    "context": {
        "project_name": "Acquisition of TargetCorp",
        "requirements_summary": "Integrate TargetCorp's systems with AcquirerCorp's platform, ensuring data consistency and security."
    },
    "project_id": project_id
}

response = requests.post(f"{mcp_server_url}/api/v1/workflow/execute", headers=headers, data=json.dumps(solution_arch_payload))
print(response.json())

```

## 5. Phase 4: Implementation

### **Prompt: Implement User Story with Context Injection**

```
# BMAD v6 Implementation Phase: Implement User Story

# Goal: Use the 'dev' agent to implement a user story with dynamic context injection.

# Instructions for Codex:
# 1. First, run the 'create-story' workflow to draft the story from the TODO state.
# 2. Then, run 'story-ready' to approve it for development.
# 3. Next, run 'story-context' to generate the expertise injection XML.
# 4. Finally, invoke the 'dev' agent with the 'dev-story' workflow to implement the story.

import requests
import json

mcp_server_url = "http://localhost:8000"
api_token = "your_jwt_token"
project_id = "targetcorp-acquisition"

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# Step 1: Create Story
create_story_payload = {
    "workflow_name": "create-story",
    "context": {},
    "project_id": project_id
}
create_story_response = requests.post(f"{mcp_server_url}/api/v1/workflow/execute", headers=headers, data=json.dumps(create_story_payload))
story_id = create_story_response.json().get("result", {}).get("story_id")

# Step 2: Story Ready
story_ready_payload = {
    "workflow_name": "story-ready",
    "context": {"story_id": story_id},
    "project_id": project_id
}
requests.post(f"{mcp_server_url}/api/v1/workflow/execute", headers=headers, data=json.dumps(story_ready_payload))

# Step 3: Story Context
story_context_payload = {
    "workflow_name": "story-context",
    "context": {"story_id": story_id},
    "project_id": project_id
}
requests.post(f"{mcp_server_url}/api/v1/workflow/execute", headers=headers, data=json.dumps(story_context_payload))

# Step 4: Dev Story
dev_story_payload = {
    "workflow_name": "dev-story",
    "context": {"story_id": story_id},
    "project_id": project_id
}
dev_response = requests.post(f"{mcp_server_url}/api/v1/workflow/execute", headers=headers, data=json.dumps(dev_story_payload))
print(dev_response.json())

```

## 6. M&A Specific Tasks

### **Prompt: Perform Financial Valuation of Target Company**

```
# BMAD v6 M&A Task: Financial Valuation

# Goal: Use the 'ma-specialist' agent to perform a financial valuation of 'TargetCorp'.

# Instructions for Codex:
# 1. Invoke the 'ma-specialist' agent on the BMAD v6 MCP Server.
# 2. Execute the 'valuation-modeling' workflow.
# 3. Provide the necessary financial data for the valuation.
# 4. The 'ma-specialist' will guide the creation of DCF and comparable analysis models.

import requests
import json

mcp_server_url = "http://localhost:8000"
api_token = "your_jwt_token"
project_id = "targetcorp-acquisition"

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

valuation_payload = {
    "workflow_name": "valuation-modeling",
    "context": {
        "deal_id": "targetcorp-deal-001",
        "target_company": "TargetCorp",
        "financials": {
            "revenue": 50000000,
            "ebitda": 10000000,
            "growth_rate": 0.15
        },
        "model_types": ["DCF", "COMPARABLE"]
    },
    "project_id": project_id
}

response = requests.post(f"{mcp_server_url}/api/v1/workflow/execute", headers=headers, data=json.dumps(valuation_payload))
print(response.json())

```

