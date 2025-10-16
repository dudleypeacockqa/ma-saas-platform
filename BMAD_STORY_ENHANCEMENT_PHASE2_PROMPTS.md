# 🎯 BMAD v6 Story Enhancement Phase 2: Systematic Story Clarification

**Date:** 2025-10-14  
**Phase:** Story Enhancement & Clarification - Phase 2  
**Objective:** Transform 19,441 stories into executable, prioritized sprints with crystal-clear acceptance criteria  
**Timeline:** 2-3 days  
**Methodology:** BMAD v6 Level 4 Story Enhancement  

---

## 📋 **PROMPT 1: Critical Gap Story Creation**

```bash
# BMAD v6 Story Enhancement Phase 2 - Task 1: Critical Gap Story Creation
# Objective: Create enhanced stories for the 8 critical gaps identified
# Expected Output: Production-ready stories with acceptance criteria

cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import json
from pathlib import Path
from datetime import datetime

print("🎯 BMAD v6 Critical Gap Story Creation")
print("=" * 70)

# Load consolidated analysis
if Path('consolidated_story_analysis.json').exists():
    with open('consolidated_story_analysis.json', 'r') as f:
        analysis_data = json.load(f)
    print("✅ Loaded consolidated story analysis")
else:
    print("❌ Missing consolidated_story_analysis.json - Run Phase 1 first")
    exit(1)

# Enhanced BMAD v6 Story Template
def create_enhanced_story(story_id, title, epic, priority, size, user_type, capability, business_value, 
                         given, when, then, additional_outcomes, frontend_req, backend_req, integration_req,
                         test_cases, integration_tests, user_tests, performance_tests, dependencies=None):
    """Create an enhanced BMAD v6 story with full specifications"""
    
    story = {
        "STORY_ID": story_id,
        "TITLE": title,
        "EPIC": epic,
        "PRIORITY": priority,
        "SIZE": size,
        "DEPENDENCIES": dependencies or [],
        "CREATED_DATE": datetime.now().strftime("%Y-%m-%d"),
        
        "USER_STORY": {
            "As_a": user_type,
            "I_want": capability,
            "So_that": business_value
        },
        
        "ACCEPTANCE_CRITERIA": {
            "Given": given,
            "When": when,
            "Then": then,
            "And": additional_outcomes
        },
        
        "TECHNICAL_REQUIREMENTS": {
            "Frontend": frontend_req,
            "Backend": backend_req,
            "Integration": integration_req
        },
        
        "DEFINITION_OF_DONE": [
            "Code implemented and tested",
            "UI/UX matches design requirements", 
            "API endpoints functional",
            "Integration tests passing",
            "User acceptance testing completed",
            "Documentation updated",
            "Deployed to staging",
            "Stakeholder approval received"
        ],
        
        "TESTING_STRATEGY": {
            "Unit_Tests": test_cases,
            "Integration_Tests": integration_tests,
            "User_Tests": user_tests,
            "Performance_Tests": performance_tests
        },
        
        "ROLLBACK_PLAN": {
            "If_Fails": f"Revert to previous working state, disable {title.lower()} feature",
            "Dependencies_Impact": "Assess impact on dependent features and user workflows"
        }
    }
    
    return story

# Create enhanced stories for critical gaps
print(f"\n🚨 Creating Enhanced Stories for Critical Gaps:")
print("-" * 50)

critical_gap_stories = []

# 1. Landing Page Access (P0 - CRITICAL)
story_1 = create_enhanced_story(
    story_id="E1.P0.001",
    title="Restore Customer Access to Platform Landing Page",
    epic="Customer Onboarding",
    priority="P0 - CRITICAL",
    size="M (2-3 days)",
    user_type="Potential customer visiting the platform",
    capability="To see a professional landing page with clear value proposition",
    business_value="I can understand the platform benefits and sign up for services",
    given="I navigate to https://ma-saas-platform.onrender.com",
    when="The page loads",
    then="I see a professional landing page with navigation, hero section, and clear CTAs",
    additional_outcomes=[
        "The page loads in under 3 seconds",
        "All images and assets display properly",
        "The page is mobile responsive",
        "I can navigate to login and pricing pages"
    ],
    frontend_req="React landing page with Tailwind CSS, responsive design, optimized assets",
    backend_req="No backend changes required, ensure proper static file serving",
    integration_req="CDN configuration for fast asset delivery",
    test_cases=["Component rendering", "Navigation functionality", "Mobile responsiveness"],
    integration_tests=["Page load performance", "Asset loading", "Cross-browser compatibility"],
    user_tests=["Manual verification on desktop/mobile", "User journey testing"],
    performance_tests=["Core Web Vitals under 3s", "Lighthouse score >90"]
)

# 2. User Registration (P0 - CRITICAL)
story_2 = create_enhanced_story(
    story_id="E1.P0.002", 
    title="Implement User Registration with Clerk Integration",
    epic="Customer Onboarding",
    priority="P0 - CRITICAL",
    size="M (2-3 days)",
    user_type="New user wanting to access the platform",
    capability="To create an account and verify my email",
    business_value="I can access the platform features and start using the service",
    given="I am on the landing page and click 'Sign Up'",
    when="I complete the registration form",
    then="I receive an email verification and can access my dashboard",
    additional_outcomes=[
        "Registration form validates input properly",
        "Email verification is sent immediately",
        "User is redirected to onboarding flow",
        "Account is created in Clerk and database"
    ],
    frontend_req="Registration form with validation, email verification UI, onboarding flow",
    backend_req="Clerk webhook integration, user profile creation, database sync",
    integration_req="Clerk authentication service, email delivery service",
    test_cases=["Form validation", "Clerk integration", "Database user creation"],
    integration_tests=["Email delivery", "Webhook processing", "User sync"],
    user_tests=["Complete registration flow", "Email verification process"],
    performance_tests=["Registration completion under 5s", "Email delivery under 30s"],
    dependencies=["E1.P0.001"]
)

# 3. Subscription Selection (P0 - CRITICAL)
story_3 = create_enhanced_story(
    story_id="E1.P0.003",
    title="Implement Subscription Plan Selection Interface",
    epic="Revenue Generation", 
    priority="P0 - CRITICAL",
    size="L (3-4 days)",
    user_type="Registered user ready to subscribe",
    capability="To select and purchase a subscription plan",
    business_value="I can access premium features and the company generates revenue",
    given="I am logged in and want to upgrade my account",
    when="I select a subscription plan and complete payment",
    then="My account is upgraded and I have access to premium features",
    additional_outcomes=[
        "Pricing plans are clearly displayed",
        "Payment processing is secure and fast",
        "Subscription status is updated immediately",
        "User receives confirmation email"
    ],
    frontend_req="Pricing page, plan comparison, Stripe checkout integration",
    backend_req="Stripe webhook processing, subscription management, feature gating",
    integration_req="Stripe payment processing, Clerk subscription sync",
    test_cases=["Plan selection", "Payment processing", "Subscription activation"],
    integration_tests=["Stripe webhook handling", "Feature access control"],
    user_tests=["Complete purchase flow", "Feature access verification"],
    performance_tests=["Checkout completion under 10s", "Webhook processing under 5s"],
    dependencies=["E1.P0.002"]
)

# 4. Welcome Dashboard (P0 - CRITICAL)
story_4 = create_enhanced_story(
    story_id="E1.P0.004",
    title="Create Welcome Dashboard for New Users",
    epic="Customer Onboarding",
    priority="P0 - CRITICAL", 
    size="M (2-3 days)",
    user_type="Newly registered user accessing the platform",
    capability="To see a welcoming dashboard that guides me through key features",
    business_value="I can quickly understand and start using the platform effectively",
    given="I have completed registration and logged in for the first time",
    when="I access my dashboard",
    then="I see a welcome interface with guided tour and quick actions",
    additional_outcomes=[
        "Dashboard shows personalized welcome message",
        "Quick action buttons for key features",
        "Progress indicators for onboarding steps",
        "Help resources and documentation links"
    ],
    frontend_req="Dashboard layout, welcome components, guided tour, progress tracking",
    backend_req="User onboarding state management, progress tracking API",
    integration_req="Analytics tracking for onboarding completion",
    test_cases=["Dashboard rendering", "Welcome flow", "Progress tracking"],
    integration_tests=["User state management", "Analytics integration"],
    user_tests=["First-time user experience", "Onboarding completion"],
    performance_tests=["Dashboard load under 2s", "Smooth animations"],
    dependencies=["E1.P0.002", "E1.P0.003"]
)

# 5. Deal Creation Interface (P1 - HIGH)
story_5 = create_enhanced_story(
    story_id="E2.P1.001",
    title="Implement Deal Creation Interface",
    epic="Deal Management",
    priority="P1 - HIGH",
    size="L (3-4 days)",
    user_type="M&A professional managing deals",
    capability="To create and configure new deals in the system",
    business_value="I can track and manage my M&A transactions effectively",
    given="I am logged in and want to create a new deal",
    when="I complete the deal creation form",
    then="A new deal is created with all required information",
    additional_outcomes=[
        "Deal form validates all required fields",
        "Deal is saved to database with proper structure",
        "User is redirected to deal detail view",
        "Deal appears in pipeline view"
    ],
    frontend_req="Deal creation form, field validation, file upload, rich text editor",
    backend_req="Deal model creation, validation, file storage, API endpoints",
    integration_req="File storage service, document processing",
    test_cases=["Form validation", "Deal creation", "File upload"],
    integration_tests=["Database persistence", "File storage", "API endpoints"],
    user_tests=["Complete deal creation flow", "Data validation"],
    performance_tests=["Form submission under 3s", "File upload progress"],
    dependencies=["E1.P0.004"]
)

# 6. Deal Pipeline View (P1 - HIGH)
story_6 = create_enhanced_story(
    story_id="E2.P1.002",
    title="Implement Deal Pipeline Kanban View",
    epic="Deal Management",
    priority="P1 - HIGH",
    size="L (3-4 days)",
    user_type="M&A professional tracking multiple deals",
    capability="To view all my deals in a visual pipeline with drag-and-drop",
    business_value="I can efficiently manage deal flow and status updates",
    given="I have created deals in the system",
    when="I access the pipeline view",
    then="I see all deals organized by status with drag-and-drop functionality",
    additional_outcomes=[
        "Deals are grouped by status columns",
        "Drag-and-drop updates deal status",
        "Pipeline shows deal summary information",
        "Filtering and search functionality works"
    ],
    frontend_req="Kanban board component, drag-and-drop, deal cards, filters",
    backend_req="Deal status management, bulk update APIs, search endpoints",
    integration_req="Real-time updates via WebSocket",
    test_cases=["Kanban rendering", "Drag-and-drop", "Status updates"],
    integration_tests=["Real-time sync", "Bulk operations", "Search functionality"],
    user_tests=["Pipeline navigation", "Deal status management"],
    performance_tests=["Pipeline load under 2s", "Smooth drag-and-drop"],
    dependencies=["E2.P1.001"]
)

# 7. AI Deal Analysis (P1 - HIGH)
story_7 = create_enhanced_story(
    story_id="E3.P1.001",
    title="Implement AI-Powered Deal Analysis Interface",
    epic="AI Intelligence",
    priority="P1 - HIGH",
    size="L (3-4 days)",
    user_type="M&A professional analyzing deal value",
    capability="To get AI-powered analysis and valuation for my deals",
    business_value="I can make data-driven decisions with intelligent insights",
    given="I have a deal with financial data in the system",
    when="I request AI analysis",
    then="I receive comprehensive analysis including valuation and risk assessment",
    additional_outcomes=[
        "Analysis includes DCF valuation model",
        "Risk factors are identified and scored",
        "Comparable deals analysis provided",
        "Report can be exported as PDF"
    ],
    frontend_req="Analysis interface, progress indicators, report viewer, PDF export",
    backend_req="Claude/OpenAI integration, analysis algorithms, report generation",
    integration_req="AI service APIs, PDF generation service",
    test_cases=["Analysis request", "Report generation", "PDF export"],
    integration_tests=["AI service integration", "Data processing", "Report accuracy"],
    user_tests=["Complete analysis workflow", "Report review"],
    performance_tests=["Analysis completion under 30s", "Report generation under 10s"],
    dependencies=["E2.P1.001"]
)

# 8. Community Networking Interface (P2 - MEDIUM)
story_8 = create_enhanced_story(
    story_id="E4.P2.001",
    title="Implement Community Networking Interface",
    epic="Community Platform",
    priority="P2 - MEDIUM",
    size="L (3-4 days)",
    user_type="Platform member wanting to network",
    capability="To connect with other M&A professionals and share insights",
    business_value="I can expand my network and discover new opportunities",
    given="I am a verified platform member",
    when="I access the community section",
    then="I can view member profiles, send connection requests, and join discussions",
    additional_outcomes=[
        "Member directory with search and filters",
        "Connection request system",
        "Discussion forums by topic",
        "Private messaging capability"
    ],
    frontend_req="Member directory, profile pages, messaging interface, forums",
    backend_req="Member management, connection system, messaging APIs, forum system",
    integration_req="Real-time messaging, notification system",
    test_cases=["Member search", "Connection requests", "Messaging"],
    integration_tests=["Real-time messaging", "Notification delivery"],
    user_tests=["Networking workflow", "Community engagement"],
    performance_tests=["Directory load under 3s", "Message delivery under 2s"],
    dependencies=["E1.P0.004"]
)

# Add all stories to list
critical_gap_stories = [story_1, story_2, story_3, story_4, story_5, story_6, story_7, story_8]

print(f"✅ Created {len(critical_gap_stories)} enhanced critical gap stories")

# Display story summaries
for i, story in enumerate(critical_gap_stories, 1):
    print(f"\n{i}. {story['STORY_ID']}: {story['TITLE']}")
    print(f"   Epic: {story['EPIC']} | Priority: {story['PRIORITY']} | Size: {story['SIZE']}")
    print(f"   User Story: As a {story['USER_STORY']['As_a']}, I want {story['USER_STORY']['I_want'][:50]}...")

# Save enhanced stories
with open('critical_gap_stories_enhanced.json', 'w') as f:
    json.dump({
        'metadata': {
            'created_date': datetime.now().isoformat(),
            'total_stories': len(critical_gap_stories),
            'methodology': 'BMAD v6 Level 4 Story Enhancement',
            'phase': 'Phase 2 - Critical Gap Creation'
        },
        'stories': critical_gap_stories
    }, f, indent=2)

print(f"\n🎯 Critical Gap Stories Summary:")
print("=" * 50)
print(f"📊 Total enhanced stories: {len(critical_gap_stories)}")
print(f"🚨 P0 Critical stories: {len([s for s in critical_gap_stories if 'P0' in s['PRIORITY']])}")
print(f"🔥 P1 High priority stories: {len([s for s in critical_gap_stories if 'P1' in s['PRIORITY']])}")
print(f"📋 P2 Medium priority stories: {len([s for s in critical_gap_stories if 'P2' in s['PRIORITY']])}")

print(f"\n💾 Enhanced stories saved to: critical_gap_stories_enhanced.json")
print(f"🎯 Next: Run PROMPT 2 for sprint organization")
EOF
```

