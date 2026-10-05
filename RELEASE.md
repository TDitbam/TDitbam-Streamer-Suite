# 🚀 TDitbam Streamer Suite - v3.6.4

## September 30, 2026 Update

- Bot Live Chat now announces a username only when the active speaker changes.
- Consecutive messages from the same user are spoken without repeating their name.
- Returning to a previous user after another person speaks announces that username again.
- Added a real-time **Speaker Change Delay** setting from 0–10 seconds, defaulting to 0.75 seconds.
- The first message and consecutive messages from the same user do not receive the speaker-change pause.
- Stopping Bot Live Chat cancels an active pause immediately and resets speaker tracking.
- Emoji shortcodes such as `:smile:` are removed before text is sent to TTS; emoji-only messages are skipped entirely.

- Redesigned the complete desktop GUI around one shared design system for consistent colors, typography, cards, controls, and spacing.
- Added active-page navigation styling and responsive layouts across Dashboard, Bot Live Chat, Optimizer, Cleanup, Windows Tools, and Settings.
- Reordered common workflows so primary actions appear before managed lists and results, reducing visual clutter and unnecessary scrolling.
- Removed startup/tray white flashes by keeping the native window transparent until its dark first frame is fully rendered.
- Restoring from the taskbar or system tray now reuses the visible widget tree instead of blanking and repainting the entire UI on every activation.
- Lazily constructs secondary pages, reducing measured GUI startup from about 893ms to 188–245ms.
- Dashboard process text now refreshes atomically, while Quick Add skips unchanged process-list redraws and preserves selection.
- Added an OS-level **Single Instance** guard. Duplicate launches are rejected before GUI, audio, collectors, tray icons, or log handlers initialize.
- Added **Auto Start Optimizer** so the optimization service can start automatically after the app UI is ready.
- Fixed Optimizer policy isolation so only explicitly managed programs/directories receive affinity or priority changes; Windows shell processes such as Explorer and DWM are left untouched.
- When `optimizer_config.ini` is missing, Optimizer downloads and validates the ready-to-use profile from GitHub, with embedded defaults available when offline.
- Added a confirmed Reset Config action that reloads the same GitHub profile, falls back safely when offline, and refreshes the active UI immediately.
- Separated the two startup settings: **Start Minimized** no longer rewrites Task Scheduler, and the startup task is updated only when **Run on Windows Startup** actually changes.
- Added 97 curated popular-game executable presets spanning major Steam, Epic, Riot, Battle.net, and online titles.
- Popular presets are stored separately from custom targets, keeping the Optimizer UI compact while user-defined policies continue to override presets.
- Added a one-time, non-destructive config migration and atomic `optimizer_config.ini` writes.
- Added a background update checker that reads stable semantic versions from the repository's public GitHub tags.
- Settings now shows the current app version, latest GitHub tag, update status, an Auto Check switch, and explicit Check/Open Release actions.
- Update checks never download or install files automatically.
- A duplicate launch now restores the existing window from the system tray instead of displaying an already-running dialog.
- Added optional native Windows notifications using the project-level `icon.ico`.
- Dashboard now has separate **Performance** and **Logs** tabs, keeping operational logs available without crowding the primary view.
- Performance reports P-Core/E-Core, RAM, GPU, and the top programs by CPU/RAM/GPU usage in real time.
- The Logs area is further split into All Logs, Bot Live Chat, and Optimizer tabs.
- Redesigned WinGet Manager with a compact action layout, command status, Enter shortcuts, and duplicate-command protection.
- The v3.6.4 application uses PyInstaller one-folder mode, keeping `StreamerSuite.exe` separate from its support files under `parts/`.
- Inno Setup produces one versioned Setup EXE and a matching SHA-256 checksum file; no BIN parts are required.
- The release script now relaunches itself through the Windows UAC prompt when Administrator permission is required and preserves the `-SkipInstaller` option.
- Optimizer targets can be selected from running processes in Quick Add; the original text/file workflow remains isolated under Manual Entry.
- Improved UI responsiveness by moving CPU/RAM/GPU sampling and process discovery off the Tk thread, caching CPU topology, and batching UI/log rendering.
- Quick Add now filters running processes while typing and refreshes its process cache automatically every five seconds.

### Bot Live Chat

- Renamed Chat-TTS to **Bot Live Chat** across the UI and documentation.
- Added strict per-session cancellation, isolated message/audio queues, bounded worker shutdown, and exclusive audio-player ownership.
- Stale network collectors can no longer inject messages or audio into a newly started session.
- Session numbers now count actual starts sequentially.

### Voice Providers

- Added selectable providers: **Edge TTS**, **gTTS**, **Gemini API Voice**, and **OpenAI API Voice**.
- Gemini supports selectable TTS models, voices, API key, and natural-language voice style.
- OpenAI supports selectable speech models, built-in voices, speed, API key, and voice instructions where supported.
- Gemini and OpenAI integrations are marked **Experimental**.
- API keys may be supplied through the UI or the `GEMINI_API_KEY` / `OPENAI_API_KEY` environment variables.

### UI and Localization

- Added immediate Thai / English (US) UI switching with persistent language preference.
- Voice settings now show only fields belonging to the selected provider.
- Fixed duplicate paste when pressing `Ctrl+V`.

---

## 🌟 What's New
### 🧰 Windows Tools Tab
We've added a dedicated **Windows Tools** tab to the primary sidebar. This section centralizes system-level utilities for easier access.

### ⏰ Advanced Auto-Shutdown Scheduler
Never worry about leaving your PC on. You can now schedule a daily shutdown directly from the app.
- **Precision:** Uses native **Windows Task Scheduler**.
- **Reliability:** The task persists even if the application is closed.
- **Safety:** Includes a 60-second warning before shutdown.

### ⚙️ E-CORE Support for Managed Directories
In the Optimizer, you can now set specific directories to run with **E-CORE** priority. This is perfect for managing background tasks or folders with low-priority processes.

---

## 🛠️ Bug Fixes & Stability
### 🎙️ Bot Live Chat Robustness
Fixed the frequent "Voice Model Error".
- **Retry Mechanism:** Automatically retries up to 3 times with exponential backoff.
- **Stable Fallback:** Seamlessly switches to **gTTS (Google TTS)** if Edge-TTS remains unavailable.
- **Thread-Safe:** Fallback generation now runs in a separate thread to prevent UI freezing.

### 🧩 Module Import & Path Fixes
Resolved the `ModuleNotFoundError` by implementing a robust **Auto-Path Correction** system. The application now correctly identifies its root directory regardless of how or where it is launched.

---

## 📂 UI/UX Enhancements
- **Restructured Navigation:** Promoted Windows Tools to a top-level menu item for better visibility.
- **Contextual Information:** Added info boxes across new features to guide users on their functionality.

---

## 📦 Deployment & Installation
- **Inno Setup (v3.4.0):** Updated installer script to handle new file structures and automatically create essential directories (`logs`, `msg_queue`, `temp_audio`).
- **Admin Privilege Handling:** Refined elevation requests to ensure system-level tools (Task Scheduler/Optimizer) function correctly.

---

**Release draft prepared on:** September 30, 2026
**Project Owner:** Tditbam

**Development Assistance:** Gemini CLI & OpenAI Codex

**Full Credits:** See [CREDITS.md](./CREDITS.md)
