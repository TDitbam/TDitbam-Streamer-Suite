# Credits — TDitbam Streamer Suite

TDitbam Streamer Suite is developed and maintained by **Tditbam**.

## Development assistance

- **Gemini CLI** — earlier architecture, implementation, packaging, and documentation assistance.
- **OpenAI Codex** — Bot Live Chat session hardening, UI/localization updates, Windows integration, build automation, testing, and v3.6.0 packaging assistance.

AI tools assisted the development process; project direction, testing decisions, assets, and release ownership remain with Tditbam.

## Runtime libraries

| Project | Used for |
|---|---|
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Desktop GUI and widgets |
| [TikTokLive](https://github.com/isaackogan/TikTokLive) | TikTok Live chat collection |
| [edge-tts](https://github.com/rany2/edge-tts) | Microsoft Edge online text-to-speech integration |
| [deep-translator](https://github.com/nidhaloff/deep-translator) | Optional chat translation |
| [pygame-ce](https://github.com/pygame-community/pygame-ce) | Audio mixer and playback |
| [psutil](https://github.com/giampaolo/psutil) | Process discovery, CPU usage, and affinity management |
| [pystray](https://github.com/moses-palmer/pystray) | Windows system tray integration and notifications |
| [Pillow](https://github.com/python-pillow/Pillow) | Icon and image loading |
| [gTTS](https://github.com/pndurette/gTTS) | Google text-to-speech provider and fallback |
| [pytchat](https://github.com/taizan-hokuto/pytchat) | YouTube Live chat collection |

These projects may include additional transitive dependencies. Their respective authors and contributors retain all rights under their own licenses.

## Voice, AI, and streaming services

- **Microsoft Edge online speech service** — Edge voice synthesis through `edge-tts`.
- **Google Translate and Google Text-to-Speech** — translation and gTTS voice features.
- **Google Gemini API** — experimental Gemini API Voice provider.
- **OpenAI API** — experimental OpenAI API Voice provider.
- **YouTube Live, Twitch, and TikTok Live** — supported chat platforms.

The project is not affiliated with or endorsed by Microsoft, Google, OpenAI, YouTube, Twitch, or TikTok. Product names and trademarks belong to their respective owners.

## Build and distribution tools

- [Python](https://www.python.org/) and its standard library, including Tk/Tcl bindings.
- [PyInstaller](https://pyinstaller.org/) — Windows one-folder executable packaging.
- [Inno Setup](https://jrsoftware.org/isinfo.php) — Windows installer and numbered disk-spanning parts.
- [Git](https://git-scm.com/) and [GitHub](https://github.com/) — source control and project distribution.

## Project assets and platform integration

- The main `icon.ico`, application identity, configuration, and release direction are provided by **Tditbam**.
- Windows integration uses operating-system facilities including Task Scheduler, process affinity APIs, system tray behavior, and notifications.

For exact installed package versions, see `requirements.txt`, `requirements-build.txt`, and the generated build manifests.
