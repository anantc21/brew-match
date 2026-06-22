"""
matching.py — brew-match core logic

Takes a user's 10 quiz answers, computes their preference axis scores,
and finds the closest matching coffee archetype using Euclidean distance.

Axis order (used consistently throughout this file):
    [roast, acidity, flavor, body, adventurousness]

Sign convention:
    Roast:  -2 = light,   +2 = dark
    Body:   -2 = light,   +2 = heavy/syrupy
    Acidity: -2 = smooth, +2 = bright/tangy
    Flavor: -2 = chocolate/nutty, +2 = fruity/floral
    Adventurousness: -2 = prefers familiar, +2 = seeks funky
"""

import math


# ---------------------------------------------------------------------------
# ARCHETYPES
# Each archetype has:
#   - profile: list of 5 axis scores [roast, acidity, flavor, body, adventurousness]
#   - description: shown to the user as their result
#   - guidance: structured buying recommendations with the following fields:
#       - countries:    specific countries to look for
#       - regions:      notable growing regions within those countries
#       - process:      processing methods that suit this archetype
#       - varieties:    coffee varieties/cultivars to look for on the bag
#       - roast_level:  roast level range
#       - flavor_notes: tasting notes to look for
#       - roasters:     roasters known for this style (easy to expand — just add to the list)
# ---------------------------------------------------------------------------

