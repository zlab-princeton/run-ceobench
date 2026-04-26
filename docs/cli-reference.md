# NovaMind CLI Reference

## `novamind-operation`

The primary CLI for interacting with the NovaMind SaaS simulator.

### Session Management

#### `novamind-operation new-session`
Create a new simulation session.

```bash
novamind-operation new-session [--days 365] [--seed 42] [--cash 1000000]
```

**Options:**
- `--days`: Total simulation days (default: 365)
- `--seed`: Random seed for reproducibility (default: 42)
- `--cash`: Initial cash balance (default: 1,000,000)

**Returns:** JSON with `session_id`, `seed`, `total_days`, `initial_cash`, `workspace` path.

#### `novamind-operation list-sessions`
List all existing sessions.

```bash
novamind-operation list-sessions
```

#### `novamind-operation status [--session ID]`
Get the current status of a session.

```bash
novamind-operation status
novamind-operation status --session abc123def456
```

#### `novamind-operation stop [--session ID]`
Stop the simulation server for a session.

```bash
novamind-operation stop
```

---

### Simulation Control

#### `novamind-operation next-week <12 cash forecasts> [--session ID]`
Advance the simulation by one week (7 days). **Requires 12 cash forecasts** as positional arguments — for each of FOUR horizons (+7d, +28d, +84d, +182d ~ 6 months) submit a point estimate plus 95% CI lower and upper bounds.

```bash
novamind-operation next-week \
    1050000 1000000 1100000 \
    1200000 1050000 1400000 \
    1800000 1400000 2300000 \
    3000000 2000000 4500000
```

**Arguments (in order):**
- `cash_1wk_point`, `cash_1wk_lower`, `cash_1wk_upper` — +7-day forecast (point + 95% CI)
- `cash_4wk_point`, `cash_4wk_lower`, `cash_4wk_upper` — +28-day forecast
- `cash_12wk_point`, `cash_12wk_lower`, `cash_12wk_upper` — +84-day forecast
- `cash_26wk_point`, `cash_26wk_lower`, `cash_26wk_upper` — +182-day (~6 month) forecast

**Constraint per horizon:** `lower <= point <= upper`. The server returns 400 if violated or if any field is missing/non-numeric.

Forecasts are stored in the `predictions` table at submission time. Scored on:
- **Point percent error:** `(point - actual) / actual` per horizon
- **95% CI coverage:** does actual cash fall inside `[lower, upper]`?
- **Sharpness:** interval width relative to actual

The agent is evaluated on prediction accuracy + calibration at each horizon in addition to realized cash.

**Output:** The weekly dashboard showing cash, subscribers, MRR, this week's metrics, current config, product quality, and inbox notifications.

---

### Code Execution

#### `novamind-operation python <script.py> [--session ID]`
Execute a Python script in the simulation environment with `novamind_api` available.

```bash
novamind-operation python my_strategy.py
```

The script runs with `novamind_api` importable. Example script:
```python
import novamind_api as nm

# Set prices
nm.pricing.set_prices(A=25, B=69, C=179)

# Check current day
print(f"Day: {nm.vars.current_day}")

# Query data
result = nm.query("SELECT COUNT(*) as n FROM subscriptions WHERE status='active'")
print(f"Active subscribers: {result['rows'][0]['n']}")
```

#### `novamind-operation python-c "<code>" [--session ID]`
Execute inline Python code.

```bash
novamind-operation python-c "import novamind_api as nm; nm.pricing.set_prices(A=29.99)"
```

---

### Direct Tool Calls

#### `novamind-operation call <tool_name> [--args '{...}'] [--session ID]`
Call a simulator tool directly with JSON arguments.

```bash
novamind-operation call set_prices --args '{"A": 29.99, "B": 69.99, "C": 179.99}'
novamind-operation call get_cost_info
novamind-operation call start_research_project --args '{"tier": "T3"}'
```

See `docs/tools-reference.md` for all available tools and their parameters.

---

### Database Queries

#### `novamind-operation query "<SQL>" [--session ID]`
Execute a read-only SQL query against the simulation database.

```bash
novamind-operation query "SELECT * FROM subscriptions WHERE status='active' LIMIT 10"
novamind-operation query "SELECT group_id, COUNT(*) as n FROM subscriptions WHERE status='active' GROUP BY group_id"
```

**Restrictions:**
- Read-only (SELECT only) — no INSERT/UPDATE/DELETE
- Schema introspection blocked (no PRAGMA, sqlite_master)
- Some internal tables and columns are hidden
- Results capped at 5,000 rows

See `docs/tables-reference.md` for available tables and columns.

---

### History

#### `novamind-operation history [--tail N] [--session ID]`
View the action history for a session.

```bash
novamind-operation history
novamind-operation history --tail 100
```

Shows recent tool calls, queries, next-day advancements, and Python executions.

---

### Session ID

All commands accept `--session <id>` to target a specific session. If omitted, the most recently created session is used.

```bash
# These are equivalent (both use latest session):
novamind-operation next-day
novamind-operation next-day --session <latest-id>

# Target a specific session:
novamind-operation next-day --session abc123def456
```
