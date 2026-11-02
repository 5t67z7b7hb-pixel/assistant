# HTML Documentation

**Domain:** Web document structure  
**Purpose:** A practical reference to authoring semantic, accessible HTML.

## What HTML does

HTML (HyperText Markup Language) describes the structure and meaning of web
content. A browser parses HTML into a document tree and combines it with CSS
and scripts to present an interactive page. HTML is markup, not a general
purpose programming language.

An element is commonly written with a start tag, content, and an end tag.
Some elements, such as `img` and `input`, are void elements and do not have an
end tag. Attributes provide additional information:

```html
<a href="https://example.com/">Visit the example site</a>
<img src="diagram.png" alt="A service connected to a database">
```

## Basic page structure

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Project Overview</title>
    <link rel="stylesheet" href="styles.css">
  </head>
  <body>
    <header>
      <h1>Project Overview</h1>
    </header>
    <main>
      <p>Welcome to the project guide.</p>
    </main>
  </body>
</html>
```

The doctype selects modern standards mode. `lang` identifies the document
language. The character encoding should be declared early. The viewport meta
element helps the page use the device's layout viewport. A descriptive title
helps users and assistive technologies identify the page.

## Semantic structure

Choose elements for their meaning:

- `header`, `nav`, `main`, `article`, `section`, and `footer` describe common
  page regions.
- `h1` through `h6` express a heading hierarchy; choose levels by structure,
  not by how large the text should look.
- `p`, `ul`, `ol`, and `li` represent paragraphs and lists.
- `button` represents an action; `a` represents navigation to a resource.
- `table`, `caption`, `th`, and `td` represent tabular data, not page layout.

Semantic HTML gives browsers and assistive technologies useful information
without requiring a developer to recreate standard behavior.

## Links, images, and forms

Use meaningful link text so the destination is understandable in context.
Provide alternative text for informative images; use an empty `alt` value for
purely decorative images. Do not put essential information only in an image.

Forms need visible labels and appropriate input types. `required` and browser
constraints improve usability but do not replace server-side validation.

```html
<form action="/signup" method="post">
  <label for="email">Email address</label>
  <input id="email" name="email" type="email" autocomplete="email" required>
  <button type="submit">Sign up</button>
</form>
```

Associate labels with controls, communicate errors in text, preserve entered
values where appropriate, and ensure the server validates all submitted data.

## Accessibility essentials

- Use native semantic elements before adding ARIA roles.
- Ensure all functionality works with a keyboard.
- Keep a logical heading order and visible focus indicators.
- Give controls accessible names and form inputs labels.
- Provide text alternatives for meaningful non-text content.
- Do not rely on color alone to convey meaning.
- Check contrast and test with assistive technology where relevant.

ARIA supplements HTML semantics; it does not automatically add keyboard
behavior or repair an inappropriate element choice.

## Security and robustness

Treat user-controlled content as untrusted. Escape or safely encode text for
its output context, use well-maintained templating and framework features,
and avoid inserting untrusted strings as raw HTML. Never rely on client-side
validation as the only validation. Use HTTPS and secure application-side
controls for sensitive operations.

Use valid, well-nested markup. Browser error recovery is not a substitute for
correct HTML, and malformed structure may cause different accessibility or
layout results.

## Further reading

- MDN HTML guide: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content
- WHATWG HTML Living Standard: https://html.spec.whatwg.org/
- W3C Web Accessibility Initiative: https://www.w3.org/WAI/
