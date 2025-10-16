# 🔍 BMAD v6 Story Audit Phase 1: Comprehensive Story Extraction

**Date:** 2025-10-14  
**Phase:** Story Audit & Enhancement - Phase 1  
**Objective:** Extract and catalog all existing stories, improvements, and planned features  
**Timeline:** 1-2 days  
**Methodology:** BMAD v6 Level 4 Story Discovery  

---

## 📋 **PROMPT 1: Codebase Story Extraction**

```bash
# BMAD v6 Story Audit Phase 1 - Task 1: Codebase Analysis
# Objective: Extract all stories from existing code, comments, and TODO items
# Expected Output: Comprehensive list of implemented and planned features

cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import os
import re
import json
from pathlib import Path
from collections import defaultdict

print("🔍 BMAD v6 Comprehensive Codebase Story Extraction")
print("=" * 70)

# Story extraction patterns
story_patterns = {
    'todo_comments': r'(?i)(?:TODO|FIXME|HACK|NOTE|BUG):\s*(.+)',
    'user_stories': r'(?i)(?:as a|as an)\s+(.+?)(?:i want|i need)\s+(.+?)(?:so that|because)\s+(.+)',
    'feature_comments': r'(?i)(?:feature|epic|story):\s*(.+)',
    'api_endpoints': r'@app\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']',
    'react_components': r'(?:function|const)\s+([A-Z][a-zA-Z0-9]+)(?:\s*=|\s*\()',
    'database_models': r'class\s+([A-Z][a-zA-Z0-9]+)(?:\([^)]*\))?:',
    'service_methods': r'(?:def|async def)\s+([a-z_][a-z0-9_]*)\s*\(',
}

def extract_from_file(file_path, patterns):
    """Extract stories and features from a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        results = {}
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                results[pattern_name] = matches
        
        return results
    except Exception as e:
        return {}

def scan_directory(directory, file_extensions):
    """Scan directory for relevant files"""
    files_to_scan = []
    for ext in file_extensions:
        files_to_scan.extend(Path(directory).rglob(f"*.{ext}"))
    return files_to_scan

# Define file types to scan
file_extensions = {
    'python': ['py'],
    'javascript': ['js', 'jsx', 'ts', 'tsx'],
    'documentation': ['md', 'txt', 'rst'],
    'configuration': ['yaml', 'yml', 'json', 'toml'],
    'sql': ['sql'],
}

all_stories = defaultdict(list)
file_analysis = {}

print("\n📂 Scanning Project Structure:")
print("-" * 50)

# Scan each directory
directories_to_scan = [
    'backend',
    'frontend', 
    'docs',
    'mcp-server',
    '.',  # Root directory
]

for directory in directories_to_scan:
    if Path(directory).exists():
        print(f"\n🔍 Scanning: {directory}/")
        
        for file_type, extensions in file_extensions.items():
            files = []
            for ext in extensions:
                files.extend(Path(directory).rglob(f"*.{ext}"))
            
            print(f"   {file_type}: {len(files)} files")
            
            for file_path in files[:50]:  # Limit to prevent overwhelming output
                relative_path = str(file_path.relative_to('.'))
                results = extract_from_file(file_path, story_patterns)
                
                if results:
                    file_analysis[relative_path] = results
                    
                    # Categorize findings
                    for pattern_name, matches in results.items():
                        for match in matches:
                            all_stories[pattern_name].append({
                                'file': relative_path,
                                'content': match if isinstance(match, str) else str(match),
                                'type': file_type
                            })

print(f"\n📊 Story Extraction Results:")
print("-" * 50)

# Analyze TODO comments and feature requests
print(f"\n💭 TODO Comments & Feature Requests:")
todos = all_stories.get('todo_comments', [])
print(f"   Found: {len(todos)} TODO items")
for i, todo in enumerate(todos[:10]):  # Show first 10
    print(f"   {i+1}. {todo['content'][:80]}... ({todo['file']})")
if len(todos) > 10:
    print(f"   ... and {len(todos) - 10} more")

# Analyze user stories
print(f"\n👤 User Stories Found:")
user_stories = all_stories.get('user_stories', [])
print(f"   Found: {len(user_stories)} user story patterns")
for i, story in enumerate(user_stories[:5]):
    print(f"   {i+1}. As a {story['content'][0]}, I want {story['content'][1]}")

# Analyze API endpoints
print(f"\n🔌 API Endpoints:")
endpoints = all_stories.get('api_endpoints', [])
print(f"   Found: {len(endpoints)} API endpoints")
endpoint_groups = defaultdict(list)
for endpoint in endpoints:
    path = endpoint['content']
    category = path.split('/')[1] if '/' in path else 'root'
    endpoint_groups[category].append(path)

for category, paths in list(endpoint_groups.items())[:10]:
    print(f"   {category}: {len(paths)} endpoints")

# Analyze React components
print(f"\n⚛️ React Components:")
components = all_stories.get('react_components', [])
print(f"   Found: {len(components)} React components")
component_names = [comp['content'] for comp in components]
for i, comp in enumerate(component_names[:15]):
    print(f"   {i+1}. {comp}")
if len(component_names) > 15:
    print(f"   ... and {len(component_names) - 15} more")

# Analyze database models
print(f"\n🗄️ Database Models:")
models = all_stories.get('database_models', [])
print(f"   Found: {len(models)} database models")
for i, model in enumerate(models[:10]):
    print(f"   {i+1}. {model['content']}")

# Analyze service methods
print(f"\n⚙️ Service Methods:")
services = all_stories.get('service_methods', [])
print(f"   Found: {len(services)} service methods")
service_groups = defaultdict(list)
for service in services:
    file_path = service['file']
    if 'service' in file_path or 'api' in file_path:
        category = Path(file_path).stem
        service_groups[category].append(service['content'])

for category, methods in list(service_groups.items())[:8]:
    print(f"   {category}: {len(methods)} methods")

print(f"\n🎯 Story Extraction Summary:")
print("=" * 50)
print(f"📁 Files analyzed: {len(file_analysis)}")
print(f"💭 TODO items: {len(todos)}")
print(f"👤 User stories: {len(user_stories)}")
print(f"🔌 API endpoints: {len(endpoints)}")
print(f"⚛️ React components: {len(components)}")
print(f"🗄️ Database models: {len(models)}")
print(f"⚙️ Service methods: {len(services)}")

# Save detailed results
with open('story_extraction_results.json', 'w') as f:
    json.dump({
        'summary': {
            'files_analyzed': len(file_analysis),
            'todos': len(todos),
            'user_stories': len(user_stories),
            'api_endpoints': len(endpoints),
            'react_components': len(components),
            'database_models': len(models),
            'service_methods': len(services),
        },
        'detailed_findings': dict(all_stories),
        'file_analysis': file_analysis
    }, f, indent=2, default=str)

print(f"\n💾 Detailed results saved to: story_extraction_results.json")
print(f"🎯 Next: Run PROMPT 2 for documentation analysis")
EOF
```

