# Automated Offer Stack Generator UX/UI Specification

_Generated on January 12, 2025 by BMad User_

## Executive Summary

The Automated Offer Stack Generator transforms M&A proposal creation from weeks of manual work to minutes of intelligent automation. This UX specification defines the user experience for generating professional acquisition proposals with 19-worksheet Excel models, interactive what-if analysis, and investment banking quality exports. The interface serves M&A professionals who need to create compelling, accurate offers quickly while maintaining the sophistication expected by sellers and stakeholders.

---

## 1. UX Goals and Principles

### 1.1 Target User Personas

**Primary Persona: Senior M&A Advisor**

- 15+ years experience in mergers & acquisitions
- Manages 5-10 active deals simultaneously
- Values accuracy, speed, and professional presentation
- Familiar with Excel financial modeling
- Time-constrained with high client expectations

**Secondary Persona: Investment Banking Analyst**

- 2-5 years experience in investment banking
- Responsible for financial modeling and analysis
- Tech-savvy but appreciates guided workflows
- Needs to produce error-free, professional outputs
- Works under tight deadlines with senior oversight

**Tertiary Persona: Business Broker**

- Represents smaller middle-market transactions
- May lack advanced financial modeling skills
- Values automation and templates
- Needs confidence in recommendations to clients
- Budget-conscious with efficiency focus

### 1.2 Usability Goals

**Speed & Efficiency**

- Complete offer generation in <5 minutes
- Real-time what-if analysis in <2 seconds
- One-click export to multiple formats
- Minimal learning curve for Excel users

**Accuracy & Trust**

- 95%+ accuracy vs manual models
- Clear visibility into assumptions and calculations
- Audit trail for all modifications
- Professional quality matching investment banks

**Flexibility & Control**

- Customize any scenario component
- Interactive sensitivity analysis
- Multiple funding structure options
- Scenario comparison capabilities

### 1.3 Design Principles

**Professional First**

- Investment banking aesthetic and quality
- Clean, sophisticated interface design
- Corporate branding integration capabilities
- Error-free presentation standards

**Intelligence Transparency**

- Clear explanations of AI recommendations
- Visible calculation methodologies
- Confidence scoring for predictions
- Override capabilities for all suggestions

**Progressive Disclosure**

- Simple wizard for basic scenarios
- Advanced options for power users
- Contextual help and guidance
- Optional complexity layers

---

## 2. Information Architecture

### 2.1 Site Map

```
Offer Generator
├── Dashboard
│   ├── Recent Offers
│   ├── Templates
│   └── Market Intelligence
├── New Offer Wizard
│   ├── Target Company Setup
│   ├── Deal Parameters
│   ├── Funding Preferences
│   └── Generate Scenarios
├── Scenario Analysis
│   ├── Scenario Comparison
│   ├── What-If Analysis
│   ├── Sensitivity Analysis
│   └── Risk Assessment
├── Export Center
│   ├── Excel Models
│   ├── PowerPoint Presentations
│   ├── PDF Summaries
│   └── Custom Exports
└── Settings
    ├── Templates
    ├── Branding
    └── Preferences
```

### 2.2 Navigation Structure

**Primary Navigation**

- Dashboard (Home)
- New Offer
- My Offers
- Templates
- Market Intel
- Settings

**Secondary Navigation** (within offer analysis)

- Overview
- Scenarios
- What-If
- Exports
- History

---

## 3. User Flows

### User Flow 1: Quick Offer Generation

**Goal:** Generate complete offer stack in minimal time
**Trigger:** User needs proposal for new opportunity

1. **Start** → Dashboard
2. **Action** → Click "New Offer" button
3. **Input** → Enter target company details
4. **Configure** → Set purchase price range and preferences
5. **Generate** → AI creates 5 scenarios automatically
6. **Review** → Compare scenarios in summary table
7. **Select** → Choose recommended scenario
8. **Export** → Download Excel model and presentation
9. **Complete** → Offer ready for stakeholder review

**Success Metrics:** <5 minutes total time, 90%+ user satisfaction

### User Flow 2: Advanced Scenario Customization

**Goal:** Create highly customized funding structure
**Trigger:** Standard scenarios don't meet specific requirements

