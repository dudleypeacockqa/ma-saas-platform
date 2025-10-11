# Detailed Wireframe Specifications

## M&A SaaS Platform - Screen-by-Screen Design

### Version: 1.0

### Format: ASCII Wireframes with Detailed Annotations

---

## 1. MAIN DASHBOARD - LANDING PAGE

```
┌────────────────────────────────────────────────────────────────────────┐
│ ┌──────┬─────────────────────────────────────────────┬──────────────┐ │
│ │ LOGO │  Deals  Documents  Teams  Analytics  Admin │ John Smith ▼ │ │
│ │      │                                             │ ○ Settings   │ │
│ └──────┴─────────────────────────────────────────────┴──────────────┘ │
│                                                                        │
│ Welcome back, John                                     Thursday, Oct 26│
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │                        Quick Stats                                  ││
│ │ ┌─────────────┬─────────────┬─────────────┬─────────────────────┐││
│ │ │ Active Deals│ This Week   │ Closing Soon│ Action Required     │││
│ │ │    [ 23 ]   │   [ +3 ]    │    [ 5 ]    │      [ 8 ]         │││
│ │ │    £347M    │   £45.2M    │   £125M     │   3 approvals      │││
│ │ └─────────────┴─────────────┴─────────────┴─────────────────────┘││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                        │
│ ┌─────────────────────────────────┬──────────────────────────────────┐│
│ │ My Active Deals                 │ Upcoming Tasks                   ││
│ │ ┌─────────────────────────────┐│ ┌──────────────────────────────┐││
│ │ │ DEAL-001 TechCo        ●●●○○││ │ □ Review SPA draft    Today  │││
│ │ │ Due Diligence    £45M  ↗75% ││ │ □ Call with TechCo    2:00pm │││
│ │ ├─────────────────────────────┤│ │ □ DD Report review    Tomorrow│││
│ │ │ DEAL-005 RetailChain   ●●●●○││ │ □ Team standup        Mon 9am│││
│ │ │ Negotiation      £23M  ↗85% ││ │ □ Board update        Mon 2pm│││
│ │ ├─────────────────────────────┤│ └──────────────────────────────┘││
│ │ │ DEAL-009 FinServ       ●●○○○││                                   ││
│ │ │ Qualifying       £67M  ↗45% ││ [View All Tasks →]               ││
│ │ └─────────────────────────────┘│                                   ││
│ │                                 │                                   ││
│ │ [View All Deals →]              │                                   ││
│ └─────────────────────────────────┴──────────────────────────────────┘│
│                                                                        │
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │ Recent Activity                                    [Filter ▼]      ││
│ │ ┌──┬───────────────────────────────────────────────────────────┐  ││
│ │ │●│ 14:32 Sarah Chen uploaded "DD Report v3" to DEAL-001       │  ││
│ │ ├──┼───────────────────────────────────────────────────────────┤  ││
│ │ │●│ 14:15 James Mitchell commented on "Term Sheet" in DEAL-005 │  ││
│ │ ├──┼───────────────────────────────────────────────────────────┤  ││
│ │ │●│ 13:45 DEAL-009 moved to Qualifying stage                   │  ││
│ │ ├──┼───────────────────────────────────────────────────────────┤  ││
│ │ │●│ 11:22 Victoria Hammond approved DEAL-012 for negotiation   │  ││
│ │ └──┴───────────────────────────────────────────────────────────┘  ││
│ └────────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────┘

ANNOTATIONS:
- Quick Stats: Real-time KPIs, clickable to drill down
- My Active Deals: Personalized list, progress bars show stage completion
- Upcoming Tasks: Next 5 tasks, checkbox for quick complete
- Recent Activity: Team-wide feed, filterable by type/person/deal
- Navigation: Persistent top nav, current section highlighted
```

---

## 2. DEAL PIPELINE - KANBAN VIEW