---

## 📋 **PROMPT 2: Documentation & Planning Analysis**

```bash
# BMAD v6 Story Audit Phase 1 - Task 2: Documentation Analysis
# Objective: Extract stories from documentation, README files, and planning documents
# Expected Output: Comprehensive list of documented features and requirements

cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import os
import re
import json
from pathlib import Path
from collections import defaultdict

print("📚 BMAD v6 Documentation & Planning Analysis")
print("=" * 70)

def extract_stories_from_markdown(file_path):
    """Extract user stories, features, and requirements from markdown files"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        stories = {
            'features': [],
            'requirements': [],
            'user_stories': [],
            'epics': [],
            'todos': [],
            'business_goals': [],
            'technical_specs': []
        }
        
        # Extract features (lines starting with - or * followed by feature-like content)
        feature_pattern = r'^[\s]*[-*]\s*(.+(?:feature|capability|function|tool|system|platform|integration|management|analysis|dashboard|interface|workflow|process).+)$'
        features = re.findall(feature_pattern, content, re.MULTILINE | re.IGNORECASE)
        stories['features'] = features
        
        # Extract requirements (lines with "must", "should", "shall")
        req_pattern = r'^[\s]*[-*]?\s*(.+(?:must|should|shall|required|mandatory|essential).+)$'
        requirements = re.findall(req_pattern, content, re.MULTILINE | re.IGNORECASE)
        stories['requirements'] = requirements
        
        # Extract user stories
        user_story_pattern = r'(?:as a|as an)\s+(.+?)(?:i want|i need)\s+(.+?)(?:so that|because)\s+(.+)'
        user_stories = re.findall(user_story_pattern, content, re.IGNORECASE | re.DOTALL)
        stories['user_stories'] = user_stories
        
        # Extract epics (headers with Epic or major feature areas)
        epic_pattern = r'^#+\s*(?:epic|phase|sprint)?\s*\d*:?\s*(.+)$'
        epics = re.findall(epic_pattern, content, re.MULTILINE | re.IGNORECASE)
        stories['epics'] = epics
        
        # Extract TODOs and action items
        todo_pattern = r'(?:TODO|FIXME|ACTION|NEXT):\s*(.+)'
        todos = re.findall(todo_pattern, content, re.IGNORECASE)
        stories['todos'] = todos
        
        # Extract business goals (revenue, customer, growth related)
        business_pattern = r'^[\s]*[-*]?\s*(.+(?:revenue|customer|growth|market|business|profit|subscription|pricing|monetization).+)$'
        business_goals = re.findall(business_pattern, content, re.MULTILINE | re.IGNORECASE)
        stories['business_goals'] = business_goals
        
        # Extract technical specifications
        tech_pattern = r'^[\s]*[-*]?\s*(.+(?:API|database|integration|authentication|deployment|infrastructure|architecture|security|performance).+)$'
        technical_specs = re.findall(tech_pattern, content, re.MULTILINE | re.IGNORECASE)
        stories['technical_specs'] = technical_specs
        
        return stories
        
    except Exception as e:
        return {}

# Find all documentation files
doc_files = []
doc_patterns = ['*.md', '*.txt', '*.rst']
for pattern in doc_patterns:
    doc_files.extend(Path('.').rglob(pattern))

print(f"📄 Found {len(doc_files)} documentation files")

all_doc_stories = defaultdict(list)
file_stories = {}

# Analyze each documentation file
for doc_file in doc_files:
    relative_path = str(doc_file.relative_to('.'))
    print(f"\n📖 Analyzing: {relative_path}")
    
    stories = extract_stories_from_markdown(doc_file)
    if any(stories.values()):
        file_stories[relative_path] = stories
        
        for story_type, story_list in stories.items():
            for story in story_list:
                all_doc_stories[story_type].append({
                    'file': relative_path,
                    'content': story,
                    'source': 'documentation'
                })

print(f"\n📊 Documentation Analysis Results:")
print("-" * 50)

# Analyze features
features = all_doc_stories.get('features', [])
print(f"\n🎯 Features Identified:")
print(f"   Total: {len(features)} features")
for i, feature in enumerate(features[:15]):
    content = feature['content']
    if isinstance(content, tuple):
        content = ' '.join(content)
    print(f"   {i+1}. {content[:80]}...")
if len(features) > 15:
    print(f"   ... and {len(features) - 15} more")

# Analyze requirements
requirements = all_doc_stories.get('requirements', [])
print(f"\n📋 Requirements Identified:")
print(f"   Total: {len(requirements)} requirements")
for i, req in enumerate(requirements[:10]):
    content = req['content']
    if isinstance(content, tuple):
        content = ' '.join(content)
    print(f"   {i+1}. {content[:80]}...")

# Analyze user stories
user_stories = all_doc_stories.get('user_stories', [])
print(f"\n👤 User Stories Documented:")
print(f"   Total: {len(user_stories)} user stories")
for i, story in enumerate(user_stories[:8]):
    if isinstance(story['content'], tuple) and len(story['content']) >= 3:
        user, want, benefit = story['content'][:3]
        print(f"   {i+1}. As a {user.strip()}, I want {want.strip()}")

# Analyze epics
epics = all_doc_stories.get('epics', [])
print(f"\n🎭 Epics & Major Areas:")
print(f"   Total: {len(epics)} epics/areas")
for i, epic in enumerate(epics[:12]):
    content = epic['content']
    if isinstance(content, tuple):
        content = ' '.join(content)
    print(f"   {i+1}. {content[:60]}")

# Analyze business goals
business_goals = all_doc_stories.get('business_goals', [])
print(f"\n💰 Business Goals:")
print(f"   Total: {len(business_goals)} business goals")
for i, goal in enumerate(business_goals[:10]):
    content = goal['content']
    if isinstance(content, tuple):
        content = ' '.join(content)
    print(f"   {i+1}. {content[:80]}...")

# Analyze technical specifications
tech_specs = all_doc_stories.get('technical_specs', [])
print(f"\n🔧 Technical Specifications:")
print(f"   Total: {len(tech_specs)} technical specs")
for i, spec in enumerate(tech_specs[:10]):
    content = spec['content']
    if isinstance(content, tuple):
        content = ' '.join(content)
    print(f"   {i+1}. {content[:80]}...")

# Analyze TODOs
todos = all_doc_stories.get('todos', [])
print(f"\n📝 Action Items & TODOs:")
print(f"   Total: {len(todos)} action items")
for i, todo in enumerate(todos[:10]):
    content = todo['content']
    if isinstance(content, tuple):
        content = ' '.join(content)
    print(f"   {i+1}. {content[:80]}...")

print(f"\n🎯 Documentation Analysis Summary:")
print("=" * 50)
print(f"📄 Files analyzed: {len(file_stories)}")
print(f"🎯 Features: {len(features)}")
print(f"📋 Requirements: {len(requirements)}")
print(f"👤 User stories: {len(user_stories)}")
print(f"🎭 Epics: {len(epics)}")
print(f"💰 Business goals: {len(business_goals)}")
print(f"🔧 Technical specs: {len(tech_specs)}")
print(f"📝 Action items: {len(todos)}")

# Save documentation analysis results
with open('documentation_analysis_results.json', 'w') as f:
    json.dump({
        'summary': {
            'files_analyzed': len(file_stories),
            'features': len(features),
            'requirements': len(requirements),
            'user_stories': len(user_stories),
            'epics': len(epics),
            'business_goals': len(business_goals),
            'technical_specs': len(tech_specs),
            'todos': len(todos),
        },
        'detailed_findings': dict(all_doc_stories),
        'file_analysis': file_stories
    }, f, indent=2, default=str)

print(f"\n💾 Documentation analysis saved to: documentation_analysis_results.json")
print(f"🎯 Next: Run PROMPT 3 for commit message analysis")
EOF
```

