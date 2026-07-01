---
name: edm-campaign
description: Produce a Frank-grade EDM campaign as email-safe, HubSpot-ready HTML — source-grounded, project-precise, and never generic. NUNU's core marketing deliverable.
---

# edm-campaign

How NUNU builds an EDM (email campaign) for a Frank Developments project that Yana can import into
HubSpot and send — at Frank's craft bar, never AI-generic. This skill is the method; the *soul* is in
[[../../nunu-soul|the Critical Rule]]: draw from the project's real materials, or don't draft at all.

## When to use
- Yana needs an EDM campaign for a specific Frank project (launch, milestone, event, price/stage release, nurture).

## Inputs (from that project's folder in nunu-wiki — REQUIRED, do not draft without them)
- The project's **guidelines** (positioning, do/don't, mandatories, legal/compliance lines).
- **Brand voice** (Frank's tone; this project's specific voice notes).
- The **Claude Design reference / exported project archive** (colours, type, imagery, hero, logo lockups).
- The **campaign brief**: goal (what buyer action?), audience segment, the project moment being promoted, any dated/price details.
- If any of these are missing → flag it to Yana and stop. Missing source = generic output = failure.

## Method
1. **Absorb the source.** Read the project's guidelines + brand voice + design reference fully before writing a word. Extract the specific, ownable details (the actual amenity, the actual locale, the actual buyer, the real hook). Generic comes from inventing; specific comes from the source.
2. **Define the job.** One campaign = one clear action (register interest / book a viewing / RSVP / download). Write the goal down; everything serves it.
3. **Structure** (adapt per brief): subject line + preheader → hero (image + headline that could only be THIS project) → 1–3 tight body sections (each a real, concrete reason, not a superlative) → single primary CTA → compliant footer (unsubscribe, address, any legal line from the guidelines).
4. **Write in Frank's voice.** Structured storytelling (lean on Yana's journalism/PR instinct). Concrete over grand. Cut every hollow adjective ("stunning", "luxurious", "nestled") unless the guidelines earn it. Rhythm and restraint. It should read like a person who knows the project wrote it.
5. **Build as email-safe HTML** (see the [[../email-html-scaffold/SKILL|email-HTML scaffold]]): tables for layout, **all CSS inline**, ~600px width, web-safe/fallback fonts, images with alt text + hosted URLs, bulletproof buttons, dark-mode-aware, no JS, no external stylesheets. HubSpot-importable as a custom/coded email.
6. **Anti-generic pass** — run the [[../brand-fidelity-check/SKILL|brand-fidelity checklist]]. The one question that governs everything: *could this email belong to any other developer or project?* If yes, it's not done — rebuild from the source materials until it could only be this one.
7. **Hand off to Yana** — deliver the `.html` + a short note: what to review, what to personalise, which merge fields/tokens to set in HubSpot, and any detail you inferred vs. sourced (flag inferences honestly). Yana is the final voice and sender; NUNU gets it to craft-ready, not shipped.

## Output
- An email-compatible `.html` file (renders in HubSpot + major clients), plus a handoff note. Saved under the project's folder in nunu-wiki with the campaign name + date.

## Gotchas (email HTML is its own world)
- **Outlook** uses Word's rendering engine — tables + inline CSS + VML for buttons/background images; flexbox/grid/float will break.
- **Image blocking** — the email must make sense with images off; real text, never text-baked-into-images; always alt text.
- **Dark mode** clients invert colours — test logos/backgrounds; use `@media (prefers-color-scheme)` where supported and pick colours that survive inversion.
- **~600px** content width; single-column is safest on mobile.
- **HubSpot import** — coded email templates need HubSpot's required tokens (unsubscribe, physical address) or it won't send; leave clean merge fields for personalisation.
- **Never fabricate** project facts, prices, dates, or claims — those come from the brief/guidelines only. A wrong price in a buyer email is a real problem.
- **Compliance** — include whatever the project guidelines mandate (disclaimers, REA/legal lines). Property marketing has rules.
