# Pomodoro Timer

A desktop Pomodoro timer built with Python and CustomTkinter. Runs in the system tray, tracks focus sessions, and stores statistics locally.

## Features

- Work / short break / long break session cycling (auto-advances after 4 pomodoros)
- Configurable durations via in-app sliders
- System tray integration — minimizes to tray on close
- Desktop notifications and alarm sound on session complete
- Task label per session
- SQLite-backed session history with today / weekly / all-time stats
- Dark and light theme toggle
- Spacebar shortcut to start/pause

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Generate assets** (icon + alarm sound — required before first run)
```bash
python generate_assets.py
```

**3. Run**
```bash
python main.py
```

## Configuration

Settings are saved locally to `settings.json` (not tracked by git). Copy `settings.default.json` to `settings.json` to start from defaults:

```bash
cp settings.default.json settings.json
```

The app will also create `settings.json` automatically on first run.

## Project Structure

```
├── main.py               Entry point
├── app.py                Main application window and logic
├── timer_engine.py       Timer state machine (IDLE / RUNNING / PAUSED)
├── models.py             SQLite session database
├── notifications.py      Toast notifications and alarm sound
├── tray.py               System tray icon and menu
├── generate_assets.py    Script to generate icon and alarm.wav
├── ui/
│   ├── timer_display.py  Clock face, progress bar, session label
│   ├── controls.py       Start / Pause / Resume / Reset / Skip buttons
│   ├── task_entry.py     Task name input field
│   ├── settings_panel.py Duration sliders and toggles
│   └── stats_panel.py    Today / week / all-time statistics view
├── assets/               Generated at runtime (gitignored)
├── settings.json         Local user config (gitignored)
└── settings.default.json Committed default config reference
```