---

## 📋 **PROMPT 3: Git History & Commit Analysis**

```bash
# BMAD v6 Story Audit Phase 1 - Task 3: Git History Analysis
# Objective: Extract stories and features from commit messages and git history
# Expected Output: Timeline of implemented features and planned improvements

cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import subprocess
import re
import json
from collections import defaultdict, Counter
from datetime import datetime

print("📈 BMAD v6 Git History & Commit Analysis")
print("=" * 70)

def run_git_command(command):
    """Run git command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except Exception as e:
        return []

def analyze_commit_message(commit_msg):
    """Analyze commit message for story patterns"""
    patterns = {
        'feature': r'(?i)(?:feat|feature)(?:\([^)]+\))?:\s*(.+)',
        'fix': r'(?i)(?:fix|bugfix)(?:\([^)]+\))?:\s*(.+)',
        'enhancement': r'(?i)(?:enhance|improve|update|upgrade)(?:\([^)]+\))?:\s*(.+)',
        'implementation': r'(?i)(?:implement|add|create)(?:\([^)]+\))?:\s*(.+)',
        'integration': r'(?i)(?:integrate|connect)(?:\([^)]+\))?:\s*(.+)',
        'deployment': r'(?i)(?:deploy|release)(?:\([^)]+\))?:\s*(.+)',
        'documentation': r'(?i)(?:docs?|documentation)(?:\([^)]+\))?:\s*(.+)',
        'testing': r'(?i)(?:test|testing)(?:\([^)]+\))?:\s*(.+)',
        'refactor': r'(?i)(?:refactor|restructure)(?:\([^)]+\))?:\s*(.+)',
        'configuration': r'(?i)(?:config|configure|setup)(?:\([^)]+\))?:\s*(.+)',
    }
    
    results = {}
    for pattern_name, pattern in patterns.items():
        match = re.search(pattern, commit_msg)
        if match:
            results[pattern_name] = match.group(1)
    
    return results

# Get git log with detailed information
print("📊 Fetching Git History...")
git_log_command = 'git log --oneline --all --since="6 months ago" --pretty=format:"%h|%ad|%s|%an" --date=short'
commit_lines = run_git_command(git_log_command)

print(f"   Found: {len(commit_lines)} commits in last 6 months")

# Analyze commits
commit_analysis = []
story_patterns = defaultdict(list)
author_stats = Counter()
date_stats = Counter()

for line in commit_lines:
    if '|' in line:
        parts = line.split('|')
        if len(parts) >= 4:
            hash_id, date, message, author = parts[:4]
            
            # Analyze commit message
            patterns = analyze_commit_message(message)
            
            commit_info = {
                'hash': hash_id,
                'date': date,
                'message': message,
                'author': author,
                'patterns': patterns
            }
            
            commit_analysis.append(commit_info)
            
            # Collect statistics
            author_stats[author] += 1
            date_stats[date] += 1
            
            # Categorize by patterns
            for pattern_type, content in patterns.items():
                story_patterns[pattern_type].append({
                    'hash': hash_id,
                    'date': date,
                    'content': content,
                    'author': author,
                    'full_message': message
                })

print(f"\n📈 Commit Analysis Results:")
print("-" * 50)

# Show commit patterns
print(f"\n🎯 Feature Development Timeline:")
features = story_patterns.get('feature', [])
print(f"   Total features: {len(features)}")
for i, feature in enumerate(features[-15:]):  # Show last 15 features
    print(f"   {feature['date']} - {feature['content'][:60]}...")

print(f"\n🔧 Implementation Activities:")
implementations = story_patterns.get('implementation', [])
print(f"   Total implementations: {len(implementations)}")
for i, impl in enumerate(implementations[-10:]):
    print(f"   {impl['date']} - {impl['content'][:60]}...")

print(f"\n🔗 Integration Work:")
integrations = story_patterns.get('integration', [])
print(f"   Total integrations: {len(integrations)}")
for i, integration in enumerate(integrations[-8:]):
    print(f"   {integration['date']} - {integration['content'][:60]}...")

print(f"\n🚀 Deployment History:")
deployments = story_patterns.get('deployment', [])
print(f"   Total deployments: {len(deployments)}")
for i, deployment in enumerate(deployments[-8:]):
    print(f"   {deployment['date']} - {deployment['content'][:60]}...")

print(f"\n🐛 Bug Fixes:")
fixes = story_patterns.get('fix', [])
print(f"   Total fixes: {len(fixes)}")
for i, fix in enumerate(fixes[-8:]):
    print(f"   {fix['date']} - {fix['content'][:60]}...")

print(f"\n⚡ Enhancements:")
enhancements = story_patterns.get('enhancement', [])
print(f"   Total enhancements: {len(enhancements)}")
for i, enhancement in enumerate(enhancements[-8:]):
    print(f"   {enhancement['date']} - {enhancement['content'][:60]}...")

# Author statistics
print(f"\n👥 Development Team Activity:")
print(f"   Active contributors: {len(author_stats)}")
for author, count in author_stats.most_common(10):
    print(f"   {author}: {count} commits")

# Recent activity
print(f"\n📅 Recent Development Activity:")
recent_dates = sorted(date_stats.keys(), reverse=True)[:14]
for date in recent_dates:
    count = date_stats[date]
    print(f"   {date}: {count} commits")

# Extract major milestones
print(f"\n🏆 Major Milestones (from commit messages):")
milestone_patterns = [
    r'(?i)(complete|finish|launch|deploy|release|live|production)',
    r'(?i)(milestone|phase|sprint|epic)',
    r'(?i)(integration|platform|system|ecosystem)',
]

milestones = []
for commit in commit_analysis:
    message = commit['message'].lower()
    for pattern in milestone_patterns:
        if re.search(pattern, message):
            milestones.append(commit)
            break

# Show recent milestones
for i, milestone in enumerate(milestones[-10:]):
    print(f"   {milestone['date']} - {milestone['message'][:70]}...")

print(f"\n🎯 Git History Analysis Summary:")
print("=" * 50)
print(f"📊 Total commits analyzed: {len(commit_analysis)}")
print(f"🎯 Features developed: {len(features)}")
print(f"🔧 Implementations: {len(implementations)}")
print(f"🔗 Integrations: {len(integrations)}")
print(f"🚀 Deployments: {len(deployments)}")
print(f"🐛 Bug fixes: {len(fixes)}")
print(f"⚡ Enhancements: {len(enhancements)}")
print(f"🏆 Major milestones: {len(milestones)}")
print(f"👥 Active contributors: {len(author_stats)}")

# Save git analysis results
with open('git_history_analysis_results.json', 'w') as f:
    json.dump({
        'summary': {
            'total_commits': len(commit_analysis),
            'features': len(features),
            'implementations': len(implementations),
            'integrations': len(integrations),
            'deployments': len(deployments),
            'fixes': len(fixes),
            'enhancements': len(enhancements),
            'milestones': len(milestones),
            'contributors': len(author_stats),
        },
        'story_patterns': dict(story_patterns),
        'author_stats': dict(author_stats),
        'recent_activity': dict(list(date_stats.items())),
        'milestones': milestones[-20:],  # Last 20 milestones
    }, f, indent=2, default=str)

print(f"\n💾 Git history analysis saved to: git_history_analysis_results.json")
print(f"🎯 Next: Run PROMPT 4 for comprehensive story consolidation")
EOF
```

