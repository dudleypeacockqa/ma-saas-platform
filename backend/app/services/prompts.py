"""M&A Domain-Specific Prompts for Claude Integration"""

MA_DOMAIN_PROMPTS = {
    "deal_analysis": """
Analyze this M&A deal with expert-level insight and provide comprehensive strategic recommendations.

DEAL DATA:
{deal_data}

CONTEXT:
{context}

Provide your analysis in the following JSON structure:
{{
    "confidence_score": <float 0-1>,
    "strategic_value": <float 0-1>,
    "risk_assessment": {{
        "financial_risk": <float 0-1>,
        "integration_risk": <float 0-1>,
        "market_risk": <float 0-1>,
        "regulatory_risk": <float 0-1>,
        "cultural_risk": <float 0-1>
    }},
    "recommendations": [<list of strategic recommendations>],
    "key_insights": [<list of critical insights>],
    "red_flags": [<list of potential issues>],
    "synergies": [<list of synergy opportunities>],
    "valuation_notes": "<assessment of valuation fairness and methodology>"
}}

Focus on:
1. Strategic fit and value creation potential
2. Risk factors and mitigation strategies
3. Synergy realization opportunities
4. Post-merger integration considerations
5. Financial structure optimization
6. Regulatory and compliance issues
7. Market positioning and competitive advantages
8. Cultural alignment and human capital factors

Be specific, quantitative where possible, and actionable in your recommendations.
""",

    "partnership_identification": """
Identify and evaluate potential strategic partnerships for this organization.

ORGANIZATION PROFILE:
{organization}

SEARCH CRITERIA:
{criteria}

Analyze potential partnerships and provide recommendations in this JSON format:
{{
    "recommendations": [
        {{
            "partner_id": "<identifier>",
            "compatibility_score": <float 0-1>,
            "strategic_fit": <float 0-1>,
            "influence_score": <float 0-1>,
            "synergy_areas": [<list of synergy areas>],
            "potential_value": "<estimated value creation>",
            "risk_factors": [<list of risks>],
            "recommended_actions": [<next steps>]
        }}
    ]
}}

Evaluation criteria:
1. Strategic alignment and complementary capabilities
2. Market position and influence
3. Financial strength and stability
4. Cultural fit and values alignment
5. Technology and innovation synergies
6. Geographic and market expansion opportunities
7. Risk profile and mitigation potential
8. Value creation and revenue synergies
9. Operational efficiency improvements
10. Network effects and ecosystem benefits

Provide at least 5 partnership recommendations ranked by compatibility score.
""",

    "strategic_insights": """
Generate strategic insights from ecosystem intelligence data for M&A decision-making.

ECOSYSTEM DATA:
{ecosystem_data}

FOCUS AREAS:
{focus_areas}

Provide comprehensive strategic insights in this JSON format:
{{
    "market_trends": [
        {{
            "trend": "<description>",
            "impact": "<high/medium/low>",
            "opportunity": "<how to capitalize>",
            "timeframe": "<expected timeline>"
        }}
    ],
    "opportunities": [
        {{
            "description": "<opportunity description>",
            "potential_value": "<estimated value>",
            "priority": "<high/medium/low>",
            "action_items": [<list of actions>]
        }}
    ],
    "threats": [
        {{
            "description": "<threat description>",
            "severity": "<high/medium/low>",
            "mitigation": "<mitigation strategy>",
            "timeline": "<urgency>"
        }}
    ],
    "competitive_positioning": {{
        "strengths": [<list>],
        "weaknesses": [<list>],
        "differentiation": "<unique value proposition>",
        "strategic_moves": [<recommended actions>]
    }},
    "recommendations": [
        {{
            "recommendation": "<specific recommendation>",
            "rationale": "<why this matters>",
            "expected_impact": "<quantified impact>",
            "implementation_timeline": "<timeframe>"
        }}
    ]
}}

Analyze through the lens of:
1. Market consolidation opportunities
2. Emerging technology disruptions
3. Regulatory and compliance changes
4. Economic and geopolitical factors
5. Industry value chain evolution
6. Customer behavior shifts
7. Competitive dynamics
8. Capital market conditions
""",

    "deal_optimization": """
Optimize this M&A deal structure to achieve specified goals.

CURRENT DEAL PARAMETERS:
{deal_parameters}

OPTIMIZATION GOALS:
{goals}

Provide optimized deal structure in this JSON format:
{{
    "optimized_structure": {{
        "deal_type": "<asset/stock/merger>",
        "consideration": "<cash/stock/mixed>",
        "financing": "<structure>",
        "earnouts": "<if applicable>",
        "escrow": "<terms>",
        "representations_warranties": "<key terms>",
        "closing_conditions": [<list>]
    }},
    "improvements": [
        {{
            "area": "<improvement area>",
            "original": "<original terms>",
            "optimized": "<new terms>",
            "benefit": "<quantified benefit>"
        }}
    ],
    "estimated_savings": <dollar amount>,
    "risk_reduction": <percentage>,
    "tax_efficiency": {{
        "structure": "<tax-optimized structure>",
        "estimated_savings": <amount>,
        "compliance_notes": "<important considerations>"
    }},
    "implementation_steps": [
        {{
            "step": "<action>",
            "responsible_party": "<who>",
            "timeline": "<when>",
            "dependencies": [<list>]
        }}
    ]
}}

Optimize for:
1. Tax efficiency and structuring
2. Risk allocation and mitigation
3. Financing optimization
4. Regulatory compliance
5. Earnout and contingent payment structures
6. Escrow and indemnification terms
7. Working capital adjustments
8. Purchase price adjustments
""",

    "integration_assessment": """
Assess post-merger integration readiness between acquirer and target.

ACQUIRER PROFILE:
{acquirer}

TARGET PROFILE:
{target}

Provide integration assessment in this JSON format:
{{
    "readiness_score": <float 0-1>,
    "integration_complexity": "<high/medium/low>",
    "estimated_timeline": "<months>",
    "key_challenges": [
        {{
            "challenge": "<description>",
            "severity": "<high/medium/low>",
            "mitigation": "<strategy>",
            "owner": "<responsible party>"
        }}
    ],
    "success_factors": [
        {{
            "factor": "<description>",
            "current_state": "<assessment>",
            "required_actions": [<list>]
        }}
    ],
    "synergy_capture": {{
        "revenue_synergies": {{
            "potential": <dollar amount>,
            "confidence": <percentage>,
            "timeline": "<months to realize>"
        }},
        "cost_synergies": {{
            "potential": <dollar amount>,
            "confidence": <percentage>,
            "timeline": "<months to realize>"
        }}
    }},
    "risk_areas": [
        {{
            "area": "<risk area>",
            "impact": "<high/medium/low>",
            "likelihood": "<high/medium/low>",
            "mitigation_plan": "<strategy>"
        }}
    ],
    "action_items": [
        {{
            "action": "<specific action>",
            "priority": "<high/medium/low>",
            "owner": "<responsible party>",
            "due_date": "<timeline>",
            "resources_required": "<what's needed>"
        }}
    ],
    "cultural_assessment": {{
        "compatibility_score": <float 0-1>,
        "key_differences": [<list>],
        "integration_approach": "<strategy>",
        "change_management": [<initiatives>]
    }},
    "technology_integration": {{
        "complexity": "<high/medium/low>",
        "critical_systems": [<list>],
        "integration_approach": "<strategy>",
        "timeline": "<months>",
        "estimated_cost": <amount>
    }}
}}

Assess across dimensions:
1. Organizational and cultural alignment
2. Technology and systems integration
3. Product and service portfolio
4. Customer and market overlap
5. Supply chain and operations
6. Financial and reporting systems
7. Human capital and talent retention
8. Regulatory and compliance requirements
9. Brand and marketing integration
10. Geographic and facility consolidation
""",

    "wealth_optimization": """
Analyze this opportunity for wealth-building optimization toward £200M goal.

OPPORTUNITY DATA:
{opportunity_data}

PORTFOLIO CONTEXT:
{portfolio_context}

Provide wealth optimization analysis in this JSON format:
{{
    "wealth_impact": {{
        "estimated_value_creation": <amount>,
        "irr_projection": <percentage>,
        "payback_period": "<years>",
        "exit_multiple": <multiple>
    }},
    "strategic_fit": {{
        "portfolio_synergies": [<list>],
        "platform_potential": "<assessment>",
        "scalability": "<high/medium/low>",
        "market_position": "<impact on portfolio>"
    }},
    "risk_return_profile": {{
        "risk_score": <float 0-1>,
        "return_potential": <float 0-1>,
        "correlation_to_portfolio": <float -1 to 1>,
        "diversification_benefit": "<assessment>"
    }},
    "optimization_strategies": [
        {{
            "strategy": "<description>",
            "value_add": <amount>,
            "implementation_complexity": "<high/medium/low>",
            "timeline": "<months>"
        }}
    ],
    "exit_scenarios": [
        {{
            "scenario": "<description>",
            "probability": <percentage>,
            "estimated_value": <amount>,
            "timeline": "<years>"
        }}
    ],
    "recommendation": {{
        "action": "<proceed/pass/restructure>",
        "rationale": "<detailed reasoning>",
        "optimal_structure": "<recommended approach>",
        "key_value_drivers": [<list>]
    }}
}}

Evaluate for:
1. Direct value creation potential
2. Platform building opportunities
3. Network effects and ecosystem value
4. Strategic positioning advantages
5. Exit optionality and liquidity
6. Risk-adjusted returns
7. Capital efficiency
8. Synergies with existing portfolio
"""
}