---

## 📋 **PROMPT 2: Sprint Organization & Prioritization**

```bash
# BMAD v6 Story Enhancement Phase 2 - Task 2: Sprint Organization
# Objective: Organize enhanced stories into executable sprints with dependencies
# Expected Output: 8-week sprint plan with clear deliverables

cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

print("📅 BMAD v6 Sprint Organization & Prioritization")
print("=" * 70)

# Load enhanced critical gap stories
if Path('critical_gap_stories_enhanced.json').exists():
    with open('critical_gap_stories_enhanced.json', 'r') as f:
        stories_data = json.load(f)
    stories = stories_data['stories']
    print(f"✅ Loaded {len(stories)} enhanced critical gap stories")
else:
    print("❌ Missing critical_gap_stories_enhanced.json - Run PROMPT 1 first")
    exit(1)

def calculate_sprint_capacity():
    """Calculate sprint capacity based on team size and velocity"""
    # Assuming 1 developer, 5 days per sprint, 6 hours productive time per day
    developer_hours_per_sprint = 5 * 6  # 30 hours
    
    # Story size estimates in hours
    size_estimates = {
        'S': 8,   # 1 day
        'M': 16,  # 2 days  
        'L': 24   # 3 days
    }
    
    return developer_hours_per_sprint, size_estimates

def extract_size_days(size_string):
    """Extract size from size string like 'M (2-3 days)'"""
    if 'S' in size_string or '1 day' in size_string:
        return 'S'
    elif 'L' in size_string or '3-4 days' in size_string:
        return 'L'
    else:
        return 'M'

def organize_sprints(stories, sprint_capacity_hours, size_estimates):
    """Organize stories into sprints based on priority and dependencies"""
    
    # Sort stories by priority and dependencies
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    
    def get_priority_score(story):
        priority = story['PRIORITY'].split(' ')[0]
        return priority_order.get(priority, 4)
    
    # Create dependency graph
    story_deps = {}
    for story in stories:
        story_id = story['STORY_ID']
        deps = story.get('DEPENDENCIES', [])
        story_deps[story_id] = deps
    
    # Topological sort for dependency resolution
    def resolve_dependencies(stories, story_deps):
        resolved = []
        remaining = stories.copy()
        
        while remaining:
            # Find stories with no unresolved dependencies
            ready_stories = []
            for story in remaining:
                story_id = story['STORY_ID']
                deps = story_deps.get(story_id, [])
                if all(dep in [s['STORY_ID'] for s in resolved] for dep in deps):
                    ready_stories.append(story)
            
            if not ready_stories:
                # If no stories are ready, take the highest priority one
                ready_stories = [min(remaining, key=get_priority_score)]
            
            # Sort ready stories by priority
            ready_stories.sort(key=get_priority_score)
            
            # Add the highest priority ready story
            next_story = ready_stories[0]
            resolved.append(next_story)
            remaining.remove(next_story)
        
        return resolved
    
    # Resolve dependencies
    ordered_stories = resolve_dependencies(stories, story_deps)
    
    # Organize into sprints
    sprints = []
    current_sprint = {
        'sprint_number': 1,
        'stories': [],
        'total_hours': 0,
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'end_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    }
    
    for story in ordered_stories:
        size = extract_size_days(story['SIZE'])
        story_hours = size_estimates[size]
        
        # Check if story fits in current sprint
        if current_sprint['total_hours'] + story_hours <= sprint_capacity_hours:
            current_sprint['stories'].append(story)
            current_sprint['total_hours'] += story_hours
        else:
            # Start new sprint
            if current_sprint['stories']:  # Only add if not empty
                sprints.append(current_sprint)
            
            sprint_num = len(sprints) + 1
            start_date = datetime.now() + timedelta(weeks=sprint_num-1)
            end_date = start_date + timedelta(days=7)
            
            current_sprint = {
                'sprint_number': sprint_num,
                'stories': [story],
                'total_hours': story_hours,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
    
    # Add final sprint if it has stories
    if current_sprint['stories']:
        sprints.append(current_sprint)
    
    return sprints

# Calculate capacity
sprint_capacity_hours, size_estimates = calculate_sprint_capacity()
print(f"📊 Sprint Capacity: {sprint_capacity_hours} hours per sprint")

# Organize stories into sprints
sprints = organize_sprints(stories, sprint_capacity_hours, size_estimates)

print(f"\n📅 Sprint Organization Results:")
print("-" * 50)

# Display sprint plan
for sprint in sprints:
    print(f"\n🚀 SPRINT {sprint['sprint_number']} ({sprint['start_date']} to {sprint['end_date']})")
    print(f"   Capacity: {sprint['total_hours']}/{sprint_capacity_hours} hours")
    print(f"   Stories: {len(sprint['stories'])}")
    
    for i, story in enumerate(sprint['stories'], 1):
        size = extract_size_days(story['SIZE'])
        hours = size_estimates[size]
        print(f"   {i}. {story['STORY_ID']}: {story['TITLE'][:50]}... [{size}, {hours}h]")
        print(f"      Priority: {story['PRIORITY']} | Epic: {story['EPIC']}")

# Create sprint deliverables summary
print(f"\n🎯 Sprint Deliverables Summary:")
print("=" * 50)

sprint_deliverables = {}
for sprint in sprints:
    sprint_num = sprint['sprint_number']
    deliverables = []
    
    for story in sprint['stories']:
        epic = story['EPIC']
        title = story['TITLE']
        deliverables.append(f"{epic}: {title}")
    
    sprint_deliverables[f"Sprint {sprint_num}"] = {
        'dates': f"{sprint['start_date']} to {sprint['end_date']}",
        'deliverables': deliverables,
        'business_impact': get_sprint_business_impact(sprint['stories'])
    }

def get_sprint_business_impact(stories):
    """Determine business impact of sprint stories"""
    impacts = []
    for story in stories:
        if 'P0' in story['PRIORITY']:
            if 'Landing Page' in story['TITLE']:
                impacts.append("🚨 CRITICAL: Restore customer access")
            elif 'Registration' in story['TITLE']:
                impacts.append("🚨 CRITICAL: Enable user onboarding")
            elif 'Subscription' in story['TITLE']:
                impacts.append("💰 CRITICAL: Enable revenue generation")
            elif 'Dashboard' in story['TITLE']:
                impacts.append("✅ CRITICAL: Complete onboarding flow")
        elif 'P1' in story['PRIORITY']:
            if 'Deal' in story['TITLE']:
                impacts.append("🎯 HIGH: Core platform functionality")
            elif 'AI' in story['TITLE']:
                impacts.append("🤖 HIGH: Competitive advantage")
        elif 'P2' in story['PRIORITY']:
            impacts.append("🌟 MEDIUM: Platform enhancement")
    
    return impacts

# Update deliverables with business impact
for sprint_key, sprint_info in sprint_deliverables.items():
    sprint_num = int(sprint_key.split()[1])
    sprint_stories = sprints[sprint_num - 1]['stories']
    sprint_info['business_impact'] = get_sprint_business_impact(sprint_stories)

# Display deliverables
for sprint_key, sprint_info in sprint_deliverables.items():
    print(f"\n🎯 {sprint_key} ({sprint_info['dates']}):")
    for impact in sprint_info['business_impact']:
        print(f"   {impact}")

# Create milestone timeline
print(f"\n🏆 Major Milestones Timeline:")
print("=" * 50)

milestones = [
    {
        'week': 1,
        'milestone': 'Customer Access Restored',
        'description': 'Landing page live, users can access platform',
        'business_value': 'Stops customer loss, enables marketing'
    },
    {
        'week': 2, 
        'milestone': 'User Onboarding Complete',
        'description': 'Registration, verification, welcome flow working',
        'business_value': 'Users can sign up and get started'
    },
    {
        'week': 3,
        'milestone': 'Revenue Generation Active',
        'description': 'Subscription selection and payment processing',
        'business_value': 'First paying customers, revenue stream'
    },
    {
        'week': 4,
        'milestone': 'Core Platform Functional',
        'description': 'Deal creation and pipeline management',
        'business_value': 'Core value proposition delivered'
    },
    {
        'week': 6,
        'milestone': 'AI Intelligence Live',
        'description': 'AI-powered deal analysis and insights',
        'business_value': 'Competitive differentiation'
    },
    {
        'week': 8,
        'milestone': 'Community Platform Ready',
        'description': 'Networking and community features',
        'business_value': 'Network effects and retention'
    }
]

for milestone in milestones:
    print(f"\n📍 Week {milestone['week']}: {milestone['milestone']}")
    print(f"   {milestone['description']}")
    print(f"   💰 Business Value: {milestone['business_value']}")

# Save sprint plan
sprint_plan = {
    'metadata': {
        'created_date': datetime.now().isoformat(),
        'total_sprints': len(sprints),
        'total_weeks': len(sprints),
        'methodology': 'BMAD v6 Level 4 Sprint Planning',
        'capacity_hours_per_sprint': sprint_capacity_hours
    },
    'sprints': sprints,
    'deliverables': sprint_deliverables,
    'milestones': milestones,
    'size_estimates': size_estimates
}

with open('bmad_sprint_plan.json', 'w') as f:
    json.dump(sprint_plan, f, indent=2)

print(f"\n🎯 Sprint Planning Summary:")
print("=" * 50)
print(f"📅 Total sprints planned: {len(sprints)}")
print(f"⏱️ Timeline: {len(sprints)} weeks")
print(f"🎯 Stories organized: {len(stories)}")
print(f"🏆 Major milestones: {len(milestones)}")
print(f"💰 Revenue milestone: Week 3")
print(f"🚀 Full platform: Week 8")

print(f"\n💾 Sprint plan saved to: bmad_sprint_plan.json")
print(f"🎯 Next: Run PROMPT 3 for execution planning")
EOF
```