ARCHETYPES = {
    "Bright & Floral Explorer": {
        "profile": [-2, +2, +2, -2, +1],
        "description": (
            "You gravitate toward coffees that are light, clean, and complex — think jasmine "
            "tea meets fresh citrus. You want brightness, not bitterness, and you're open to "
            "coffees that surprise you."
        ),
        "guidance": {
            "countries":    ["Ethiopia", "Kenya", "Colombia"],
            "regions":      ["Yirgacheffe", "Gedeo", "Nyeri", "Kirinyaga", "Huila"],
            "process":      ["Washed"],
            "varieties":    ["Ethiopian Heirloom", "SL28", "SL34", "Gesha"],
            "roast_level":  "Light",
            "flavor_notes": ["Jasmine", "Bergamot", "Orange blossom", "Citrus", "Stone fruit", "Black tea"],
            "roasters":     ["Sey Coffee", "Heart Coffee Roasters", "Sweet Bloom", "Black & White Coffee Roasters"],
        },
    },
    "Funky Fermenter": {
        "profile": [-1, +1, +2, +1, +2],
        "description": (
            "You're not just open to unusual coffee — you actively seek it out. Tropical fruit, "
            "wine-like complexity, and fermented funk are features, not bugs."
        ),
        "guidance": {
            "countries":    ["Ethiopia", "Colombia", "Ecuador", "Panama"],
            "regions":      ["Gedeo", "Huila", "Nariño", "Pichincha"],
            "process":      ["Natural", "Anaerobic", "Co-fermented", "Carbonic maceration"],
            "varieties":    ["Ethiopian Heirloom", "Gesha", "Pink Bourbon", "Sidra", "Typica Mejorado"],
            "roast_level":  "Light to light-medium",
            "flavor_notes": ["Tropical fruit", "Blueberry", "Red wine", "Passion fruit", "Mango", "Fermented complexity"],
            "roasters":     ["Onyx Coffee Lab", "Sweet Bloom", "Black & White Coffee Roasters", "Hydrangea Coffee"],
        },
    },
    "Clean Classic": {
        "profile": [-1, +1, 0, -1, -1],
        "description": (
            "You appreciate quality and brightness but don't need anything wild. A well-sourced, "
            "cleanly roasted coffee from a reliable origin is your sweet spot — no drama, just "
            "good coffee."
        ),
        "guidance": {
            "countries":    ["Colombia", "Costa Rica", "Guatemala", "Peru"],
            "regions":      ["Huila", "Nariño", "Tarrazu", "Antigua", "Cajamarca"],
            "process":      ["Washed"],
            "varieties":    ["Caturra", "Castillo", "Catuai", "Bourbon", "Typica"],
            "roast_level":  "Light to light-medium",
            "flavor_notes": ["Balanced sweetness", "Light citrus", "Caramel", "Apple", "Clean finish"],
            "roasters":     ["Prodigal Coffee", "Passenger Coffee", "Heart Coffee Roasters", "Sweet Bloom"],
        },
    },
    "Balanced Curious": {
        "profile": [0, 0, 0, 0, 0],
        "description": (
            "You're in the middle on most things — not chasing brightness or boldness, not "
            "seeking the unusual but not avoiding it either. A great starting point for "
            "exploring specialty coffee."
        ),
        "guidance": {
            "countries":    ["Colombia", "Brazil", "Peru", "Honduras"],
            "regions":      ["Huila", "Sul de Minas", "Cajamarca", "Marcala"],
            "process":      ["Washed", "Honey"],
            "varieties":    ["Caturra", "Bourbon", "Yellow Bourbon", "Catuai"],
            "roast_level":  "Medium",
            "flavor_notes": ["Caramel", "Milk chocolate", "Apple", "Brown sugar", "Gentle sweetness"],
            "roasters":     ["Prodigal Coffee", "Passenger Coffee", "Sweet Bloom"],
        },
    },
    "Smooth Operator": {
        "profile": [0, -1, -1, +1, -1],
        "description": (
            "You want your coffee to feel comfortable — not sour, not thin, not weird. "
            "Sweetness, body, and smoothness matter more to you than brightness or complexity."
        ),
        "guidance": {
            "countries":    ["Brazil", "Costa Rica", "Peru", "Bolivia"],
            "regions":      ["Sul de Minas", "Cerrado", "Tarrazu", "Cajamarca"],
            "process":      ["Honey", "Pulped natural", "Yellow honey"],
            "varieties":    ["Yellow Bourbon", "Red Catuai", "Catuai", "Mundo Novo"],
            "roast_level":  "Medium",
            "flavor_notes": ["Caramel", "Brown sugar", "Milk chocolate", "Hazelnut", "Nougat", "Soft body"],
            "roasters":     ["Passenger Coffee", "Prodigal Coffee", "Onyx Coffee Lab"],
        },
    },
    "Cozy Comforter": {
        "profile": [+1, -2, -2, +1, -2],
        "description": (
            "Coffee should be warm, familiar, and comforting. You're not looking for brightness "
            "or complexity — you want something rich, sweet, and reliable that feels like home."
        ),
        "guidance": {
            "countries":    ["Indonesia", "Brazil", "Guatemala"],
            "regions":      ["Sumatra (Mandheling, Gayo)", "Sul de Minas", "Antigua"],
            "process":      ["Wet-hulled", "Natural", "Pulped natural"],
            "varieties":    ["Bourbon", "Typica", "Tim Tim", "Jember"],
            "roast_level":  "Medium-dark",
            "flavor_notes": ["Dark chocolate", "Baking spice", "Molasses", "Brown sugar", "Cedar", "Full body"],
            "roasters":     ["Onyx Coffee Lab", "Passenger Coffee"],
        },
    },
    "Bold Brewer": {
        "profile": [+2, -2, -1, +2, -2],
        "description": (
            "You want your coffee to mean business — bold, heavy, and unapologetically dark. "
            "Nothing delicate, nothing sour. Works great with milk if you drink it that way."
        ),
        "guidance": {
            "countries":    ["Indonesia", "Brazil", "blends"],
            "regions":      ["Sumatra (Mandheling)", "Sulawesi", "Cerrado"],
            "process":      ["Wet-hulled", "Natural"],
            "varieties":    ["Bourbon", "Typica", "Tim Tim", "espresso blends"],
            "roast_level":  "Dark",
            "flavor_notes": ["Smoky", "Dark chocolate", "Molasses", "Cedar", "Tobacco", "Great with cream"],
            "roasters":     ["Onyx Coffee Lab", "Passenger Coffee"],
        },
    },
}


# ---------------------------------------------------------------------------
# STEP 1: compute axis scores from 10 answers
# ---------------------------------------------------------------------------

def compute_axis_scores(answers):
    """
    Takes a list of 10 answers (each -2, -1, 0, +1, or +2) and returns
    a list of 5 axis scores, one per axis.

    Question-to-axis mapping (0-indexed):
        Q1, Q2  → roast          (answers[0], answers[1])
        Q3, Q4  → acidity        (answers[2], answers[3])
        Q5, Q6  → flavor         (answers[4], answers[5])
        Q7, Q8  → body           (answers[6], answers[7])
        Q9, Q10 → adventurousness (answers[8], answers[9])

    Each axis score is the average of its two questions.
    Result is a list: [roast, acidity, flavor, body, adventurousness]
    """

    # Validate — we need exactly 10 answers, each between -2 and +2
    if len(answers) != 10:
        raise ValueError(f"Expected 10 answers, got {len(answers)}")
    for i, answer in enumerate(answers):
        if answer not in [-2, -1, 0, 1, 2]:
            raise ValueError(f"Answer {i+1} must be -2, -1, 0, 1, or 2. Got: {answer}")

    # Average each pair to get an axis score
    roast           = (answers[0] + answers[1]) / 2
    acidity         = (answers[2] + answers[3]) / 2
    flavor          = (answers[4] + answers[5]) / 2
    body            = (answers[6] + answers[7]) / 2
    adventurousness = (answers[8] + answers[9]) / 2

    return [roast, acidity, flavor, body, adventurousness]