```
┌────────────────────────────────────────────────────────────────────────┐
│ Pipeline Management                           [List][Kanban][Calendar] │
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │ [🔍 Search deals...]  [Filter ▼] [Sort ▼] [Group ▼]  [+ New Deal] ││
│ │ Active filters: Stage: All | Team: My Team | Value: > £1M  [Clear]││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                        │
│ ┌─────────────┬─────────────┬─────────────┬─────────────┬──────────┐│
│ │ SOURCING    │ QUALIFYING  │ DUE DILIG.  │ NEGOTIATION │ CLOSING  ││
│ │ 8 deals     │ 5 deals     │ 3 deals     │ 4 deals     │ 2 deals  ││
│ │ £45.2M      │ £82.5M      │ £124.3M     │ £95.7M      │ £67.4M   ││
│ ├─────────────┼─────────────┼─────────────┼─────────────┼──────────┤│
│ │┌───────────┐│┌───────────┐│┌───────────┐│┌───────────┐│┌─────────┐│
│ ││ DEAL-001  ││ DEAL-005  ││ DEAL-009  ││ DEAL-013  ││DEAL-017 ││
│ ││ TechCo    ││ RetailX   ││ FinServ   ││ ManuCo    ││LogisCo  ││
│ ││ ─────────  ││ ─────────  ││ ─────────  ││ ─────────  ││───────── ││
│ ││ Software  ││ Retail    ││ Banking   ││ Manufact. ││Logistics││
│ ││ £5.2M     ││ £12.8M    ││ £45.0M    ││ £23.5M    ││£34.2M   ││
│ ││           ││           ││           ││           ││         ││
│ ││ ●●●○○ 60% ││ ●●●●○ 75% ││ ●●●●● 95% ││ ●●●●○ 80% ││●●●●● 90%││
│ ││           ││           ││           ││           ││         ││
│ ││ 📅 Q2 2025││ 📅 Q1 2025││ 📅 Q1 2025││ 📅 Q2 2025││📅 Dec'24││
│ ││           ││           ││           ││           ││         ││
│ ││ J.Smith   ││ S.Chen    ││ T.Brown   ││ K.Davis   ││M.Wilson ││
│ ││ 👥 3      ││ 👥 4      ││ 👥 5      ││ 👥 4      ││👥 6     ││
│ ││           ││           ││ ⚠ 2 risks ││           ││! Action ││
│ ││ [···]     ││ [···]     ││ [···]     ││ [···]     ││[···]    ││
│ │└───────────┘│└───────────┘│└───────────┘│└───────────┘│└─────────┘│
│ │┌───────────┐│┌───────────┐│┌───────────┐│┌───────────┐│          ││
│ ││ DEAL-002  ││ DEAL-006  ││ DEAL-010  ││ DEAL-014  ││          ││
│ ││ DataInc   ││ FoodCo    ││ InsureTech││ ChemCorp  ││          ││
│ ││ ─────────  ││ ─────────  ││ ─────────  ││ ─────────  ││          ││
│ ││ Analytics ││ Food&Bev  ││ Insurance ││ Chemicals ││          ││
│ ││ £8.7M     ││ £19.3M    ││ £38.5M    ││ £18.9M    ││          ││
│ │└───────────┘│└───────────┘│└───────────┘│└───────────┘│          ││
│ │             │             │┌───────────┐│             │          ││
│ │[+Drop here] │[+Drop here] ││ DEAL-011  ││[+Drop here] │[+Drop]   ││
│ │             │             │└───────────┘│             │          ││
│ └─────────────┴─────────────┴─────────────┴─────────────┴──────────┘│
│                                                                        │
│ Showing 22 of 47 deals                           [Load More ▼]        │
└────────────────────────────────────────────────────────────────────────┘

CARD ELEMENTS:
- Deal ID & Name: Click to open detail
- Industry tag: Colored by sector
- Value: Deal size in currency
- Progress bar: % probability with numeric display
- Target close: Calendar icon with date
- Lead: Avatar or initials
- Team size: Number of members
- Alerts: Warning icons for risks/actions
- Menu: Three dots for quick actions

INTERACTIONS:
- Drag cards between stages
- Hover shows preview tooltip
- Double-click for quick edit
- Right-click for context menu
```

---

## 3. DEAL DETAIL - OVERVIEW TAB