---

## 📋 **PROMPT 4: Story Consolidation & Gap Analysis**

```bash
# BMAD v6 Story Audit Phase 1 - Task 4: Story Consolidation & Gap Analysis
# Objective: Consolidate all extracted stories and identify gaps
# Expected Output: Comprehensive story inventory with gap analysis

cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import json
import re
from collections import defaultdict, Counter
from pathlib import Path

print("🔄 BMAD v6 Story Consolidation & Gap Analysis")
print("=" * 70)

# Load all analysis results
analysis_files = [
    'story_extraction_results.json',
    'documentation_analysis_results.json', 
    'git_history_analysis_results.json'
]

all_data = {}
for file_name in analysis_files:
    if Path(file_name).exists():
        with open(file_name, 'r') as f:
            all_data[file_name.replace('_results.json', '')] = json.load(f)
        print(f"✅ Loaded: {file_name}")
    else:
        print(f"⚠️ Missing: {file_name}")

def normalize_story(story_text):
    """Normalize story text for deduplication"""
    if isinstance(story_text, (list, tuple)):
        story_text = ' '.join(str(x) for x in story_text)
    
    # Clean and normalize
    normalized = re.sub(r'[^\w\s]', ' ', str(story_text).lower())
    normalized = ' '.join(normalized.split())
    return normalized

def categorize_story(story_text):
    """Categorize story by domain"""
    text = str(story_text).lower()
    
    categories = {
        'authentication': ['auth', 'login', 'signup', 'user', 'clerk', 'jwt', 'token'],
        'deal_management': ['deal', 'transaction', 'm&a', 'merger', 'acquisition', 'pipeline'],
        'ai_intelligence': ['ai', 'claude', 'openai', 'analysis', 'intelligence', 'prediction'],
        'financial': ['financial', 'valuation', 'dcf', 'revenue', 'pricing', 'billing'],
        'community': ['community', 'network', 'social', 'member', 'connect'],
        'events': ['event', 'calendar', 'meeting', 'webinar', 'conference'],
        'documents': ['document', 'file', 'upload', 'storage', 'pdf'],
        'dashboard': ['dashboard', 'analytics', 'report', 'chart', 'metric'],
        'api': ['api', 'endpoint', 'rest', 'graphql', 'service'],
        'frontend': ['react', 'component', 'ui', 'interface', 'page'],
        'backend': ['database', 'model', 'schema', 'migration', 'server'],
        'deployment': ['deploy', 'production', 'staging', 'docker', 'render'],
        'integration': ['integration', 'webhook', 'sync', 'connect', 'import'],
        'security': ['security', 'permission', 'role', 'access', 'encrypt'],
        'performance': ['performance', 'optimization', 'cache', 'speed', 'load'],
    }
    
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category
    
    return 'general'

def estimate_story_size(story_text):
    """Estimate story size based on complexity indicators"""
    text = str(story_text).lower()
    
    # Size indicators
    large_indicators = ['platform', 'system', 'architecture', 'integration', 'migration']
    medium_indicators = ['feature', 'component', 'service', 'workflow', 'process']
    small_indicators = ['fix', 'update', 'add', 'create', 'simple']
    
    if any(indicator in text for indicator in large_indicators):
        return 'L'
    elif any(indicator in text for indicator in medium_indicators):
        return 'M'
    elif any(indicator in text for indicator in small_indicators):
        return 'S'
    else:
        return 'M'  # Default to medium

# Consolidate all stories
print(f"\n🔄 Consolidating Stories from All Sources:")
print("-" * 50)

consolidated_stories = []
story_sources = defaultdict(list)
duplicate_tracker = set()

# Process codebase stories
if 'story_extraction' in all_data:
    codebase_data = all_data['story_extraction']['detailed_findings']
    for story_type, stories in codebase_data.items():
        for story in stories:
            normalized = normalize_story(story['content'])
            if normalized not in duplicate_tracker and len(normalized) > 10:
                duplicate_tracker.add(normalized)
                
                story_entry = {
                    'id': f"CB_{len(consolidated_stories)+1:03d}",
                    'source': 'codebase',
                    'type': story_type,
                    'content': story['content'],
                    'file': story.get('file', ''),
                    'category': categorize_story(story['content']),
                    'size': estimate_story_size(story['content']),
                    'status': 'identified'
                }
                consolidated_stories.append(story_entry)
                story_sources['codebase'].append(story_entry)

print(f"   Codebase stories: {len(story_sources['codebase'])}")

# Process documentation stories
if 'documentation_analysis' in all_data:
    doc_data = all_data['documentation_analysis']['detailed_findings']
    for story_type, stories in doc_data.items():
        for story in stories:
            normalized = normalize_story(story['content'])
            if normalized not in duplicate_tracker and len(normalized) > 10:
                duplicate_tracker.add(normalized)
                
                story_entry = {
                    'id': f"DOC_{len(consolidated_stories)+1:03d}",
                    'source': 'documentation',
                    'type': story_type,
                    'content': story['content'],
                    'file': story.get('file', ''),
                    'category': categorize_story(story['content']),
                    'size': estimate_story_size(story['content']),
                    'status': 'documented'
                }
                consolidated_stories.append(story_entry)
                story_sources['documentation'].append(story_entry)

print(f"   Documentation stories: {len(story_sources['documentation'])}")

# Process git history stories
if 'git_history_analysis' in all_data:
    git_data = all_data['git_history_analysis']['story_patterns']
    for story_type, stories in git_data.items():
        for story in stories:
            normalized = normalize_story(story['content'])
            if normalized not in duplicate_tracker and len(normalized) > 10:
                duplicate_tracker.add(normalized)
                
                story_entry = {
                    'id': f"GIT_{len(consolidated_stories)+1:03d}",
                    'source': 'git_history',
                    'type': story_type,
                    'content': story['content'],
                    'file': story.get('hash', ''),
                    'category': categorize_story(story['content']),
                    'size': estimate_story_size(story['content']),
                    'status': 'implemented' if story_type in ['feature', 'implementation'] else 'in_progress'
                }
                consolidated_stories.append(story_entry)
                story_sources['git_history'].append(story_entry)

print(f"   Git history stories: {len(story_sources['git_history'])}")

print(f"\n📊 Consolidated Story Analysis:")
print("-" * 50)
print(f"Total unique stories: {len(consolidated_stories)}")

# Analyze by category
category_stats = Counter(story['category'] for story in consolidated_stories)
print(f"\n🏷️ Stories by Category:")
for category, count in category_stats.most_common():
    print(f"   {category}: {count} stories")

# Analyze by size
size_stats = Counter(story['size'] for story in consolidated_stories)
print(f"\n📏 Stories by Size:")
for size, count in size_stats.most_common():
    size_name = {'S': 'Small (1 day)', 'M': 'Medium (2-3 days)', 'L': 'Large (4+ days)'}
    print(f"   {size_name.get(size, size)}: {count} stories")

# Analyze by status
status_stats = Counter(story['status'] for story in consolidated_stories)
print(f"\n📈 Stories by Status:")
for status, count in status_stats.most_common():
    print(f"   {status}: {count} stories")

# Identify top categories for detailed analysis
print(f"\n🔍 Top Categories Detailed Analysis:")
top_categories = [cat for cat, count in category_stats.most_common(8)]

for category in top_categories:
    category_stories = [s for s in consolidated_stories if s['category'] == category]
    implemented = len([s for s in category_stories if s['status'] == 'implemented'])
    total = len(category_stories)
    completion = (implemented / total * 100) if total > 0 else 0
    
    print(f"\n   📂 {category.upper()} ({total} stories, {completion:.1f}% complete)")
    
    # Show sample stories
    for i, story in enumerate(category_stories[:5]):
        content = str(story['content'])
        if isinstance(story['content'], (list, tuple)):
            content = ' '.join(str(x) for x in story['content'])
        print(f"      {i+1}. [{story['size']}] {content[:60]}...")

# Gap Analysis
print(f"\n🔍 Gap Analysis - Missing Critical Stories:")
print("-" * 50)

# Define critical user journeys
critical_journeys = {
    'customer_onboarding': [
        'landing page access',
        'user registration',
        'email verification', 
        'subscription selection',
        'payment processing',
        'welcome dashboard'
    ],
    'deal_management': [
        'deal creation',
        'deal editing',
        'deal pipeline view',
        'deal status updates',
        'deal analytics',
        'deal sharing'
    ],
    'ai_features': [
        'ai deal analysis',
        'valuation modeling',
        'risk assessment',
        'market insights',
        'recommendation engine'
    ],
    'community_features': [
        'member profiles',
        'networking interface',
        'deal sharing',
        'discussion forums',
        'event calendar'
    ]
}

missing_stories = []
for journey, required_features in critical_journeys.items():
    print(f"\n   🎯 {journey.upper()} Journey:")
    for feature in required_features:
        # Check if feature exists in stories
        found = any(feature.lower() in str(story['content']).lower() 
                   for story in consolidated_stories)
        if found:
            print(f"      ✅ {feature}")
        else:
            print(f"      ❌ {feature} - MISSING")
            missing_stories.append({
                'journey': journey,
                'feature': feature,
                'priority': 'high' if journey in ['customer_onboarding', 'deal_management'] else 'medium'
            })

print(f"\n🚨 Critical Missing Stories: {len(missing_stories)}")
for story in missing_stories[:10]:
    print(f"   - {story['feature']} ({story['journey']})")

# Save consolidated results
consolidated_data = {
    'summary': {
        'total_stories': len(consolidated_stories),
        'by_source': {source: len(stories) for source, stories in story_sources.items()},
        'by_category': dict(category_stats),
        'by_size': dict(size_stats),
        'by_status': dict(status_stats),
        'missing_critical': len(missing_stories)
    },
    'all_stories': consolidated_stories,
    'missing_stories': missing_stories,
    'critical_journeys': critical_journeys
}

with open('consolidated_story_analysis.json', 'w') as f:
    json.dump(consolidated_data, f, indent=2, default=str)

print(f"\n🎯 Story Consolidation Summary:")
print("=" * 50)
print(f"📊 Total unique stories identified: {len(consolidated_stories)}")
print(f"📂 Categories covered: {len(category_stats)}")
print(f"🚨 Critical gaps identified: {len(missing_stories)}")
print(f"📈 Implementation status:")
for status, count in status_stats.items():
    percentage = (count / len(consolidated_stories) * 100)
    print(f"   {status}: {count} stories ({percentage:.1f}%)")

print(f"\n💾 Consolidated analysis saved to: consolidated_story_analysis.json")
print(f"🎯 PHASE 1 COMPLETE - Ready for Phase 2: Story Enhancement")
print(f"\n🚀 Next Steps:")
print(f"   1. Review consolidated story list")
print(f"   2. Prioritize critical missing stories")
print(f"   3. Begin Phase 2: Story Enhancement & Clarification")
EOF
```

