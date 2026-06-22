# Quiz Design

This doc is the authoritative reference for the quiz — axes, questions, scoring, and archetypes.
The matching logic and Streamlit app are both built from this spec.

---

## Sign convention

For axes with a "light" concept (Roast, Body):
- **Light/delicate = -2**
- **Heavy/dark = +2**

For all other axes (Acidity, Flavor, Adventurousness):
- **Low end = -2** (smooth, chocolatey, unadventurous)
- **High end = +2** (tangy, fruity/floral, adventurous)

This convention must be followed consistently in every question, every archetype profile, and all
matching logic — flipping it in one place without the others silently breaks the scoring.

---

## Preference axes

Each question maps to one of 5 axes. A user's final score on each axis is the average of the two
questions that feed it.

| Axis | What it captures | Range |
|---|---|---|
| **Roast** | Preferred roast level / coffee intensity | -2 (light) → +2 (dark) |
| **Acidity** | Tolerance for brightness/tartness | -2 (prefers smooth) → +2 (loves bright) |
| **Flavor** | Preferred flavor family | -2 (chocolate/nutty) → +2 (fruity/floral) |
| **Body** | Preferred mouthfeel / texture | -2 (light, tea-like) → +2 (heavy, syrupy) |
| **Adventurousness** | Openness to unusual/experimental coffee | -2 (prefers familiar) → +2 (seeks funky) |

---

## Questions

Each question has 5 options scored -2, -1, 0, +1, +2.

### Q1 — Roast
**When you imagine your ideal cup of coffee, what's the vibe?**
| Score | Option |
|---|---|
| -2 | Light & delicate, tea-like |
| -1 | Light-medium |
| 0 | Balanced, middle of the road |
| +1 | Rich, medium-dark |
| +2 | Bold, dark, intense |

### Q2 — Roast
**How strong or intense do you like your coffee to taste?**
| Score | Option |
|---|---|
| -2 | Very mild & delicate |
| -1 | Somewhat mild |
| 0 | Medium strength |
| +1 | Fairly strong |
| +2 | Very strong & intense |

### Q3 — Acidity
**Do you enjoy tangy or tart flavors generally — citrus, tart fruit, lemonade?**
| Score | Option |
|---|---|
| -2 | Not at all, prefer smooth |
| -1 | Not really, prefer mild |
| 0 | Fine in moderation |
| +1 | Yes, I like some brightness |
| +2 | Love it, the tangier the better |

### Q4 — Acidity
**A coffee tastes "sour" to you — is that a dealbreaker?**
| Score | Option |
|---|---|
| -2 | Sourness ruins it for me |
| -1 | Mostly a turnoff |
| 0 | Depends on context |
| +1 | Not really bothered |
| +2 | Not at all, that's brightness! |

### Q5 — Flavor
**Pick a flavor you'd want to taste in your coffee:**
| Score | Option |
|---|---|
| -2 | Chocolate, nuts, or baking spice |
| -1 | Caramel leaning spiced or nutty |
| 0 | Caramel or vanilla, neutral |
| +1 | Mild fruit, apple, or light citrus |
| +2 | Bold berries, citrus, or floral |

### Q6 — Flavor
**Sweet treat pairing — pick one:**
| Score | Option |
|---|---|
| -2 | Brownie |
| -1 | Spiced cookie |
| 0 | Caramel flan |
| +1 | Citrus tart |
| +2 | Fresh berry tart |

### Q7 — Body
**Ideal coffee texture or mouthfeel?**
| Score | Option |
|---|---|
| -2 | Light, like tea |
| -1 | Light-medium |
| 0 | Medium |
| +1 | Medium-heavy |
| +2 | Thick, syrupy, coats your mouth |

### Q8 — Body
**Milk or no milk, normally?**
| Score | Option |
|---|---|
| -2 | Black, nothing added |
| -1 | Just a splash sometimes |
| 0 | A little milk regularly |
| +1 | Regular milk or cream |
| +2 | Latte or cream-heavy |

### Q9 — Adventurousness
**How do you feel about trying weird or experimental things in food or drink?**
| Score | Option |
|---|---|
| -2 | Like to know exactly what I'm getting |
| -1 | Rarely venture out |
| 0 | Open occasionally |
| +1 | Pretty open generally |
| +2 | Love it, bring on the unusual |

### Q10 — Adventurousness
**Have you ever intentionally ordered a coffee that sounded weird or unfamiliar?**
| Score | Option |
|---|---|
| -2 | No, and I wouldn't |
| -1 | No, probably wouldn't |
| 0 | Maybe once or twice |
| +1 | Yes, a few times |
| +2 | Yes, regularly — that's half the fun |

