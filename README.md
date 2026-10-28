# VEIL: Steer the Contagion

Open `veil.html` in any modern browser. It is one self-contained file with no dependencies and works offline.

## Progression and locks
- Natures (8): Spore and Vector are open. Viral and Dormant unlock at 1 win, Fungal at 2, Parasite at 3, Prion at 4, Synthetic at 5.
- Scenarios (8): Bloom is open. Ghost at 1 win, Iron at 2, Fire at 3, Monsoon at 4, Frostbite at 5, Fortress at 6, Open Skies at 7.
- Marathon unlocks at 1 win, Brutal at 2.
- Campaign: Chapter 1 is open; each chapter unlocks when you win the one before.
- The title screen shows what is unlocked and what your next unlock is. Progress is saved in your browser. Use "Reset progress" on the title screen (click twice) to start fresh.

## Pathogens (natures)
- Spore: resilient and slow. Vector: long, unpredictable jumps. Viral: fast but fragile. Dormant: quiet, erupts in waves.
- Fungal: thrives in hot regions, struggles in the cold.
- Parasite: very hidden and spreads only overland (no air or sea).
- Prion: nearly uncurable, but slow.
- Synthetic: evolves on its own every cycle, but leaves a loud signature (detection creeps up).

## Scenarios
- Bloom (classic), Ghost (stealth), Iron (ruthless research), Fire (fast and loud).
- Monsoon: hot regions are fertile. Frostbite: cold regions favour you. Fortress: borders start sealed. Open Skies: air and sea routes are doubled, but surveillance is high.

## Trait tree (24 adaptations in four branches, plus the six core mutations)
- Tabs: Core, Spread, Survive, Stealth, Special. Each adaptation has prerequisites shown on its button. Hotkeys 1-9 buy the numbered item on the current tab.
- Spread: Aerosol Hops, Frequent Flyers, Cargo Stowaways, Urban Density, Rural Reach, Insect Vectors, Waterborne, Rapid Replication.
- Survive: Hardened Shell, Host Memory, Heat Adaptation, Cold Adaptation, Drug Resistance, Sleeper Cells.
- Stealth: Silent Carriers, Cure Sabotage, Border Whispers, Cellular Camouflage, Media Fog, Lab Infiltration, Border Breakers.
- Special: Viral Load, Black Ledger, Overclock.

## Modes
- **Standard run** (about 15 minutes): the default.
- **Marathon** (about twice as long): slower spread, slower cure, a 90-cycle cap, a later earliest win, and 1.4x score. Pick it on the title screen.
- **Campaign: The Long Quiet** (10 chapters): click Campaign on the title screen. Each chapter has its own scenario, nature, difficulty and starting handicap. Winning unlocks the next chapter and carries up to two of your adaptations forward. Progress is saved.
  1. First Breath (easy, Bloom/Spore)
  2. Crossing Water (Ghost/Vector)
  3. Cold Front (Iron/Viral)
  4. Glass Houses (Fire/Spore, the world is watching)
  5. Iron Curtain (Iron/Spore, halfway point)
  6. Rising Tide (Monsoon/Fungal)
  7. Deep Freeze (Frostbite/Parasite)
  8. Fortress World (Fortress/Synthetic)
  9. Open Skies (Open Skies/Dormant)
  10. The Last Veil (Iron/Synthetic, the finale)
  Later chapters let you carry more adaptations forward.

## Design system
- A single theme layer (`theme.css`) defines the look: dark "surveillance console" surfaces with glass panels, a refined type stack (Inter or the system UI font, with monospaced tabular numbers for data), a consistent icon set drawn as inline vector masks, and colour tokens for every stat (presence, detection, counter, influence, stability).
- HUD: each stat has an icon, a large live value and a sparkline of its history. The race bars show quarter ticks.
- Title screen: animated outbreak map, segmented controls for run length and difficulty, and mode cards for Campaign, Daily Challenge and Tutorial with live status.
- Cards, buttons, tabs, switches, toasts and dialogs share one style. Dialogs become bottom sheets on phones. Colours come from CSS variables, so the colorblind palette recolours everything automatically.
- Responsive: desktop uses a pinned-map cockpit; phones use a pinned map with a bottom navigation dock (Mutate, Region, Events) and a large Advance button.

## Layout (no more scrolling between the map and the controls)
- Desktop: the stats and race bars stay pinned at the top. The map is pinned on the left with the region details and the events log directly under it. The mutation panel is on the right, and the Advance button stays reachable at the bottom of it. During the start-region choice, the placement bar replaces the events panel under the map.
- Phone: the stats and map stay pinned at the top. Below the map, three tabs (Mutate, Region, Events) switch panels, the tab bar stays pinned under the map while you scroll, and the Advance button is fixed at the bottom. The Region tab opens automatically while you choose a start and when you tap a region, and the Events tab shows a dot when something new happens.

