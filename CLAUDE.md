# CLAUDE.md

Guidance for AI assistants working in this repository.

## Overview

A desktop Pomodoro timer built with Python and **CustomTkinter**. It runs as a
single-window GUI app that minimizes to the system tray, cycles through
work / short break / long break sessions, fires desktop notifications and an
alarm sound, and stores completed work sessions in a local SQLite database for
statistics.

The app is **Windows-targeted**: `notifications.py` uses `winsound`, and the
PyInstaller spec hardcodes Windows hidden imports (`pystray._win32`,
`plyer.platforms.win.notification`). See "Platform notes" before touching
sound or packaging.

## Commands

```bash
pip install -r requirements.txt    # install deps
python generate_assets.py          # generate assets/ (icon.ico, icon.png, alarm.wav) — required before first run
python main.py                     # run the app
```

There is **no test suite, linter, or CI** configured yet (all listed as TODO).
`pip` and `python` invocations are pre-approved in `.claude/settings.local.json`.

Packaging to a Windows executable:
```bash
python -m PyInstaller PomodoroTimer.spec
```

## Architecture

The app separates timer logic, persistence, OS integration, and UI. The
central object is `PomodoroApp(ctk.CTk)` in `app.py`, which wires everything
together and owns all callbacks.

**Core (non-UI) modules:**
- `main.py` — entry point; adds app dir to `sys.path` and launches `PomodoroApp`.
- `app.py` — main window + controller. Loads/saves `settings.json`, builds the
  UI, owns the `TimerEngine` callbacks (`_on_tick`, `_on_complete`), and
  coordinates DB writes, tray, and notifications.
- `timer_engine.py` — pure state machine. States `IDLE / RUNNING / PAUSED`,
  session types `WORK / SHORT_BREAK / LONG_BREAK`. **Has no Tk dependency**: it
  receives `schedule_fn`/`cancel_fn` (Tk's `after`/`after_cancel`) and
  `on_tick`/`on_complete` callbacks via the constructor. Ticks every 200ms and
  computes remaining time from a wall-clock `_target_time` (drift-resistant).
- `models.py` — `Database` class wrapping SQLite (`pomodoro.db`). Single
  `sessions` table; only `session_type='work'` rows are recorded and counted in
  stats. Provides today / week / all-time queries.
- `notifications.py` — `send_toast` (via `plyer`, on a daemon thread) and
  `play_sound` (via `winsound`, with a `Beep` fallback).
- `tray.py` — `TrayManager` runs a `pystray` icon on a **background thread**.
- `generate_assets.py` — one-off script that draws the icon and synthesizes the
  alarm `.wav`. Output goes to `assets/` and is **gitignored**.

**UI modules (`ui/`)** — each is a `ctk.CTkFrame` subclass, presentational only,
driven by `app.py` callbacks:
- `timer_display.py` — clock face, progress bar, session label, pomodoro count.
- `controls.py` — Start / Pause / Resume / Reset / Skip; swaps visible buttons by `TimerState`.
- `task_entry.py` — "what are you working on" text field.
- `settings_panel.py` — duration sliders (stored in **minutes** in the UI,
  **seconds** everywhere else) and theme/sound/always-on-top toggles.
- `stats_panel.py` — today / this week / all-time stats, refreshed from the DB.

### Data flow
`TimerEngine` runs the countdown → calls `_on_tick` (updates display + tray
tooltip) and `_on_complete` (records the work session in SQLite, refreshes
stats, fires notification + sound, then auto-advances to the next session).
Session advance logic: after a WORK session, a LONG_BREAK happens every
`long_break_interval` (4) completed pomodoros, otherwise a SHORT_BREAK.

## Conventions & gotchas

- **Durations are seconds internally, minutes in the UI.** `app.py` settings,
  `settings.json`, and `TimerEngine.durations` all use seconds; only the
  sliders in `settings_panel.py` display/convert minutes (`// 60`, `* 60`).
- **Thread safety:** the tray runs on its own thread. All tray menu callbacks
  marshal back to the GUI thread via `self._root.after(0, ...)` — preserve this
  pattern; never touch Tk widgets directly from the tray thread.
- **Engine stays UI-agnostic.** Keep `timer_engine.py` free of Tk imports;
  inject scheduling and callbacks rather than calling Tk from inside it. This is
  what makes the engine unit-testable (see TODO).
- **Settings persistence:** `settings.json` and `pomodoro.db` are gitignored
  (user-local). `settings.default.json` is the committed reference; loading
  merges saved values over `DEFAULT_SETTINGS` in `app.py`.
- **Generated assets are gitignored** — `assets/` must be regenerated with
  `generate_assets.py` after a fresh clone, or the window icon and alarm sound
  are silently skipped (code degrades gracefully).
- **Errors are swallowed** in settings load/save, notifications, and sound by
  design (best-effort, never crash the timer). Keep new OS-integration code
  similarly defensive.

## Platform notes

`winsound` is Windows-only. To run or test on macOS/Linux, sound playback will
fail (caught silently). Making sound cross-platform is an open TODO — prefer a
fallback library (`playsound`/`pygame`) rather than removing the `winsound`
path.

## Known issues

See `TODO.md` for the tracked list. Notable open bug: skipping the very first
WORK session lands on a LONG break instead of a short one, because
`completed_pomodoros % 4 == 0` is true at 0 (`timer_engine.py:135`).
