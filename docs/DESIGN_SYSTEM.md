# M&A Ecosystem Platform - Design System

**Version:** 1.0.0
**Last Updated:** 2025-10-11
**Platform:** Web (Desktop & Mobile)

---

## Design Tokens

### Color System

```scss
// Primary Colors
$primary-500: #2563eb; // Primary brand color
$primary-600: #1d4ed8; // Hover state
$primary-700: #1e40af; // Active state
$primary-50: #eff6ff; // Light backgrounds
$primary-100: #dbeafe; // Subtle backgrounds

// Semantic Colors
$success-500: #10b981;
$success-50: #f0fdf4;
$warning-500: #f59e0b;
$warning-50: #fffbeb;
$error-500: #ef4444;
$error-50: #fef2f2;
$info-500: #3b82f6;
$info-50: #eff6ff;

// Neutral Scale
$gray-900: #111827; // Primary text
$gray-700: #374151; // Secondary text
$gray-500: #6b7280; // Tertiary text
$gray-400: #9ca3af; // Placeholder text
$gray-300: #d1d5db; // Borders
$gray-200: #e5e7eb; // Dividers
$gray-100: #f3f4f6; // Subtle backgrounds
$gray-50: #f9fafb; // Light backgrounds
$white: #ffffff;

// Deal Stage Colors
$stage-prospecting: #8b5cf6;
$stage-qualification: #3b82f6;
$stage-duediligence: #f59e0b;
$stage-negotiation: #10b981;
$stage-closing: #059669;
$stage-closed: #6b7280;
```

### Typography

```scss
// Font Families
$font-primary:
  'Inter',
  -apple-system,
  BlinkMacSystemFont,
  'Segoe UI',
  sans-serif;
$font-mono: 'JetBrains Mono', 'Courier New', monospace;

// Font Sizes
$text-xs: 12px; // line-height: 16px
$text-sm: 14px; // line-height: 20px
$text-base: 16px; // line-height: 24px
$text-lg: 18px; // line-height: 28px
$text-xl: 20px; // line-height: 28px
$text-2xl: 24px; // line-height: 32px
$text-3xl: 30px; // line-height: 36px
$text-4xl: 36px; // line-height: 40px

// Font Weights
$font-normal: 400;
$font-medium: 500;
$font-semibold: 600;
$font-bold: 700;

// Letter Spacing
$tracking-tight: -0.02em;
$tracking-normal: 0;
$tracking-wide: 0.02em;
```

### Spacing & Layout

```scss
// Spacing Scale (4px base)
$space-0: 0px;
$space-1: 4px;
$space-2: 8px;
$space-3: 12px;
$space-4: 16px;
$space-5: 20px;
$space-6: 24px;
$space-8: 32px;
$space-10: 40px;
$space-12: 48px;
$space-16: 64px;
$space-20: 80px;
$space-24: 96px;

// Container Widths
$container-sm: 640px;
$container-md: 768px;
$container-lg: 1024px;
$container-xl: 1280px;
$container-2xl: 1536px;

// Border Radius
$radius-none: 0px;
$radius-sm: 2px;
$radius-base: 4px;
$radius-md: 6px;
$radius-lg: 8px;
$radius-xl: 12px;
$radius-2xl: 16px;
$radius-full: 9999px;
```

### Shadows & Effects

```scss
// Box Shadows
$shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
$shadow-sm:
  0 1px 3px 0 rgba(0, 0, 0, 0.1),
  0 1px 2px 0 rgba(0, 0, 0, 0.06);
$shadow-base:
  0 4px 6px -1px rgba(0, 0, 0, 0.1),
  0 2px 4px -1px rgba(0, 0, 0, 0.06);
$shadow-md:
  0 10px 15px -3px rgba(0, 0, 0, 0.1),
  0 4px 6px -2px rgba(0, 0, 0, 0.05);
$shadow-lg:
  0 20px 25px -5px rgba(0, 0, 0, 0.1),
  0 10px 10px -5px rgba(0, 0, 0, 0.04);
$shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

// Focus States
$focus-ring: 0 0 0 3px rgba(37, 99, 235, 0.1);
$focus-outline: 2px solid #2563eb;

// Transitions
$transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
$transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
$transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
```

---

## Component Library

### Buttons

