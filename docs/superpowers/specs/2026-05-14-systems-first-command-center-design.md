# Systems-first Command Center (Web UI) — Design

## Goal
Create a “Systems-first” web Command Center for the HYPER BRAIN v3.0 that is served by the existing FastAPI app and provides:
- Live system + service status
- Gamification HUD (level, XP, coins, streak)
- Events stream
- Quick actions: Morning Briefing, Snapshot, Start Focus, End Focus

Route: `GET /ui`

## Scope
### In scope (MVP)
- Static assets under a new `web/` folder (vanilla HTML/CSS/JS)
- Serve UI at `/ui` and assets under `/ui/assets`
- Add missing API endpoints needed by the UI:
  - `GET /events?limit=10`
  - `GET /gamification/summary`
- Wire existing endpoints to UI buttons:
  - `POST /briefing/generate`
  - `POST /focus/snapshot`
  - `POST /focus/start`
  - `POST /focus/end`
- Maintain an “active session” in the browser (store `session_id` locally) so End Focus is one click

### Out of scope (MVP)
- Authentication / accounts
- Realtime websockets
- Editing vault content from UI (UI is read-only + triggers actions)
- Full achievements engine (MVP shows streaks + a small derived achievements grid)

## Architecture
### Static UI
- Folder: `web/`
  - `index.html`
  - `styles.css`
  - `app.js`
- Served by FastAPI:
  - `GET /ui` -> `web/index.html`
  - `GET /ui/assets/styles.css` -> `web/styles.css`
  - `GET /ui/assets/app.js` -> `web/app.js`

### API
UI reads from:
- `GET /health` (already exists)
- `GET /focus/status` (already exists)
- `GET /events?limit=10` (new)
- `GET /gamification/summary` (new)

UI triggers:
- `POST /briefing/generate` (already exists)
- `POST /focus/snapshot` (already exists)
- `POST /focus/start` (already exists)
- `POST /focus/end` (already exists)

## UI Layout (Systems-first)
### Topbar
- Brand: “HYPER BRAIN”
- Connection pill:
  - Online/offline based on `/health`
  - Version from `/health.version`
- HUD:
  - Level from `/health.level`
  - XP (7d total) and Coins (7d total) from `/gamification/summary`
  - Streak from `/gamification/summary.streaks.current_streak`

### Main Grid
- Constellation Tiles
  - Tiles derived from `/health.services`
  - States:
    - online: `true`
    - offline: `false`
- System JSON Panel
  - Toggle views: `health`, `focus_status`, `gamification_summary`
- Quick Actions + Output
  - Buttons: Generate Briefing, Snapshot Now
  - Output panel shows latest action response JSON + link/path fields when present
- Focus Controls
  - Start Focus form
    - intent (text, required)
    - estimated_minutes (number)
    - project (text)
    - tags (comma-separated)
    - difficulty_preference (auto/easy/medium/hard)
  - End Focus form
    - session_id (pre-filled from local active session)
    - actual_minutes (number, required)
    - mood (1–10)
    - notes (text)
  - Active session display
    - session_id, intent, elapsed estimate
    - “Clear active session” button (local only)
- Achievements Grid (derived)
  - Render 12–16 badges with locked/unlocked states from summary signals (streaks, sessions_7d)
- Events Stream
  - Render latest N events from `/events?limit=N`
  - Show timestamp, type, summary, optional payload preview

## Data Model
### Events
`GET /events?limit=10` returns:
```json
{
  "events": [
    {
      "ts": "2026-05-14T12:34:56Z",
      "type": "focus_start | focus_end | snapshot | briefing | webhook",
      "summary": "Human readable one-liner",
      "payload": { "optional": "object" }
    }
  ]
}
```
Storage approach (MVP):
- In-memory ring buffer inside the FastAPI process (no persistence guarantee)
- Add events when routes are called (`/focus/start`, `/focus/end`, `/focus/snapshot`, `/briefing/generate`, webhook handlers)

### Gamification Summary
`GET /gamification/summary` returns:
```json
{
  "level": 20,
  "coins_total_7d": 0,
  "xp_total_7d": 0,
  "sessions_7d": 0,
  "streaks": {
    "current_streak": 0,
    "longest_streak": 0,
    "recovery_tokens": 1
  },
  "generated_at": "2026-05-14T12:34:56Z"
}
```
Computation approach (MVP):
- Read streaks from existing streak file (`07-Streaks-Achievements/streak-data.json`)
- Compute `coins_total_7d`, `xp_total_7d`, `sessions_7d` by scanning the last 7 days of session notes in `05-Focus-Sessions/` and summing YAML frontmatter fields:
  - `coins_earned`
  - `xp_earned`

## Client Behavior (app.js)
- On load, fetch in parallel:
  - `/health`
  - `/focus/status`
  - `/events?limit=10`
  - `/gamification/summary`
- Store active session id in `localStorage.hyper_brain_active_session_id`
- Start Focus:
  - POST `/focus/start` with body mapping to the server model
  - Save returned `session.id` into localStorage
  - Refresh focus status + events + gamification summary
- End Focus:
  - POST `/focus/end` with body:
    - session_id from localStorage (or input override)
    - actual_minutes, mood, notes
  - Clear localStorage session id on success
  - Refresh focus status + events + gamification summary
- Error handling:
  - Connection pill shows offline if fetch fails
  - Output panel renders error JSON with status code and message
- Accessibility:
  - Reduced motion support in CSS
  - Keyboard focus visible for buttons/inputs

## Security / Safety (MVP)
- No secrets in UI
- Avoid logging request bodies containing notes (server-side)
- `/events` should not return raw large payloads; keep summaries short and payload optional

## Verification
- Manual:
  - Load `http://localhost:8100/ui`
  - Start focus -> confirm session_id stored + focus/status updates
  - End focus -> confirm session note written + streaks update visible in HUD
  - Generate briefing + snapshot -> confirm output panel and events stream updates
- Automated (nice-to-have for MVP):
  - Unit test for `/gamification/summary` parser over a sample session note
  - Unit test for `/events` ring buffer ordering and limit handling