1. **Start** → Existing offer analysis
2. **Customize** → Select scenario to modify
3. **Adjust** → Change funding components and terms
4. **Model** → Real-time recalculation of metrics
5. **Validate** → Review impact on returns and risk
6. **Save** → Create new custom scenario
7. **Compare** → Side-by-side with original scenarios
8. **Finalize** → Export customized analysis

**Success Metrics:** <10 minutes for complex customization

### User Flow 3: Interactive What-If Analysis

**Goal:** Understand scenario sensitivity to key variables
**Trigger:** Need to stress-test assumptions

1. **Start** → Scenario analysis view
2. **Select** → Choose what-if analysis tab
3. **Adjust** → Use sliders for key variables
4. **Observe** → Real-time updates to charts and metrics
5. **Test** → Multiple sensitivity scenarios
6. **Document** → Save key insights and scenarios
7. **Export** → Include in presentation materials

**Success Metrics:** <2 seconds for each calculation update

### User Flow 4: Multi-Format Export Generation

**Goal:** Create professional presentation package
**Trigger:** Ready to present to stakeholders

1. **Start** → Completed offer analysis
2. **Access** → Navigate to export center
3. **Select** → Choose export formats needed
4. **Customize** → Apply branding and formatting
5. **Generate** → Create all exports (2-3 minutes)
6. **Download** → Access completed files
7. **Distribute** → Share with stakeholders

**Success Metrics:** Professional quality, <5 minutes total

### User Flow 5: Collaborative Review Process

**Goal:** Share analysis for team review and feedback
**Trigger:** Need stakeholder input before finalization

1. **Start** → Completed offer analysis
2. **Share** → Generate collaboration link
3. **Invite** → Add team members with permissions
4. **Review** → Stakeholders provide feedback
5. **Iterate** → Modify scenarios based on input
6. **Approve** → Final sign-off from senior team
7. **Finalize** → Lock scenarios and generate finals

**Success Metrics:** 80%+ faster review cycles

---

## 4. Component Library and Design System

### 4.1 Design System Approach

**Foundation:** Material Design 3 with financial services customizations
**Framework:** React with TypeScript for type safety
**Styling:** Tailwind CSS with custom design tokens
**Icons:** Lucide React with custom financial iconography
**Charts:** Recharts for financial data visualization

### 4.2 Core Components

**Input Components**

- `CurrencyInput`: Formatted monetary values
- `PercentageSlider`: Interactive percentage adjustments
- `DateRangePicker`: Timeline selections
- `CompanySelector`: Searchable company database
- `ScenarioBuilder`: Drag-and-drop funding structure

**Display Components**

- `MetricsCard`: Key financial metrics display
- `ScenarioComparison`: Side-by-side scenario table
- `FinancialChart`: Interactive charts and graphs
- `RiskAssessment`: Visual risk scoring
- `ProgressTracker`: Multi-step process indication

**Action Components**

- `ExportButton`: Multi-format export trigger
- `ShareDialog`: Collaboration and sharing
- `SaveScenario`: Scenario persistence
- `WhatIfPanel`: Interactive analysis controls
- `QuickActions`: Common task shortcuts

---

## 5. Visual Design Foundation

### 5.1 Color Palette

**Primary Colors**

- `primary-900`: #1E3A8A (Deep Blue - Trust, Professionalism)
- `primary-600`: #2563EB (Primary Blue - Actions, Links)
- `primary-100`: #DBEAFE (Light Blue - Backgrounds)

**Secondary Colors**

- `accent-600`: #DC2626 (Red - Alerts, Risk)
- `accent-500`: #EF4444 (Orange - Warnings)
- `success-600`: #16A34A (Green - Success, Positive)

**Neutral Colors**

- `gray-900`: #111827 (Primary Text)
- `gray-600`: #4B5563 (Secondary Text)
- `gray-100`: #F3F4F6 (Backgrounds)
- `white`: #FFFFFF (Cards, Overlays)

### 5.2 Typography

**Font Families:**

- Primary: Inter (Clean, professional, excellent readability)
- Monospace: JetBrains Mono (Financial data, code)
- Display: Inter Display (Headers, large text)

**Type Scale:**