---

## 📋 **PROMPT 3: Execution Planning & Codex Generation**

```bash
# BMAD v6 Story Enhancement Phase 2 - Task 3: Execution Planning
# Objective: Create detailed execution plans and Codex prompts for each sprint
# Expected Output: Ready-to-execute Codex prompts for systematic development

cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import json
from pathlib import Path
from datetime import datetime

print("⚡ BMAD v6 Execution Planning & Codex Generation")
print("=" * 70)

# Load sprint plan
if Path('bmad_sprint_plan.json').exists():
    with open('bmad_sprint_plan.json', 'r') as f:
        sprint_data = json.load(f)
    sprints = sprint_data['sprints']
    print(f"✅ Loaded sprint plan with {len(sprints)} sprints")
else:
    print("❌ Missing bmad_sprint_plan.json - Run PROMPT 2 first")
    exit(1)

def generate_codex_prompt(story, sprint_context):
    """Generate a comprehensive Codex CLI prompt for a story"""
    
    story_id = story['STORY_ID']
    title = story['TITLE']
    epic = story['EPIC']
    
    # Extract technical requirements
    frontend_req = story['TECHNICAL_REQUIREMENTS']['Frontend']
    backend_req = story['TECHNICAL_REQUIREMENTS']['Backend']
    integration_req = story['TECHNICAL_REQUIREMENTS']['Integration']
    
    # Extract acceptance criteria
    given = story['ACCEPTANCE_CRITERIA']['Given']
    when = story['ACCEPTANCE_CRITERIA']['When']
    then = story['ACCEPTANCE_CRITERIA']['Then']
    additional = story['ACCEPTANCE_CRITERIA']['And']
    
    prompt = f"""
# BMAD v6 Codex Prompt: {story_id} - {title}

## 🎯 Story Context
**Epic:** {epic}
**Priority:** {story['PRIORITY']}
**Size:** {story['SIZE']}
**Sprint:** {sprint_context['sprint_number']} ({sprint_context['start_date']} to {sprint_context['end_date']})

## 👤 User Story
**As a** {story['USER_STORY']['As_a']}
**I want** {story['USER_STORY']['I_want']}
**So that** {story['USER_STORY']['So_that']}

## ✅ Acceptance Criteria
**Given** {given}
**When** {when}
**Then** {then}
**And:**
{chr(10).join(f"- {outcome}" for outcome in additional)}

## 🔧 Technical Implementation

### Frontend Requirements:
{frontend_req}

### Backend Requirements:
{backend_req}

### Integration Requirements:
{integration_req}

## 📋 Implementation Steps

### Step 1: Setup and Planning
```bash
# Navigate to project directory
cd /mnt/c/Projects/ma-saas-platform

