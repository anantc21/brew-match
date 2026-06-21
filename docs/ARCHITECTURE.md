# Architecture

This doc captures the *why* behind the design, not just the *what* — so future-me (or anyone else)
understands the reasoning, not just the file structure.

## Core design decision: this is NOT a machine learning project

Recommendation engines often default to "train a model on past data." That doesn't apply here:
there's no large set of (user preferences → coffee they loved) pairs to learn from, especially for
strangers using the app once. Instead, this is a **transparent scoring system**: quiz answers map to
preference axes, axes are scored against a catalog of coffees, best matches win. Every recommendation
should be explainable ("matched: washed process, floral notes overlap with your 'floral' answer"),
not a black box.

## Core design decision: decouple the catalog from the live app

**The problem:** roaster offerings change constantly (days, not months). Coffees sell out. Live
scraping on every quiz submission would be slow, fragile (one roaster's site changes layout, app
breaks), and a bad first impression for a public Reddit launch.

**The solution:** split into two independent systems that only share a data file.

1. **Catalog builder** (`/scraper`) — runs occasionally, on a schedule, NOT as part of a user's quiz
   session. Scrapes roaster sites, cleans the data, writes it to `catalog/catalog.json`. If a scraper
   for one roaster breaks, it doesn't take down the live app — it just means that roaster's listings
   go stale until fixed.
2. **Live app** (`/app`) — a Streamlit app that only ever reads `catalog/catalog.json`. Fast, has no
   live network dependency on roaster websites, never breaks because an external site changed.

This means the app is shippable with a hand-curated catalog (no scraper at all) on day one, and the
scraper becomes a pure upgrade later with zero changes needed to the quiz or matching logic.

## Core design decision: be honest about staleness, don't hide it

Even with scheduled refreshing, the catalog will never be perfectly real-time. Rather than pretend
otherwise:

- Every catalog entry has a `last_verified` timestamp, shown to the user.
- Every recommendation includes a **direct link to the roaster's product page** — the app's
  recommendation is "a good lead," the roaster's page is the source of truth on actual availability.
- Copy in the app should frame results as "a coffee in this style, last seen at this roaster" rather
  than a guaranteed in-stock claim.

## Keeping the catalog fresh: scheduled automation, not manual refresh

The scraper script is run automatically on a timer using **GitHub Actions** (a free CI/CD feature of
GitHub repos that can run scripts on a schedule, e.g. weekly). Flow:

```
GitHub Actions (cron schedule)
  → runs scraper script on GitHub's servers
  → scraper writes updated catalog/catalog.json
  → commits the change back to the repo
  → Streamlit Cloud auto-redeploys / re-reads the updated file
```

This means the catalog stays reasonably fresh without requiring a personal server running 24/7, and
without you needing to remember to run anything manually.

## Why Streamlit (not Flask/React) for the app

Beginner-appropriate: turns a Python script into a shareable, public web app with minimal extra
concepts (no separate frontend/backend split to learn yet). Free hosting via Streamlit Community
Cloud, which also makes the GitHub-Actions-refresh → auto-redeploy flow simple, since it reads
straight from the repo.

## Scraping considerations / open risk

No standardized API exists across specialty coffee roasters — each site needs its own scraping logic,
and logic can break when a site redesigns. Before scraping any given roaster's site, check their
`robots.txt` and terms of service. This is the highest-maintenance, highest-risk part of the project,
which is why it's explicitly decoupled (see above) rather than load-bearing for the app to function.

## Core design decision: phase the project — archetype first, specific coffees later

**The problem this solves:** seeding a real catalog of specific coffees turned out to be far harder
than expected even for a one-time manual pass — most roaster websites load their product listings
with JavaScript that simple scraping/fetching tools can't see, and the data that *is* reachable is
fragmented and inconsistently fresh. Building a reliable catalog is genuinely a project of its own
(see the scraper section above), and it shouldn't block the rest of the app from shipping.

**The resolution:** split the product into two phases with different scopes, not two different
products.

- **Phase 1 (build now):** the quiz produces a **taste archetype** plus **general buying guidance**
  — e.g. "look for washed Ethiopian or Colombian coffees, light roast, notes like jasmine or stone
  fruit." This requires no catalog, no scraper, and nothing that can go stale, because it's
  describing a *style*, not a specific in-stock product. This is a complete, shippable app on its
  own — not a placeholder.
- **Phase 2 (later, after Phase 1 ships):** layer specific, real coffee recommendations on top of
  the archetype, sourced from the catalog described above (manually seeded at first, automated via
  scraper + GitHub Actions eventually). This was originally roadmap step 7 ("stretch scraper
  module") — it's unchanged in scope, just explicitly positioned as additive rather than a
  blocker.

This means the hardest, most failure-prone part of the project (live, current coffee data) is no
longer load-bearing for getting anything real into users' hands.

## Note on scraping technique (learned during Phase 1 research)

Most specialty roasters run on Shopify. Shopify stores conventionally expose a `/products.json`
endpoint with clean, structured product data (no JavaScript rendering required) — this is the
likely foundation for the Phase 2 scraper, found while testing catalog-seeding approaches. Worth
re-validating per roaster when Phase 2 starts, since not every store has this open and not every
roaster uses Shopify.

## Open questions / not yet decided

- Exact quiz questions and preference axes
- Archetype definitions and the buying-guidance text for each
- Matching/scoring algorithm details (now: quiz answers → archetype, not yet: archetype → catalog)
- Catalog schema and scraper approach — deferred to Phase 2
