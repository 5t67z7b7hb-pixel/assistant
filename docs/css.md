# CSS Documentation

**Domain:** Web presentation and layout  
**Purpose:** A practical reference to styling HTML with maintainable,
responsive CSS.

## What CSS does

CSS (Cascading Style Sheets) describes how HTML and other document content
should be presented. A browser matches selectors to elements, resolves
cascade and inheritance, computes layout, and paints the result.

```css
body {
  color: #202124;
  font-family: system-ui, sans-serif;
  line-height: 1.5;
}
```

## Selectors and declarations

A rule contains a selector and a declaration block. A declaration sets a
property to a value. Common selectors include element names, classes, IDs,
attribute selectors, and combinators:

```css
p { margin-block: 0 1rem; }
.notice { border-inline-start: 0.25rem solid #2457a7; }
input[type="email"] { max-width: 32rem; }
nav a { text-decoration: none; }
```

Prefer reusable class selectors for component styling. Avoid unnecessary
specificity and broad selectors that make later overrides difficult.

## Cascade, specificity, and inheritance

When multiple declarations apply, the cascade considers origin, importance,
layer, specificity, scope, and source order according to CSS rules. In
general, selectors with more specificity can override less-specific rules.
Some properties, such as `color` and `font-family`, commonly inherit;
properties such as `margin` do not.

Avoid relying on repeated `!important` declarations. Use clear component
styles, custom properties, and a deliberate stylesheet organization.

## Box model and layout

By default, an element's declared width applies to its content box. A common
reset is:

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}
```

Use Flexbox for one-dimensional alignment and distribution, and CSS Grid for
two-dimensional layouts. Normal document flow is often the best default.
Positioning should serve a specific layout need rather than compensate for
unclear markup.

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr));
  gap: 1rem;
}
```

## Responsive design

Responsive design adapts layouts and content to different viewport sizes and
user settings. Start with flexible layouts and intrinsic sizing, then add
media queries where the content needs a change:

```css
.page {
  width: min(100% - 2rem, 72rem);
  margin-inline: auto;
}

@media (min-width: 48rem) {
  .page-layout {
    display: grid;
    grid-template-columns: 16rem minmax(0, 1fr);
    gap: 2rem;
  }
}
```

Test narrow and wide viewports, text zoom, long content, and keyboard
navigation. Avoid assuming a particular device model or screen size.

## Custom properties and maintainability

CSS custom properties make repeated values easier to manage:

```css
:root {
  --color-text: #202124;
  --color-surface: #fff;
  --space-2: 0.5rem;
  --space-4: 1rem;
}

.panel {
  color: var(--color-text);
  background: var(--color-surface);
  padding: var(--space-4);
}
```

Organize styles consistently with the project. Keep component rules cohesive,
remove obsolete overrides, and avoid duplicating a design token across many
files.

## Accessibility and user preferences

Provide visible focus styles and sufficient contrast. Do not use color as the
only signal. Preserve sensible text resizing and avoid fixed heights that
clip content. Respect preferences such as reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Use motion only when it improves comprehension or feedback, and ensure
animated content does not obstruct access or cause discomfort.

## Debugging and common pitfalls

- Use browser developer tools to inspect computed styles, specificity, box
  dimensions, and layout.
- Check whether a declaration is overridden or invalid before adding another
  override.
- Prefer `min-width: 0` or `minmax(0, 1fr)` when grid/flex children overflow
  because of intrinsic content sizing.
- Avoid using fixed pixel widths for every region; combine flexible units,
  constraints, and intrinsic sizing.
- Validate contrast, keyboard focus, and content at zoomed text sizes.

## Further reading

- MDN CSS guide: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics
- MDN CSS reference: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference
- W3C CSS specifications: https://www.w3.org/Style/CSS/