# Create feature branch
git checkout -b feature/{story_id.lower().replace('.', '-')}-{title.lower().replace(' ', '-')[:30]}

# Verify current state
git status
npm run test
```

### Step 2: Backend Implementation
```bash
# Backend changes (if required)
{generate_backend_steps(backend_req, story)}
```

### Step 3: Frontend Implementation  
```bash
# Frontend changes
{generate_frontend_steps(frontend_req, story)}
```

### Step 4: Integration & Testing
```bash
# Integration testing
{generate_integration_steps(integration_req, story)}
```

### Step 5: Verification & Deployment
```bash
# Run full test suite
npm run test
npm run test:e2e

# Build and verify
npm run build
npm run preview

# Deploy to staging
git add .
git commit -m "feat({epic.lower()}): {title}"
git push origin feature/{story_id.lower().replace('.', '-')}-{title.lower().replace(' ', '-')[:30]}

# Create PR
gh pr create --title "{story_id}: {title}" --body "Implements {title.lower()} for {epic}"
```

## 🧪 Testing Checklist
{chr(10).join(f"- [ ] {test}" for test in story['TESTING_STRATEGY']['Unit_Tests'])}
{chr(10).join(f"- [ ] {test}" for test in story['TESTING_STRATEGY']['Integration_Tests'])}
{chr(10).join(f"- [ ] {test}" for test in story['TESTING_STRATEGY']['User_Tests'])}
{chr(10).join(f"- [ ] {test}" for test in story['TESTING_STRATEGY']['Performance_Tests'])}

## ✅ Definition of Done
{chr(10).join(f"- [ ] {item}" for item in story['DEFINITION_OF_DONE'])}

## 🔄 Rollback Plan
**If implementation fails:** {story['ROLLBACK_PLAN']['If_Fails']}
**Dependencies impact:** {story['ROLLBACK_PLAN']['Dependencies_Impact']}

---
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Methodology:** BMAD v6 Level 4 Execution Planning
"""
    
    return prompt

def generate_backend_steps(backend_req, story):
    """Generate specific backend implementation steps"""
    if "No backend changes required" in backend_req:
        return "# No backend changes required for this story"
    
    steps = []
    
    if "api" in backend_req.lower() or "endpoint" in backend_req.lower():
        steps.append("# Create/update API endpoints")
        steps.append("# Add route handlers in backend/app/routers/")
        steps.append("# Update API documentation")
    
    if "database" in backend_req.lower() or "model" in backend_req.lower():
        steps.append("# Update database models in backend/app/models/")
        steps.append("# Create migration if needed")
        steps.append("# Update CRUD operations")
    
    if "integration" in backend_req.lower():
        steps.append("# Add integration services in backend/app/services/")
        steps.append("# Configure external API connections")
        steps.append("# Add error handling and retries")
    
    return "\n".join(steps) if steps else "# Backend implementation as per requirements"

def generate_frontend_steps(frontend_req, story):
    """Generate specific frontend implementation steps"""
    steps = []
    
    if "component" in frontend_req.lower():
        steps.append("# Create React components in frontend/src/components/")
        steps.append("# Add component styling with Tailwind CSS")
        steps.append("# Implement component logic and state management")
    
    if "page" in frontend_req.lower() or "interface" in frontend_req.lower():
        steps.append("# Create page components in frontend/src/pages/")
        steps.append("# Add routing configuration")
        steps.append("# Implement navigation and layout")
    
    if "form" in frontend_req.lower():
        steps.append("# Implement form validation with React Hook Form")
        steps.append("# Add form submission handling")
        steps.append("# Create error and success states")
    
    if "api" in frontend_req.lower():
        steps.append("# Add RTK Query API slice")
        steps.append("# Implement data fetching and caching")
        steps.append("# Add loading and error states")
    
    return "\n".join(steps) if steps else "# Frontend implementation as per requirements"

def generate_integration_steps(integration_req, story):
    """Generate specific integration implementation steps"""
    if "No" in integration_req or not integration_req.strip():
        return "# No external integrations required"
    
    steps = []
    
    if "clerk" in integration_req.lower():
        steps.append("# Configure Clerk authentication")
        steps.append("# Test user registration and login flow")
        steps.append("# Verify webhook processing")
    
    if "stripe" in integration_req.lower():
        steps.append("# Configure Stripe payment processing")
        steps.append("# Test checkout flow")
        steps.append("# Verify webhook handling")
    
    if "ai" in integration_req.lower() or "claude" in integration_req.lower():
        steps.append("# Test AI service integration")
        steps.append("# Verify API key configuration")
        steps.append("# Test response processing")
    
    return "\n".join(steps) if steps else "# Integration testing as per requirements"

# Generate Codex prompts for each sprint
print(f"\n⚡ Generating Codex Prompts for Each Sprint:")
print("-" * 50)

all_codex_prompts = {}

for sprint in sprints:
    sprint_num = sprint['sprint_number']
    print(f"\n🚀 Generating prompts for Sprint {sprint_num}...")
    
    sprint_prompts = []
    
    for story in sprint['stories']:
        prompt = generate_codex_prompt(story, sprint)
        sprint_prompts.append({
            'story_id': story['STORY_ID'],
            'title': story['TITLE'],
            'prompt': prompt
        })
        print(f"   ✅ {story['STORY_ID']}: {story['TITLE'][:40]}...")
    
    all_codex_prompts[f"sprint_{sprint_num}"] = {
        'sprint_info': {
            'number': sprint_num,
            'start_date': sprint['start_date'],
            'end_date': sprint['end_date'],
            'total_stories': len(sprint['stories'])
        },
        'prompts': sprint_prompts
    }

# Create sprint execution guide
execution_guide = {
    'metadata': {
        'created_date': datetime.now().isoformat(),
        'methodology': 'BMAD v6 Level 4 Execution Planning',
        'total_sprints': len(sprints),
        'total_prompts': sum(len(sprint['prompts']) for sprint in all_codex_prompts.values())
    },
    'execution_instructions': {
        'overview': 'Execute prompts in sprint order, one story at a time',
        'daily_workflow': [
            'Start with highest priority story in current sprint',
            'Copy-paste Codex prompt into Cursor CLI',
            'Follow implementation steps systematically',
            'Complete testing checklist before moving to next story',
            'Commit and push changes with proper commit message',
            'Update sprint progress tracking'
        ],
        'sprint_ceremonies': [
            'Sprint Planning: Review upcoming sprint prompts',
            'Daily Standup: Progress check against current story',
            'Sprint Review: Demo completed stories',
            'Sprint Retrospective: Process improvement'
        ]
    },
    'codex_prompts': all_codex_prompts
}

# Save execution guide
with open('bmad_execution_guide.json', 'w') as f:
    json.dump(execution_guide, f, indent=2)

# Create individual prompt files for easy access
prompts_dir = Path('codex_prompts')
prompts_dir.mkdir(exist_ok=True)

for sprint_key, sprint_data in all_codex_prompts.items():
    sprint_num = sprint_data['sprint_info']['number']
    
    for prompt_data in sprint_data['prompts']:
        story_id = prompt_data['story_id']
        filename = f"{story_id.replace('.', '_')}_prompt.md"
        
        with open(prompts_dir / filename, 'w') as f:
            f.write(prompt_data['prompt'])

print(f"\n🎯 Execution Planning Summary:")
print("=" * 50)
print(f"📅 Total sprints: {len(sprints)}")
print(f"⚡ Total Codex prompts: {sum(len(sprint['prompts']) for sprint in all_codex_prompts.values())}")
print(f"📁 Individual prompt files: {len(list(prompts_dir.glob('*.md')))}")
print(f"🎯 Ready for systematic execution")

print(f"\n💾 Files created:")
print(f"   📋 bmad_execution_guide.json - Complete execution guide")
print(f"   📁 codex_prompts/ - Individual prompt files")

print(f"\n🚀 Next Steps:")
print(f"   1. Review Sprint 1 prompts in codex_prompts/")
print(f"   2. Begin execution with E1_P0_001_prompt.md")
print(f"   3. Follow systematic daily workflow")
print(f"   4. Track progress against sprint milestones")

print(f"\n🎯 PHASE 2 COMPLETE - Ready for Systematic Execution")
EOF
```