```typescript
// Primary Button
<Button variant="primary" size="md">
  Save Deal
</Button>

// Secondary Button
<Button variant="secondary" size="md">
  Cancel
</Button>

// Ghost Button
<Button variant="ghost" size="md">
  View Details
</Button>

// Sizes: xs | sm | md | lg | xl
// States: default | hover | active | disabled | loading
```

**Design Specifications:**

- Height: 32px (sm), 36px (md), 40px (lg)
- Padding: 8px 16px (md)
- Border radius: 6px
- Font weight: 500
- Transition: all 200ms ease

### Form Elements

```typescript
// Text Input
<TextField
  label="Deal Name"
  placeholder="Enter deal name"
  error="This field is required"
  helperText="Use a descriptive name"
/>

// Select Dropdown
<Select
  label="Deal Stage"
  options={dealStages}
  value={selectedStage}
/>

// Checkbox
<Checkbox
  label="Include in pipeline"
  checked={included}
/>

// Radio Group
<RadioGroup
  label="Deal Type"
  options={dealTypes}
  value={selectedType}
/>
```

### Cards

```typescript
// Deal Card
<DealCard
  deal={dealData}
  view="expanded"
  actions={cardActions}
/>

// Metric Card
<MetricCard
  title="Pipeline Value"
  value="$12.5M"
  change="+15%"
  trend="up"
/>

// Activity Card
<ActivityCard
  user={userData}
  action="updated"
  target="Project Atlas"
  timestamp={date}
/>
```

### Navigation

```typescript
// Top Navigation
<TopNav
  user={currentUser}
  workspace={activeWorkspace}
  notifications={unreadCount}
/>

// Side Navigation
<SideNav
  items={navigationItems}
  collapsed={isCollapsed}
  activeItem={currentPath}
/>

// Breadcrumbs
<Breadcrumbs
  items={[
    { label: 'Deals', href: '/deals' },
    { label: 'Project Atlas', href: '/deals/123' },
    { label: 'Documents' }
  ]}
/>
```

### Data Display

```typescript
// Data Table
<DataTable
  columns={tableColumns}
  data={dealData}
  sortable
  filterable
  paginated
/>

// Pipeline Board
<PipelineBoard
  stages={dealStages}
  deals={dealsData}
  onDragEnd={handleDragEnd}
/>

// Chart Components
<LineChart
  data={revenueData}
  xAxis="date"
  yAxis="value"
/>
```

### Feedback

```typescript
// Toast Notifications
toast.success('Deal updated successfully');
toast.error('Failed to save changes');
toast.info('New message received');

// Modal Dialog
<Modal
  title="Confirm Action"
  open={isOpen}
  onClose={handleClose}
>
  <ModalContent />
</Modal>

// Loading States
<Skeleton variant="text" width={200} />
<Skeleton variant="rectangular" height={100} />
<Spinner size="md" />
```

---

## Patterns & Guidelines

### Layout Patterns

#### Dashboard Layout

```
┌─────────────────────────────────────┐
│ TopNav (60px)                       │
├────────┬────────────────────────────┤
│ SideNav│ Main Content Area          │
│ (240px)│                            │
│        │ ┌────────────────────────┐ │
│        │ │ Page Header            │ │
│        │ ├────────────────────────┤ │
│        │ │ Content Grid           │ │
│        │ └────────────────────────┘ │
└────────┴────────────────────────────┘
```

#### Split View Layout

```
┌─────────────────────────────────────┐
│ Header                              │
├──────────────┬──────────────────────┤
│ List View    │ Detail View          │
│ (40%)        │ (60%)                │
│              │                      │
│ • Item 1     │ Selected Item Detail │
│ • Item 2     │                      │
│ • Item 3     │                      │
└──────────────┴──────────────────────┘
```

### Interaction Patterns

#### Progressive Disclosure

- Start with essential information
- Reveal complexity on demand
- Use accordions for grouped content
- Implement "Show more" for long lists

#### Optimistic Updates

- Update UI immediately on user action
- Show loading indicator subtly
- Rollback on error with notification
- Maintain previous state for recovery

#### Drag and Drop

- Visual feedback on hover (cursor: grab)
- Ghost element while dragging
- Drop zone highlighting
- Smooth animations on drop

### Responsive Behavior

#### Breakpoint System

