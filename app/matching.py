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
# QUESTIONS
# Each question is a dict with:
#   - text:    the question shown to the user
#   - axis:    which preference axis this question feeds into
#   - options: list of (display_label, score) tuples, always 5 options
#              ordered from most negative (-2) to most positive (+2)
# ---------------------------------------------------------------------------

QUESTIONS = [
    {
        "text": "When you imagine your ideal cup of coffee, what's the vibe?",
        "axis": "roast",
        "options": [
            ("Light & delicate, tea-like", -2),
            ("Light-medium", -1),
            ("Balanced, middle of the road", 0),
            ("Rich, medium-dark", 1),
            ("Bold, dark, intense", 2),
        ],
    },
    {
        "text": "How strong or intense do you like your coffee to taste?",
        "axis": "roast",
        "options": [
            ("Very mild & delicate", -2),
            ("Somewhat mild", -1),
            ("Medium strength", 0),
            ("Fairly strong", 1),
            ("Very strong & intense", 2),
        ],
    },
    {
        "text": "Do you enjoy tangy or tart flavors generally — citrus, tart fruit, lemonade?",
        "axis": "acidity",
        "options": [
            ("Not at all, prefer smooth", -2),
            ("Not really, prefer mild", -1),
            ("Fine in moderation", 0),
            ("Yes, I like some brightness", 1),
            ("Love it, the tangier the better", 2),
        ],
    },
    {
        "text": "A coffee tastes \"sour\" to you — is that a dealbreaker?",
        "axis": "acidity",
        "options": [
            ("Sourness ruins it for me", -2),
            ("Mostly a turnoff", -1),
            ("Depends on context", 0),
            ("Not really bothered", 1),
            ("Not at all, that's brightness!", 2),
        ],
    },
    {
        "text": "Pick a flavor you'd want to taste in your coffee:",
        "axis": "flavor",
        "options": [
            ("Bold berries, citrus, or floral", 2),
            ("Mild fruit, apple, or light citrus", 1),
            ("Caramel or vanilla, neutral", 0),
            ("Caramel leaning spiced or nutty", -1),
            ("Chocolate, nuts, or baking spice", -2),
        ],
    },
    {
        "text": "When you add flavor to something (yogurt, oatmeal, a smoothie), what do you usually reach for?",
        "axis": "flavor",
        "options": [
            ("Berries or citrus", 2),
            ("Stone fruit like peach or apricot", 1),
            ("Vanilla or maple", 0),
            ("Caramel or honey", -1),
            ("Chocolate or nuts", -2),
        ],
    },
    {
        "text": "Ideal coffee texture or mouthfeel?",
        "axis": "body",
        "options": [
            ("Light, like tea", -2),
            ("Light-medium", -1),
            ("Medium", 0),
            ("Medium-heavy", 1),
            ("Thick, syrupy, coats your mouth", 2),
        ],
    },
    {
        "text": "Which texture do you prefer in food and drink generally?",
        "axis": "body",
        "options": [
            ("Light and delicate — nothing too heavy", -2),
            ("Mostly light, occasionally something richer", -1),
            ("No strong preference either way", 0),
            ("I like some richness and weight", 1),
            ("Rich and full — the heavier the better", 2),
        ],
    },
    {
        "text": "How do you feel about trying weird or experimental things in food or drink?",
        "axis": "adventurousness",
        "options": [
            ("Like to know exactly what I'm getting", -2),
            ("Rarely venture out", -1),
            ("Open occasionally", 0),
            ("Pretty open generally", 1),
            ("Love it, bring on the unusual", 2),
        ],
    },
    {
        "text": "Have you ever intentionally ordered a coffee that sounded weird or unfamiliar?",
        "axis": "adventurousness",
        "options": [
            ("No, and I don't think I would", -2),
            ("No, I tend to stick to what I know", -1),
            ("Maybe once or twice", 0),
            ("Yes, a few times", 1),
            ("Yes, regularly — that's half the fun", 2),
        ],
    },
]


# ---------------------------------------------------------------------------
# ARCHETYPES
# Each archetype has:
#   - profile:      list of 5 axis scores [roast, acidity, flavor, body, adventurousness]
#   - description:  shown to the user as their result
#   - barista_line: what to say to a barista to get a coffee in this style
#   - brewing:      how to brew this style at home
#       - methods:  recommended brew methods
#       - temp:     water temperature
#       - grind:    grind size direction
#       - tip:      one key brewing tip
#   - guidance:     structured buying recommendations
#       - countries, regions, process, varieties, roast_level, flavor_notes, roasters
# ---------------------------------------------------------------------------