```
┌────────────────────────────────────────────────────────────────────────┐
│ ← Back to Pipeline                                    [Edit][Share][⋮]│
├────────────────────────────────────────────────────────────────────────┤
│ DEAL-001                                                              │
│ TechCo Acquisition - Enterprise Software Platform                     │
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │ Status: Due Diligence | Priority: High | Lead: John Smith          ││
│ │ Created: Oct 1, 2024 | Updated: 2 hours ago | Code: PROJ-ALPHA     ││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                        │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ [Overview][Documents(12)][Team(5)][Activity][Financials][DD][⚙] │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│ ┌─────────────────────────────────┬──────────────────────────────────┐│
│ │ Key Metrics                     │ Quick Actions                    ││
│ │ ┌─────────────────────────────┐│ ┌──────────────────────────────┐││
│ │ │ Deal Value      │ £45.2M    ││ │ [📄 Upload Document]         │││
│ │ │ Probability     │ 75%       ││ │ [📅 Schedule Meeting]        │││
│ │ │ Expected Close  │ Q2 2025   ││ │ [✓ Add Task]               │││
│ │ │ Days in Stage   │ 14        ││ │ [💬 Add Note]               │││
│ │ │ IRR Expected    │ 24.5%     ││ │ [📊 Generate Report]        │││
│ │ │ MOIC Target     │ 2.8x      ││ │ [✉ Send Update]            │││
│ │ └─────────────────────────────┘│ └──────────────────────────────┘││
│ └─────────────────────────────────┴──────────────────────────────────┘│
│                                                                        │
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │ Executive Summary                                      [Edit ✏]    ││
│ │ ┌──────────────────────────────────────────────────────────────┐  ││
│ │ │ Strategic acquisition of a leading B2B SaaS platform serving  │  ││
│ │ │ enterprise customers in the financial services sector. The    │  ││
│ │ │ target has strong recurring revenue (£12.5M ARR), excellent  │  ││
│ │ │ retention metrics (95% GRR), and significant growth          │  ││
│ │ │ potential through product expansion and geographic reach.    │  ││
│ │ └──────────────────────────────────────────────────────────────┘  ││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                        │
│ ┌─────────────────────────────┬───────────────────────────────────┐  │
│ │ Target Information          │ Deal Structure                    │  │
│ │ ┌───────────────────────────┤ ┌─────────────────────────────────┤  │
│ │ │ Company:    TechCo Ltd    │ │ Type:        Asset Purchase   │  │
│ │ │ Industry:   Software      │ │ Structure:   100% Equity      │  │
│ │ │ Founded:    2015          │ │ Financing:   60% Cash, 40% Stock│ │
│ │ │ Employees:  85            │ │ Earnout:     £5M over 2 years│  │
│ │ │ HQ:         London, UK    │ │ Escrow:      10% for 18 months│ │
│ │ │ Website:    techco.com    │ │                               │  │
│ │ └───────────────────────────┘ └─────────────────────────────────┘  │
│ └─────────────────────────────┴───────────────────────────────────┘  │
│                                                                        │
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │ Financial Highlights                              [View Details →] ││
│ │ ┌──────────────┬──────────────┬──────────────┬────────────────┐  ││
│ │ │              │ 2023A        │ 2024E        │ 2025P          │  ││
│ │ ├──────────────┼──────────────┼──────────────┼────────────────┤  ││
│ │ │ Revenue      │ £10.2M       │ £12.5M       │ £15.8M         │  ││
│ │ │ EBITDA       │ £2.1M        │ £3.2M        │ £4.5M          │  ││
│ │ │ EBITDA %     │ 20.6%        │ 25.6%        │ 28.5%          │  ││
│ │ │ Growth YoY   │ 32%          │ 23%          │ 26%            │  ││
│ │ └──────────────┴──────────────┴──────────────┴────────────────┘  ││
│ └────────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────┘

INTERACTIVE ELEMENTS:
- Tabs: Click to switch views, badge shows count
- Edit buttons: Inline editing with auto-save
- Quick actions: One-click common tasks
- Financial table: Clickable cells for detail view
- Links: Blue underlined text opens related items
```

---

## 4. DOCUMENT COLLABORATION VIEW