```scss
// Mobile First Approach
$breakpoint-sm: 640px; // Small tablets
$breakpoint-md: 768px; // Tablets
$breakpoint-lg: 1024px; // Small desktops
$breakpoint-xl: 1280px; // Desktops
$breakpoint-2xl: 1536px; // Large screens
```

#### Component Adaptations

- **Navigation:** Hamburger menu on mobile
- **Tables:** Horizontal scroll or card view
- **Modals:** Full screen on mobile
- **Forms:** Single column on mobile
- **Charts:** Simplified on small screens

### Accessibility Standards

#### WCAG 2.1 Level AA Compliance

- Color contrast ratio: 4.5:1 minimum
- Focus indicators on all interactive elements
- Keyboard navigation support
- Screen reader announcements
- Alternative text for images
- ARIA labels and descriptions

#### Keyboard Shortcuts

- `Tab` - Navigate forward
- `Shift + Tab` - Navigate backward
- `Enter/Space` - Activate buttons
- `Arrow keys` - Navigate menus
- `Esc` - Close modals/dropdowns
- `Cmd/Ctrl + S` - Save forms

### Animation Guidelines

#### Timing Functions

```scss
$ease-in: cubic-bezier(0.4, 0, 1, 1);
$ease-out: cubic-bezier(0, 0, 0.2, 1);
$ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
$spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

#### Animation Durations

- **Micro:** 100-150ms (hover states)
- **Short:** 200-300ms (toggles, dropdowns)
- **Medium:** 300-400ms (modals, drawers)
- **Long:** 400-600ms (page transitions)

#### Performance Rules

- Use `transform` and `opacity` only
- Avoid animating `width`, `height`, `top`, `left`
- Enable hardware acceleration with `will-change`
- Respect `prefers-reduced-motion`

---

## Implementation Guide

### CSS Architecture

```scss
// BEM Naming Convention
.deal-card {
} // Block
.deal-card__header {
} // Element
.deal-card--expanded {
} // Modifier
.deal-card__title--highlighted {
} // Element with Modifier

// Utility Classes
.u-text-center {
}
.u-mt-4 {
}
.u-hidden-mobile {
}
```

### Component Structure

```typescript
// Component File Structure
components/
├── DealCard/
│   ├── DealCard.tsx        // Component logic
│   ├── DealCard.module.scss // Styles
│   ├── DealCard.test.tsx   // Tests
│   ├── DealCard.stories.tsx // Storybook
│   └── index.ts            // Export
```

### Theme Provider

```typescript
// Theme Configuration
const theme = {
  colors: { ...colorTokens },
  typography: { ...typographyTokens },
  spacing: { ...spacingTokens },
  shadows: { ...shadowTokens },
  transitions: { ...transitionTokens }
};

// Usage in Components
<ThemeProvider theme={theme}>
  <App />
</ThemeProvider>
```

### Design Token Export

```javascript
// design-tokens.js
module.exports = {
  colors: {
    /* ... */
  },
  typography: {
    /* ... */
  },
  spacing: {
    /* ... */
  },
  // Export for Figma Plugin
  figmaTokens: {
    /* ... */
  },
};
```

---

## Figma Integration

### Component Library Structure

```
Figma Components/
├── 📁 Foundations
│   ├── Colors
│   ├── Typography
│   └── Icons
├── 📁 Components
│   ├── Buttons
│   ├── Forms
│   ├── Cards
│   └── Navigation
├── 📁 Patterns
│   ├── Empty States
│   ├── Error States
│   └── Loading States
└── 📁 Templates
    ├── Dashboard
    ├── Deal Detail
    └── Data Room
```

### Design Handoff Checklist

- [ ] All components use design tokens
- [ ] Responsive variants documented
- [ ] Interactive states defined
- [ ] Annotations for developers
- [ ] Export assets at 1x, 2x, 3x
- [ ] Icon library as SVG sprites
- [ ] Spacing and layout guides
- [ ] Accessibility notes included

---

## Version History

### v1.0.0 (2025-10-11)

- Initial design system release
- Core component library
- Design tokens established
- Accessibility guidelines
- Animation specifications

### Planned Updates (v1.1.0)

- Dark mode support
- Extended component variants
- Advanced data visualization
- Mobile-specific patterns
- Performance optimizations

---

_This design system is a living document that evolves with the platform. Regular updates ensure consistency and scalability as the product grows._
