# Roadmap

Tracks build order and progress. Update as steps complete.

## Phase 1 — archetype + buying guidance (no catalog, no scraper) ✅ COMPLETE

- [x] **1. Catalog schema** — _superseded: not needed for Phase 1, see Phase 2 below_
- [x] **2. Quiz design** — 10 questions across 5 preference axes, 7 archetypes with full buying
      guidance (countries, regions, process, varieties, roast level, flavor notes, roasters)
- [x] **3. Matching logic** — Euclidean distance scoring in `app/matching.py`; also contains
      QUESTIONS list imported by the app
- [x] **4. Streamlit app** — one-question-at-a-time quiz with Back/Next, progress bar, results
      page with full archetype guidance in styled cards
- [x] **5. Deploy** — live at https://brew-match.streamlit.app/

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

- **Phase ordering decided:** catalog-seeding research showed most roaster sites are hard to scrape
  reliably (JavaScript-rendered product pages), so the original single-phase plan was split into
  Phase 1 (archetype only, ships fast, no stale-data risk) and Phase 2 (specific coffees, deferred
  until the scraper exists). See ARCHITECTURE.md for full reasoning.

- **Phase 1 complete (June 2026):** shipped a fully working public quiz app at
  https://brew-match.streamlit.app/. Users answer 10 multiple-choice questions across 5 preference
  axes (roast, acidity, flavor, body, adventurousness), get matched to one of 7 archetypes via
  Euclidean distance, and receive detailed buying guidance (countries, regions, process, varieties,
  roast level, flavor notes, roasters). Built with Streamlit, deployed via Streamlit Community
  Cloud, source on GitHub at github.com/anantc21/brew-match. Key learnings: Streamlit session
  state for multi-page quiz flow, decoupling design from data, phasing a project to ship fast
  without being blocked by the hardest parts.
