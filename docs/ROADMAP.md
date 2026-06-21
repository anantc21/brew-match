# Roadmap

Tracks build order and progress. Update as steps complete.

- [ ] **1. Catalog schema** — define fields (origin, process, variety, roaster, flavor notes, roast
      level, intensity/body, price, buy link, last_verified)
- [ ] **2. Seed catalog manually** — hand-enter ~20-30 coffees so the app has something to recommend
      from day one, no scraper required yet
- [ ] **3. Quiz design** — questions → preference axes → archetype definitions
- [ ] **4. Matching logic** — score catalog coffees against a finished archetype, return top N with
      explanation of why each matched
- [ ] **5. Streamlit app** — quiz flow + results page, reading from `catalog/catalog.json`
- [ ] **6. Deploy** — push to GitHub, deploy via Streamlit Community Cloud, get a public shareable link
- [ ] **7. (Stretch) Scraper module** — automate catalog growth/freshness per roaster, scheduled via
      GitHub Actions; added incrementally, one roaster at a time

## Milestone log

_(Add an entry here each time a step above is completed — what was built, how it works, what was
learned. This becomes the project's reference entry for the knowledge base doc.)_