# ---------------------------------------------------------------------------
# STEP 2: calculate Euclidean distance between user scores and one archetype
# ---------------------------------------------------------------------------

def euclidean_distance(user_scores, archetype_profile):
    """
    Measures how far apart a user's axis scores are from one archetype's profile.
    Lower = closer match.

    Euclidean distance across 5 dimensions:
        sqrt( (u1-a1)^2 + (u2-a2)^2 + (u3-a3)^2 + (u4-a4)^2 + (u5-a5)^2 )

    Think of it like measuring straight-line distance between two points,
    but in 5-dimensional space (one dimension per axis) instead of 2D or 3D.
    """

    # zip() pairs up corresponding values: user_scores[0] with archetype_profile[0], etc.
    squared_differences = [
        (user_val - archetype_val) ** 2
        for user_val, archetype_val in zip(user_scores, archetype_profile)
    ]

    return math.sqrt(sum(squared_differences))


# ---------------------------------------------------------------------------
# STEP 3: find the best matching archetype
# ---------------------------------------------------------------------------

def find_match(answers):
    """
    Takes a list of 10 answers, computes axis scores, then finds the archetype
    with the smallest Euclidean distance to those scores.

    Returns a dict with:
        - name: the archetype name
        - description: the result description shown to the user
        - guidance: buying guidance dict
        - axis_scores: the user's 5 axis scores (useful for debugging)
        - distance: how close the match was (lower = better)
    """

    # Step 1: turn 10 answers into 5 axis scores
    user_scores = compute_axis_scores(answers)

    # Step 2: find the closest archetype
    best_name     = None
    best_distance = float("inf")  # start with infinity so any real distance beats it

    for name, archetype in ARCHETYPES.items():
        distance = euclidean_distance(user_scores, archetype["profile"])

        if distance < best_distance:
            best_distance = distance
            best_name     = name

    # Step 3: return the winner with everything needed to display the result
    winner = ARCHETYPES[best_name]

    return {
        "name":        best_name,
        "description": winner["description"],
        "guidance":    winner["guidance"],
        "axis_scores": {
            "roast":           user_scores[0],
            "acidity":         user_scores[1],
            "flavor":          user_scores[2],
            "body":            user_scores[3],
            "adventurousness": user_scores[4],
        },
        "distance": round(best_distance, 3),
    }


# ---------------------------------------------------------------------------
# QUICK TEST — run this file directly to verify it works
# python matching.py
# ---------------------------------------------------------------------------

def print_result(label, result):
    """Helper to print a result in a readable format for testing."""
    g = result["guidance"]
    print(f"{label}")
    print(f"  Match:        {result['name']}")
    print(f"  Distance:     {result['distance']}")
    print(f"  Axis scores:  {result['axis_scores']}")
    print(f"  Description:  {result['description'][:80]}...")
    print(f"  Countries:    {', '.join(g['countries'])}")
    print(f"  Regions:      {', '.join(g['regions'])}")
    print(f"  Process:      {', '.join(g['process'])}")
    print(f"  Varieties:    {', '.join(g['varieties'])}")
    print(f"  Roast level:  {g['roast_level']}")
    print(f"  Flavor notes: {', '.join(g['flavor_notes'])}")
    print(f"  Roasters:     {', '.join(g['roasters'])}")
    print()


if __name__ == "__main__":

    # Test case 1: should match "Bright & Floral Explorer"
    test_answers_light = [-2, -2, +2, +2, +2, +2, -2, -2, +1, +2]
    print_result("Test 1 — light/floral/adventurous:", find_match(test_answers_light))

    # Test case 2: should match "Bold Brewer"
    test_answers_dark = [+2, +2, -2, -2, -2, -2, +2, +2, -2, -2]
    print_result("Test 2 — dark/bold/unadventurous:", find_match(test_answers_dark))

    # Test case 3: should match "Balanced Curious"
    test_answers_balanced = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    print_result("Test 3 — all neutral:", find_match(test_answers_balanced))
