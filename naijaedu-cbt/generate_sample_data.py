#!/usr/bin/env python3
"""
NaijaEdu CBT — Sample Data Generator
Populates the database with realistic JAMB/WAEC-style questions
and two demo user accounts.

Usage:
    python generate_sample_data.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import DatabaseManager
from config import DATA_DIR


# ─── Demo Users ───────────────────────────────────────────────────────────────

DEMO_USERS = [
    {
        "username"   : "student1",
        "password"   : "student1",
        "full_name"  : "John Doe",
        "exam_number": "12345678AB",
        "email"      : "john.doe@example.com",
    },
    {
        "username"   : "admin",
        "password"   : "admin123",
        "full_name"  : "Administrator",
        "exam_number": None,
        "email"      : "admin@naijaedu.com",
    },
]


# ─── Question Banks ───────────────────────────────────────────────────────────

QUESTIONS = [

    # ═══════════════ MATHEMATICS ════════════════════════════════════════════

    # JAMB Mathematics
    dict(exam_type="JAMB", subject="Mathematics", year=2023,
         question_text="If 2^x = 32, find the value of x.",
         option_a="4", option_b="5", option_c="6", option_d="3",
         correct_option="B", explanation="2^5 = 32, so x = 5.",
         topic="Indices", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2023,
         question_text="Find the gradient of the line passing through (2, 3) and (4, 7).",
         option_a="1", option_b="2", option_c="3", option_d="4",
         correct_option="B", explanation="Gradient = (7-3)/(4-2) = 4/2 = 2.",
         topic="Coordinate Geometry", difficulty="Medium"),

    dict(exam_type="JAMB", subject="Mathematics", year=2022,
         question_text="Simplify: log₁₀ 100 + log₁₀ 10",
         option_a="3", option_b="4", option_c="2", option_d="1",
         correct_option="A", explanation="log₁₀ 100 = 2, log₁₀ 10 = 1. Sum = 3.",
         topic="Logarithms", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2022,
         question_text="The sum of angles in a triangle is:",
         option_a="90°", option_b="270°", option_c="360°", option_d="180°",
         correct_option="D", explanation="The interior angles of any triangle sum to 180°.",
         topic="Geometry", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2021,
         question_text="Solve for x: 3x - 7 = 14",
         option_a="5", option_b="6", option_c="7", option_d="8",
         correct_option="C", explanation="3x = 21, x = 7.",
         topic="Linear Equations", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2021,
         question_text="What is the derivative of y = x³ + 2x with respect to x?",
         option_a="3x² + 2", option_b="3x + 2", option_c="x² + 2", option_d="3x²",
         correct_option="A", explanation="dy/dx = 3x² + 2 by the power rule.",
         topic="Calculus", difficulty="Medium"),

    dict(exam_type="JAMB", subject="Mathematics", year=2020,
         question_text="If a = 3 and b = -2, evaluate 2a² - 3b.",
         option_a="12", option_b="18", option_c="24", option_d="22",
         correct_option="C", explanation="2(9) - 3(-2) = 18 + 6 = 24.",
         topic="Algebra", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2020,
         question_text="The area of a circle with radius 7 cm is: (Take π = 22/7)",
         option_a="44 cm²", option_b="154 cm²", option_c="22 cm²", option_d="88 cm²",
         correct_option="B", explanation="A = πr² = (22/7)(49) = 154 cm².",
         topic="Mensuration", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2019,
         question_text="Find the 10th term of the arithmetic sequence: 3, 7, 11, 15, ...",
         option_a="39", option_b="43", option_c="35", option_d="47",
         correct_option="A", explanation="a = 3, d = 4. T₁₀ = 3 + 9(4) = 39.",
         topic="Sequences & Series", difficulty="Medium"),

    dict(exam_type="JAMB", subject="Mathematics", year=2019,
         question_text="If P = {1, 2, 3, 4} and Q = {3, 4, 5, 6}, find P ∪ Q.",
         option_a="{1,2,3,4,5,6}", option_b="{3,4}", option_c="{1,2}", option_d="{5,6}",
         correct_option="A", explanation="Union contains all distinct elements from both sets.",
         topic="Set Theory", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2018,
         question_text="Factorise completely: x² - 5x + 6",
         option_a="(x+2)(x+3)", option_b="(x-2)(x-3)", option_c="(x-1)(x-6)", option_d="(x+1)(x-6)",
         correct_option="B", explanation="(x-2)(x-3) = x²-5x+6. Check: -2×-3=6, -2+-3=-5.",
         topic="Quadratic Equations", difficulty="Medium"),

    dict(exam_type="JAMB", subject="Mathematics", year=2018,
         question_text="Evaluate: ⁵C₂",
         option_a="10", option_b="20", option_c="5", option_d="15",
         correct_option="A", explanation="⁵C₂ = 5!/(2!3!) = (5×4)/(2×1) = 10.",
         topic="Permutation & Combination", difficulty="Medium"),

    dict(exam_type="JAMB", subject="Mathematics", year=2017,
         question_text="Convert 110₂ to base 10.",
         option_a="5", option_b="6", option_c="7", option_d="4",
         correct_option="B", explanation="1×4 + 1×2 + 0×1 = 4+2+0 = 6.",
         topic="Number Bases", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2017,
         question_text="A bag contains 4 red and 6 blue balls. Find the probability of picking a red ball.",
         option_a="2/5", option_b="3/5", option_c="1/4", option_d="1/2",
         correct_option="A", explanation="P(red) = 4/10 = 2/5.",
         topic="Probability", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2016,
         question_text="If tan θ = 3/4, find sin θ.",
         option_a="3/5", option_b="4/5", option_c="3/4", option_d="4/3",
         correct_option="A", explanation="Hypotenuse = 5. sin θ = opposite/hyp = 3/5.",
         topic="Trigonometry", difficulty="Medium"),

    dict(exam_type="JAMB", subject="Mathematics", year=2016,
         question_text="A trader bought goods for ₦8,000 and sold for ₦10,000. What is the profit %?",
         option_a="20%", option_b="25%", option_c="15%", option_d="30%",
         correct_option="B", explanation="Profit = 2000. % = (2000/8000)×100 = 25%.",
         topic="Commercial Arithmetic", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2015,
         question_text="Find the mean of: 4, 8, 12, 16, 20",
         option_a="10", option_b="12", option_c="14", option_d="16",
         correct_option="B", explanation="Mean = (4+8+12+16+20)/5 = 60/5 = 12.",
         topic="Statistics", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2015,
         question_text="If f(x) = 2x + 3, find f(5).",
         option_a="11", option_b="13", option_c="15", option_d="10",
         correct_option="B", explanation="f(5) = 2(5)+3 = 13.",
         topic="Functions", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2014,
         question_text="Solve: x² - 9 = 0",
         option_a="x = ±3", option_b="x = 3", option_c="x = -3", option_d="x = 9",
         correct_option="A", explanation="x² = 9, x = ±3.",
         topic="Quadratic Equations", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2014,
         question_text="What is the LCM of 12 and 18?",
         option_a="36", option_b="72", option_c="24", option_d="54",
         correct_option="A", explanation="12 = 2²×3, 18 = 2×3². LCM = 2²×3² = 36.",
         topic="Number Theory", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Mathematics", year=2013,
         question_text="The bearing of B from A is 060°. What is the bearing of A from B?",
         option_a="240°", option_b="300°", option_c="120°", option_d="180°",
         correct_option="A", explanation="Back bearing = 060° + 180° = 240°.",
         topic="Bearings", difficulty="Medium"),

    # WAEC Mathematics
    dict(exam_type="WAEC", subject="Mathematics", year=2023,
         question_text="Simplify: (2³ × 2²) ÷ 2⁴",
         option_a="2", option_b="4", option_c="8", option_d="16", option_e="1",
         correct_option="A", explanation="2^(3+2-4) = 2^1 = 2.",
         topic="Indices", difficulty="Easy"),

    dict(exam_type="WAEC", subject="Mathematics", year=2022,
         question_text="The HCF of 24 and 36 is:",
         option_a="6", option_b="8", option_c="12", option_d="18", option_e="4",
         correct_option="C", explanation="Factors of 24: 1,2,3,4,6,8,12,24. Factors of 36: 1,2,3,4,6,9,12,18,36. HCF = 12.",
         topic="Number Theory", difficulty="Easy"),

    dict(exam_type="WAEC", subject="Mathematics", year=2021,
         question_text="Find the volume of a cube with side 5 cm.",
         option_a="25 cm³", option_b="75 cm³", option_c="125 cm³", option_d="150 cm³", option_e="100 cm³",
         correct_option="C", explanation="V = s³ = 5³ = 125 cm³.",
         topic="Mensuration", difficulty="Easy"),

    # ═══════════════ ENGLISH LANGUAGE ═══════════════════════════════════════

    dict(exam_type="JAMB", subject="English Language", year=2023,
         question_text="Choose the word that is nearest in meaning to BENEVOLENT.",
         option_a="Cruel", option_b="Kind", option_c="Hostile", option_d="Selfish",
         correct_option="B", explanation="Benevolent means well-meaning and kindly.",
         topic="Vocabulary", difficulty="Easy"),

    dict(exam_type="JAMB", subject="English Language", year=2023,
         question_text="Identify the figure of speech in: 'The wind whispered through the trees.'",
         option_a="Simile", option_b="Metaphor", option_c="Personification", option_d="Hyperbole",
         correct_option="C", explanation="Attributing human action (whispering) to the wind is personification.",
         topic="Literary Devices", difficulty="Medium"),

    dict(exam_type="JAMB", subject="English Language", year=2022,
         question_text="Choose the option that best completes: 'Neither the students nor the teacher ___ ready.'",
         option_a="were", option_b="was", option_c="are", option_d="have been",
         correct_option="B", explanation="When neither/nor is used, the verb agrees with the closer subject (teacher - singular).",
         topic="Grammar", difficulty="Medium"),

    dict(exam_type="JAMB", subject="English Language", year=2022,
         question_text="The plural of 'phenomenon' is:",
         option_a="Phenomenons", option_b="Phenomena", option_c="Phenomenas", option_d="Phenomenon",
         correct_option="B", explanation="'Phenomena' is the correct plural of the Greek-origin word 'phenomenon'.",
         topic="Grammar", difficulty="Medium"),

    dict(exam_type="JAMB", subject="English Language", year=2021,
         question_text="Choose the antonym of VERBOSE.",
         option_a="Wordy", option_b="Talkative", option_c="Concise", option_d="Loquacious",
         correct_option="C", explanation="Verbose means using too many words; concise is its antonym.",
         topic="Vocabulary", difficulty="Medium"),

    dict(exam_type="JAMB", subject="English Language", year=2021,
         question_text="Which sentence is grammatically correct?",
         option_a="He don't know the answer.", option_b="She have gone to school.",
         option_c="They has finished the work.", option_d="I have already eaten.",
         correct_option="D", explanation="'I have already eaten' correctly uses the present perfect tense.",
         topic="Grammar", difficulty="Easy"),

    dict(exam_type="JAMB", subject="English Language", year=2020,
         question_text="The word 'INEFFABLE' means:",
         option_a="Too great to be expressed in words", option_b="Easily described",
         option_c="Very noisy", option_d="Clearly visible",
         correct_option="A", explanation="Ineffable: too great or extreme to be expressed in words.",
         topic="Vocabulary", difficulty="Hard"),

    dict(exam_type="JAMB", subject="English Language", year=2020,
         question_text="Identify the passive voice: 'The letter was written by Amaka.'",
         option_a="Active voice", option_b="Passive voice", option_c="Interrogative", option_d="Imperative",
         correct_option="B", explanation="The subject (letter) receives the action — this is passive voice.",
         topic="Grammar", difficulty="Easy"),

    dict(exam_type="JAMB", subject="English Language", year=2019,
         question_text="Choose the correctly spelt word:",
         option_a="Accomodation", option_b="Accomadation", option_c="Accommodation", option_d="Acomodation",
         correct_option="C", explanation="'Accommodation' has double 'c' and double 'm'.",
         topic="Spelling", difficulty="Easy"),

    dict(exam_type="JAMB", subject="English Language", year=2019,
         question_text="A word that imitates a sound is called:",
         option_a="Oxymoron", option_b="Onomatopoeia", option_c="Alliteration", option_d="Assonance",
         correct_option="B", explanation="Onomatopoeia is the use of words that imitate sounds (e.g., buzz, hiss).",
         topic="Literary Devices", difficulty="Medium"),

    # ═══════════════ PHYSICS ════════════════════════════════════════════════

    dict(exam_type="JAMB", subject="Physics", year=2023,
         question_text="The unit of electric resistance is:",
         option_a="Ampere", option_b="Volt", option_c="Ohm", option_d="Watt",
         correct_option="C", explanation="The SI unit of electrical resistance is the Ohm (Ω).",
         topic="Electricity", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Physics", year=2023,
         question_text="Which of the following is a vector quantity?",
         option_a="Mass", option_b="Temperature", option_c="Speed", option_d="Velocity",
         correct_option="D", explanation="Velocity has both magnitude and direction, making it a vector quantity.",
         topic="Mechanics", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Physics", year=2022,
         question_text="The acceleration due to gravity on Earth is approximately:",
         option_a="6.8 m/s²", option_b="9.8 m/s²", option_c="10.8 m/s²", option_d="8.8 m/s²",
         correct_option="B", explanation="g ≈ 9.8 m/s² (often approximated as 10 m/s² in calculations).",
         topic="Mechanics", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Physics", year=2022,
         question_text="Sound cannot travel through:",
         option_a="Water", option_b="Steel", option_c="A vacuum", option_d="Air",
         correct_option="C", explanation="Sound is a mechanical wave requiring a medium; it cannot travel through a vacuum.",
         topic="Waves", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Physics", year=2021,
         question_text="Ohm's Law states that V = IR. If V = 12V and R = 4Ω, find I.",
         option_a="3A", option_b="4A", option_c="48A", option_d="8A",
         correct_option="A", explanation="I = V/R = 12/4 = 3A.",
         topic="Electricity", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Physics", year=2021,
         question_text="The phenomenon of light bending as it passes from one medium to another is called:",
         option_a="Reflection", option_b="Refraction", option_c="Diffraction", option_d="Dispersion",
         correct_option="B", explanation="Refraction is the bending of light at the boundary between two media.",
         topic="Optics", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Physics", year=2020,
         question_text="Which type of mirror is used in a car's rear-view mirror?",
         option_a="Concave", option_b="Plane", option_c="Convex", option_d="Parabolic",
         correct_option="C", explanation="Convex mirrors give a wider field of view, making them ideal for rear-view mirrors.",
         topic="Optics", difficulty="Medium"),

    dict(exam_type="JAMB", subject="Physics", year=2020,
         question_text="The energy stored in a stretched elastic band is:",
         option_a="Kinetic energy", option_b="Thermal energy", option_c="Chemical energy", option_d="Elastic potential energy",
         correct_option="D", explanation="Stretched objects store elastic potential energy.",
         topic="Energy", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Physics", year=2019,
         question_text="What is the SI unit of power?",
         option_a="Joule", option_b="Newton", option_c="Watt", option_d="Pascal",
         correct_option="C", explanation="Power is measured in Watts (W = J/s).",
         topic="Work, Energy & Power", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Physics", year=2019,
         question_text="Half-life is a concept associated with:",
         option_a="Electromagnetic waves", option_b="Radioactivity", option_c="Sound waves", option_d="Light",
         correct_option="B", explanation="Half-life is the time taken for half of the atoms in a radioactive sample to decay.",
         topic="Nuclear Physics", difficulty="Medium"),

    dict(exam_type="JAMB", subject="Physics", year=2018,
         question_text="A body moves in a circle at constant speed. Its acceleration is directed:",
         option_a="Tangentially", option_b="Outward from centre", option_c="Toward the centre", option_d="Upward",
         correct_option="C", explanation="Centripetal acceleration always points toward the centre of the circular path.",
         topic="Circular Motion", difficulty="Medium"),

    # ═══════════════ CHEMISTRY ══════════════════════════════════════════════

    dict(exam_type="JAMB", subject="Chemistry", year=2023,
         question_text="The atomic number of Carbon is:",
         option_a="8", option_b="6", option_c="12", option_d="14",
         correct_option="B", explanation="Carbon has 6 protons, so its atomic number is 6.",
         topic="Atomic Structure", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Chemistry", year=2023,
         question_text="Which of the following is a noble gas?",
         option_a="Nitrogen", option_b="Chlorine", option_c="Argon", option_d="Oxygen",
         correct_option="C", explanation="Argon (Ar) is in Group 18 — the noble gases.",
         topic="Periodic Table", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Chemistry", year=2022,
         question_text="The chemical formula of water is:",
         option_a="HO", option_b="H₂O₂", option_c="H₂O", option_d="OH₂",
         correct_option="C", explanation="Water consists of 2 hydrogen atoms bonded to 1 oxygen atom.",
         topic="Chemical Formulae", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Chemistry", year=2022,
         question_text="Which type of bond is formed when electrons are shared between atoms?",
         option_a="Ionic bond", option_b="Covalent bond", option_c="Metallic bond", option_d="Hydrogen bond",
         correct_option="B", explanation="Covalent bonds form when atoms share electrons.",
         topic="Chemical Bonding", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Chemistry", year=2021,
         question_text="What is the pH of a neutral solution at 25°C?",
         option_a="0", option_b="7", option_c="14", option_d="3",
         correct_option="B", explanation="A pH of 7 is neutral — neither acidic nor basic.",
         topic="Acids, Bases & Salts", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Chemistry", year=2021,
         question_text="Which gas is produced when zinc reacts with dilute hydrochloric acid?",
         option_a="Oxygen", option_b="Carbon dioxide", option_c="Hydrogen", option_d="Chlorine",
         correct_option="C", explanation="Zn + 2HCl → ZnCl₂ + H₂↑. Hydrogen gas is evolved.",
         topic="Metals & Their Reactions", difficulty="Medium"),

    dict(exam_type="JAMB", subject="Chemistry", year=2020,
         question_text="The process by which plants make food using sunlight is called:",
         option_a="Respiration", option_b="Photosynthesis", option_c="Fermentation", option_d="Combustion",
         correct_option="B", explanation="Photosynthesis converts CO₂ and water into glucose using light energy.",
         topic="Applied Chemistry", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Chemistry", year=2020,
         question_text="Alloys are:",
         option_a="Pure metals", option_b="Mixtures of metals", option_c="Chemical compounds", option_d="Non-metals",
         correct_option="B", explanation="An alloy is a mixture of two or more metals (or a metal and a non-metal).",
         topic="Metals & Alloys", difficulty="Easy"),

    # ═══════════════ BIOLOGY ════════════════════════════════════════════════

    dict(exam_type="JAMB", subject="Biology", year=2023,
         question_text="The basic unit of life is the:",
         option_a="Tissue", option_b="Organ", option_c="Cell", option_d="Organism",
         correct_option="C", explanation="The cell is the fundamental structural and functional unit of all living organisms.",
         topic="Cell Biology", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Biology", year=2023,
         question_text="Photosynthesis takes place in the:",
         option_a="Mitochondria", option_b="Nucleus", option_c="Chloroplast", option_d="Ribosome",
         correct_option="C", explanation="Chloroplasts contain chlorophyll and are the site of photosynthesis.",
         topic="Plant Biology", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Biology", year=2022,
         question_text="Which blood group is the universal donor?",
         option_a="A", option_b="B", option_c="AB", option_d="O",
         correct_option="D", explanation="Blood group O negative is the universal donor.",
         topic="Blood & Circulation", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Biology", year=2022,
         question_text="The process of breaking down glucose to release energy is called:",
         option_a="Photosynthesis", option_b="Respiration", option_c="Transpiration", option_d="Digestion",
         correct_option="B", explanation="Cellular respiration breaks down glucose (C₆H₁₂O₆) to release ATP.",
         topic="Respiration", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Biology", year=2021,
         question_text="The genetic material found in the nucleus is:",
         option_a="RNA", option_b="ATP", option_c="DNA", option_d="Protein",
         correct_option="C", explanation="DNA (deoxyribonucleic acid) carries hereditary information in the nucleus.",
         topic="Genetics", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Biology", year=2021,
         question_text="Which organ is responsible for filtering blood in humans?",
         option_a="Liver", option_b="Kidney", option_c="Spleen", option_d="Lung",
         correct_option="B", explanation="The kidneys filter blood and produce urine as waste.",
         topic="Excretion", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Biology", year=2020,
         question_text="Osmosis is defined as the movement of water molecules:",
         option_a="From low to high concentration of solute through any membrane",
         option_b="From high to low concentration of water through a semi-permeable membrane",
         option_c="Against the concentration gradient",
         option_d="From region of high water potential to low water potential through a semi-permeable membrane",
         correct_option="D",
         explanation="Osmosis is the movement of water across a semi-permeable membrane from high to low water potential.",
         topic="Transport in Plants", difficulty="Medium"),

    # ═══════════════ ECONOMICS ══════════════════════════════════════════════

    dict(exam_type="JAMB", subject="Economics", year=2023,
         question_text="When demand exceeds supply, the price will:",
         option_a="Fall", option_b="Rise", option_c="Remain constant", option_d="Be indeterminate",
         correct_option="B", explanation="Excess demand creates upward pressure on prices.",
         topic="Demand & Supply", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Economics", year=2023,
         question_text="The full meaning of GDP is:",
         option_a="Gross Domestic Product", option_b="General Domestic Price",
         option_c="Gross Demand Price", option_d="General Demand Product",
         correct_option="A", explanation="GDP stands for Gross Domestic Product — total value of goods and services produced.",
         topic="National Income", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Economics", year=2022,
         question_text="A market structure with only one seller is called:",
         option_a="Oligopoly", option_b="Monopoly", option_c="Perfect competition", option_d="Duopoly",
         correct_option="B", explanation="A monopoly has a single seller dominating the entire market.",
         topic="Market Structures", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Economics", year=2022,
         question_text="Inflation means a sustained:",
         option_a="Fall in the value of money", option_b="Rise in the value of money",
         option_c="Fall in unemployment", option_d="Rise in production",
         correct_option="A", explanation="Inflation is a general rise in price levels, which erodes the value of money.",
         topic="Inflation", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Economics", year=2021,
         question_text="The barter system was replaced by money because:",
         option_a="Barter was too fast", option_b="Barter required double coincidence of wants",
         option_c="Barter was illegal", option_d="Money was invented by government",
         correct_option="B", explanation="Barter required that both parties want exactly what the other offers — this is double coincidence of wants.",
         topic="Money & Banking", difficulty="Medium"),

    # ═══════════════ GOVERNMENT ═════════════════════════════════════════════

    dict(exam_type="JAMB", subject="Government", year=2023,
         question_text="Nigeria became a republic in:",
         option_a="1960", option_b="1963", option_c="1966", option_d="1979",
         correct_option="B", explanation="Nigeria became a republic on October 1, 1963.",
         topic="Nigerian History", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Government", year=2023,
         question_text="The principle of separation of powers was propounded by:",
         option_a="John Locke", option_b="Jean-Jacques Rousseau", option_c="Montesquieu", option_d="Thomas Hobbes",
         correct_option="C", explanation="Baron de Montesquieu developed the doctrine of separation of powers in 'The Spirit of Laws' (1748).",
         topic="Political Theory", difficulty="Medium"),

    dict(exam_type="JAMB", subject="Government", year=2022,
         question_text="The ECOWAS was established in:",
         option_a="1960", option_b="1975", option_c="1980", option_d="1963",
         correct_option="B", explanation="The Economic Community of West African States was established on May 28, 1975 in Lagos.",
         topic="International Relations", difficulty="Medium"),

    dict(exam_type="JAMB", subject="Government", year=2022,
         question_text="Federalism is a system of government in which power is:",
         option_a="Concentrated in one body", option_b="Shared between central and regional governments",
         option_c="Exercised by the military", option_d="Held by the judiciary",
         correct_option="B", explanation="Federalism divides power between a national government and sub-national (state/regional) governments.",
         topic="Systems of Government", difficulty="Easy"),

    # ═══════════════ GEOGRAPHY ══════════════════════════════════════════════

    dict(exam_type="JAMB", subject="Geography", year=2023,
         question_text="The longest river in Africa is the:",
         option_a="Congo", option_b="Zambezi", option_c="Nile", option_d="Niger",
         correct_option="C", explanation="The Nile River is the longest river in Africa and the world, stretching about 6,650 km.",
         topic="African Geography", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Geography", year=2023,
         question_text="Latitude lines run:",
         option_a="North to South", option_b="East to West", option_c="Diagonally", option_d="Vertically",
         correct_option="B", explanation="Lines of latitude run horizontally (east-west) and measure distance from the equator.",
         topic="Mapping", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Geography", year=2022,
         question_text="The major gas responsible for the greenhouse effect is:",
         option_a="Oxygen", option_b="Nitrogen", option_c="Carbon dioxide", option_d="Hydrogen",
         correct_option="C", explanation="Carbon dioxide (CO₂) traps heat in the atmosphere, contributing to global warming.",
         topic="Climate & Environment", difficulty="Easy"),

    # ═══════════════ CIVIC EDUCATION ════════════════════════════════════════

    dict(exam_type="JAMB", subject="Civic Education", year=2023,
         question_text="The primary function of the police is to:",
         option_a="Make laws", option_b="Maintain law and order", option_c="Interpret the constitution", option_d="Collect taxes",
         correct_option="B", explanation="The police force's primary role is to maintain law, order, and public safety.",
         topic="Government Institutions", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Civic Education", year=2022,
         question_text="Rule of law means:",
         option_a="The military rules the country", option_b="Everyone is subject to the law equally",
         option_c="Politicians are above the law", option_d="The rich can buy justice",
         correct_option="B", explanation="Rule of law means that all persons and institutions are equally accountable to the law.",
         topic="Democracy & Governance", difficulty="Easy"),

    # ═══════════════ ACCOUNTING ═════════════════════════════════════════════

    dict(exam_type="JAMB", subject="Accounting", year=2023,
         question_text="The accounting equation is:",
         option_a="Assets = Liabilities + Capital", option_b="Assets = Liabilities - Capital",
         option_c="Capital = Assets + Liabilities", option_d="Liabilities = Assets + Capital",
         correct_option="A", explanation="The fundamental accounting equation: Assets = Liabilities + Owner's Equity (Capital).",
         topic="Basic Accounting Concepts", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Accounting", year=2022,
         question_text="A credit entry is made on the ___ side of an account.",
         option_a="Left", option_b="Right", option_c="Top", option_d="Bottom",
         correct_option="B", explanation="In double-entry bookkeeping, credits are recorded on the right side of an account.",
         topic="Double-Entry Bookkeeping", difficulty="Easy"),

    dict(exam_type="JAMB", subject="Accounting", year=2021,
         question_text="Depreciation is charged on:",
         option_a="Current assets", option_b="Fixed assets", option_c="Liabilities", option_d="Capital",
         correct_option="B", explanation="Depreciation is the systematic allocation of the cost of a fixed (non-current) asset over its useful life.",
         topic="Fixed Assets", difficulty="Medium"),

]


# ─── Seeder ───────────────────────────────────────────────────────────────────

def seed(db: DatabaseManager):
    print("\n── NaijaEdu Sample Data Generator ────────────────────")

    # Users
    print("\n[1/2] Creating demo users …")
    for u in DEMO_USERS:
        if db.username_exists(u["username"]):
            print(f"  • {u['username']} already exists — skipped.")
            continue
        uid = db.create_user(
            username    = u["username"],
            password    = u["password"],
            full_name   = u["full_name"],
            exam_number = u.get("exam_number"),
            email       = u.get("email"),
        )
        print(f"  ✓ Created user '{u['username']}' (id={uid})")

    # Questions
    print(f"\n[2/2] Inserting {len(QUESTIONS)} questions …")
    added = 0
    for q in QUESTIONS:
        try:
            db.add_question(q)
            added += 1
        except Exception as e:
            print(f"  ✗ Failed: {e}")

    print(f"  ✓ {added} questions inserted.")

    # Summary
    print("\n── Summary ─────────────────────────────────────────────")
    print("  Default accounts:")
    print("    Student  →  student1 / student1")
    print("    Admin    →  admin    / admin123")
    print("\n  To launch the app:")
    print("    python main.py")
    print("────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db = DatabaseManager()
    seed(db)
    db.close()
