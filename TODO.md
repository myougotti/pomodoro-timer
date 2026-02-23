# TODO

## Bugs

- [ ] **Skip from WORK with 0 completed goes to long break** — `_advance_session` checks `completed_pomodoros % 4 == 0`, which is true at start (0 % 4 = 0), so skipping the very first work session lands on a long break instead of a short break. ([timer_engine.py:135](timer_engine.py#L135))
- [ ] **Window title doesn't reflect live countdown** — tray tooltip updates correctly, but the title bar stays "Pomodoro Timer" the whole time.

## Features

- [ ] **Long break interval setting** — currently hardcoded to 4 in `TimerEngine`; expose it as a slider in Settings ([timer_engine.py:27](timer_engine.py#L27), [ui/settings_panel.py](ui/settings_panel.py))
- [ ] **Auto-start next session** — add a toggle so the timer automatically starts the next session without user interaction
- [ ] **Quit confirmation** — prompt before closing when a session is actively running
- [ ] **Task history / autocomplete** — remember previously typed task labels and suggest them in the entry field
- [ ] **Clear history button** — add a "Clear all" or "Clear today" button in the Stats panel
- [ ] **Export stats** — CSV export of session history from the Stats panel

## Polish

- [ ] **Keyboard shortcut for reset** — e.g. `Escape` key to reset when paused
- [ ] **Tray icon color changes with session** — work = red, break = green, long break = blue (matching UI colors)
- [ ] **Cross-platform sound** — `notifications.py` uses `winsound` (Windows-only); add a fallback via `playsound` or `pygame` for macOS/Linux

## Maintenance

- [ ] **Tests** — unit tests for `TimerEngine` state transitions and `Database` queries
- [ ] **CI** — GitHub Actions workflow to run tests on push