---

## Scoring

For each axis, average the scores of its two questions:

```
roast_score          = (Q1 + Q2) / 2
acidity_score        = (Q3 + Q4) / 2
flavor_score         = (Q5 + Q6) / 2
body_score           = (Q7 + Q8) / 2
adventurousness_score = (Q9 + Q10) / 2
```

Each axis score is a float in the range [-2.0, +2.0].

---

## Archetype matching

Find the archetype whose profile is closest to the user's axis scores. "Closest" is measured
using **Euclidean distance** across all 5 axes — the archetype with the smallest distance wins.

```
distance = sqrt(
    (user_roast - archetype_roast)^2 +
    (user_acidity - archetype_acidity)^2 +
    (user_flavor - archetype_flavor)^2 +
    (user_body - archetype_body)^2 +
    (user_adventurousness - archetype_adventurousness)^2
)
```

The archetype with the **lowest distance** is the recommendation.

---

## Archetypes

Profiles listed as: Roast / Acidity / Flavor / Body / Adventurousness

### 1. Bright & Floral Explorer
**Profile:** -2 / +2 / +2 / -2 / +1

**Description:** You gravitate toward coffees that are light, clean, and complex — think jasmine
tea meets fresh citrus. You want brightness, not bitterness, and you're open to coffees that
surprise you.

**Buying guidance:**
- **Origin:** Ethiopia (Yirgacheffe, Gedeo), Kenya
- **Process:** Washed
- **Roast:** Light
- **Notes to look for:** Jasmine, bergamot, orange blossom, citrus, stone fruit

---

### 2. Funky Fermenter
**Profile:** -1 / +1 / +2 / +1 / +2

**Description:** You're not just open to unusual coffee — you actively seek it out. Tropical fruit,
wine-like complexity, and fermented funk are features, not bugs.

**Buying guidance:**
- **Origin:** Ethiopia, Colombia, Ecuador
- **Process:** Natural, anaerobic, or co-fermented
- **Roast:** Light to light-medium
- **Notes to look for:** Tropical fruit, blueberry, red wine, passion fruit, fermented complexity

---

### 3. Clean Classic
**Profile:** -1 / +1 / 0 / -1 / -1

**Description:** You appreciate quality and brightness but don't need anything wild. A well-sourced,
cleanly roasted coffee from a reliable origin is your sweet spot — no drama, just good coffee.

**Buying guidance:**
- **Origin:** Colombia, Costa Rica, Guatemala
- **Process:** Washed
- **Roast:** Light to light-medium
- **Notes to look for:** Balanced sweetness, light citrus, caramel, clean finish

---

### 4. Balanced Curious
**Profile:** 0 / 0 / 0 / 0 / 0

**Description:** You're in the middle on most things — not chasing brightness or boldness, not
seeking the unusual but not avoiding it either. A great starting point for exploring specialty
coffee.

**Buying guidance:**
- **Origin:** Colombia, Brazil, Peru — approachable origins with broad appeal
- **Process:** Washed or honey
- **Roast:** Medium
- **Notes to look for:** Caramel, milk chocolate, apple, gentle sweetness — nothing polarizing

---

### 5. Smooth Operator
**Profile:** 0 / -1 / -1 / +1 / -1

**Description:** You want your coffee to feel comfortable — not sour, not thin, not weird. Sweetness,
body, and smoothness matter more to you than brightness or complexity.

**Buying guidance:**
- **Origin:** Brazil, Costa Rica, Peru
- **Process:** Honey or pulped natural
- **Roast:** Medium
- **Notes to look for:** Caramel, brown sugar, milk chocolate, hazelnut, soft body

---

### 6. Cozy Comforter
**Profile:** +1 / -2 / -2 / +1 / -2

**Description:** Coffee should be warm, familiar, and comforting. You're not looking for brightness
or complexity — you want something rich, sweet, and reliable that feels like home.

**Buying guidance:**
- **Origin:** Sumatra, Brazil, or house blends
- **Process:** Wet-hulled (Sumatra), natural (Brazil)
- **Roast:** Medium-dark
- **Notes to look for:** Dark chocolate, baking spice, molasses, brown sugar, full body

---

### 7. Bold Brewer
**Profile:** +2 / -2 / -1 / +2 / -2

**Description:** You want your coffee to mean business — bold, heavy, and unapologetically dark.
Nothing delicate, nothing sour. Works great with milk if you drink it that way.

**Buying guidance:**
- **Origin:** Sumatra, blends designed for espresso or dark roast
- **Process:** Wet-hulled or natural
- **Roast:** Dark
- **Notes to look for:** Smoky, dark chocolate, molasses, cedar — great as espresso or with cream
