---
name: email-html-scaffold
description: The reusable email-safe HTML template NUNU fills per EDM — renders across clients + imports clean to HubSpot. Used by edm-campaign.
---

# email-html-scaffold

The base HTML NUNU starts every EDM from. The file is **`scaffold.html`** in this folder — copy it,
fill the `{{PLACEHOLDERS}}` from the project's guidelines + Claude Design reference, and test.

## When to use
- Any time NUNU builds an EDM (called by [[../edm-campaign/SKILL|edm-campaign]] at the HTML-build step).

## How to use
1. Copy `scaffold.html` to the project's campaign file (`projects/<project>/campaigns/<name>.html`).
2. Replace every `{{PLACEHOLDER}}` with sourced content — colours/type/imagery/logo from the Claude Design
   reference; copy from edm-campaign; real URLs for images + CTA; HubSpot tokens for unsubscribe/address.
3. Keep the rules: tables for layout, CSS inline on elements, ~600px, single column, no JS/external CSS,
   bulletproof (VML) button for Outlook, alt text on all images, dark-mode-aware.
4. Test in Outlook (Windows), Gmail, Apple Mail, iOS, and dark mode before handing to Yana.

## Output
- A filled, tested `.html` an EDM campaign uses; Yana imports it into HubSpot as a coded email.

## Gotchas
- The `<style>` block is progressive-enhancement only — assume some clients strip it; never rely on it.
- Outlook = Word engine: no flexbox/grid/float; tables + inline CSS + VML only.
- Must read correctly with images OFF (real text, alt text) — clients block images by default.
- HubSpot won't send without its required unsubscribe + physical-address tokens.
- Never bake copy into images (breaks accessibility, translation, image-off).