## Sound, music and settings
- Press Sound (header) to turn audio on. Music is generated live in your browser: a slow ambient bed that adds pulse, brightness and tension as detection and the countermeasure climb. Effects cover mutations, cycles, events, decisions, flights, purges, wins and losses.
- Settings (header) has separate Music and Effects switches and volume sliders, a colorblind-safe palette, Reduce motion, and Larger text. Everything is saved in your browser.
- The colorblind palette swaps green/red cues for blue, yellow, purple and orange, changes the map legend to match, and uses dashed versus solid rings so meaning never depends on color alone.

## Daily Challenge
- Click Daily Challenge on the title screen. Everyone gets the same scenario, pathogen, modifier and random seed for the UTC day. Choose your starting region, retry as often as you like, and your best result counts.
- It tracks your best score for the day, your streak and days played, and gives you a Copy daily result button on the end screen to share. New achievements: Daily Driver and On a Roll (3-day streak).
- Modifiers: Cold Open, Rich Start, Loud World, Walled Borders, Fast Lab, Sleepy Lab, Unstable Form, Head Start.

## Learning the game
- A guided tutorial starts automatically the first time you play. It highlights each part of the screen, waits for you to act (choose a region, buy a mutation, advance a cycle), and can be skipped. Replay it any time with the Tutorial button on the title screen.
- Influence is your currency. The Influence box shows your balance and your income (+X / cycle). Click it, or the Glossary button, for definitions of every number. Mutation buttons show how many more Influence you need and roughly how many cycles that takes, and glow when you can afford them.

## Playing
- Choose where it begins: each run starts by picking a region on the map (tap it, check its population, science, openness and links, then confirm), or press Random.
- Difficulty: Casual / Normal / Brutal (Brutal scores 25% more, Casual 15% less).
- The world has 41 sub-regions. Click any land area to select it. Seed Reservoir targets the selected region when it is weak.
- Hotkeys: 1-9 buy mutations, Space/Enter advances a cycle, Esc closes dialogs. In a decision dialog press 1-3.
- Decisions: 17 different dilemmas; each appears at most once per run.
- World events: 24 scripted events; each fires at most twice per run and never twice in a row.
- Airports and ports seed far-away regions; the world closes them when detection or seals are high.
- Adaptations are one-time perks with prerequisites: Silent Carriers -> Cure Sabotage; Hardened Shell -> Aerosol Hops -> Border Whispers / Frequent Flyers; Hardened Shell -> Cargo Stowaways; Host Memory.
- Win by becoming permanent before the countermeasure hits 100%. Sealed, detected regions get purged.
- After each run you get a recap chart. Progress, stats, achievements and campaign state save automatically in your browser.

## Tuning
    python3 build.py CURE_K PURGE_K CURE_PURGE PP PC PT JK EVT_P AIRK PORTK
    current: 7.2 3.3 1.8 58 37 16 1.35 0.4 0.2 0.1
Marathon and campaign multipliers are in `systems2.js` and `build.py` (search for MARA and CHAPTERS).

## Files (all in this one folder)
- `veil.html`: the game (built output)
- `veil_original.html`: your original game
- `map_art_original.png`, `map_clean.png`: the map art
- `land_parent.json`, `make_regions.py`, `regions.json`, `land.json`: region and land data (41 regions)
- `events.js`: 24 world events
- `systems.js`: decisions, air/sea transmission, recap chart, save/resume, stats
- `systems2.js`: more decisions, Marathon mode, the campaign
- `systems3.js`: unlock progression, lock display, reset progress
- `systems5.js`: trait-tree tabs and the ongoing effects of adaptations and new pathogens
- `guide.js`: Influence readout, glossary, affordability hints, and the guided tutorial
- `audio.js`: music, sound effects, settings and the colorblind palette
- `layout.js`: the pinned-map cockpit layout, mobile tabs and fixed Advance bar
- `theme.css`, `theme.js`: the design system, animated title map and HUD sparklines
- `daily.js`: seeded random numbers, the Daily Challenge and result sharing
- `det.js`: proves the daily seed is deterministic (same seed, same outcome)
- `systems4.js`: choose-your-starting-region step
- `build.py`: re-applies every change to the original and writes veil.html
- `tune.js`, `tune_modes.js`, `tune_new.js`, `tune_ch.js`: balance simulations (per pathogen, per scenario, Marathon, each chapter)
- `stress.js`: runs thousands of random games and reports any exception
- `game.js`: generated by build.py

## Rebuild / re-test (run from this folder; needs Python 3 and Node, plus numpy for make_regions.py)
    python3 build.py 7.2 3.3 1.8 58 37 16 1.35 0.4 0.2 0.1
    node tune_modes.js 20
    node stress.js
