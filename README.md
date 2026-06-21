# brew-match

A public, free quiz app that asks users about their coffee preferences and recommends:
1. A **coffee archetype** (a "type" of coffee — e.g. "Bright & Funky Explorer," "Classic Comforting Roast")
2. **Specific coffees** currently available from real roasters that match that archetype

Built as a personal learning project — first major step beyond the `coffee-log` MCP server, focused on
data pipelines, scheduled automation, and shipping something other people can actually use.

## Status

🟡 **Planning / documentation phase** — architecture decided, no code yet.

## How it works (high level)

1. User takes a short quiz in a web app (Streamlit)
2. Quiz answers map to preference axes (acidity, body, roast level, adventurousness, etc.)
3. Axes combine into an **archetype**
4. Archetype is matched against a **catalog** of real coffees (scraped from roaster sites, refreshed on a schedule)
5. User gets back: their archetype description + a short list of matching coffees with links to buy

## Why this is harder than it sounds

Roasters change their offerings constantly. A catalog scraped once goes stale fast. See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for how this project handles that — short version:
the catalog is built by a separate, scheduled scraper job (not live-scraped per user), and every
recommendation shows a "last verified" date plus a direct link to the roaster so the user always
has ground truth, not a stale promise.

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