- `text-4xl`: 36px/40px (Page headers)
- `text-2xl`: 24px/32px (Section headers)
- `text-lg`: 18px/28px (Subheadings)
- `text-base`: 16px/24px (Body text)
- `text-sm`: 14px/20px (Labels, captions)
- `text-xs`: 12px/16px (Metadata, footnotes)

### 5.3 Spacing and Layout

**Spacing Scale**

- 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px, 96px

**Layout Grid**

- 12-column CSS Grid for desktop
- 4-column for tablet
- 1-column for mobile
- 24px gutters, 16px margins

**Container Widths**

- `max-w-7xl`: 1280px (Main content)
- `max-w-4xl`: 896px (Forms, detailed views)
- `max-w-md`: 448px (Modals, sidebars)

---

## 6. Responsive Design

### 6.1 Breakpoints

- `sm`: 640px and up (Large phones)
- `md`: 768px and up (Tablets)
- `lg`: 1024px and up (Small laptops)
- `xl`: 1280px and up (Desktop)
- `2xl`: 1536px and up (Large desktop)

### 6.2 Adaptation Patterns

**Desktop (1280px+)**

- Full scenario comparison tables
- Side-by-side panels for what-if analysis
- Multiple charts and visualizations
- Complete toolbar and navigation

**Tablet (768px - 1279px)**

- Stacked scenario cards
- Collapsible panels
- Simplified charts
- Touch-optimized controls

**Mobile (< 768px)**

- Single-column layout
- Progressive disclosure
- Gesture-based navigation
- Essential features only

---

## 7. Accessibility

### 7.1 Compliance Target

**WCAG 2.1 AA Compliance**

- Full keyboard navigation
- Screen reader compatibility
- High contrast support
- Focus management

### 7.2 Key Requirements

**Keyboard Navigation**

- Tab order follows logical flow
- All interactive elements accessible
- Escape key closes modals/dropdowns
- Arrow keys for chart navigation

**Screen Reader Support**

- Semantic HTML structure
- ARIA labels for complex components
- Table headers for financial data
- Status announcements for calculations

**Visual Accessibility**

- 4.5:1 contrast ratio minimum
- No color-only information conveyance
- Scalable text up to 200%
- High contrast mode support

---

## 8. Interaction and Motion

### 8.1 Motion Principles

**Performance First**

- 60fps animations
- Hardware acceleration
- Reduced motion respect
- Loading state management

**Purposeful Animation**

- Guide user attention
- Provide feedback
- Smooth transitions
- Maintain spatial relationships

### 8.2 Key Animations

**Data Updates**

- Number counter animations for metric changes
- Chart transitions for scenario switches
- Progress bars for generation process
- Smooth slider interactions

**Navigation**

- Page transitions with subtle slides
- Modal entrance/exit
- Panel expand/collapse
- Tab switching

**Feedback**

- Button press states
- Form validation
- Success/error states
- Loading spinners

---

## 9. Design Files and Wireframes

### 9.1 Design Files

**Figma Design System**

- Complete component library
- Interactive prototypes
- Design tokens
- Usage guidelines

**File Structure:**

```
/Offer Generator Design System
├── 01-Foundations
│   ├── Colors
│   ├── Typography
│   └── Spacing
├── 02-Components
│   ├── Forms
│   ├── Data Display
│   └── Navigation
├── 03-Patterns
│   ├── Page Layouts
│   ├── Modal Patterns
│   └── Data Visualization
└── 04-Prototypes
    ├── New Offer Flow
    ├── What-If Analysis
    └── Export Process
```

### 9.2 Key Screen Layouts

**Offer Generation Dashboard**