```
┌────────────────────────────────────────────────────────────────────────┐
│ Documents - DEAL-001 TechCo Acquisition              [Grid][List][←→] │
├────────────────────────────────────────────────────────────────────────┤
│ [🔍 Search docs...]  [Type ▼][Status ▼][Date ▼]  [📤Upload][📁New Folder]│
│                                                                        │
│ 📁 Deal Documents / Due Diligence / Legal                             │
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │     Name                        Modified    Status    Version  Size││
│ │ ┌──────────────────────────────────────────────────────────────┐  ││
│ │ │ □ 📄 Share Purchase Agreement  2 hrs ago  Review    v3.2   2.1MB│ ││
│ │ │   └─ 💬 3 comments · 2 unresolved · Last: S.Chen 1 hr ago    │  ││
│ │ ├──────────────────────────────────────────────────────────────┤  ││
│ │ │ □ 📄 Due Diligence Report      Yesterday  Approved  v2.0   5.4MB│ ││
│ │ │   └─ ✓ Approved by V.Hammond · 4 reviewers                   │  ││
│ │ ├──────────────────────────────────────────────────────────────┤  ││
│ │ │ □ 📊 Financial Model           3 days ago Draft     v1.3   1.2MB│ ││
│ │ │   └─ 📎 Excel with 12 sheets · J.Mitchell editing now        │  ││
│ │ ├──────────────────────────────────────────────────────────────┤  ││
│ │ │ □ 📑 Term Sheet                5 days ago Final     v4.0   450KB│ ││
│ │ │   └─ 🔒 Locked for signing · Awaiting counterparty           │  ││
│ │ └──────────────────────────────────────────────────────────────┘  ││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                        │
│ Selected: Share Purchase Agreement                     [Open][Compare]│
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │ Document Preview                           Comments & Activity     ││
│ │ ┌──────────────────────────┬──────────────────────────────────┐  ││
│ │ │                          │ ┌────────────────────────────────┐│  ││
│ │ │ SHARE PURCHASE AGREEMENT│ │ Comments (3)        [Resolve All]│  ││
│ │ │                          │ ├────────────────────────────────┤│  ││
│ │ │ This Agreement is made...│ │ S.Chen · 1 hour ago     📍L42 ││  ││
│ │ │                          │ │ "Warranty clause needs revision││  ││
│ │ │ 1. DEFINITIONS           │ │  for IP protection"            ││  ││
│ │ │ 1.1 In this Agreement:  │ │ [Reply] [Resolve] [@Mention]   ││  ││
│ │ │ [Highlighted text]       │ ├────────────────────────────────┤│  ││
│ │ │                          │ │ J.Mitchell · 2 hours ago   ✓  ││  ││
│ │ │ 2. SALE AND PURCHASE    │ │ "Added escrow terms as discussed││ ││
│ │ │ 2.1 The Vendor agrees...│ │  in yesterday's call"          ││  ││
│ │ │                          │ ├────────────────────────────────┤│  ││
│ │ │ [Page 1 of 47]           │ │ System · 3 hours ago           ││  ││
│ │ │ [▼]                      │ │ "Version 3.2 uploaded by T.Brown││ ││
│ │ └──────────────────────────┴──────────────────────────────────┘│  ││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                        │
│ [Download][Print][Share Link][Request Approval][View History]         │
└────────────────────────────────────────────────────────────────────────┘

DOCUMENT FEATURES:
- Multi-select: Checkbox for bulk operations
- Status badges: Color-coded (Draft/Review/Approved/Final)
- Version tracking: Click version to see history
- Real-time collaboration: Live user indicators
- Comments: Threaded discussions with line references
- Preview: In-browser viewing for common formats
```

---

## 5. TEAM WORKSPACE