---

## 🎯 **Phase 2 Completion Checklist**

### **Execute These Prompts in Sequence:**
- [ ] **PROMPT 1**: Critical Gap Story Creation
- [ ] **PROMPT 2**: Sprint Organization & Prioritization
- [ ] **PROMPT 3**: Execution Planning & Codex Generation

### **Expected Outputs:**
- [ ] `critical_gap_stories_enhanced.json` - Enhanced stories with acceptance criteria
- [ ] `bmad_sprint_plan.json` - 8-week sprint organization
- [ ] `bmad_execution_guide.json` - Complete execution guide
- [ ] `codex_prompts/` - Individual Codex prompts for each story

### **Success Criteria:**
- [ ] All 8 critical gap stories enhanced with clear acceptance criteria
- [ ] Stories organized into executable sprints with dependencies
- [ ] Codex prompts ready for copy-paste execution
- [ ] Clear 8-week roadmap to revenue generation
- [ ] Systematic daily workflow defined

---

## 🚀 **What Happens Next (Execution Phase)**

After completing Phase 2, you'll have:

1. **8 Enhanced Critical Stories** with crystal-clear acceptance criteria
2. **Systematic Sprint Plan** organized by priority and dependencies  
3. **Ready-to-Execute Codex Prompts** for each story
4. **Clear 8-Week Roadmap** to revenue generation
5. **Daily Workflow Process** for systematic execution

**Execute these prompts to transform your 19,441 stories into a systematic, executable plan that will get your M&A platform generating revenue within 8 weeks.**
