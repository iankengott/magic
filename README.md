# Vector-Regnum (Magic System Design Notes)

Vector-Regnum is a structured magic framework where spells are *built* like programs instead of selected from a fixed list. Mana is shaped through sigils placed in a clockwise spiral, and each sigil acts as an instruction in an execution chain.

---

## 1) Core Identity

- **Name:** Vector-Regnum ("Realm of Direction")
- **Genre fit:** Systemic, logic-driven spell construction
- **Design pillar:** Magic = ritual + math + architecture
- **Risk model:** Miscompiled spells can mutate into unstable outcomes

### High-level premise
- Every spell starts from a magic circle.
- Sigils are placed in sequence and execute in order.
- Incomplete/invalid logic does not safely fail; it can produce random side effects and temporarily lock mana-channeling.

---

## 2) Current Design Problems

1. Powerful spells are too easy to make.
2. It is unclear which effects should passively drain mana.
3. Ongoing spells need a clearer drain-over-time formula.

---

## 3) Proposed Solutions

### Problem 1: Power creep / easy high-tier spells
1. Make compiler workload increase mana requirements so high complexity has meaningful energy cost.
2. Require manual construction steps for top-tier spells (reduce "free automation" at high power).
3. Reduce sigil user-friendliness (more sigils / more explicit construction).
4. Assign different mana weights to different sigils.

### Problem 2: Passive drain tracking
- Track spell-created entities/objects.
- Calculate alive time + delta since last tick.
- Charge caster continuously while entity/effect remains active.

### Problem 3: Drain scaling
- Use a percentage of the spell's base cast cost as recurring upkeep.

---

## 4) System Rules (Actualization)

### Global rule
- Every spell must have a termination point.
- If no valid termination exists, miscompile rules apply.

### Vision / targeting / interaction rules
1. **Visibility** — `Visible(Source, Target)`
   - Raycast-style clear-path check (mana/light path).
   - Blocked by material or mana shield.
2. **Targeting** — `Select(n)` / `Push(Active_Stack)`
   - Assigns UID into memory.
   - Target can remain known after line-of-sight break if memory persists.
3. **Collision** — `Collision(A, B)`
   - Hard-physics contact detection.
4. **Rendering** — `Render(Effect)`
   - Visual-only layer; can exist without collision/targeting.

---

## 5) Atomic Sigil Language

### Entity primitives
- `Manifest` — create null construct
- `Bind(mat)` — apply material/state
- `Scale(s)` — scale target dimensions

### Spatial primitives
- `Point(x,y,z)` — fixed coordinate
- `Vector(v)` — direction + magnitude
- `Origin` — center of active circle
- `GetPos(target)` — target position

### Sensors
- `Collision(A,B)`
- `Proximity(A,B)`

### Logic & math
- `If / Else`
- `Compare(=,<,>)`
- `Sum / Diff`

### Time
- `Tick`
- `Delay(t)`
- `Duration(d)`

### Dynamics
- `Impulse(v)`
- `Accel(v)`
- `Damping(f)`

### Perception
- `Visible(A,B)`
- `Render(Effect)`

### Memory
- `Push / Pop`
- `Iterator`

---

## 6) Redstone Integration Concepts

### Redstone Logic (decision maker)
- Uses `Compare + If/Else` on memory stack values.
- Enables branching and logic gates (AND/XOR-style behavior).

### Remote Activation (wireless trigger)
- Primary circle targets secondary origin via `Point`.
- Secondary circle listens via `Collision` at its origin.

### Multi-Threading (parallel behavior)
- `Tick` provides shared clock.
- `Iterator` cycles sub-origins each tick for effectively parallel subroutines.

### Data Bridge (thread hand-off)
- One thread `Push`es UID/coordinates.
- Another thread `Pop`s and continues logic (e.g., target lock persistence).

---

## 7) Mana Cost Model (Draft)

### Categories
- **Logic & Flow:** low-per-tick logical switching cost
- **Perception:** cost scales with range (inverse-square-inspired scaling)
- **Physical Work:** tied to kinetic/work-like factors (mass, force, time)
- **Creation:** base + material rarity/complexity
- **Memory:** per-write cost for stable data states

### Example scaling ideas
- `If`, `Compare`, `Branch`: small per-tick cost
- `Loop`, `Tick`: higher cyclic cost
- `Visible/Scan`: range-sensitive cost
- `Impulse`: mass × delta-v style cost
- `Accel/Duration`: continuous force-over-time drain
- `Push/Pop/Variable`: per operation/write cost

---

## 8) Progression & World Integration

- Start with basic sigils; unlock atomic sigils over time.
- Mages should be able to choose/manage mana streams.
- Mana is not freely regenerative (except rare/advanced cases).
- Casters expand capacity via crystals/ritual/external reservoirs.
- Distance from sources weakens draw strength.
- Elemental compatibility gates source usage.

---

## 9) Casting Mediums

- **World-etched circles:** strongest, expensive, permanent-ish infrastructure.
- **Scroll casting:** fast, disposable, consumed on use.
- **Tome preparation:** high upfront prep, repeatable casts, lower peak ceiling.

Medium rarity + labor investment determine potential spell level.

---

## 10) Power Tiers

### Standard casters
- Limited mana, strict element constraints, high risk from bad construction.

### Archmages
- Natural mana generation (slow), broader element access, extreme spell scale.
- Achieved through dangerous high-tier progression/trial.

---

## 11) Completed Spells

1. God is Dead
2. Pocket Dimension
3. AoE Push

---

## 12) Spell Ideas Backlog

- Hither (bring selected item to caster)
- Ugly (social aversion aura around target object)
- Plain Sight (object invisibility)
- Invisibility (caster invisibility)
- Curse (long-lasting random push effect)
- AoE Gravity (excluding caster)
- Magic Missile
- Raise Undead
- Force-Field
- Create Fire
- Smelt
- Craft
- Thunder Strike
- Gate (long-lasting teleportation AoE)
- Time Stop
- Mass Heal
- Mending
- Fireball
- Summon (mark entity/type and choose what/how many to summon)

---

## 13) Example Logic Chain: "Smart Arrow"

1. `Scan` entities in radius.
2. `Visible` filter for non-obscured targets.
3. `Select` nearest target and store variable.
4. Loop:
   - `GetPos(target)`
   - `Accel(vector_to_target)`
   - `Collision(self,target)`
   - `If(True)` => execute explosion subspell

---

## 14) Condensed Description

Vector-Regnum is a dangerous, expressive spell-language where identity, materials, and formal structure determine magical outcomes. It rewards planning, logic, and mastery; it punishes careless casting with unstable, often costly miscompilation.
