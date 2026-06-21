# Roadmap

Tracks build order and progress. Update as steps complete.

## Phase 1 — archetype + buying guidance (no catalog, no scraper)

- [x] **1. Catalog schema** — _superseded: not needed for Phase 1, see Phase 2 below_
- [ ] **2. Quiz design** — questions → preference axes → archetype definitions, plus the general
      buying-guidance text for each archetype (origins/processes/roast levels/notes to look for)
- [ ] **3. Matching logic** — score quiz answers against the axes, return the best-fit archetype
- [ ] **4. Streamlit app** — quiz flow + results page showing archetype + buying guidance
- [ ] **5. Deploy** — push to GitHub, deploy via Streamlit Community Cloud, get a public shareable
      link, post it

## Phase 2 — specific coffee recommendations (deferred until Phase 1 ships)

- [ ] **6. Catalog schema** — define fields (origin, process, variety, roaster, flavor notes, roast
      level, intensity/body, price, buy link, last_verified, status)
- [ ] **7. Seed catalog** — hand-enter or research an initial set of real coffees per archetype
- [ ] **8. Archetype → catalog matching** — score catalog coffees against an archetype, return top N
      with explanation
- [ ] **9. Wire into the app** — results page shows specific coffee examples alongside the archetype
- [ ] **10. Scraper module** — automate catalog growth/freshness per roaster (Shopify
      `/products.json` is the likely starting technique — see ARCHITECTURE.md), scheduled via
      GitHub Actions, added incrementally one roaster at a time

## Milestone log

_(Add an entry here each time a step above is completed — what was built, how it works, what was
learned. This becomes the project's reference entry for the knowledge base doc.)_

- Phase ordering decided: catalog-seeding research showed most roaster sites are hard to scrape
  reliably (JavaScript-rendered product pages), so the original single-phase plan was split into
  Phase 1 (archetype only, ships fast, no stale-data risk) and Phase 2 (specific coffees, deferred
  until the scraper exists). See ARCHITECTURE.md for full reasoning.