```
┌─────────────────────────────────────────────────────┐
│ Navigation Bar                                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Welcome Back, John                [New Offer] BTN  │
│                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │Recent Offers│ │  Templates  │ │Market Intel │    │
│  │             │ │             │ │             │    │
│  │ 5 Active    │ │ 12 Available│ │ 15 Updates  │    │
│  └─────────────┘ └─────────────┘ └─────────────┘    │
│                                                     │
│  Recent Offers                         [View All]   │
│  ┌─────────────────────────────────────────────────┐│
│  │Company A  │ $5.2M │ 22.5% IRR │ 2 days ago     ││
│  │Company B  │ $8.1M │ 18.7% IRR │ 1 week ago     ││
│  └─────────────────────────────────────────────────┘│
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Scenario Comparison View**

```
┌─────────────────────────────────────────────────────┐
│ Company X Acquisition Analysis                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Scenario Comparison              [Export] [Share]   │
│                                                     │
│ ┌─────────┬─────────┬─────────┬─────────┬─────────┐ │
│ │Metric   │  Cash   │  Debt   │Seller F.│ Hybrid  │ │
│ ├─────────┼─────────┼─────────┼─────────┼─────────┤ │
│ │Price    │ $6.0M   │ $6.0M   │ $6.0M   │ $6.0M   │ │
│ │IRR      │ 18.5%   │ 25.2%   │ 22.1%   │ 24.8%   │ │
│ │Multiple │  2.4x   │  3.1x   │  2.8x   │  3.0x   │ │
│ │Accept % │  85%    │  70%    │  80%    │  82%    │ │
│ └─────────┴─────────┴─────────┴─────────┴─────────┘ │
│                                                     │
│ [What-If Analysis] [Sensitivity] [Risk Assessment]  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Interactive What-If Panel**

```
┌─────────────────────────────────────────────────────┐
│ What-If Analysis - Hybrid Scenario                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Revenue Growth    [====█====] 15%    IRR: 24.8%    │
│ EBITDA Margin     [===█=====] 12%    Multiple: 3.0x│
│ Cost Synergies    [==█======] 18%    Risk: Medium  │
│ Exit Multiple     [====█====] 8.5x                 │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │         IRR Sensitivity Chart                   │ │
│ │    30% ┌─────────────────────────────────────┐  │ │
│ │        │              ████                    │  │ │
│ │    20% │         ████      ████               │  │ │
│ │        │    ████              ████            │  │ │
│ │    10% └─────────────────────────────────────┘  │ │
│ │         Rev   EBITDA  Synerg   Exit            │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ [Reset] [Save Scenario] [Export Analysis]          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 10. Next Steps

### 10.1 Immediate Actions

**Design Phase (Week 1-2)**

- Complete high-fidelity mockups for all key screens
- Build interactive prototype for user testing
- Finalize component specifications
- Create design system documentation

**Development Handoff (Week 3)**

- Provide design tokens and assets
- Create component implementation guide
- Set up design-development collaboration tools
- Establish design review process

**User Testing (Week 4)**

- Conduct usability testing with target personas
- Test accessibility compliance
- Validate performance requirements
- Gather feedback for iterations

### 10.2 Design Handoff Checklist

**Assets Delivered**

- [ ] Complete Figma design system
- [ ] Exported SVG icons and assets
- [ ] Design tokens (colors, spacing, typography)
- [ ] Component specifications
- [ ] Interactive prototypes

**Documentation**

- [ ] UX specification (this document)
- [ ] Component usage guidelines
- [ ] Accessibility requirements
- [ ] Responsive behavior specifications
- [ ] Animation and interaction details

**Development Support**

- [ ] Design review schedule established
- [ ] QA design criteria defined
- [ ] Design system maintenance plan
- [ ] User feedback integration process

---

## Appendix

### Related Documents

- PRD: `AUTOMATED_OFFER_STACK_GENERATOR.md`
- Epics: `CLAUDE_AI_INTEGRATION_USER_STORIES.md`
- Tech Spec: `offer_generation.py`
- Architecture: `IRRESISTIBLE_MA_PLATFORM_ARCHITECTURE.md`

### Version History

| Date       | Version | Changes               | Author    |
| ---------- | ------- | --------------------- | --------- |
| 2025-01-12 | 1.0     | Initial specification | BMad User |

**Success Criteria:**

- 95%+ user task completion rate
- <5 minutes average offer generation time
- 9.0+ System Usability Scale (SUS) score
- 90%+ user satisfaction with export quality
- WCAG 2.1 AA compliance verification

This UX specification ensures the Automated Offer Stack Generator delivers a world-class user experience that matches the sophistication of the underlying financial intelligence while remaining intuitive and efficient for M&A professionals.
