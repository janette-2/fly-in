_This project has been created as part of the 42 curriculum by janrodri._

# fly-in

A drone routing simulator. Drones navigate through a network of zones
(hubs) connected by paths. The goal is to move all drones from the
start zone to the end zone in as few turns as possible.

---

## Table of Contents

1. [How the Map Works](#1-how-the-map-works)
2. [Project Structure](#2-project-structure)
3. [Requirements & Setup](#3-requirements--setup)
4. [Makefile Commands](#4-makefile-commands)
5. [The Parser (reading the map)](#5-the-parser-reading-the-map)
6. [Pathfinding (finding the route)](#6-pathfinding-finding-the-route)
   - [6.1 What is a graph?](#61-what-is-a-graph)
   - [6.2 _build_graph() — turning the map into a graph](#62-_build_graph--turning-the-map-into-a-graph)
   - [6.3 Dijkstra's algorithm explained with pictures](#63-dijkstras-algorithm-explained-with-pictures)
   - [6.4 The key tools in Dijkstra](#64-the-key-tools-in-dijkstra)
   - [6.5 Why Dijkstra beats "pick the cheapest neighbor"](#65-why-dijkstra-beats-pick-the-cheapest-neighbor)
7. [The Simulator (moving the drones)](#7-the-simulator-moving-the-drones)
8. [Subject Specifications Summary](#8-subject-specifications-summary)
9. [Draft Notes](#9-draft-notes)
10. [Testing & Benchmarks](#10-testing--benchmarks)
11. [Resources](#11-resources)

---

## 1. How the Map Works

A map file describes the drone network. It looks like this:

```
nb_drones: 5
start_hub: start 0 0 [color=green max_drones=4]
hub: slow_path1 1 -1 [zone=restricted color=red]
hub: fast_path 2 0 [zone=priority color=blue]
end_hub: goal 4 0 [color=green max_drones=4]
connection: start-slow_path1
connection: start-fast_path
connection: fast_path-goal
connection: slow_path1-goal
```

**What each line means:**

```
start_hub:  name    x  y   [metadata]
   ↑          ↑     ↑  ↑       ↑
   role    unique  coord   optional settings
          identifier        in brackets
```

**Zone types (from the subject):**

| Type | Cost | Can drones enter? | Description |
|------|------|-------------------|-------------|
| `normal` | 1 turn | Yes | Standard zone (default) |
| `priority` | 1 turn | Yes | Same cost as normal, but pathfinding should prefer it |
| `restricted` | 2 turns | Yes | Slow zone — takes 2 turns to move into |
| `blocked` | never | No | Inaccessible — drones cannot enter or pass through |

**Connection metadata:**
- `max_link_capacity=N` — limits how many drones can cross this connection
  in the same turn (default: 1)

**Zone metadata:**
- `zone=TYPE` — sets the zone type (default: normal)
- `color=VALUE` — any single word for terminal display (default: none)
- `max_drones=N` — max drones in this zone at once (default: 1)

---

## 2. Project Structure

```
fly-in/
├── main.py          # Entry point — run this
├── parser.py        # Reads and validates map files
├── zones.py         # Zone (hub) class
├── connections.py   # Connection class
├── errors.py        # Custom error class
├── simulator.py     # Drone + Simulation (pathfinding + turn engine)
├── Makefile         # Automation commands
├── maps/            # Map files (easy, medium, hard, challenger)
│   ├── easy/
│   ├── medium/
│   ├── hard/
│   └── challenger/
├── subject.md       # Full project specification
└── README.md        # This file
```

---

## 3. Requirements & Setup

**You need:**
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — a fast Python package manager

**Why uv?**
- It installs tools in **isolated directories** (`~/.local/share/uv/tools/`),
  not in your system Python. No pollution.
- It avoids the `externally-managed-environment` error on Debian/Ubuntu.
- It is 10-100x faster than pip.

```sh
# Install uv (recommended way)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pipx
pipx install uv
```

---

## 4. Makefile Commands

| Command | What it does |
|---------|--------------|
| `make` or `make all` | Runs **lint** (default target) |
| `make install` | Installs `flake8` and `mypy` with uv |
| `make run MAP=<file>` | Runs the simulator with a specific map |
| `make debug MAP=<file>` | Runs the simulator with pdb (debugger) |
| `make clean` | Deletes `__pycache__`, `.mypy_cache`, `.pytest_cache`, `*.pyc` |
| `make lint` | Runs `flake8 .` + `mypy .` (with subject flags) |
| `make lint-strict` | Runs `flake8 .` + `mypy . --strict` |

**Example usage:**
```sh
make install          # install flake8 and mypy
make                  # lint the project
make run MAP=maps/easy/01_linear_path.txt
```

---

## 5. The Parser (reading the map)

The parser (`MapParser` in `parser.py`) does three things in order:

### Step 1: Clean the file

```
Raw file                     →  After cleaning
┌──────────────────────┐        ┌──────────────────────┐
│ # this is a comment  │        │ nb_drones: 5         │
│ nb_drones: 5         │   →   │ start_hub: start ...  │
│                      │        │ hub: fast_path ...    │
│ start_hub: start ... │        │ end_hub: goal ...     │
│ [empty line]         │        │ connection: start-... │
│ hub: fast_path ...   │        └──────────────────────┘
│ end_hub: goal ...    │
│ connection: start-.. │
└──────────────────────┘
```

- Lines starting with `#` are removed (comments)
- Empty lines are removed
- `\n` characters are stripped

### Step 2: Validate each line

```
For every line:
    │
    ├── "nb_drones:"  → check it's a positive integer
    ├── "start_hub:"  → parse name, x, y, metadata; check it's unique
    ├── "hub:"        → same as start_hub but can have many
    ├── "end_hub:"    → same as start_hub but exactly one
    └── "connection:" → parse zone1-zone2, check zones exist
                        check no duplicates (a-b = b-a)

After all lines:
    └── Exactly 1 start_hub and 1 end_hub? If not → error
```

### Step 3: Store the data

```
self.zones = {
    "start": Zones(name="start", x=0, y=0, role="start", ...),
    "fast_path": Zones(name="fast_path", x=2, y=0, role="hub", ...),
    "goal": Zones(name="goal", x=4, y=0, role="end", ...),
    ...
}

self.connections = {
    ("start", "fast_path"): Connections(zone1="start", zone2="fast_path"),
    ("fast_path", "goal"): Connections(zone1="fast_path", zone2="goal"),
    ...
}
```

**If anything is wrong, an error is raised:**

```
Error at line 12: Invalid zone type: 'super_fast'
Error at line 5: The connection needs two zones
Error at line 0: Map must contain exactly one start_hub and one end_hub
```

---

## 6. Pathfinding (finding the route)

This is the brain of the simulator. Given a start zone and an end zone,
find the path that takes the **fewest turns**.

### 6.1 What is a graph?

A map is really a **graph** — a collection of **nodes** (zones) connected
by **edges** (connections).

```
Visual:
                   ┌──────────┐
                   │  start   │
                   └────┬─────┘
                       / \
                      /   \
               ┌─────┘     └──────┐
               │                  │
        ┌──────┴──────┐    ┌──────┴──────┐
        │  slow_path1 │    │ fast_junction│
        │ (restricted)│    │  (priority)  │
        └──────┬──────┘    └──────┬──────┘
               │                  │
               │           ┌──────┴──────┐
               │           │  fast_path  │
               │           │  (priority) │
               │           └──────┬──────┘
               │                  │
        ┌──────┴──────┐    ┌──────┴──────┐
        │  slow_path2 │    │ merge_point │
        │ (restricted)│    │   (normal)  │
        └──────┬──────┘    └──────┬──────┘
               │                  │
               └──────┬───────────┘
                      │
               ┌──────┴──────┐
               │    goal     │
               └─────────────┘
```

Pathfinding algorithms work on graphs. They do not care about the
visual layout — only about **which zone connects to which** and
**how much each connection costs**.

### 6.2 `_build_graph()` — turning the map into a graph

The parser stores zones and connections in **two separate dictionaries**.
This is good for validation, but bad for pathfinding. Pathfinding needs
to ask: *"From zone X, which neighbors can I go to, and what does it cost?"*

`_build_graph()` merges everything into one structure:

```
Before (parser):
    zones = {
        "start": {...},
        "fast_junction": {... zone="priority" ...},
        "slow_path1": {... zone="restricted" ...},
        ...
    }
    connections = {
        ("start", "fast_junction"): {...},
        ("start", "slow_path1"): {...},
        ...
    }

After _build_graph():
    graph = {
        "start":         [("fast_junction", 1), ("slow_path1", 2)],
        "fast_junction": [("start", 1), ("fast_path", 1), ("slow_path1", 1)],
        "fast_path":     [("fast_junction", 1), ("merge_point", 1)],
        "slow_path1":    [("start", 1), ("fast_junction", 1), ("slow_path2", 2)],
        "slow_path2":    [("slow_path1", 2), ("merge_point", 1)],
        "merge_point":   [("fast_path", 1), ("slow_path2", 2), ("goal", 1)],
        "goal":          [("merge_point", 1)],
    }
```

Each entry in the graph says:
- `"start": [("fast_junction", 1), ("slow_path1", 2)]`
  → From `start`, you can go to `fast_junction` (costs 1 turn)
    or to `slow_path1` (costs 2 turns, because it's restricted).

**Blocked zones are excluded entirely** — they do not appear as keys
or as neighbors. Drones can never enter them.

### 6.3 Dijkstra's algorithm explained with pictures

Let's trace the algorithm step by step on this graph:

```
start ─── fast_junction ─── fast_path ─── merge_point ─── goal
                                                    │
slow_path1 ─── slow_path2 ──────────────────────────┘
```

**Step 0 — Initial state:**

We create a table. Every zone starts with distance `∞` (infinity,
we use `9999999`), except `start` which is `0`.

```
┌─────────────────────────────────────────────────────────────┐
│      Zone      │ Distance from start │ Came from │ Processed │
├────────────────┼─────────────────────┼───────────┼───────────┤
│ start          │          0          │    —      │     ✗     │
│ fast_junction  │       9999999       │    ?      │     ✗     │
│ fast_path      │       9999999       │    ?      │     ✗     │
│ slow_path1     │       9999999       │    ?      │     ✗     │
│ slow_path2     │       9999999       │    ?      │     ✗     │
│ merge_point    │       9999999       │    ?      │     ✗     │
│ goal           │       9999999       │    ?      │     ✗     │
└────────────────┴─────────────────────┴───────────┴───────────┘
```

**Step 1 — Process `start` (distance 0):**

Look at all neighbors of `start`:
- `fast_junction`: 0 + 1 = 1 → better than 9999999 → **update!**
- `slow_path1`: 0 + 2 = 2 → better than 9999999 → **update!**

Mark `start` as processed.

```
┌─────────────────────────────────────────────────────────────┐
│      Zone      │ Distance from start │ Came from │ Processed │
├────────────────┼─────────────────────┼───────────┼───────────┤
│ start          │          0          │    —      │     ✓     │
│ fast_junction  │          1          │   start   │     ✗     │
│ fast_path      │       9999999       │    ?      │     ✗     │
│ slow_path1     │          2          │   start   │     ✗     │
│ slow_path2     │       9999999       │    ?      │     ✗     │
│ merge_point    │       9999999       │    ?      │     ✗     │
│ goal           │       9999999       │    ?      │     ✗     │
└────────────────┴─────────────────────┴───────────┴───────────┘
```

**Step 2 — Pick the UNPROCESSED zone with the SMALLEST distance:**

That is `fast_junction` (distance 1). Look at its neighbors:
- `start`: already processed → skip
- `fast_path`: 1 + 1 = 2 → better than 9999999 → **update!**
- `slow_path1`: 1 + 1 = 2 → NOT better than 2 (same) → skip

Mark `fast_junction` as processed.

```
┌─────────────────────────────────────────────────────────────┐
│      Zone      │ Distance from start │ Came from │ Processed │
├────────────────┼─────────────────────┼───────────┼───────────┤
│ start          │          0          │    —      │     ✓     │
│ fast_junction  │          1          │   start   │     ✓     │
│ fast_path      │          2          │fast_junc. │     ✗     │
│ slow_path1     │          2          │   start   │     ✗     │
│ slow_path2     │       9999999       │    ?      │     ✗     │
│ merge_point    │       9999999       │    ?      │     ✗     │
│ goal           │       9999999       │    ?      │     ✗     │
└────────────────┴─────────────────────┴───────────┴───────────┘
```

**Step 3 — Unprocessed with smallest distance:**

Two zones have distance 2: `fast_path` and `slow_path1`.
We pick `fast_path` (the first one we find).

Neighbors of `fast_path`:
- `fast_junction`: processed → skip
- `merge_point`: 2 + 1 = 3 → better than 9999999 → **update!**

Mark `fast_path` as processed.

```
┌─────────────────────────────────────────────────────────────┐
│      Zone      │ Distance from start │ Came from │ Processed │
├────────────────┼─────────────────────┼───────────┼───────────┤
│ start          │          0          │    —      │     ✓     │
│ fast_junction  │          1          │   start   │     ✓     │
│ fast_path      │          2          │fast_junc. │     ✓     │
│ slow_path1     │          2          │   start   │     ✗     │
│ slow_path2     │       9999999       │    ?      │     ✗     │
│ merge_point    │          3          │ fast_path │     ✗     │
│ goal           │       9999999       │    ?      │     ✗     │
└────────────────┴─────────────────────┴───────────┴───────────┘
```

**Step 4 — Unprocessed with smallest distance: `slow_path1` (2).**

Neighbors of `slow_path1`:
- `start`: processed → skip
- `fast_junction`: processed → skip
- `slow_path2`: 2 + 2 = 4 → better than 9999999 → **update!**

Mark `slow_path1` as processed.

```
┌─────────────────────────────────────────────────────────────┐
│      Zone      │ Distance from start │ Came from │ Processed │
├────────────────┼─────────────────────┼───────────┼───────────┤
│ start          │          0          │    —      │     ✓     │
│ fast_junction  │          1          │   start   │     ✓     │
│ fast_path      │          2          │fast_junc. │     ✓     │
│ slow_path1     │          2          │   start   │     ✓     │
│ slow_path2     │          4          │slow_path1 │     ✗     │
│ merge_point    │          3          │ fast_path │     ✗     │
│ goal           │       9999999       │    ?      │     ✗     │
└────────────────┴─────────────────────┴───────────┴───────────┘
```

**Step 5 — Unprocessed with smallest distance: `merge_point` (3).**

Neighbors of `merge_point`:
- `fast_path`: processed → skip
- `slow_path2`: 3 + 2 = 5 → NOT better than 4 → skip
- `goal`: 3 + 1 = 4 → better than 9999999 → **update!**

Mark `merge_point` as processed.

```
┌─────────────────────────────────────────────────────────────┐
│      Zone      │ Distance from start │ Came from │ Processed │
├────────────────┼─────────────────────┼───────────┼───────────┤
│ start          │          0          │    —      │     ✓     │
│ fast_junction  │          1          │   start   │     ✓     │
│ fast_path      │          2          │fast_junc. │     ✓     │
│ slow_path1     │          2          │   start   │     ✓     │
│ slow_path2     │          4          │slow_path1 │     ✗     │
│ merge_point    │          3          │ fast_path │     ✓     │
│ goal           │          4          │merge_pt.  │     ✗     │
└────────────────┴─────────────────────┴───────────┴───────────┘
```

**Step 6 — Unprocessed with smallest distance: `goal` (4).**

We picked `goal` — that is our destination! **We stop.**

**Step 7 — Reconstruct the path:**

Start at `goal` and follow the breadcrumbs backward:

```
goal  ← came from "merge_point"
  merge_point  ← came from "fast_path"
    fast_path  ← came from "fast_junction"
      fast_junction  ← came from "start"
        start  ← this is the start!
```

Now reverse the list:

```
start → fast_junction → fast_path → merge_point → goal
```

**That is the shortest path in turns!**

### 6.4 The key tools in Dijkstra

| Tool | Type | What it does |
|------|------|--------------|
| `graph` | `dict[str, list[tuple[str, int]]]` | The adjacency list: from each zone, who are its neighbors and what is the cost? |
| `distances` | `dict[str, int]` | The best known distance (in turns) from `start` to each zone |
| `previous` | `dict[str, str \| None]` | For each zone, which zone did we come from? Used to reconstruct the path |
| `unvisited` | `list[str]` | Zones that have not been fully processed yet |
| `track_zone` | `str` | The unprocessed zone with the smallest distance — the one we are processing right now |

### 6.5 Why Dijkstra beats "pick the cheapest neighbor"

A naive approach (greedy) always picks the cheapest next step.
This fails on maps like this one:

```
         ┌─ A (cost 1) ── dead_end (cost 1)
start ───┤
         └─ B (cost 2) ── goal (cost 1)
```

**Greedy:**
1. From `start`, neighbors are `A`(1) and `B`(2). Pick `A` (cheaper).
2. From `A`, the only neighbor is `dead_end`(1). Go there.
3. From `dead_end`, no neighbors. **Stuck.**

**Dijkstra:**
1. From `start`, discover `A=1` and `B=2`. Process `start`.
2. Pick `A` (smallest unprocessed: 1). Discover `dead_end=2`. Process `A`.
3. Pick `B` (smallest unprocessed: 2). Discover `goal=3`. Process `B`.
4. Pick `goal` (3). **Arrived!**

The difference: Dijkstra maintains a **global view** (the distance table),
so it does not commit to a path until it has explored all alternatives.

---

## 7. The Simulator (moving the drones)

The simulation engine moves all drones from start to end turn by turn.

1. **Init:** Drones are created at the start zone with their paths
   pre-calculated by Dijkstra.

2. **Each turn:** Every undelivered drone evaluates one step along its path.
   Movement cost depends on the destination zone type (1 turn for normal/priority,
   2 turns for restricted).

3. **Capacity rules (from the subject):**
   - Each zone has a `max_drones` limit (default: 1)
   - Each connection has a `max_link_capacity` limit (default: 1)
   - Drones leaving a zone free up capacity in the same turn
   - Drones entering a restricted zone take 2 turns (they occupy
     the connection while in transit)

4. **Output format (from the subject):**
   ```
   D1-roof1 D2-corridorA
   D1-roof2 D2-tunnelB
   D1-goal D2-goal
   ```

5. **End condition:** All drones have reached the end zone.

### Algorithm: four-phase turn loop

Each turn runs four phases in sequence:

```
fly_simulation()
│
├── Init: occupation counters, shift=0
│
└── while not all delivered:              ← EACH TURN
    │
    ├── Init turn: output, to_enter,
    │   to_leave, used_connections, attempted_moves
    │
    ├── for drone in drones:              ← PHASE 1 + 2
    │   │
    │   └── if not drone.delivered:
    │       │
    │       ├── if drone.in_transit:      ← PHASE 1: arrivals
    │       │   └── to_enter[zone]++, deliver if goal, output
    │       │
    │       └── if not in_transit and
    │           not moved_in_shift:       ← PHASE 2: collect intents
    │               └── attempted_moves.append()
    │
    ├── for intent in attempted_moves:    ← PHASE 3: validate capacity
    │   └── if zone_free and conn_free:
    │       └── apply movement
    │
    ├── for zone in zones:                ← PHASE 4: update occupations
    │   └── occupation[zone] += to_enter - to_leave
    │
    ├── if output: print
    │
    └── for drone in drones:
        └── reset moved_in_shift
```

**Indentation rule:** each `for` or `if` doubles the indent level.
Phase 3 is at the **same level** as the `for drone` loop (not nested inside it).

### Occupancy projection (capacity check)

When a drone wants to move into a zone, the engine checks:

```
projected = occupation[zone] + to_enter[zone] - to_leave[zone]
```

If `projected < max_drones[zone]` (or the zone is start/end), the move is allowed.
This guarantees no zone ever exceeds its capacity within a single turn.

### Visual representation

Zone names in the simulation output are colorized using ANSI escape codes.
Each zone declares an optional `color=...` in the map file. The `colors.py`
module maps common color names (red, green, blue, cyan, yellow, magenta,
orange, etc.) to their terminal codes. Unknown colors fall back to plain text.

Example:
```
D1-goal D2-corridorA
```
The zone names appear in their declared colors. This helps track which drone
goes where at a glance, especially on complex maps with many zones.

### The building analogy (English)

Imagine your code is a **3-story building**. Each indentation level is a floor.

```
GROUND FLOOR (level 0):
  while turn active:

1ST FLOOR (level 1) ──────────────────────────
  for drone:          ← collect, don't decide
  ├── Phase 1: arrivals (if in_transit)
  └── Phase 2: ask intent (append to list)

  for intent:         ← review the FULL list ─┐  same floor,
  └── Phase 3: validate capacity              │   NOT inside
                                              │   the drone loop
  for zone:
  └── Phase 4: update counters

  for drone:
  └── reset flag

2ND FLOOR (level 2) ──────────────────────────
  if not delivered:
    if in_transit:      ← Phase 1 logic
    if can move:        ← Phase 2 logic

3RD FLOOR (level 3) ──────────────────────────
  attempted_moves.append(...)
```

**The golden rule:** `for drone` and `for intent` are on the **same floor** (same indentation). They run one after another, NOT nested. If Phase 3 were inside `for drone`, each drone would reprocess ALL previous intents — like going back to floor 1 every time you meant to stay on floor 2.


---

## 8. Subject Specifications Summary

### Required Makefile rules

| Rule | Command |
|------|---------|
| install | Install dependencies (uv, pip, pipx, etc.) |
| run | Execute main.py with a map argument |
| debug | Execute main.py with pdb |
| clean | Remove caches (__pycache__, .mypy_cache, *.pyc) |
| lint | flake8 . + mypy . with specific flags |
| lint-strict (optional) | flake8 . + mypy . --strict |

### Movement rules

- normal: 1 turn
- restricted: 2 turns (drone is "in transit" on the connection)
- priority: 1 turn (should be preferred by pathfinding)
- blocked: Cannot be entered

### Occupancy rules

- Default zone capacity: 1 drone at a time
- max_drones=N overrides this
- start zone: all drones can start there (special exception)
- end zone: multiple drones can arrive (special exception)
- Connection capacity: max_link_capacity limits simultaneous crossings

### Map validation rules

- First line: `nb_drones: <positive integer>`
- Exactly one start_hub and one end_hub
- All zone names must be unique
- Zone names cannot contain dashes or spaces
- Connection zones must already exist
- No duplicate connections (a-b = b-a)
- Zone types: normal, blocked, restricted, priority
- Colors: any single-word string
- max_drones and max_link_capacity: positive integers

### Simulation output format

- One line per turn
- Each line lists all drone movements separated by spaces
- Format: `D<ID>-<zone>` or `D<ID>-<connection>` (for in-transit drones)
- Drones that do not move are omitted
- Delivered drones are no longer tracked

---

## 9. Testing & Benchmarks

### How to run a single map

```bash
make run MAP=maps/easy/01_linear_path.txt
# or directly:
python3 main.py maps/easy/01_linear_path.txt
```

### How to count simulation turns

Pipe through `wc -l` — each line is one turn:

```bash
python3 main.py maps/hard/03_ultimate_challenge.txt | wc -l
```

### Run all maps automatically with the benchmark tester

```bash
python3 benchmark.py
```

This runs every map, counts turns, compares against the target, and prints ✅ or ❌ for each one.

### Run all maps manually (one-liners)

```bash
# Easy
for m in maps/easy/*.txt; do
  echo "$(basename $m): $(python3 main.py "$m" | wc -l) turns"
done

# Medium
for m in maps/medium/*.txt; do
  echo "$(basename $m): $(python3 main.py "$m" | wc -l) turns"
done

# Hard
for m in maps/hard/*.txt; do
  echo "$(basename $m): $(python3 main.py "$m" | wc -l) turns"
done

# Challenger (optional)
echo "challenger: $(python3 main.py maps/challenger/01_the_impossible_dream.txt | wc -l) turns"
```

### Performance benchmarks reference

| Category | Map | Drones | Target | Our result |
|----------|-----|--------|--------|------------|
| 🟢 Easy | 01_linear_path | 2 | ≤6 | 4 |
| 🟢 Easy | 02_simple_fork | 4 | ≤8 | 6 |
| 🟢 Easy | 03_basic_capacity | 4 | ≤6 | 4 |
| 🟡 Medium | 01_dead_end_trap | 5 | ≤12 | 8 |
| 🟡 Medium | 02_circular_loop | 6 | ≤15 | 10 |
| 🟡 Medium | 03_priority_puzzle | 5 | ≤12 | 8 |
| 🔴 Hard | 01_maze_nightmare | 8 | ≤30 | 13 |
| 🔴 Hard | 02_capacity_hell | 12 | ≤35 | 16 |
| 🔴 Hard | 03_ultimate_challenge | 15 | ≤45 | 26 |
| ⚫ Challenger | 01_the_impossible_dream | 25 | 45* | **43** |

\* Reference record (optional, does not affect grade)

### What the output tells you

- **One line per turn** — drones that don't move are omitted
- **Format:** `D<ID>-<zone>` for normal moves, `D<ID>-<from>-<to>` for restricted (in-transit)
- **End:** when all drones reach the goal, simulation stops
- **Empty output** means something is wrong (all drones stuck or loop)

---

## 10. Resources

- [Graph theory (Wikipedia)](https://es.wikipedia.org/wiki/Teor%C3%ADa_de_grafos)
- [uv package manager](https://docs.astral.sh/uv/)
- [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code) — terminal colors
- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) — shortest path on weighted graphs

**AI usage:** This project was developed with AI assistance for:
- Code structure and type annotations
- Algorithm design (turn engine + occupancy projection)
- Documentation and README writing
- Debugging and testing against benchmark maps

All AI-generated code was reviewed, understood, and validated by the author before submission.

---