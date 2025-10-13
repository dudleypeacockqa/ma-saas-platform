# 📋 Clerk Feature Extraction Guide

**Purpose:** Get the exact feature list from your Clerk Dashboard to ensure perfect alignment
**Time Required:** 10-15 minutes
**Impact:** Ensures £2.4M ARR system delivers correct value per tier

---

## 🎯 WHY WE NEED THIS

Currently, we have:

- ✅ Correct pricing in Clerk and codebase
- ✅ Correct plan IDs
- ❌ **Unknown:** Exact feature keys configured in Clerk
- ❌ **Unknown:** Which features are assigned to which plans

**The Risk:** Feature gating might not work correctly, allowing users to access features they shouldn't have.

---

## 📸 OPTION A: Take Screenshots (Easiest - 10 mins)

### Step 1: Navigate to Plans

1. Go to: https://dashboard.clerk.com
2. Click: **"Billing"** in left sidebar
3. Click: **"Subscription plans"**

### Step 2: Open Each Plan

For EACH of the 8 plans, do this:

#### Plan 1: Solo Dealmaker (Monthly)

1. Click on **"Solo Dealmaker (Monthly)"** plan card
2. Scroll to **"Features"** section
3. Take screenshot showing ALL features
4. **IMPORTANT:** Make sure feature names are clearly visible
5. Save as: `clerk-features-solo-monthly.png`

#### Plan 2: Solo Dealmaker (Annual)

1. Click on **"Solo Dealmaker (Annual)"** plan card
2. Scroll to **"Features"** section
3. Take screenshot
4. Save as: `clerk-features-solo-annual.png`

#### Plan 3: Growth Firm (Monthly)

1. Click on **"Growth Firm (Monthly)"** plan card
2. Scroll to **"Features"** section
3. Take screenshot
4. Save as: `clerk-features-growth-monthly.png`

#### Plan 4: Growth Firm (Annual)

1. Click on **"Growth Firm (Annual)"** plan card
2. Scroll to **"Features"** section
3. Take screenshot
4. Save as: `clerk-features-growth-annual.png`

#### Plan 5: Enterprise (Monthly)

1. Click on **"Enterprise (Monthly)"** plan card
2. Scroll to **"Features"** section
3. Take screenshot
4. Save as: `clerk-features-enterprise-monthly.png`

#### Plan 6: Enterprise (Annual)

1. Click on **"Enterprise (Annual)"** plan card
2. Scroll to **"Features"** section
3. Take screenshot
4. Save as: `clerk-features-enterprise-annual.png`

#### Plan 7: Community Leader (Monthly)

1. Click on **"Community Leader (Monthly)"** plan card
2. Scroll to **"Features"** section
3. Take screenshot
4. Save as: `clerk-features-community-monthly.png`

#### Plan 8: Community Leader (Annual)

1. Click on **"Community Leader (Annual)"** plan card
2. Scroll to **"Features"** section
3. Take screenshot
4. Save as: `clerk-features-community-annual.png`

### Step 3: Share Screenshots

Send me all 8 screenshots via:

- Claude Code chat (paste images)
- Or save in project: `c:\Projects\ma-saas-platform\clerk-screenshots\`

---

## ✍️ OPTION B: Manual List (If screenshots don't work - 15 mins)

### Format to use:

```
SOLO DEALMAKER (MONTHLY) - Plan ID: cplan_340Nm3k5AOIb
Features:
1. [exact feature name from Clerk]
2. [exact feature name from Clerk]
3. [exact feature name from Clerk]
...

SOLO DEALMAKER (ANNUAL) - Plan ID: cplan_340P2yr6bRYq
Features:
1. [exact feature name from Clerk]
2. [exact feature name from Clerk]
...

GROWTH FIRM (MONTHLY) - Plan ID: cplan_340GsAT2Ch6t
Features:
1. [exact feature name from Clerk]
2. [exact feature name from Clerk]
...

GROWTH FIRM (ANNUAL) - Plan ID: cplan_340J0FWGfMvI
Features:
1. [exact feature name from Clerk]
...

ENTERPRISE (MONTHLY) - Plan ID: cplan_340gLX8XLUMd
Features:
1. [exact feature name from Clerk]
...

ENTERPRISE (ANNUAL) - Plan ID: cplan_340Qh256zZRl
Features:
1. [exact feature name from Clerk]
...

COMMUNITY LEADER (MONTHLY) - Plan ID: cplan_3404f88Hi6fU
Features:
1. [exact feature name from Clerk]
...

COMMUNITY LEADER (ANNUAL) - Plan ID: cplan_340xSdbE7elf
Features:
1. [exact feature name from Clerk]
...
```

### How to extract manually:

1. For each plan, click to open it
2. Find the "Features" section
3. **Copy each feature name EXACTLY as shown**
4. Paste into the format above

**IMPORTANT:**

- Include punctuation exactly as shown
- Don't paraphrase or shorten
- If features use special characters or IDs, include them

---

## 🔍 WHAT I'M LOOKING FOR

From your Clerk dashboard, features might look like:

**Example A: Simple Text Features**

```
Features:
- Full M&A Platform Access
- Essential Community Membership
- Monthly Networking Webinars
- AI-Powered Deal Analysis
- Basic Masterclass Library
```

**Example B: Feature Keys**

```
Features:
- platform_access_full
- community_essential
- webinars_monthly
- ai_deal_analysis
- masterclass_basic
```

**Example C: Mixed Format**

```
Features:
- platform_access: Full M&A Platform Access
- community_essential: Essential Community Membership
```

**I need to see EXACTLY what format Clerk uses so I can align the code correctly.**

---

## ❓ TROUBLESHOOTING

### Can't find "Features" section?

**Try this:**

1. Click on a plan in Clerk Dashboard
2. Look for sections named:
   - "Features"
   - "Included features"
   - "Plan features"
   - "Benefits"
   - "What's included"

### Features section is empty?

This means you haven't configured features yet in Clerk. You have two options:

**Option 1: Use our feature list (recommended)**
I'll provide you with a complete feature list to ADD to Clerk based on your pricing tiers.

**Option 2: Skip features**
You can skip feature-based gating and just use tier-based gating (less granular).

### Screenshot is too small to read?

**Use browser zoom:**

1. In Clerk Dashboard, press `Ctrl` + `+` (Windows) or `Cmd` + `+` (Mac)
2. Zoom to 150-200%
3. Take screenshot
4. Feature names should be clearly readable

---

## 💡 WHAT HAPPENS NEXT

Once you provide the feature list:

1. **I will create:** `CLERK_FEATURE_REGISTRY.md` with master mapping
2. **I will update:** All 25 feature keys in code to match Clerk exactly
3. **I will align:** Frontend display, backend checks, documentation
4. **I will create:** Testing guide to verify each feature works
5. **Result:** Perfect BMAD alignment → Clerk ↔ Codebase ↔ Docs

---

## ⚡ QUICK START

**Fastest path:** Take 8 screenshots (one per plan) showing features section.

**Time:** 10 minutes
**Impact:** Ensures £2.4M ARR system works correctly
**Risk if skipped:** Users might access premium features for free

---

**Ready when you are! Just share the screenshots or manual list.** 🎯
