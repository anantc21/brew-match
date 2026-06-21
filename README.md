# brew-match

A public, free quiz app that asks users about their coffee preferences and recommends:
1. A **coffee archetype** (a "type" of coffee — e.g. "Bright & Funky Explorer," "Classic Comforting Roast")
2. **Specific coffees** currently available from real roasters that match that archetype

Built as a personal learning project — first major step beyond the `coffee-log` MCP server, focused on
data pipelines, scheduled automation, and shipping something other people can actually use.

## Status

🟡 **Planning / documentation phase** — architecture decided, no code yet.

## How it works (high level)

**Phase 1 (building now):**
1. User takes a short quiz in a web app (Streamlit)
2. Quiz answers map to preference axes (acidity, body, roast level, adventurousness, etc.)
3. Axes combine into an **archetype**, shown along with general buying guidance (origins,
   processes, roast levels, and flavor notes to look for)

**Phase 2 (later, deferred):**
4. The archetype is matched against a **catalog** of real, current coffees (scraped from roaster
   sites, refreshed on a schedule)
5. User also gets back a short list of specific matching coffees with links to buy

## Why this is harder than it sounds

Roasters change their offerings constantly, and most roaster websites turned out to be difficult to
reliably scrape for a one-time seed (JavaScript-rendered product pages, inconsistent site
structures). Rather than let that block the whole project, Phase 1 ships without any real-coffee
catalog at all — see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full reasoning behind
this phased approach, and why a scraped catalog is deferred to Phase 2 rather than required up
front.

## Project structure (planned)

```
brew-match/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md      # key design decisions and why
│   └── ROADMAP.md           # build order / milestones
├── catalog/
│   └── catalog.json         # the coffee catalog data (built by the scraper)
├── scraper/                 # catalog builder — runs on a schedule, not live
├── app/                     # the Streamlit app
└── .github/workflows/       # scheduled scraper automation (GitHub Actions)
```

## Learning goals for this project

- Building a small data pipeline (scrape → clean → store → serve)
- Scheduled automation (GitHub Actions on a cron schedule)
- Shipping a simple public web app (Streamlit)
- Designing for stale/unreliable external data honestly, instead of pretending it's real-time
