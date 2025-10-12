# BMad document-project Workflow - Quick Start Guide

**Version**: 1.2.0
**Added**: October 12, 2025
**Location**: `bmad/bmm/workflows/1-analysis/document-project/`
**Purpose**: Comprehensive brownfield codebase analysis and documentation

---

## What It Does

Automatically analyzes and documents your existing codebase, creating comprehensive reference documentation for AI-assisted development and epic planning.

---

## Quick Start (3 Steps)

### 1. Run the Workflow

```bash
# From project root
cd c:\Projects\ma-saas-platform

# Launch workflow
bmad analyst document-project
```

### 2. Choose Scan Level

- **Quick** (2-5 min) - Overview and basic structure ⭐ Recommended for first run
- **Deep** (10-30 min) - Detailed analysis with code patterns
- **Exhaustive** (30-120 min) - Complete deep-dive documentation

### 3. Review Output

Check `docs/` folder for generated files:

- `index.md` - Master documentation entry point
- `architecture.md` - System architecture
- `source-tree.md` - Directory structure
- `project-scan-report.json` - Resumption state

---

## Use Cases for M&A Platform

### Backend Documentation

```bash
# Document FastAPI backend
bmad analyst document-project
# Choose: Quick scan
# Directory: backend/
```

**Generates**:

- FastAPI endpoint documentation
- Database model documentation
- Service layer architecture
- Dependencies and integrations

### Frontend Analysis

```bash
# Document React frontend
bmad analyst document-project
# Choose: Quick scan
# Directory: frontend/
```

**Generates**:

- Component hierarchy
- State management patterns
- Routing structure
- API integrations

### Full Platform Baseline

```bash
# Document entire platform
bmad analyst document-project
# Choose: Deep scan
# Directory: . (project root)
```

**Generates**:

- Multi-part project documentation
- Cross-system integrations
- Complete architecture map
- Technical debt report

---

## Scan Level Comparison

| Level          | Time       | Best For            | Output Detail               |
| -------------- | ---------- | ------------------- | --------------------------- |
| **Quick**      | 2-5 min    | First run, overview | Structure + tech stack      |
| **Deep**       | 10-30 min  | Module analysis     | + Patterns + dependencies   |
| **Exhaustive** | 30-120 min | Complete baseline   | + Deep-dive docs per module |

---

## Key Features

### ✅ Resumable

If interrupted, workflow saves state and can resume:

- Looks for `project-scan-report.json`
- Offers to resume from last step
- Safe to pause for large codebases

### ✅ Context-Safe

Write-as-you-go approach prevents memory issues:

- Generates docs incrementally
- No context window exhaustion
- Suitable for large projects

### ✅ Multi-Part Support

Handles complex project structures:

- Monorepos with multiple apps
- Separate frontend/backend repos
- Microservices architectures
- CLI tools and libraries

### ✅ Smart Detection

Automatically identifies:

- 12+ project types (web, mobile, backend, etc.)
- Tech stack and frameworks
- Architecture patterns
- Integration points
- Technical debt indicators

---

## Output Files

### Standard Outputs (All Scan Levels)

```
docs/
├── index.md                     # Master documentation
├── architecture.md              # System architecture
├── source-tree.md              # Directory structure
├── project-scan-report.json    # State file (resumption)
└── tech-stack.md               # Technology inventory
```

### Deep/Exhaustive Additional Outputs

```
docs/
├── modules/
│   ├── {module-name}-deep-dive.md
│   └── {module-name}-patterns.md
├── dependencies.md
├── integration-points.md
└── technical-debt-report.md
```

---

## When to Use

### ✅ Perfect For

- New team members joining project
- Starting epic planning on brownfield code
- Before major refactoring
- Technical debt assessment
- AI context preparation
- Architecture documentation updates

### ⚠️ Not Needed For

- Greenfield (new) projects
- Single-file changes
- Well-documented codebases
- Level 0-1 projects

---

## Common Workflows

### Scenario 1: First-Time Documentation

```bash
1. Run Quick scan on backend/
2. Review generated architecture.md
3. Run Quick scan on frontend/
4. Run Deep scan on critical modules
5. Use docs for epic planning
```

### Scenario 2: Pre-Sprint Analysis

```bash
1. Check if project-scan-report.json exists
2. If > 1 week old, re-run Quick scan
3. Review technical debt report
4. Update epic priorities based on findings
```