```
┌────────────────────────────────────────────────────────────────────────┐
│ Team Dashboard - London M&A Division                   [Settings ⚙]   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │ Team Performance This Quarter                      [Export PDF 📊] ││
│ │ ┌──────────────┬──────────────┬──────────────┬────────────────┐  ││
│ │ │ Active Deals │ Closed Deals │ Pipeline Val │ Avg Deal Size  │  ││
│ │ │     23       │      8       │   £347.5M    │    £15.1M      │  ││
│ │ │   ↑ 15%      │   ↑ 33%      │   ↑ 28%      │    ↑ 12%       │  ││
│ │ └──────────────┴──────────────┴──────────────┴────────────────┘  ││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                        │
│ Team Members (12)                                    [+ Invite Member]│
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │ Name              Role           Deals  Workload  Status    Actions││
│ │ ┌──────────────────────────────────────────────────────────────┐  ││
│ │ │ 👤 Sarah Chen    Sr. Advisor    8     ████████  🟢 Online  [📧]│ ││
│ │ ├──────────────────────────────────────────────────────────────┤  ││
│ │ │ 👤 James Mitchell Associate     6     ██████    🟢 Online  [📧]│ ││
│ │ ├──────────────────────────────────────────────────────────────┤  ││
│ │ │ 👤 Tom Brown     Analyst        5     █████     🟡 Away    [📧]│ ││
│ │ ├──────────────────────────────────────────────────────────────┤  ││
│ │ │ 👤 Kate Davis    Legal Counsel  4     ████      🟢 Online  [📧]│ ││
│ │ └──────────────────────────────────────────────────────────────┘  ││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                        │
│ ┌─────────────────────────────┬───────────────────────────────────┐  │
│ │ Deal Assignment Matrix      │ Upcoming Team Events              │  │
│ │ ┌───────────────────────────┤ ┌─────────────────────────────────┤  │
│ │ │         │Chen│Mitch│Brown││ │ Today                         │  │
│ │ ├─────────┼────┼─────┼─────┤│ │ 14:00 Deal Review - DEAL-001 │  │
│ │ │DEAL-001 │ ● │  ○  │     ││ │ 15:30 Partner Update Call    │  │
│ │ │DEAL-005 │   │  ●  │  ○  ││ │                               │  │
│ │ │DEAL-009 │ ○ │     │  ●  ││ │ Tomorrow                      │  │
│ │ │DEAL-013 │ ● │  ○  │  ○  ││ │ 09:00 Team Standup           │  │
│ │ └───────────────────────────┘│ │ 11:00 DD Presentation        │  │
│ │ ● Lead  ○ Support            │ │ 14:00 Client Meeting         │  │
│ └─────────────────────────────┴─────────────────────────────────┘  │
│                                                                        │
│ Activity Feed                                         [Filter ▼]      │
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │ ┌──────────────────────────────────────────────────────────────┐  ││
│ │ │ 14:32 S.Chen completed due diligence review for DEAL-001     │  ││
│ │ │ 14:15 J.Mitchell uploaded 3 documents to DEAL-005           │  ││
│ │ │ 13:45 Team meeting scheduled for tomorrow 9:00 AM           │  ││
│ │ │ 11:22 K.Davis requested approval for term sheet changes      │  ││
│ │ └──────────────────────────────────────────────────────────────┘  ││
│ └────────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────┘

TEAM FEATURES:
- Workload bars: Visual capacity indicator
- Status indicators: Real-time presence
- Assignment matrix: Role clarity at a glance
- Activity feed: Filterable by person/deal/type
- Quick actions: One-click email/chat/assign
```

---

## 6. EXECUTIVE ANALYTICS DASHBOARD