---

## 🎯 **Phase 1 Completion Checklist**

### **Execute These Prompts in Sequence:**
- [ ] **PROMPT 1**: Codebase Story Extraction
- [ ] **PROMPT 2**: Documentation & Planning Analysis  
- [ ] **PROMPT 3**: Git History & Commit Analysis
- [ ] **PROMPT 4**: Story Consolidation & Gap Analysis

### **Expected Outputs:**
- [ ] `story_extraction_results.json` - Codebase analysis
- [ ] `documentation_analysis_results.json` - Documentation analysis
- [ ] `git_history_analysis_results.json` - Git history analysis
- [ ] `consolidated_story_analysis.json` - Complete story inventory

### **Success Criteria:**
- [ ] All 60+ stories identified and cataloged
- [ ] Critical gaps in user journeys identified
- [ ] Stories categorized by domain and priority
- [ ] Implementation status assessed for each story
- [ ] Ready for Phase 2 enhancement process

---

## 🚀 **What Happens Next (Phase 2)**

After completing Phase 1, we'll move to **Phase 2: Story Enhancement & Clarification** where we'll:

1. **Rewrite each story** using the enhanced BMAD v6 template
2. **Add crystal-clear acceptance criteria** for every story
3. **Define testing and verification steps** for each story
4. **Organize stories into executable sprints** with dependencies
5. **Create the systematic execution plan** for your 8-week roadmap

**Ready to begin? Execute PROMPT 1 first, then proceed through all four prompts in sequence.**
