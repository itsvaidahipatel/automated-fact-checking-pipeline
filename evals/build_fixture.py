"""Generate labeled_claims.json (180 samples). Run: python evals/build_fixture.py"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).parent / "fixtures" / "labeled_claims.json"

# (claim, label, claim_type, category, tags?)
SEED: list[tuple] = [
    (
        "According to a 1998 Lancet paper, the MMR vaccine was definitively proven to cause autism in peer-reviewed research.",
        "false",
        "scientific",
        "health",
        ["adversarial", "well_sourced_lie"],
    ),
    (
        "The 2020 U.S. presidential election was won by the candidate who received the most electoral college votes.",
        "true",
        "political",
        "civics",
        [],
    ),
    (
        "The unemployment rate can rise while the number of employed people also rises if the labor force grows faster than employment.",
        "true",
        "statistical",
        "economics",
        [],
    ),
]

TRUE_SCIENTIFIC = [
    "Water boils at 100 degrees Celsius at standard atmospheric pressure.",
    "The speed of light in vacuum is approximately 299792458 meters per second.",
    "DNA carries genetic information in living organisms.",
    "Vaccines stimulate the immune system to develop protection against specific diseases.",
    "Antibiotics are effective against bacterial infections, not viral infections.",
    "The human heart has four chambers.",
    "Photosynthesis converts light energy into chemical energy in plants.",
    "Earth orbits the Sun.",
    "The Moon reflects light from the Sun rather than producing its own visible light.",
    "Table salt is composed of sodium and chlorine ions.",
    "Oxygen is necessary for human cellular respiration.",
    "Sound cannot travel through a perfect vacuum.",
    "Ice is less dense than liquid water at 0°C.",
    "Metals conduct electricity more readily than typical insulators.",
    "Bacteria are single-celled organisms.",
    "The periodic table organizes elements by atomic number.",
    "Gravity causes unsupported objects near Earth to accelerate downward.",
    "Chlorophyll contributes to the green color of many plants.",
    "The pH scale measures acidity and alkalinity.",
    "Friction opposes relative motion between surfaces in contact.",
]

FALSE_SCIENTIFIC = [
    "Humans have three lungs.",
    "The Sun orbits Earth once per day.",
    "Water is not a chemical compound.",
    "Diamonds are made primarily of silicon.",
    "Blood is blue before it is oxygenated in arteries.",
    "Lightning never strikes the same place twice.",
    "Bats are a type of bird.",
    "Sharks are mammals.",
    "The Great Wall of China is visible from the Moon with the naked eye.",
    "Gold has the chemical symbol Fe.",
    "Vaccines contain microchips for government tracking.",
    "Evolution is not supported by fossil evidence.",
    "The human body is 90% brain tissue by mass.",
    "Glass is a slow-moving liquid at room temperature.",
    "Antibiotics cure the common cold caused by rhinoviruses.",
    "Nuclear power plants generate electricity by burning coal inside reactors.",
    "The human appendix has no possible function in any person.",
    "Seasons are caused solely by changes in Earth's distance from the Sun.",
    "All plastics are biodegradable within one year in landfills.",
    "Meteorites never contain organic molecules.",
]

TRUE_GEO = [
    "Paris is the capital of France.",
    "Tokyo is the capital of Japan.",
    "Ottawa is the capital of Canada.",
    "Canberra is the capital of Australia.",
    "Brasília is the capital of Brazil.",
    "The Nile is one of the longest rivers in the world.",
    "Mount Everest is the highest mountain above sea level on Earth.",
    "The Pacific Ocean is the largest ocean on Earth.",
    "Russia spans Europe and Asia.",
    "The Sahara is a hot desert in Africa.",
]

FALSE_GEO = [
    "Sydney is the capital of Australia.",
    "New York City is the capital of the United States.",
    "The Amazon River is located in Europe.",
    "Mount Everest is located in South Africa.",
    "The capital of Italy is Barcelona.",
    "The Arctic Ocean surrounds Antarctica.",
    "London is the capital of Germany.",
    "The Danube flows primarily through South America.",
    "The capital of Spain is Lisbon.",
    "The Mississippi River flows through Asia.",
]

TRUE_HISTORY = [
    "World War II ended in 1945.",
    "The United States declared independence in 1776.",
    "The Titanic sank in 1912.",
    "Neil Armstrong walked on the Moon in 1969.",
    "The printing press was developed in Europe before 1500.",
    "The Roman Empire existed in antiquity.",
    "The Berlin Wall fell in 1989.",
    "The Magna Carta was signed in 1215.",
    "The Wright brothers made powered flight advances in the early 1900s.",
    "The Renaissance was a European cultural movement.",
]

FALSE_HISTORY = [
    "World War I ended in 1925.",
    "The American Civil War ended in 1901.",
    "Cleopatra lived closer in time to the Moon landing than to the building of the Great Pyramid.",
    "The Titanic sank in 2001.",
    "Napoleon Bonaparte was emperor of Germany.",
    "The Great Depression began in 1999.",
    "The Declaration of Independence was signed in 1876.",
    "The Cold War ended in 1940.",
    "The first iPhone was released in 1984.",
    "Ancient Rome was founded in 1776.",
]

TRUE_TECH = [
    "Python is a programming language.",
    "HTTP is used for communication on the web.",
    "A byte consists of 8 bits.",
    "Linux is an operating system kernel.",
    "GPUs accelerate many machine learning workloads.",
    "Wi-Fi is a wireless networking technology.",
    "Open-source software may be freely used under certain licenses.",
    "Databases store structured data for applications.",
    "Encryption can protect data confidentiality.",
    "Version control systems track changes to source code.",
]

FALSE_TECH = [
    "JavaScript can only run on servers, never in browsers.",
    "Bluetooth uses only visible red light for communication.",
    "RAM is a form of permanent storage that retains data without power.",
    "IPv4 addresses are unlimited in number.",
    "All programming languages compile directly to machine code only.",
    "HTTP stands for HyperText Transmission Protocol only for email.",
    "Quantum computers have replaced all classical servers in production.",
    "Python cannot be used for web development.",
    "Git is a relational database management system.",
    "CSS is a general-purpose systems programming language.",
]

TRUE_STAT = [
    "The mean of 2, 4, and 6 is 4.",
    "A probability must lie between 0 and 1 inclusive.",
    "Correlation does not imply causation.",
    "The median is less sensitive to extreme outliers than the mean for skewed data.",
    "A sample size of 5 is generally too small to estimate national unemployment precisely.",
    "Percentages can exceed 100% only in specific relative-change contexts, not as a share of a whole.",
    "Standard deviation measures spread around the mean.",
    "Doubling a rate from 1% to 2% is a 100% relative increase but a 1 percentage-point absolute increase.",
    "Random assignment in experiments helps reduce confounding.",
    "A p-value is not the probability that the null hypothesis is true.",
]

FALSE_STAT = [
    "The mean of 1, 2, and 9 is 3.",
    "A correlation of -0.99 proves that one variable causes the other.",
    "Increasing sample size always decreases measurement error to zero.",
    "If event A and B are independent, P(A and B) equals P(A) + P(B).",
    "The median of 1, 1, 100 is 100.",
    "A study with p=0.06 proves the null hypothesis is true.",
    "All statistically significant results are practically important.",
    "Base rates can be ignored when evaluating diagnostic test results.",
    "A 200% decrease in price is mathematically possible for any good.",
    "Regression to the mean never occurs in repeated measurements.",
]

TRUE_POLITICAL = [
    "The United Nations was founded after World War II.",
    "Democracies hold elections to select representatives or leaders in many systems.",
    "Freedom of the press is protected in many constitutional democracies.",
    "Treaties between countries can create binding international obligations when ratified.",
    "Census data are used to apportion representation in many countries.",
    "Central banks often adjust interest rates to influence inflation.",
    "Civil rights legislation in the U.S. addressed legal segregation in the 1960s.",
    "NATO is a military alliance that includes the United States and Canada.",
    "Lobbying is a legal form of political advocacy in many democracies.",
    "Judicial review allows courts to assess constitutionality of laws in some systems.",
]

FALSE_POLITICAL = [
    "The U.S. Constitution was written in 2020.",
    "Monarchies never exist in the modern world.",
    "International law has no effect on any sovereign state ever.",
    "All countries use the same electoral system for national elections.",
    "The European Union is a single unified country with one president.",
    "Impeachment automatically removes a U.S. president without any Senate process.",
    "Only dictatorships have written constitutions.",
    "Voting is mandatory in every country worldwide.",
    "The United Nations can deploy binding military forces in any country without consent.",
    "Political parties are banned in all democracies.",
]

# Well-sourced lie style (false but citation-baiting)
FALSE_ADVERSARIAL = [
    (
        "A Harvard Medical School press release confirmed that drinking eight glasses of water per hour cures type 2 diabetes within one week.",
        "false",
        "scientific",
        "health",
        ["adversarial", "well_sourced_lie"],
    ),
    (
        "Official NASA telemetry published in 2019 showed the International Space Station orbits at 50,000 km above Earth.",
        "false",
        "scientific",
        "space",
        ["adversarial", "well_sourced_lie"],
    ),
    (
        "The Congressional Budget Office reported in 2015 that U.S. federal debt was zero due to a one-time accounting change.",
        "false",
        "statistical",
        "economics",
        ["adversarial", "well_sourced_lie"],
    ),
]


def _row(claim: str, label: str, claim_type: str, category: str, tags: list | None = None) -> dict:
    item = {
        "claim": claim,
        "label": label,
        "claim_type": claim_type,
        "category": category,
    }
    if tags:
        item["tags"] = tags
    return item


def main() -> None:
    rows: list[dict] = []

    for item in SEED:
        rows.append(_row(*item))

    for c in TRUE_SCIENTIFIC:
        rows.append(_row(c, "true", "scientific", "science"))
    for c in FALSE_SCIENTIFIC:
        rows.append(_row(c, "false", "scientific", "science"))
    for c in TRUE_GEO:
        rows.append(_row(c, "true", "scientific", "geography"))
    for c in FALSE_GEO:
        rows.append(_row(c, "false", "scientific", "geography"))
    for c in TRUE_HISTORY:
        rows.append(_row(c, "true", "political", "history"))
    for c in FALSE_HISTORY:
        rows.append(_row(c, "false", "political", "history"))
    for c in TRUE_TECH:
        rows.append(_row(c, "true", "scientific", "technology"))
    for c in FALSE_TECH:
        rows.append(_row(c, "false", "scientific", "technology"))
    for c in TRUE_STAT:
        rows.append(_row(c, "true", "statistical", "statistics"))
    for c in FALSE_STAT:
        rows.append(_row(c, "false", "statistical", "statistics"))
    for c in TRUE_POLITICAL:
        rows.append(_row(c, "true", "political", "civics"))
    for c in FALSE_POLITICAL:
        rows.append(_row(c, "false", "political", "civics"))

    for adv in FALSE_ADVERSARIAL:
        rows.append(_row(*adv))

    # Social URL sample
    rows.append(
        _row(
            "YouTube is a video-sharing platform owned by Google.",
            "true",
            "scientific",
            "social_url",
        )
        | {"url": "https://www.youtube.com/"}
    )

    EXTRA_TRUE = [
        ("The influenza vaccine is updated in some years to match circulating strains.", "scientific", "health"),
        ("Handwashing with soap reduces transmission of many pathogens.", "scientific", "health"),
        ("Smoking increases the risk of lung cancer.", "scientific", "health"),
        ("Plate tectonics explains continental drift.", "scientific", "geoscience"),
        ("Atoms consist of protons, neutrons, and electrons.", "scientific", "chemistry"),
        ("The greenhouse effect involves trapping of infrared radiation by gases.", "scientific", "climate"),
        ("HIV attacks the immune system.", "scientific", "health"),
        ("CRISPR can be used to edit DNA sequences in laboratory settings.", "scientific", "biology"),
        ("The speed of sound in air increases with temperature at constant humidity.", "scientific", "physics"),
        ("Mitochondria are involved in energy production in eukaryotic cells.", "scientific", "biology"),
        ("The Bill of Rights comprises the first ten amendments to the U.S. Constitution.", "political", "law"),
        ("The Supreme Court can strike down laws inconsistent with the Constitution.", "political", "law"),
        ("Gerrymandering refers to drawing electoral districts for political advantage.", "political", "civics"),
        ("A filibuster in the U.S. Senate can delay votes on legislation.", "political", "civics"),
        ("The median voter theorem is used in political science models.", "political", "theory"),
        ("Turnout rates vary across elections and jurisdictions.", "political", "elections"),
        ("Inflation measures the rate of increase in a price index over time.", "statistical", "economics"),
        ("GDP measures the market value of final goods and services produced.", "statistical", "economics"),
        ("Confidence intervals quantify uncertainty around an estimate.", "statistical", "methods"),
        ("Selection bias can occur when samples are not representative.", "statistical", "methods"),
    ]
    EXTRA_FALSE = [
        ("The flu vaccine guarantees you will never get any respiratory illness.", "scientific", "health"),
        ("Washing hands has no effect on infection rates.", "scientific", "health"),
        ("Smoking improves lung capacity.", "scientific", "health"),
        ("Continents never move relative to each other.", "scientific", "geoscience"),
        ("Atoms contain only neutrons.", "scientific", "chemistry"),
        ("Carbon dioxide has no heat-trapping properties.", "scientific", "climate"),
        ("HIV is cured by drinking lemon water daily.", "scientific", "health"),
        ("All gene editing is impossible in any organism.", "scientific", "biology"),
        ("Sound travels faster in vacuum than in air.", "scientific", "physics"),
        ("Mitochondria are found only in plants, never in animals.", "scientific", "biology"),
        ("The U.S. has no written constitution.", "political", "law"),
        ("Courts never review legislation for constitutionality.", "political", "law"),
        ("Electoral districts are always perfect squares by law.", "political", "civics"),
        ("The Senate requires unanimous consent for every vote with no exceptions.", "political", "civics"),
        ("Voter turnout is always 100% in every democracy.", "political", "elections"),
        ("Inflation means prices never change.", "statistical", "economics"),
        ("GDP counts unpaid household work at market prices by default in all countries.", "statistical", "economics"),
        ("A 95% confidence interval means there is a 95% chance the parameter is in the interval in all interpretations.", "statistical", "methods"),
        ("A convenience sample is always representative.", "statistical", "methods"),
    ]
    for claim, ctype, cat in EXTRA_TRUE:
        rows.append(_row(claim, "true", ctype, cat))
    for claim, ctype, cat in EXTRA_FALSE:
        rows.append(_row(claim, "false", ctype, cat))

    seen: set[str] = set()
    unique: list[dict] = []
    for r in rows:
        if r["claim"] not in seen:
            seen.add(r["claim"])
            unique.append(r)

    if len(unique) < 150:
        raise SystemExit(f"Fixture too small: {len(unique)} claims; add more seeds.")

    unique = unique[:180]

    OUT.write_text(json.dumps(unique, indent=2), encoding="utf-8")
    print(f"Wrote {len(unique)} claims to {OUT}")
    from collections import Counter

    print("claim_type:", Counter(r["claim_type"] for r in unique))


if __name__ == "__main__":
    main()