```
┌────────────────────────────────────────────────────────────────────────┐
│ Executive Dashboard                    Q4 2024        [▼][Export][🖨] │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│ ┌────────────────────────────────────────────────────────────────────┐│
│ │                    Pipeline Health Score: 87/100                    ││
│ │ ████████████████████████████████████████████░░░░░  ↑5 from last mo ││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                        │
│ Key Metrics                                          [Customize ⚙]    │
│ ┌──────────────┬──────────────┬──────────────┬──────────────────────┐│
│ │ Total Pipeline│ Win Rate     │ Avg Deal Size│ Time to Close        ││
│ │   £347.5M    │    67%       │   £15.1M     │   4.2 months        ││
│ │   23 deals   │   ↑ 5%       │   ↑ £2.1M    │   ↓ 0.8 months      ││
│ │              │              │              │                      ││
│ │ ███████████  │ ████████     │ ██████████   │ ████████████        ││
│ └──────────────┴──────────────┴──────────────┴──────────────────────┘│
│                                                                        │
│ Pipeline Funnel                          Value by Stage               │
│ ┌─────────────────────────────┬───────────────────────────────────┐ │
│ │   Sourcing     ████████ 45 │ │ Sourcing    █████ £45M          │ │
│ │   Qualifying   ██████ 32   │ │ Qualifying  ████████ £83M       │ │
│ │   Due Dilig.   ████ 18     │ │ Due Dilig.  ████████████ £124M  │ │
│ │   Negotiation  ███ 12      │ │ Negotiation ████████ £96M       │ │
│ │   Closing      ██ 8        │ │ Closing     ██████ £67M         │ │
│ │                             │ │                                  │ │
│ │   Conversion: 18%           │ │ Total: £415M                     │ │
│ └─────────────────────────────┴───────────────────────────────────┘ │
│                                                                        │
│ Deal Velocity Trend (12 months)         Top Performers               │
│ ┌─────────────────────────────┬───────────────────────────────────┐ │
│ │     ▲                       │ │ Advisor      Deals  Value  Win%│ │
│ │    ╱ ╲    ╱╲               │ │ ┌─────────────────────────────┐│ │
│ │   ╱   ╲  ╱  ╲    ╱╲       │ │ │ S.Chen       8    £124M  75%││ │
│ │  ╱     ╲╱    ╲  ╱  ╲      │ │ │ J.Mitchell   6    £87M   67%││ │
│ │ ╱             ╲╱    ╲───  │ │ │ T.Brown      5    £65M   60%││ │
│ │ J F M A M J J A S O N D   │ │ │ K.Davis      4    £48M   75%││ │
│ └─────────────────────────────┴───────────────────────────────────┘ │
│                                                                        │
│ Risk & Attention Required                         Quick Insights      │
│ ┌─────────────────────────────┬───────────────────────────────────┐ │
│ │ ⚠ High Risk Deals (3)      │ │ 💡 5 deals closing next month  │ │
│ │ • DEAL-009: Legal issues   │ │ 💡 Pipeline grew 23% QoQ       │ │
│ │ • DEAL-014: Financing gap  │ │ 💡 Tech sector performing best │ │
│ │ • DEAL-021: Competition    │ │ 💡 Need more early-stage deals │ │
│ │                             │ │ 💡 Team at 85% capacity        │ │
│ │ 🔴 3 Overdue Actions        │ │                                │ │
│ └─────────────────────────────┴───────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘

DASHBOARD FEATURES:
- Real-time metrics: Auto-refresh every 5 min
- Drill-down: Click any metric for details
- Customizable widgets: Drag to rearrange
- Export options: PDF, Excel, PowerPoint
- Trend indicators: Green up/red down arrows
- Smart insights: AI-generated observations
```

---

## 7. MOBILE RESPONSIVE VIEWS

### 7.1 Mobile Deal List (iPhone 14 Pro - 390x844)

```
┌─────────────────────┐
│ ≡  Deals        🔍 │
├─────────────────────┤
│ Active Deals (23)   │
│                     │
│ ┌───────────────────┤
│ │ DEAL-001         ││
│ │ TechCo           ││
│ │ £45.2M • 75%     ││
│ │ Due Diligence    ││
│ │ J.Smith • Q2'25  ││
│ └───────────────────┤
│ ┌───────────────────┤
│ │ DEAL-005      ⚠  ││
│ │ RetailChain      ││
│ │ £23.8M • 85%     ││
│ │ Negotiation      ││
│ │ S.Chen • Q1'25   ││
│ └───────────────────┤
│ ┌───────────────────┤
│ │ DEAL-009         ││
│ │ FinServ          ││
│ │ £67.4M • 45%     ││
│ │ Qualifying       ││
│ │ T.Brown • Q2'25  ││
│ └───────────────────┤
│                     │
│ [Load More ▼]       │
├─────────────────────┤
│ Pipeline│Docs│Tasks││
└─────────────────────┘
```

### 7.2 Tablet Pipeline View (iPad Pro - 1024x1366)

