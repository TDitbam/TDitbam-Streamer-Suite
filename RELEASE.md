# 🚀 TDitbam Streamer Suite - v3.4.0

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
### 🎙️ Chat-TTS Robustness
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
**Author:** Tditbam & Gemini CLI