ARCHETYPES = {
    "Bright & Floral Explorer": {
        "profile": [-2, +2, +2, -2, +1],
        "description": (
            "You gravitate toward coffees that are light, clean, and complex — think jasmine "
            "tea meets fresh citrus. You want brightness, not bitterness, and you're open to "
            "coffees that surprise you."
        ),
        "barista_line": (
            "I'm looking for a washed Ethiopian or Kenyan, light roast — "
            "anything floral or citrusy."
        ),
        "brewing": {
            "methods":  ["V60", "Chemex", "AeroPress"],
            "temp":     "93–96°C (200–205°F)",
            "grind":    "Medium-fine",
            "tip":      (
                "Use a slow, controlled pour and a longer bloom (45–50 seconds) to "
                "preserve delicate floral and citrus notes. These coffees open up as "
                "they cool — don't rush through the cup."
            ),
        },
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
        "barista_line": (
            "Do you have any naturals or anaerobics? I love tropical fruit "
            "and funky fermented complexity."
        ),
        "brewing": {
            "methods":  ["V60", "AeroPress"],
            "temp":     "90–93°C (194–200°F)",
            "grind":    "Medium-fine",
            "tip":      (
                "Try brewing slightly cooler than usual — lower temp tames the fermented "
                "intensity and keeps tropical fruit notes vibrant rather than overwhelming. "
                "A shorter brew time also helps."
            ),
        },
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
        "barista_line": (
            "I'd love a washed Colombian or Costa Rican, light to medium roast — "
            "something balanced and clean."
        ),
        "brewing": {
            "methods":  ["V60", "Chemex", "Drip"],
            "temp":     "93–95°C (200–203°F)",
            "grind":    "Medium",
            "tip":      (
                "These coffees are forgiving and consistent — great for dialing in "
                "your technique. A standard 1:15 or 1:16 ratio works well. "
                "Any pour-over method will serve you well here."
            ),
        },
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
        "barista_line": (
            "I'm open to anything — maybe a medium roast single origin? "
            "Something approachable and not too polarizing."
        ),
        "brewing": {
            "methods":  ["Drip", "French Press", "V60"],
            "temp":     "93°C (200°F)",
            "grind":    "Medium",
            "tip":      (
                "Start with whatever equipment you already have. A medium grind, "
                "standard 1:15 ratio, and 93°C water will get you a great result "
                "without needing to dial anything in carefully."
            ),
        },
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
        "barista_line": (
            "Any honey-process coffees? I prefer something sweet and smooth, "
            "medium roast, not too acidic."
        ),
        "brewing": {
            "methods":  ["French Press", "AeroPress", "Drip"],
            "temp":     "91–93°C (196–200°F)",
            "grind":    "Medium-coarse (French Press) or medium (AeroPress/drip)",
            "tip":      (
                "Full immersion methods like French Press complement the sweetness "
                "and body of honey-process coffees. Let it steep 4 minutes before "
                "pressing slowly. Avoid over-filtering — you want some texture."
            ),
        },
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
        "barista_line": (
            "I like something warm and comforting — medium-dark roast, "
            "chocolatey, low acidity. Nothing too bright or unusual."
        ),
        "brewing": {
            "methods":  ["French Press", "Drip", "Moka Pot"],
            "temp":     "91–93°C (196–200°F)",
            "grind":    "Medium-coarse",
            "tip":      (
                "French Press is ideal — it brings out the full body and chocolate "
                "notes these coffees are known for. Don't press too hard or too fast. "
                "A moka pot also works beautifully for a bolder, espresso-adjacent result."
            ),
        },
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
        "barista_line": (
            "I want something bold and dark — full body, low acidity, dark roast. "
            "Espresso roast is great too, especially if it works with milk."
        ),
        "brewing": {
            "methods":  ["French Press", "Espresso", "Moka Pot"],
            "temp":     "91–93°C (196–200°F)",
            "grind":    "Coarse (French Press) / Fine (espresso) / Medium-fine (moka pot)",
            "tip":      (
                "Dark roasts extract quickly — use a slightly coarser grind and "
                "shorter brew time than you'd expect to avoid bitterness. "
                "If you drink it with milk, espresso or moka pot gives you the "
                "intensity to cut through."
            ),
        },
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
# GLOSSARY
# Plain English explanations for coffee terms used in the results page.
# Shown as small helper text next to each guidance field in the app.
# ---------------------------------------------------------------------------

GLOSSARY = {
    "countries":    "The country where the coffee was grown. Origin has a huge impact on flavor — Ethiopia produces very different coffee than Brazil.",
    "regions":      "Specific growing regions within a country. Like wine appellations — Yirgacheffe in Ethiopia is as specific and meaningful as Burgundy in France.",
    "process":      "How the coffee cherry is processed after picking. Washed = clean and bright. Natural = fruit dried on, produces sweeter and fruitier flavors. Honey = in between.",
    "varieties":    "The cultivar of coffee plant — like grape varieties in wine. Gesha is prized for floral complexity; Bourbon is a classic with balanced sweetness.",
    "roast_level":  "How long the beans were roasted. Light roasts preserve more of the bean's original character — fruit, floral notes. Dark roasts develop bolder, more uniform flavors.",
    "flavor_notes": "Descriptors on the bag tell you what flavors the roaster tastes. They're not added ingredients — they're naturally occurring compounds in the bean.",
    "roasters":     "Roasters that specialize in this style. Buying from a roaster known for a style is a shortcut to consistently finding coffees you'll enjoy.",
}




# ---------------------------------------------------------------------------
# VARIETY PROFILES
# Plain English descriptions of each coffee variety/cultivar mentioned
# across the archetypes. Shown on the results page when a user receives
# that variety as a recommendation.
# ---------------------------------------------------------------------------

VARIETY_PROFILES = {
    "Ethiopian Heirloom": (
        "Ethiopia has thousands of wild and semi-wild coffee varieties that haven't "
        "been formally classified — collectively called 'heirloom.' This genetic "
        "diversity is why Ethiopian coffees are so complex and varied. When a bag "
        "says 'Ethiopian Heirloom,' it means the exact variety is unknown or mixed, "
        "but the result is often strikingly floral, fruity, and unlike anything grown "
        "from a single named cultivar elsewhere."
    ),
    "SL28": (
        "Developed in Kenya in the 1930s by Scott Laboratories (hence 'SL'). SL28 "
        "is famous for producing some of the most intensely flavored coffees in the "
        "world — blackcurrant, tomato, red fruit, and citrus with high acidity. "
        "It's drought-tolerant but vulnerable to disease, which is why it's "
        "increasingly rare. A bag listing SL28 is usually a signal of quality."
    ),
    "SL34": (
        "A sibling of SL28, also developed by Scott Laboratories in Kenya. SL34 "
        "thrives at higher rainfall and produces coffees with similar intensity — "
        "blackcurrant, dark fruit, high acidity — but with slightly more body. "
        "Often blended with SL28, and both together define the classic Kenyan flavor profile."
    ),
    "Gesha": (
        "Originally from the Gesha village in Ethiopia, but made world-famous by "
        "Hacienda La Esmeralda in Panama in the early 2000s. Gesha is prized above "
        "almost all other varieties for its extraordinary floral complexity — jasmine, "
        "bergamot, peach, tropical fruit. It commands some of the highest prices in "
        "specialty coffee. If you see Gesha on a bag, expect something exceptional "
        "and expect to pay for it."
    ),
    "Pink Bourbon": (
        "A naturally occurring mutation of the Bourbon variety, named for its "
        "distinctive pink-colored coffee cherries. Originally from Colombia's Huila "
        "region. Pink Bourbon produces coffees with exceptional sweetness and "
        "complexity — tropical fruit, floral notes, and a silky texture. It's become "
        "one of the most sought-after varieties in the specialty world and scores "
        "extremely well in competitions."
    ),
    "Sidra": (
        "A relatively new and rare variety from Ecuador, believed to be a cross "
        "between Ethiopian Heirloom and Bourbon. Sidra is prized for its extraordinary "
        "cup quality — tropical fruit, floral notes, and wine-like complexity that "
        "rivals Gesha. It's still uncommon and commands high prices, but is quickly "
        "gaining a reputation as one of the most exciting varieties in specialty coffee."
    ),
    "Typica Mejorado": (
        "A selection of the classic Typica variety developed in Ecuador for improved "
        "cup quality. It produces coffees with a distinctive tropical fruit character — "
        "mango, passion fruit, papaya — and is increasingly used by specialty roasters "
        "for competition lots. 'Mejorado' means 'improved' in Spanish."
    ),
    "Caturra": (
        "A natural mutation of Bourbon discovered in Brazil in the early 1900s. "
        "Caturra is a workhorse variety — compact, high-yielding, and easy to farm — "
        "that produces clean, bright, balanced coffees. It's widely grown in Colombia "
        "and Central America. Not the flashiest variety, but reliably good and "
        "representative of its origin's character."
    ),
    "Castillo": (
        "Developed by Colombia's Cenicafé research center as a disease-resistant "
        "alternative to Caturra. Castillo is controversial among coffee purists — "
        "it's highly productive and resistant to coffee leaf rust, but some argue "
        "it produces slightly less complex cups than older varieties. When well-farmed "
        "and carefully processed, it produces excellent results."
    ),
    "Catuai": (
        "A hybrid of Mundo Novo and Caturra developed in Brazil. Catuai is widely "
        "planted across Latin America for its high yield and wind resistance. It "
        "produces clean, balanced coffees — reliable rather than exciting. Red and "
        "Yellow Catuai (named for cherry color) are both common and broadly similar "
        "in cup profile."
    ),
    "Bourbon": (
        "One of the oldest and most important arabica varieties, descended from plants "
        "brought to Bourbon Island (now Réunion) from Yemen. Bourbon produces coffees "
        "with classic sweetness — caramel, stone fruit, red apple — and good balance. "
        "It's the ancestral variety for many modern cultivars (Pink Bourbon, Caturra, "
        "Catuai). Red Bourbon is the most common; Yellow Bourbon is sweeter and "
        "often found in Brazil."
    ),
    "Typica": (
        "One of the oldest arabica varieties, and the genetic basis for most of the "
        "world's arabica coffee. Typica produces clean, elegant cups with mild acidity "
        "and a classic coffee sweetness. It's lower-yielding than modern hybrids, "
        "which is why it's been largely replaced by more productive varieties — but "
        "well-grown Typica from historic origins (Jamaica, Hawaii, Peru) can be "
        "exceptional."
    ),
    "Yellow Bourbon": (
        "A mutation of Bourbon with yellow-colored cherries instead of red, most "
        "commonly found in Brazil. Yellow Bourbon tends to produce sweeter cups than "
        "red Bourbon — caramel, hazelnut, honey — and is popular for natural and "
        "pulped natural processing where the yellow fruit adds extra sweetness to "
        "the drying process."
    ),
    "Red Catuai": (
        "A Catuai variant with red-colored cherries, widely grown in Brazil and "
        "Central America. Red Catuai produces balanced, chocolatey, low-acidity "
        "coffees — reliable and food-friendly. It's a common base variety for "
        "espresso blends due to its consistency and body."
    ),
    "Mundo Novo": (
        "A natural cross between Typica and Bourbon, discovered in Brazil in the "
        "1940s. Mundo Novo ('New World') is vigorous, disease-resistant, and "
        "high-yielding. It produces full-bodied, chocolatey coffees with low acidity "
        "— well-suited to medium and dark roasts and popular in Brazilian espresso blends."
    ),
    "Tim Tim": (
        "A variety unique to Sumatra, Indonesia, also known as Timtim or Ateng. "
        "It contributes to the distinctive earthy, herbal, full-bodied character "
        "associated with Sumatran coffees. Tim Tim is particularly associated with "
        "the wet-hulling process (Giling Basah) used in Sumatra, which amplifies "
        "its rustic, low-acid profile."
    ),
    "Jember": (
        "An Indonesian variety (also called S795) developed at the Jember research "
        "station, used widely across Sumatra and other Indonesian islands. Jember "
        "produces full-bodied, low-acid coffees with earthy and spicy notes. "
        "Like Tim Tim, it's well-suited to the wet-hulling process and is commonly "
        "found in Sumatran and Sulawesi lots."
    ),
    "espresso blends": (
        "Not a variety — a blend of multiple origins and sometimes varieties, "
        "formulated specifically for espresso. Blends are designed for consistency "
        "and balance under pressure: typically low acidity, full body, chocolate or "
        "caramel sweetness, and crema stability. Most large roasters have a house "
        "espresso blend; specialty roasters often label theirs with the component origins."
    ),
}


# ---------------------------------------------------------------------------
# REGION PROFILES
# Descriptions of specific growing regions mentioned across the archetypes.
# Shown on the results page when a user receives that region as a recommendation.
# ---------------------------------------------------------------------------

REGION_PROFILES = {
    "Yirgacheffe": (
        "A small but legendary zone within Ethiopia's Gedeo zone. Yirgacheffe "
        "produces some of the world's most prized washed coffees — intensely floral, "
        "with jasmine, bergamot, and citrus notes that are unlike anything from "
        "other origins. High altitude and heirloom varieties are the key factors."
    ),
    "Gedeo": (
        "A broader zone in southern Ethiopia that includes Yirgacheffe. Gedeo "
        "coffees share the same floral, citrus-driven character but can vary more "
        "widely in style. Both washed and natural lots are produced here, and it's "
        "one of the most biodiverse coffee-growing areas in the world."
    ),
    "Nyeri": (
        "One of Kenya's most celebrated coffee regions, located on the slopes of "
        "Mount Kenya. Nyeri coffees are known for intense blackcurrant, tomato, "
        "and red fruit notes with high acidity and full body. The combination of "
        "red volcanic soil, altitude, and SL28/SL34 varieties makes Nyeri "
        "consistently exceptional."
    ),
    "Kirinyaga": (
        "A Kenyan region neighboring Nyeri, also on Mount Kenya's slopes. Kirinyaga "
        "produces similarly bright, complex coffees with blackcurrant and citrus "
        "character. Slightly less well-known than Nyeri but equally high quality — "
        "a region worth seeking out."
    ),
    "Huila": (
        "Colombia's most celebrated coffee department, located in the Andes in "
        "southwestern Colombia. Huila's high altitude, diverse microclimates, and "
        "small farmer culture produce some of the country's most complex and "
        "sought-after lots — caramel sweetness, bright citrus, and clean finish. "
        "Many award-winning Colombian coffees come from here."
    ),
    "Nariño": (
        "A Colombian department bordering Ecuador, with some of the highest-altitude "
        "coffee farms in the country. The extreme altitude slows cherry development, "
        "producing dense beans with high acidity, bright citrus, and exceptional "
        "sweetness. Nariño coffees are often described as some of the most "
        "elegant and refined in Colombia."
    ),
    "Tarrazu": (
        "Costa Rica's most famous coffee region, located in the mountains south of "
        "San José. Tarrazu coffees are known for their clean brightness, citrus "
        "acidity, and honey sweetness. The high altitude and volcanic soil produce "
        "dense, well-structured beans that roast beautifully at light to medium levels."
    ),
    "Antigua": (
        "A historic coffee-growing valley in Guatemala, surrounded by three volcanoes. "
        "Antigua coffees are known for their full body, chocolate and spice notes, "
        "and mild acidity — a classic Central American profile. The volcanic ash soil "
        "contributes to the region's distinctive character."
    ),
    "Cajamarca": (
        "Peru's most recognized specialty coffee region, located in the northern "
        "Andes. Cajamarca produces clean, sweet coffees with mild acidity and "
        "caramel or stone fruit notes. The region is home to many small-scale "
        "farmers and cooperatives producing increasingly high-quality lots."
    ),
    "Sul de Minas": (
        "One of Brazil's most important specialty coffee regions, located in "
        "Minas Gerais state. Sul de Minas coffees are known for their sweetness, "
        "full body, and chocolate or nutty notes — the classic Brazilian profile. "
        "The region produces large volumes and is the backbone of many espresso "
        "blends worldwide."
    ),
    "Cerrado": (
        "A Brazilian region in Minas Gerais state with a distinct dry season that "
        "allows for very consistent, uniform harvests. Cerrado coffees are "
        "full-bodied, sweet, and low-acid — chocolatey and smooth, well-suited "
        "to medium-dark roasting and espresso preparation."
    ),
    "Marcala": (
        "A denomination of origin in Honduras's La Paz department — the first "
        "in Central America to receive geographic indication status. Marcala "
        "coffees are grown at high altitude and produce bright, balanced cups "
        "with stone fruit and caramel notes. A rising region in specialty coffee."
    ),
    "Pichincha": (
        "A province in Ecuador surrounding Quito, producing some of Ecuador's "
        "most exciting specialty lots. The high altitude and proximity to the "
        "equator create ideal conditions for slow cherry development. Pichincha "
        "is associated with experimental processing and rare varieties like "
        "Sidra and Typica Mejorado."
    ),
    "Sumatra (Mandheling, Gayo)": (
        "Two of Sumatra's most important coffee-producing areas. Mandheling "
        "(in North Sumatra) is known for earthy, full-bodied, low-acid coffees "
        "with herbal and cedar notes — the classic Sumatran profile. Gayo "
        "(in Aceh province) produces similar coffees but often slightly cleaner "
        "and more complex. Both use the wet-hulling process that defines "
        "Indonesian coffee."
    ),
    "Sumatra (Mandheling)": (
        "Located in North Sumatra, Mandheling is the origin most associated with "
        "the classic Sumatran flavor profile — earthy, herbal, full-bodied, and "
        "low-acid, with cedar and dark chocolate notes. The wet-hulling process "
        "used here is unique to Indonesia and produces the region's distinctive "
        "rustic, heavy character."
    ),
    "Sulawesi": (
        "An Indonesian island producing coffees with a similar profile to Sumatra — "
        "full body, low acidity, earthy and spicy notes — but often considered "
        "slightly cleaner and more refined. The Toraja and Kalosi regions within "
        "Sulawesi are the most recognized. Good for dark roast lovers who want "
        "body and sweetness without harsh bitterness."
    ),
}

# ---------------------------------------------------------------------------
# STEP 1: compute axis scores from 10 answers
# ---------------------------------------------------------------------------

def compute_axis_scores(answers):
    """
    Takes a list of 10 answers (each -2, -1, 0, +1, or +2) and returns
    a list of 5 axis scores, one per axis.

    Question-to-axis mapping (0-indexed):
        Q1, Q2  → roast           (answers[0], answers[1])
        Q3, Q4  → acidity         (answers[2], answers[3])
        Q5, Q6  → flavor          (answers[4], answers[5])
        Q7, Q8  → body            (answers[6], answers[7])
        Q9, Q10 → adventurousness (answers[8], answers[9])

    Each axis score is the average of its two questions.
    Result is a list: [roast, acidity, flavor, body, adventurousness]
    """

    if len(answers) != 10:
        raise ValueError(f"Expected 10 answers, got {len(answers)}")
    for i, answer in enumerate(answers):
        if answer not in [-2, -1, 0, 1, 2]:
            raise ValueError(f"Answer {i+1} must be -2, -1, 0, 1, or 2. Got: {answer}")

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
    """
    squared_differences = [
        (user_val - archetype_val) ** 2
        for user_val, archetype_val in zip(user_scores, archetype_profile)
    ]
    return math.sqrt(sum(squared_differences))


# ---------------------------------------------------------------------------
# STEP 3: confidence label based on distance
# ---------------------------------------------------------------------------

def get_confidence(distance):
    """
    Converts a raw Euclidean distance into a human-readable confidence label.

    Thresholds (tuned for this 5-axis, -2 to +2 scale):
        < 1.5   → Strong match
        1.5–2.5 → Good match
        > 2.5   → Mixed signals (genuinely between archetypes)
    """
    if distance < 1.5:
        return "Strong match"
    elif distance < 2.5:
        return "Good match"
    else:
        return "Mixed signals — you sit between a couple of archetypes"


# ---------------------------------------------------------------------------
# STEP 4: find the best matching archetype (and runner-up)
# ---------------------------------------------------------------------------

def find_match(answers):
    """
    Takes a list of 10 answers, computes axis scores, ranks all archetypes
    by Euclidean distance, and returns the winner and runner-up.

    Returns a dict with:
        - name:        winner archetype name
        - description: winner description
        - guidance:    winner buying guidance dict
        - distance:    winner distance (lower = better)
        - confidence:  human-readable confidence label
        - axis_scores: user's 5 axis scores (used by radar chart)
        - runner_up:   dict with name, description, guidance for 2nd closest
    """

    user_scores = compute_axis_scores(answers)

    # Rank all archetypes by distance, closest first
    ranked = sorted(
        [
            (euclidean_distance(user_scores, archetype["profile"]), name)
            for name, archetype in ARCHETYPES.items()
        ]
    )

    best_distance, best_name   = ranked[0]
    runup_distance, runup_name = ranked[1]

    winner = ARCHETYPES[best_name]
    runner = ARCHETYPES[runup_name]

    return {
        "name":         best_name,
        "description":  winner["description"],
        "barista_line": winner["barista_line"],
        "brewing":      winner["brewing"],
        "guidance":     winner["guidance"],
        "distance":     round(best_distance, 3),
        "confidence":   get_confidence(best_distance),
        "axis_scores": {
            "roast":           user_scores[0],
            "acidity":         user_scores[1],
            "flavor":          user_scores[2],
            "body":            user_scores[3],
            "adventurousness": user_scores[4],
        },
        "runner_up": {
            "name":        runup_name,
            "description": runner["description"],
            "guidance":    runner["guidance"],
            "distance":    round(runup_distance, 3),
        },
    }


# ---------------------------------------------------------------------------
# QUICK TEST
# ---------------------------------------------------------------------------

def print_result(label, result):
    print(f"\n{label}")
    print(f"  Match:      {result['name']} ({result['confidence']})")
    print(f"  Distance:   {result['distance']}")
    print(f"  Runner-up:  {result['runner_up']['name']} (distance: {result['runner_up']['distance']})")
    print(f"  Axis scores: {result['axis_scores']}")


if __name__ == "__main__":
    print_result("Test 1 — light/floral/adventurous:", find_match([-2, -2, +2, +2, +2, +2, -2, -2, +1, +2]))
    print_result("Test 2 — dark/bold/unadventurous:",  find_match([+2, +2, -2, -2, -2, -2, +2, +2, -2, -2]))
    print_result("Test 3 — all neutral:",              find_match([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))


# ---------------------------------------------------------------------------
# COUNTRY PROFILES
# Tasting descriptions per origin country — shown on the results page
# when a user gets that country as a recommendation.
# ---------------------------------------------------------------------------

COUNTRY_PROFILES = {
    "Ethiopia": (
        "The birthplace of coffee. Ethiopian coffees are prized for their complexity — "
        "especially from Yirgacheffe and Gedeo, where washed coffees produce striking "
        "floral and citrus notes (jasmine, bergamot, lemon). Naturals from the same "
        "regions lean toward blueberry and stone fruit. No other origin produces this "
        "level of aromatic complexity at light roast."
    ),
    "Kenya": (
        "Kenyan coffees are bold and bright — known for a distinctive 'blackcurrant' "
        "or tomato-like acidity that's unlike any other origin. SL28 and SL34 varieties "
        "produce intense, wine-like flavors with high acidity and full body. If you love "
        "brightness and complexity, Kenya consistently delivers."
    ),
    "Colombia": (
        "One of the most versatile and approachable specialty origins. Colombian coffees "
        "tend toward balanced sweetness — caramel, mild citrus, red apple — with a clean "
        "finish. Huila and Nariño produce some of the most complex Colombian lots, while "
        "the country as a whole is reliably consistent across roasters."
    ),
    "Costa Rica": (
        "Costa Rican coffees are clean, sweet, and predictable in the best way — a safe "
        "bet for anyone who wants quality without surprises. Tarrazu is the most famous "
        "region, known for bright acidity and clean citrus or honey notes. Honey-process "
        "Costa Ricans add sweetness and body without the funk of a natural."
    ),
    "Guatemala": (
        "Guatemalan coffees tend toward chocolate, brown sugar, and mild spice — "
        "approachable and comforting. Antigua and Huehuetenango are the standout regions. "
        "They roast well at medium to medium-dark, making them popular among people who "
        "want quality coffee that doesn't taste sour or unusual."
    ),
    "Peru": (
        "Often underrated, Peruvian coffees (especially from Cajamarca) can be elegant "
        "and nuanced — mild acidity, caramel sweetness, and a clean finish. They're "
        "rarely the flashiest option but are reliable and food-friendly."
    ),
    "Brazil": (
        "Brazil is the world's largest coffee producer, and its coffees tend toward "
        "low acidity, full body, and flavors of nuts, chocolate, and brown sugar. "
        "Sul de Minas and Cerrado are the quality regions. Brazilian naturals are a "
        "classic base for espresso blends — sweet, heavy, and smooth."
    ),
    "Honduras": (
        "Honduran specialty coffees punch above their reputation — Marcala and Copán "
        "produce bright, balanced coffees with stone fruit and caramel notes. A good "
        "value origin that's improving rapidly in quality."
    ),
    "Indonesia": (
        "Indonesian coffees (especially Sumatra) are unlike anything else — earthy, "
        "herbal, and full-bodied, with a distinctive 'wet earth' or cedar quality from "
        "the wet-hulling process. Not for everyone, but loved by people who want bold, "
        "low-acid, heavy coffee that feels nothing like bright specialty fare."
    ),
    "Ecuador": (
        "Ecuador is emerging as an exciting origin, particularly for experimental "
        "processing. The Pichincha region produces coffees with tropical fruit and "
        "complex fermented notes. Typica Mejorado and Sidra varieties grown here are "
        "producing some of the most interesting lots in South America."
    ),
    "Panama": (
        "Home to some of the world's most expensive and celebrated coffees — the "
        "Gesha variety from Boquete is legendary for its jasmine, bergamot, and "
        "stone fruit complexity. Panamanian Geshas set the benchmark that other "
        "floral coffees are measured against."
    ),
    "Bolivia": (
        "A small but high-quality origin producing clean, sweet coffees with mild "
        "acidity and caramel or stone fruit notes. Similar in profile to Peru — "
        "underrated and worth seeking out when available."
    ),
}

# ---------------------------------------------------------------------------
# PROCESS PROFILES
# Plain English explanation of each process — shown when a user's result
# includes that processing method.
# ---------------------------------------------------------------------------

PROCESS_PROFILES = {
    "Washed": (
        "The coffee fruit (cherry) is removed before the bean is dried, so the bean "
        "dries clean. This produces transparent, bright flavors where the origin's "
        "terroir — soil, altitude, variety — comes through clearly. Washed coffees "
        "tend to taste cleaner, brighter, and more 'coffeelike' in the classic sense. "
        "If you like clarity and acidity, this is your process."
    ),
    "Natural": (
        "The whole coffee cherry is dried with the fruit still on. As it dries, the "
        "fruit's sugars ferment into the bean — producing sweeter, fruitier, sometimes "
        "wine-like flavors. Natural coffees often taste like blueberry, tropical fruit, "
        "or jam. More body, less acidity than washed. Higher risk of fermentation "
        "defects, but the best naturals are stunning."
    ),
    "Honey": (
        "A middle ground — the skin is removed but some of the sticky fruit mucilage "
        "is left on during drying. Produces sweetness and body without the full "
        "fermented intensity of a natural. 'Yellow honey' has less mucilage (cleaner), "
        "'black honey' has more (sweeter and heavier). Approachable and crowd-pleasing."
    ),
    "Pulped natural": (
        "Similar to honey process — skin is removed, some mucilage remains during "
        "drying. Common in Brazil, where it produces chocolatey, nutty, full-bodied "
        "coffees with low acidity. A classic process for people who want sweetness "
        "and body without brightness."
    ),
    "Anaerobic": (
        "Coffee ferments in sealed, oxygen-free tanks before drying. The lack of "
        "oxygen produces unusual flavor compounds — often intense tropical fruit, "
        "spice, or wine-like notes. Polarizing: some people love the complexity, "
        "others find it overwhelming or artificial-tasting. If you want funky and "
        "distinctive, this is your process."
    ),
    "Co-fermented": (
        "Coffee ferments alongside added ingredients — fruit juices, spices, or "
        "other fermentable materials — to impart additional flavor. Very experimental "
        "and not universally loved, but produces coffees unlike anything traditional "
        "processing can achieve. Common in competition-circuit lots."
    ),
    "Carbonic maceration": (
        "Borrowed from winemaking — whole cherries ferment under CO₂ pressure before "
        "processing. Produces very clean but intensely fruity, almost candy-like "
        "flavors. A precision process that's gaining popularity among roasters chasing "
        "distinctive, high-scoring lots."
    ),
    "Wet-hulled": (
        "A process unique to Indonesia (called 'Giling Basah' locally). The parchment "
        "layer is removed while the bean is still wet, then it dries at lower moisture "
        "content. This produces the earthy, herbal, full-bodied character Sumatran "
        "coffees are known for. Not to everyone's taste, but unmistakable."
    ),
    "Yellow honey": (
        "The lightest honey process — only a small amount of mucilage is left on "
        "during drying. Produces a cleaner cup than other honeys, closer to washed "
        "but with extra sweetness and a slightly heavier body."
    ),
}