```
┌────────────────────────────────────────────┐
│ ☰ M&A Platform          John Smith ▼      │
├────────────────────────────────────────────┤
│ Pipeline Overview            [+New][Filter]│
│                                            │
│ ┌──────────────┬────────────────┐         │
│ │ SOURCING (8) │ QUALIFYING (5) │         │
│ │ £45.2M       │ £82.5M         │         │
│ ├──────────────┼────────────────┤         │
│ │ □ DEAL-001   │ □ DEAL-005     │         │
│ │   TechCo     │   RetailX      │         │
│ │   £5.2M      │   £12.8M       │         │
│ │              │                │         │
│ │ □ DEAL-002   │ □ DEAL-006     │         │
│ │   DataInc    │   FoodCo       │         │
│ │   £8.7M      │   £19.3M       │         │
│ └──────────────┴────────────────┘         │
│                                            │
│ ┌──────────────┬────────────────┐         │
│ │ DUE DILIG(3) │ NEGOTIATION(4) │         │
│ │ £124.3M      │ £95.7M         │         │
│ ├──────────────┼────────────────┤         │
│ │ □ DEAL-009   │ □ DEAL-013     │         │
│ │   FinServ    │   ManuCo       │         │
│ │   £45.0M     │   £23.5M       │         │
│ └──────────────┴────────────────┘         │
│                                            │
│ [Deals][Documents][Analytics][Team]       │
└────────────────────────────────────────────┘
```

---

## 8. EMPTY STATES & ONBOARDING

### 8.1 Empty Deal Pipeline

```
┌────────────────────────────────────────────────────────────────────────┐
│ Deal Pipeline                                         [+ Create Deal] │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                                                                        │
│                         ┌──────────────┐                              │
│                         │              │                              │
│                         │      💼      │                              │
│                         │              │                              │
│                         └──────────────┘                              │
│                                                                        │
│                     Start Building Your Pipeline                      │
│                                                                        │
│               Create your first deal to begin tracking                │
│                     your M&A opportunities                            │
│                                                                        │
│                        [+ Create First Deal]                          │
│                                                                        │
│                              - or -                                   │
│                                                                        │
│                    [Import from Excel] [Use Template]                 │
│                                                                        │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Onboarding Wizard - Step 1

```
┌────────────────────────────────────────────────────────────────────────┐
│ Welcome to M&A Platform                                    Step 1 of 4│
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  Let's set up your workspace                                          │
│                                                                        │
│  Tell us about your organization:                                     │
│                                                                        │
│  Organization Name *                                                  │
│  ┌──────────────────────────────────────────────────┐                │
│  │ Apex Capital Partners                             │                │
│  └──────────────────────────────────────────────────┘                │
│                                                                        │
│  Industry Focus *                                                     │
│  ┌──────────────────────────────────────────────────┐                │
│  │ Technology & Software                        ▼    │                │
│  └──────────────────────────────────────────────────┘                │
│                                                                        │
│  Typical Deal Size                                                    │
│  ┌──────────────────────────────────────────────────┐                │
│  │ £10M - £100M                                ▼    │                │
│  └──────────────────────────────────────────────────┘                │
│                                                                        │
│  Team Size                                                            │
│  ○ 1-5  ● 6-20  ○ 21-50  ○ 50+                                     │
│                                                                        │
│                              [Skip] [Next →]                          │
│                                                                        │
│  ●  ○  ○  ○                                                          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## DESIGN ANNOTATIONS

### Navigation Patterns

- **Persistent top nav**: Always visible, context-aware
- **Breadcrumbs**: Show location in deep hierarchies
- **Tab navigation**: For related content sections
- **Quick actions**: Floating action button on mobile

### Data Display Patterns

- **Progressive disclosure**: Show summary, expand for details
- **Inline editing**: Double-click or edit icon
- **Bulk operations**: Checkbox selection pattern
- **Infinite scroll**: With load more fallback

### Feedback Patterns

- **Loading**: Skeleton screens for structure
- **Success**: Green toast, 3s auto-dismiss
- **Errors**: Red inline message, persist until resolved
- **Warnings**: Yellow banner, dismissible

### Responsive Strategies

- **Desktop-first**: Optimize for power users
- **Breakpoints**: 1440px, 1024px, 768px
- **Touch targets**: Minimum 44x44px on mobile
- **Gesture support**: Swipe, pinch, long-press

---

_Wireframe Specifications v1.0_
_Created: October 2025_
_Next Review: November 2025_
