# 🚀 TDitbam Streamer Suite - v3.6.0

## August 7, 2026 Update

- Added an OS-level **Single Instance** guard. Duplicate launches are rejected before GUI, audio, collectors, tray icons, or log handlers initialize.
- Added **Auto Start Optimizer** so the optimization service can start automatically after the app UI is ready.
- A duplicate launch now restores the existing window from the system tray instead of displaying an already-running dialog.
- Added optional native Windows notifications using the project-level `icon.ico`.
- Dashboard now reports separate P-Core and E-Core utilization percentages, plus active Optimizer cores versus total logical cores.
- Dashboard console output is split into All Logs, Bot Live Chat, and Optimizer tabs.
- The v3.6.0 application uses PyInstaller one-folder mode, keeping `StreamerSuite.exe` separate from its support files under `parts/`.
- Inno Setup disk spanning separates installer payloads into 50 MB numbered BIN parts and writes a SHA-256 part manifest.
- Optimizer targets can be selected from running processes in Quick Add; the original text/file workflow remains isolated under Manual Entry.
- Improved UI responsiveness by moving CPU sampling and process discovery off the Tk thread, caching CPU topology, batching log rendering, and limiting retained dashboard logs.
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

**Released on:** Wednesday, June 17, 2026
**Project Owner:** Tditbam

**Development Assistance:** Gemini CLI & OpenAI Codex

**Full Credits:** See [CREDITS.md](./CREDITS.md)
