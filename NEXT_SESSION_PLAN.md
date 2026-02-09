# 🔮 Phase 2 Plan: Digital Darwinism (Persona Evolution)

**Objective:** Use real-world usage data to optimize the AI Persona library. "Let the users verify the best roles."

## 1. Data Analysis (The "Selection Pressure")
We now have the `persona_density` grid in `get_dashboard_telemetry`.
- **High Utility:** Personas with high usage counts (e.g. "Venture Capitalist" on "Gemini").
- **Low Utility:** Personas with 0 usage over 30 days.

## 2. Implementation Strategy
### A. The "Promotion" Loop
- Create a new script `analyze_personas.py` that queries the database.
- **Trigger:** When admin visits `/dashboard`.
- **Action:** If a specific combo (e.g. `Architect + Claude`) exceeds 50 usages, suggest making it a "Top Stack" preset in the UI.

### B. The "Pruning" Loop
- Identify roles in `ROLES_REFERENCE.md` that have zero DB entries.
- Flag them in the Dashboard as "At Risk" (Red color in grid).
- Allow admin to one-click "Retire" (hide) them to declutter the UI.

### C. The "Mutation" Loop (Advanced)
- If a user frequently overrides a persona's instructions (e.g. "Be more concise"), capture valid feedback.
- Use an LLM to *rewrite* the base system prompt for that persona to include the user's preference automatically.

## 3. Next Session Tasks
1.  [ ] Write `analyze_personas.py`.
2.  [ ] Add "Promote / Retire" buttons to the Dashboard Grid rows.
3.  [ ] Link Dashboard directly to `ROLES_REFERENCE.md` for live updates.