### Scenario 3: New Developer Onboarding

```bash
1. Run Deep scan on project root
2. Generate complete documentation set
3. New developer reads index.md
4. Links to architecture.md and module docs
5. Reduces onboarding time by 50%
```

---

## Integration with BMad Workflows

### Before Planning Phase

```
document-project (Analysis Phase)
    ↓ Generates baseline documentation
plan-project (Planning Phase)
    ↓ Uses documented architecture
3-solutioning (Solutioning Phase)
    ↓ Extends architecture
Implementation (Development Phase)
```

### Planning Phase Requirement

The `plan-project` workflow now checks for baseline documentation:

```
If brownfield && no documentation:
    HALT → "Run document-project workflow first"
```

---

## Tips & Best Practices

### 🎯 Start Small

- First run: Quick scan on one directory
- Validate output quality
- Then expand to larger scopes

### 📊 Regular Updates

- Re-run monthly or after major changes
- Keep documentation in sync with code
- Track technical debt reduction

### 🔄 Use Resumability

- Large codebases: Run in stages
- Safe to interrupt and resume
- State saved in JSON file

### 📝 Review Generated Docs

- Validate accuracy
- Add human insights
- Use as AI context for development

### 🚀 Speed Optimization

- Exclude `node_modules/`, `venv/`, etc.
- Focus on source directories
- Use Quick scan for frequent updates

---

## Troubleshooting

### Issue: Scan Takes Too Long

**Solution**:

- Start with Quick scan
- Exclude build directories
- Focus on specific modules

### Issue: Output Too Generic

**Solution**:

- Use Deep or Exhaustive scan
- Ensure project type detected correctly
- Check tech stack detection

### Issue: Resume Not Offered

**Solution**:

- Check for `project-scan-report.json` in output folder
- Verify JSON file not corrupted
- If > 7 days old, workflow starts fresh

### Issue: Missing Architecture Details

**Solution**:

- Run Deep scan instead of Quick
- Check if architecture templates match project type
- Manually enhance generated architecture.md

---

## Next Steps After Documentation

1. **Review Baseline**: Read `index.md` and `architecture.md`
2. **Identify Gaps**: Note areas needing improvement
3. **Update Planning**: Use findings in epic planning
4. **Share Context**: Provide docs to AI assistants
5. **Track Debt**: Monitor technical debt reduction

---

## Advanced Usage

### Custom Output Location

Configured in: `bmad/bmm/config.yaml`

```yaml
output_folder: '{project-root}/docs'
```

### Architecture Template Selection

Auto-detected from: `bmad/bmm/workflows/3-solutioning/templates/`

- Backend API templates
- Frontend SPA templates
- Microservices templates
- Monorepo templates

### Documentation Requirements

Defined in: `documentation-requirements.csv`

- Project type specific
- Customizable per domain
- Extensible for new project types

---

## Command Reference

```bash
# Standard usage
bmad analyst document-project

# With specific directory
cd backend && bmad analyst document-project

# Resume interrupted scan
bmad analyst document-project
# Choose option: Resume from where we left off

# Fresh scan (ignore previous state)
bmad analyst document-project
# Choose option: Start fresh
```

---

## Support & Documentation

- **Full README**: `bmad/bmm/workflows/1-analysis/document-project/README.md`
- **Workflow Config**: `bmad/bmm/workflows/1-analysis/document-project/workflow.yaml`
- **Template Examples**: `bmad/bmm/workflows/1-analysis/document-project/templates/`
- **Upstream Issues**: https://github.com/bmad-code-org/BMAD-METHOD/issues

---

## Version History

- **v1.2.0** (October 12, 2025) - Added to your project
  - Context-safe architecture
  - Resumable workflows
  - Write-as-you-go documentation
  - Intelligent batching for large projects

---

**🎯 Recommended First Action**: Run Quick scan on `backend/` directory to establish baseline documentation for your M&A platform.

```bash
cd c:\Projects\ma-saas-platform
bmad analyst document-project
# Select: Quick (2-5 min)
# Directory: backend/
```

This will generate comprehensive documentation of your existing FastAPI backend, providing critical context for informed epic planning and systematic development.

---

**Updated**: October 12, 2025
**Status**: Ready for Production Use ✅
