# ฐานความรู้ฉบับรวม: TDitbam Streamer Suite v3.6.2

เอกสารนี้เรียบเรียงจากบทสนทนา การแก้โค้ด การทดสอบ การ Build และการเตรียม GitHub Release ของโปรเจกต์ TDitbam Streamer Suite จนถึงวันที่ 23 สิงหาคม 2026 เพื่อใช้เป็นแหล่งข้อมูลใน Google NotebookLM

> หมายเหตุ: เอกสารนี้เป็นการรวบรวมเนื้อหาแบบมีโครงสร้าง ไม่ใช่ Transcript คำต่อคำ แต่ครอบคลุมความต้องการ การตัดสินใจ การแก้บัค สถานะไฟล์ และงานค้างทั้งหมดที่คุยกัน

---

## 1. ข้อมูลโครงการ

- ชื่อโครงการ: **TDitbam Streamer Suite**
- ชื่อระบบอ่านแชทปัจจุบัน: **Bot Live Chat**
- เวอร์ชันที่กำลังเตรียม: **3.6.2**
- เจ้าของโครงการและผู้กำหนดทิศทาง: **Tditbam**
- Repository: https://github.com/TDitbam/TDitbam-Streamer-Suite
- Workspace บนเครื่องพัฒนา: `D:\code\TDitbam-Streamer-Suite`
- ระบบปฏิบัติการเป้าหมายหลัก: Windows
- ภาษา UI: ไทย และ English (US)
- GUI framework: CustomTkinter/Tkinter
- ภาษาโปรแกรมหลัก: Python
- ระบบ Build: PyInstaller แบบ one-folder
- ระบบ Installer: Inno Setup 6
- ไอคอนหลัก: `D:\code\TDitbam-Streamer-Suite\icon.ico`

### วิสัยทัศน์ของโปรเจกต์

โปรแกรมนี้ตั้งใจเป็นเครื่องมือ All-in-One สำหรับสตรีมเมอร์ โดยรวมระบบอ่านแชทสดด้วยเสียง ระบบปรับ CPU ตาม P-Core/E-Core การติดตาม CPU/RAM/GPU ระบบล้างไฟล์ ระบบจัดการโปรแกรม Windows และเครื่องมือช่วยดูแลเครื่องไว้ใน UI เดียวที่ไม่รกและใช้งานง่าย

---

## 2. ความต้องการทั้งหมดที่พูดคุยกัน

### Bot Live Chat และ TTS

- แก้ `Ctrl + V` วางข้อความซ้ำ
- แก้ Start/Stop Bot Live Chat แล้วเสียง Session เก่ากลับมาเล่นซ้อน
- ทำให้ Stop ล้าง Session, queue, audio และ worker เก่าอย่างเด็ดขาด
- ปรับเลข Session ให้นับเฉพาะการ Start จริงเป็น 1, 2, 3 ตามลำดับ
- เปลี่ยนชื่อ Chat-TTS เป็น Bot Live Chat
- รองรับ YouTube Live, Twitch และ TikTok Live
- รองรับ Edge TTS, gTTS, Gemini API Voice และ OpenAI API Voice
- Gemini และ OpenAI API Voice ต้องระบุว่าอยู่ในขั้นทดลอง
- รองรับ API key จาก UI และ environment variables
- API key ใน UI ถูกบันทึกเป็นข้อความธรรมดาใน `config.ini` จึงไม่ใช่ระบบเก็บ Secret แบบเข้ารหัส

### ภาษาและ UI

- เพิ่ม UI ภาษาไทยและ English (US)
- ปรับ GUI ทั้งหมดให้ไม่รก
- ลด UI อืดและการกระพริบสีขาวตอน Refresh/เปลี่ยนหน้า
- แยก Console Log เป็น Tabs
- Dashboard ต้องเน้น RAM, GPU, P-Core/E-Core และโปรแกรมที่ใช้ทรัพยากรสูงสุด
- Logs ยังอยู่ใน Dashboard แต่ต้องแยก Tab ไม่ให้เบียดข้อมูลสำคัญ
- ปรับ Windows System Tools และ WinGet Manager UI
- Quick Add ต้องค้นหาโปรเซสด้วยการพิมพ์ได้ทันที
- แยก Quick Add และ Manual Entry

### Windows และการเริ่มโปรแกรม

- ป้องกันการเปิดโปรแกรมซ้ำด้วย Single Instance
- ถ้าเปิดซ้ำให้เรียกหน้าต่างเดิมจาก System Tray แทนกล่องข้อความ
- เพิ่ม Start Minimized to System Tray
- เพิ่ม Run on Windows Startup ผ่าน Task Scheduler
- เพิ่ม Auto Start Optimizer หลังเปิดโปรแกรม
- เพิ่ม Windows Notifications โดยใช้ `icon.ico`
- `build_release.ps1` ต้องขอสิทธิ์ Administrator อัตโนมัติ

### Optimizer และระบบเครื่อง

- แสดงเปอร์เซ็นต์ P-Core และ E-Core
- แสดงจำนวนคอร์ทั้งหมดและจำนวนคอร์ที่ Optimizer ใช้งานจริง
- เพิ่มโปรแกรมจากรายการโปรเซสที่กำลังรันได้
- เพิ่ม preset เกมยอดนิยมจำนวนมาก
- ห้าม Optimizer ไปปรับโปรเซส Windows ที่ผู้ใช้ไม่ได้กำหนด
- แผนในอนาคต: เพิ่มระบบสั่งเปิดเครื่องมือจาก `christitustech/winutil`
- มีการพูดถึงการให้ GPU ช่วยทำงาน แต่ Tk/CustomTkinter ไม่มี hardware-rendering backend สำหรับเร่ง widget construction โดยตรง ปัจจุบัน Windows DWM ทำ GPU compositing ให้อยู่แล้ว งานที่ทำจริงคือย้าย monitoring และ process scan ออกจาก UI thread

### Build, Installer และ GitHub

- เปลี่ยนเวอร์ชันจาก 3.6.0 เป็น 3.6.1 และปัจจุบันเป็น 3.6.2
- Installer ต้องเป็น Setup EXE ไฟล์เดียว
- ไม่มีไฟล์ `.bin` หรือ Disk Spanning Part
- ตัว App แบบ one-folder ยังมี `StreamerSuite.exe` และโฟลเดอร์ dependency ชื่อ `parts`
- สร้าง SHA-256 สำหรับตรวจสอบ Setup
- อัปเดต `.md` และ `.txt`
- เตรียม GitHub Draft Release ภาษาไทย

---

## 3. ประวัติการแก้ไขตามรุ่น

### รุ่น 3.6.0

เน้นแก้บัค Bot Live Chat, ปรับ UI, แยก Log, เพิ่ม Quick Add, Auto Start, Windows Notification, Single Instance, TTS providers และระบบ Installer

ข้อความประชาสัมพันธ์ที่เคยจัดเตรียม:

> อัพเดท 3.6.0 tditbam-streamer-suite แล้วนะครับ  
> อัพเดทน้อยแต่เน้น แก้บัคและใช้ง่ายขึ้น  
> แก้เสียง Bot Live Chat เล่นซ้อน  
> ปรับ UI ให้ลื่นและไม่รก  
> แยก Console Log และ P-Core/E-Core ชัดเจน  
> เพิ่ม Quick Add พร้อมระบบค้นหา  
> เพิ่ม Auto Start, Windows Notification และป้องกันเปิดโปรแกรมซ้ำ  
> รองรับ TTS และ API Voice มากขึ้น  
> อัปเดต Installer แบบแยก Part ดาวน์โหลดและจัดการง่ายขึ้น

ลิงก์รุ่น 3.6.0: https://github.com/TDitbam/TDitbam-Streamer-Suite/releases/tag/v3.6.0

### รุ่น 3.6.1

- ปรับ GUI ทั้งโปรแกรมด้วย Design System กลาง
- ลด White Flash ตอนเปิดและ Restore หน้าต่าง
- Lazy-load หน้ารองเพื่อลดเวลาเริ่ม GUI
- แยก Performance และ Logs ใน Dashboard
- ปรับ WinGet Manager
- เพิ่ม Quick Add Search แบบเรียลไทม์
- ปรับ `build_release.ps1` ให้ขอสิทธิ์ Administrator
- Installer เป็นไฟล์เดียว ไม่มี BIN Part

### รุ่น 3.6.2

- แก้ Optimizer ไปแตะ Explorer/DWM/RuntimeBroker และโปรเซส Windows อื่น
- แยก Start Minimized ออกจาก Run on Windows Startup
- เพิ่ม preset เกมยอดนิยม 97 ชื่อโปรเซส
- เพิ่ม config migration ที่ไม่ทับค่าผู้ใช้
- บันทึก optimizer config แบบ atomic
- เพิ่มเลขเวอร์ชันในคุณสมบัติ EXE
- เพิ่มระบบ Auto Check Update ผ่าน GitHub Tags API
- เพิ่ม Version & Updates ในหน้า Settings
- สร้าง EXE, Setup, SHA-256 และ GitHub Draft ภาษาไทย

---

## 4. Bot Live Chat Session Lifecycle

### อาการเดิม

เมื่อกด Stop แล้ว Start ใหม่ worker หรือเสียงจาก Session เก่ายังไม่จบ จึงสามารถกลับมาใส่ข้อความหรือเล่นไฟล์เสียงใน Session ใหม่ได้ ทำให้เสียงเก่าและเสียงใหม่เล่นซ้อนกัน

ตัวอย่าง Log ที่เคยพบ:

```text
Starting Engine Session 3...
Player started (Session: 3)
Generator started (Session: 3)
Stopping Chat-TTS System...
Session invalidated; 1 network worker(s) still shutting down in isolation.
Engine session stopped and cleared.

Starting Engine Session 5...
Player started (Session: 5)
Generator started (Session: 5)
```

ผู้ใช้สับสนว่าทำไมเลข Session กระโดดจาก 3 ไป 5 จึงปรับให้เลขเพิ่มเฉพาะการ Start จริง

### วิธีแก้

- แต่ละ Start มี Session ID ของตัวเอง
- แต่ละ Session มี cancellation event, message queue และ audio queue แยกกัน
- Worker ตรวจ Session ID และ cancellation state ก่อนส่งข้อความหรือเสียง
- Audio player มีเจ้าของได้เพียง Session เดียว
- Stop จะยกเลิก worker, หยุดเสียง, ล้าง queue และล้างไฟล์ชั่วคราว
- Worker เก่าที่ติด Network I/O จะถูกกักแยก ไม่สามารถย้อนกลับมาป้อนข้อมูลให้ Session ใหม่
- การเริ่มใหม่ไม่รอให้ worker เครือข่ายเก่าที่ค้างปิดตัวแบบไม่มีกำหนด

---

## 5. บัค Ctrl + V วางข้อความซ้ำ

### สาเหตุ

Tk widget class binding จัดการ Ctrl+V อยู่แล้ว แต่ Global shortcut handler ของโปรแกรมสร้าง `<<Paste>>` เพิ่มอีกครั้ง ทำให้ข้อความถูกวางสองรอบ

### วิธีแก้

- ถ้า physical key และ keysym เป็น `V` ปกติ ให้ Tk จัดการเอง
- สร้าง `<<Paste>>` เองเฉพาะกรณี Keyboard Layout ทำให้ physical V key มี keysym ต่างออกไป
- ทดสอบแล้วไม่วางซ้ำ

---

## 6. Single Instance และ System Tray

- ใช้ Windows Mutex ชื่อ `Local\TDitbamStreamerSuite.SingleInstance`
- ใช้ Windows Event ชื่อ `Local\TDitbamStreamerSuite.ActivateWindow`
- Instance แรกถือ Mutex ตลอดอายุโปรแกรม
- Instance ที่เปิดซ้ำจะส่ง Activation Event แล้วปิดทันที
- Instance หลัก Poll Event และเรียกหน้าต่างเดิมจาก System Tray
- Duplicate process ถูกหยุดก่อนสร้าง GUI, audio engine, collectors, tray icons และ log handlers

---

## 7. Startup & Background

หน้า Settings มีตัวเลือก:

1. **Start Minimized to System Tray**  
   เปิดโปรแกรมแบบเงียบและเก็บไว้ใน Tray

2. **Run on Windows Startup via Task Scheduler**  
   เปิดโปรแกรมอัตโนมัติหลัง Sign in Windows โดย Task ชื่อ `TDitbam_Startup`

3. **Auto Start Optimizer after app launch**  
   เริ่ม Optimizer หลัง UI พร้อม

4. **Windows Notifications**  
   เปิด/ปิดการแจ้งเตือนผ่าน System Tray

5. **Automatically check for updates**  
   ตรวจ GitHub Tag หนึ่งครั้งใน Background หลังเปิดโปรแกรม

### บัคและการแก้ Startup

- เดิม App เรียก Sync Startup Task ทุกครั้งที่เปิด
- เดิม Save Settings จะลบและสร้าง Task ใหม่แม้เปลี่ยนเพียง Start Minimized
- ปัจจุบัน Start Minimized ไม่แตะ Task Scheduler
- Task Scheduler เปลี่ยนเฉพาะเมื่อ `run_on_startup` เปลี่ยนจริง
- ตอนเปิด Startup ใช้ `/create /f` อัปเดต Task เดิมโดยไม่ลบทิ้งก่อน
- ถ้าสร้าง Task ใหม่ล้มเหลว Task เดิมยังอยู่
- ตอนปิด Startup ระบบตรวจสอบว่าการลบสำเร็จหรือ Task ไม่มีอยู่แล้ว

---

## 8. บัคคล้าย Windows + D ทุกครั้งที่กดเมาส์

### ผลตรวจ

- ไม่พบโค้ดที่ส่งปุ่ม `Windows + D`
- ไม่พบ `SendInput`, `keybd_event`, pyautogui, keyboard hotkey หรือ Show Desktop command
- Mouse binding จาก CustomTkinter มีเพียง `focus_set()` ภายในแอป ไม่ได้ส่งปุ่มให้ Windows

### จุดผิดปกติที่พบ

Policy Engine เดิมคืนค่า `NORMAL` ให้ทุกโปรเซสที่ไม่ได้อยู่ในรายการ ส่งผลให้ Optimizer ไปเรียก CPU affinity และ priority กับโปรเซสทั้งหมด เช่น:

- `explorer.exe`
- `dwm.exe`
- `SearchHost.exe`
- `StartMenuExperienceHost.exe`
- `ShellExperienceHost.exe`
- `RuntimeBroker.exe`

### วิธีแก้

- ถ้าโปรเซสไม่ตรงกับ Custom Target, Managed Directory หรือ Popular Game preset ให้คืน `None`
- Optimizer ข้ามโปรเซสนั้นโดยไม่สร้าง Registry State และไม่เรียก Enforcer
- `P-CORE`, `E-CORE` และ `NORMAL` ยังทำงานได้สำหรับรายการที่ผู้ใช้กำหนดอย่างชัดเจน
- Windows shell processes ไม่ถูกแตะโดยอัตโนมัติอีกต่อไป

---

## 9. Optimizer และ P-Core/E-Core

### Policy ที่รองรับ

- `P-CORE`: ใช้ Performance cores และ High priority
- `E-CORE`: ใช้ Efficiency cores และ Below Normal priority
- `NORMAL`: ใช้ logical cores ทั้งหมดและ Normal priority
- Unmanaged: ไม่เปลี่ยน affinity หรือ priority

### Dashboard

- แสดง P-Core Usage
- แสดง E-Core Usage
- แสดงจำนวนคอร์ทั้งหมด
- แสดงจำนวนคอร์ที่ Optimizer กำลังใช้จริง
- แสดง RAM Usage
- แสดง GPU Usage
- แสดงโปรแกรมที่ใช้ CPU/RAM/GPU สูงสุด
- Windows GPU Engine counters ไม่ผูกกับยี่ห้อ GPU

### UI Performance

- CPU/RAM/GPU sampling ทำงานนอก Tk main thread
- Cache CPU topology
- Batch log rendering
- Quick Add ข้ามการ redraw เมื่อรายชื่อโปรเซสไม่เปลี่ยน
- Process list refresh ทุก 5 วินาที
- Dashboard ใช้ atomic text replacement ไม่ล้างกล่องจนว่างก่อนวาดใหม่

---

## 10. Popular Game Presets

- จำนวนชื่อโปรเซส: **97**
- Preset version: `1`
- Policy เริ่มต้น: `P-CORE`
- เก็บใน Section `[PopularGames]`
- โปรแกรมที่ผู้ใช้เพิ่มเองเก็บใน `[Targets]`
- Custom Target มีสิทธิ์สูงกว่า PopularGames
- Migration ทำครั้งเดียวผ่าน `[Presets] popular_games_version`
- ถ้าผู้ใช้ลบ preset หลัง migration จะไม่ถูกเพิ่มกลับทุกครั้งที่เปิดโปรแกรม
- หลีกเลี่ยง launcher, anti-cheat, crash reporter และ shared runtime เช่น `javaw.exe`

### รายชื่อโปรเซสทั้ง 97 รายการ

#### Competitive / Shooter / Battle Royale / MOBA

`cs2.exe`, `dota2.exe`, `VALORANT-Win64-Shipping.exe`, `League of Legends.exe`, `FortniteClient-Win64-Shipping.exe`, `TslGame.exe`, `r5apex.exe`, `Overwatch.exe`, `RainbowSix.exe`, `RainbowSix_Vulkan.exe`, `cod.exe`, `RocketLeague.exe`, `Marvel-Win64-Shipping.exe`, `DeadByDaylight-Win64-Shipping.exe`, `Discovery.exe`, `BrawlhallaGame.exe`, `destiny2.exe`, `helldivers2.exe`

#### Open World / Action / RPG

`GTA5.exe`, `GTA5_Enhanced.exe`, `FiveM_GTAProcess.exe`, `RDR2.exe`, `Cyberpunk2077.exe`, `eldenring.exe`, `bg3.exe`, `bg3_dx11.exe`, `witcher3.exe`, `SkyrimSE.exe`, `Fallout4.exe`, `HogwartsLegacy.exe`, `MonsterHunterWilds.exe`, `MonsterHunterWorld.exe`, `MonsterHunterRise.exe`, `Palworld-Win64-Shipping.exe`

#### Asian Online / Gacha / MMO

`GenshinImpact.exe`, `YuanShen.exe`, `StarRail.exe`, `ZenlessZoneZero.exe`, `Wuthering Waves.exe`, `NarakaBladepoint.exe`, `Warframe.x64.exe`, `ffxiv_dx11.exe`, `BlackDesert64.exe`, `LOSTARK.exe`, `NewWorld.exe`, `Wow.exe`, `WowClassic.exe`, `Diablo IV.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile2.exe`, `PathOfExile2Steam.exe`, `aces.exe`

#### Survival / Sandbox / Crafting

`RustClient.exe`, `DayZ_x64.exe`, `7DaysToDie.exe`, `ArkAscended.exe`, `ShooterGame.exe`, `valheim.exe`, `Terraria.exe`, `ProjectZomboid64.exe`, `FactoryGame-Win64-Shipping.exe`, `enshrouded.exe`, `SonsOfTheForest.exe`, `RobloxPlayerBeta.exe`, `Minecraft.Windows.exe`

#### Strategy / Simulation / Management

`eurotrucks2.exe`, `amtrucks.exe`, `FarmingSimulator2025Game.exe`, `TS4_x64.exe`, `CivilizationVI.exe`, `CivilizationVI_DX12.exe`, `AoE2DE_s.exe`, `hoi4.exe`, `stellaris.exe`, `Warhammer3.exe`, `factorio.exe`, `RimWorldWin64.exe`, `Cities2.exe`

#### Co-op / Indie / Social

`Stardew Valley.exe`, `GeometryDash.exe`, `isaac-ng.exe`, `PEAK.exe`, `REPO.exe`, `Among Us.exe`, `Lethal Company.exe`, `Phasmophobia.exe`, `FallGuys_client_game.exe`, `VRChat.exe`

#### Sports / Racing / Fighting

`FC24.exe`, `FC25.exe`, `FC26.exe`, `eFootball.exe`, `ForzaHorizon4.exe`, `ForzaHorizon5.exe`, `StreetFighter6.exe`, `TEKKEN 8.exe`

---

## 11. Auto Check Update ผ่าน GitHub Tag

### หลักการ

- Current version อยู่ที่ `core/version.py`
- Current version: `3.6.2`
- Repository: `TDitbam/TDitbam-Streamer-Suite`
- Endpoint: `GET https://api.github.com/repos/TDitbam/TDitbam-Streamer-Suite/tags?per_page=100`
- ใช้ Public GitHub REST API ไม่ต้องใช้ API key
- ส่ง Headers: GitHub JSON Accept, User-Agent และ GitHub API version
- Timeout 8 วินาที
- ทำงานใน daemon thread ไม่บล็อก Tk

### การเลือกเวอร์ชัน

- รองรับ Tag รูปแบบ `v3.6.2` หรือ `3.6.2`
- รับเฉพาะ stable semantic version สามส่วน
- ข้าม Tag เช่น `v3.7.0-beta` หรือ `nightly`
- เลือกเลขเวอร์ชัน stable ที่สูงที่สุด ไม่เชื่อว่ารายการแรกต้องใหม่ที่สุด

### สถานะที่แสดง

- ยังไม่ได้ตรวจสอบ
- กำลังตรวจสอบ GitHub Tag
- มีเวอร์ชันใหม่
- กำลังใช้เวอร์ชันล่าสุด
- Build นี้ใหม่กว่า GitHub Tag ล่าสุด
- ไม่สามารถตรวจสอบอัปเดตได้

### UI หน้า Settings

- Current Version
- Latest GitHub Tag
- Update Status
- Automatically Check for Updates
- Check Now
- Open Release

### ขอบเขตความปลอดภัย

- ระบบตรวจสอบเท่านั้น
- ไม่ดาวน์โหลดไฟล์เอง
- ไม่ติดตั้งไฟล์เอง
- ไม่เรียกใช้ EXE จากอินเทอร์เน็ต
- ผู้ใช้ต้องกดเปิดหน้า GitHub Release และเลือกดาวน์โหลดเอง

### สถานะ API ที่ตรวจจริง

วันที่ 23 สิงหาคม 2026 GitHub Tags API คืน Tag stable ล่าสุดของ Repository เป็น `v3.6.0` ดังนั้นโปรแกรม `3.6.2` จะแสดงว่าเป็น Build ใหม่กว่า Tag ล่าสุดจนกว่าจะ Publish และสร้าง Tag `v3.6.2`

---

## 12. Voice Providers

### Edge TTS

- ใช้งานทั่วไป
- มีเสียงภาษาไทย เช่น Premwadee และ Niwat

### gTTS

- รองรับภาษาไทยและอังกฤษ

### Gemini API Voice

- สถานะ Experimental
- เลือก Model, Voice และ Style
- รับ API key จาก UI หรือ `GEMINI_API_KEY`

### OpenAI API Voice

- สถานะ Experimental
- เลือก Model, Voice, Style/Instructions และ Speed
- รับ API key จาก UI หรือ `OPENAI_API_KEY`

---

## 13. Dashboard, Logs และ WinGet

### Dashboard

- Tab Performance สำหรับข้อมูลเครื่อง
- Tab Logs สำหรับ Log
- Log ย่อย: All Logs, Bot Live Chat และ Optimizer
- จำกัดจำนวนบรรทัด Log เพื่อไม่ให้โปรแกรมช้าหลังเปิดนาน

### Quick Add

- อ่านรายชื่อโปรเซสที่กำลังทำงาน
- ช่อง Search กรองทันทีขณะพิมพ์
- เลือก P-CORE, E-CORE หรือ NORMAL
- เพิ่มโปรแกรมโดยไม่ต้องพิมพ์ชื่อ `.exe`
- Manual Entry ยังอยู่แยกสำหรับผู้ใช้เดิม

### WinGet Manager

- ค้นหา Package
- ติดตั้งด้วย Package ID
- Upgrade All
- รองรับกด Enter
- ป้องกันคำสั่งทำงานซ้อน
- แสดงสถานะและผลลัพธ์ใน Tab แยก

---

## 14. โครงสร้างไฟล์สำคัญ

### จุดเริ่มโปรแกรม

- `main.py`: ขอสิทธิ์ Administrator, จัดการ Single Instance, สร้าง Engine และ GUI

### Core

- `core/tts_engine.py`: Session lifecycle, queues, voice generation, audio player
- `core/single_instance.py`: Mutex และ activation event
- `core/system_metrics.py`: CPU/RAM/GPU และ per-process metrics
- `core/app_logger.py`: Log และ AppData paths
- `core/version.py`: เวอร์ชันกลางและ GitHub URLs
- `core/update_checker.py`: GitHub Tag update checker
- `core/collectors/`: YouTube, Twitch และ TikTok collectors

### GUI

- `gui/app.py`: App lifecycle, config, language, tray, lazy frames
- `gui/dashboard.py`: Performance และ Logs
- `gui/chat_frame.py`: Bot Live Chat settings
- `gui/optimizer_frame.py`: CPU strategy, Quick Add, Manual Entry, Directories
- `gui/settings_frame.py`: ภาษา, Startup, Notifications, Version & Updates
- `gui/windows_tools_frame.py`: Scheduler และ WinGet
- `gui/logic.py`: เชื่อม UI กับ Engine, Scheduler, Optimizer และ Update Checker
- `gui/i18n.py`: คำแปลไทย/English
- `gui/ui_theme.py`: สี, typography, cards และ spacing

### Optimizer

- `optimizer/policy/engine.py`: ตัดสิน P-CORE/E-CORE/NORMAL/Unmanaged
- `optimizer/engine/enforcer.py`: บังคับ affinity และ priority
- `optimizer/engine/registry.py`: State ของโปรเซส
- `optimizer/optimizer_core/optimizer_engine.py`: Loop ตรวจและปรับโปรเซส
- `optimizer/optimizer_core/config_loader.py`: Settings, Targets, Paths, PopularGames และ atomic writes
- `optimizer/optimizer_core/game_presets.py`: 97 game process presets
- `optimizer/optimizer_core/cpu_topology.py`: แยก P-Core/E-Core

### Build และ Release

- `build_exe.spec`: PyInstaller one-folder, GUI no console, UAC admin, icon และ version resource
- `version_info.txt`: FileVersion/ProductVersion 3.6.2
- `build_release.ps1`: Clean build, UAC elevation, EXE, Setup และ SHA-256
- `installer_script.iss`: Inno Setup v3.6.2
- `RELEASE.md`: Release notes ภาษาอังกฤษ
- `RELEASE_DRAFT_TH.md`: Release notes ภาษาไทยสำหรับ GitHub Draft
- `Release notes.txt`: Release notes แบบข้อความ
- `CREDITS.md`: เครดิตเจ้าของโครงการ, AI, libraries, services และ build tools

---

## 15. ตำแหน่ง Config และข้อมูลผู้ใช้

### App Config

Windows:

`%APPDATA%\TDitbam-Streamer-Suite\config.ini`

ค่าหลักที่เกี่ยวข้อง:

- language
- start_minimized
- run_on_startup
- auto_start_optimizer
- windows_notifications
- auto_check_updates
- Bot Live Chat connections
- Voice provider และ API settings

### Optimizer Config

`%APPDATA%\TDitbam-Streamer-Suite\optimizer_config.ini`

Sections:

- `[Settings]`
- `[Targets]` โปรแกรมที่ผู้ใช้เพิ่มเอง
- `[PopularGames]` preset เกมยอดนิยม
- `[Paths]` managed directories
- `[Presets]` migration version

### Log

`%APPDATA%\TDitbam-Streamer-Suite\logs\`

---

## 16. Build และ Installer v3.6.2

### App Build

- Main executable: `dist\StreamerSuite\StreamerSuite.exe`
- Support directory: `dist\StreamerSuite\parts\`
- Support files: 1,128 ไฟล์ใน Build ล่าสุด
- Product Version: `3.6.2`
- File Version: `3.6.2.0`

### Setup

- Path: `installer\TDitbam-Streamer-Suite-Setup-v3.6.2.exe`
- ขนาด: 30,990,760 bytes
- Installer เป็นไฟล์เดียว
- BIN Part count: 0

### Checksum

```text
6762FFF425F4BE5058833A2D7A0F88C209CAD5D4D21BA9462A2EEB1A9A407695
```

ไฟล์ Checksum:

`installer\TDitbam-Streamer-Suite-Setup-v3.6.2-SHA256.txt`

### Digital Signature

- EXE และ Setup ยังไม่ได้เซ็น Digital Signature
- Windows SmartScreen อาจแสดงคำเตือน
- ถ้าต้องการลดคำเตือน ต้องมี Code Signing Certificate

---

## 17. การทดสอบ

จำนวน Unit Tests ล่าสุด: **13 รายการ**

หัวข้อที่ทดสอบ:

- Popular game migration
- ไม่เขียนทับ Custom policy
- ลบ preset แล้วไม่เพิ่มกลับทุกครั้ง
- Unmanaged Windows processes ถูกข้าม
- P-CORE/E-CORE/NORMAL ยังทำงาน
- Managed Directory ยัง match
- Start Minimized ไม่แตะ Task Scheduler
- Run on Startup sync เพียงครั้งเดียว
- เปิด Startup ไม่ลบ Task ก่อนสร้าง
- Parse stable GitHub tags
- เลือก stable version สูงสุด
- จัดการ invalid/empty API response
- เปรียบเทียบ current/latest version

การตรวจอื่น:

- Python compileall ผ่าน
- `git diff --check` ผ่าน
- PowerShell parser ของ `build_release.ps1` ผ่าน
- Settings Version & Updates UI smoke test ผ่าน
- GitHub Tags API จริงผ่านและคืน `v3.6.0`
- PyInstaller archive มี `core.update_checker`, `core.version`, `gui.settings_frame` และ `game_presets`
- Setup SHA-256 ตรงกับ Manifest
- ไม่มี `.bin` Part

คำสั่งทดสอบหลัก:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q gui optimizer core tests main.py
```

คำสั่ง Build:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build_release.ps1
```

---

## 18. GitHub Draft Release v3.6.2

- สถานะ: Draft
- Tag name ที่เตรียมไว้: `v3.6.2`
- Tag ref จริงยังไม่ถูกสร้างจนกว่าจะ Publish
- ชื่อ Draft: `TDitbam Streamer Suite v3.6.2 — แก้บัคและปรับปรุงระบบ`
- ภาษา Release Notes: ไทย
- Assets: 2 ไฟล์
  - `TDitbam-Streamer-Suite-Setup-v3.6.2.exe`
  - `TDitbam-Streamer-Suite-Setup-v3.6.2-SHA256.txt`
- Draft URL: https://github.com/TDitbam/TDitbam-Streamer-Suite/releases/tag/untagged-4cbb7022befb23d4b1aa
- Target branch ขณะสร้าง Draft: `agent/release-3.6.1`

### ข้อควรระวังก่อน Publish

- โค้ด 3.6.2 ล่าสุดยังไม่ได้ Commit/Push
- ห้าม Publish Draft ก่อน Commit และ Push โค้ดล่าสุด
- ควรตรวจ Target branch หรือสร้าง branch/release branch 3.6.2 ให้ชัดเจน
- หลัง Push แล้วจึง Publish เพื่อให้ Tag `v3.6.2` ชี้ไปยัง Commit ที่มีโค้ดตรงกับ Setup
- เมื่อ Tag `v3.6.2` ถูกสร้าง ระบบ Auto Check จะมองเห็นรุ่น 3.6.2

---

## 19. สถานะ Git ปัจจุบัน ณ เวลาจัดทำเอกสาร

- Branch: `agent/release-3.6.1`
- Commit ล่าสุด: `d453635 Fix shutdown lifecycle`
- มีไฟล์แก้ไขและไฟล์ใหม่ที่ยังไม่ได้ Commit
- กลุ่มไฟล์ใหม่สำคัญ:
  - `core/update_checker.py`
  - `core/version.py`
  - `optimizer/optimizer_core/game_presets.py`
  - `tests/`
  - `version_info.txt`
  - `RELEASE_DRAFT_TH.md`
- กลุ่มไฟล์แก้ไขสำคัญ:
  - GUI และ Settings
  - Optimizer Policy/Engine/Config
  - Build/Installer
  - README/Release Notes/Credits

---

## 20. งานที่ยังไม่เสร็จและแผนอนาคต

### งานที่ยังไม่เสร็จทันที

1. Review `git diff` รอบสุดท้าย
2. Commit โค้ด 3.6.2
3. Push ไป GitHub
4. ตรวจ Draft Target branch
5. ทดสอบติดตั้ง Setup บนเครื่องสะอาดหรือ Windows VM
6. Publish Draft เมื่อ Tag พร้อม
7. ตรวจ Auto Check หลัง Tag `v3.6.2` ถูกสร้าง

### แผนในอนาคต

- เพิ่มการเชื่อมต่อหรือคำสั่งเปิด `christitustech/winutil`
- พิจารณา Code Signing Certificate
- ขยาย game presets ใน version ถัดไปโดยไม่คืน preset ที่ผู้ใช้ปิด
- เพิ่มระบบ Cache/ETag สำหรับ GitHub update check ถ้าจำเป็น
- เพิ่มการทดสอบ Installer บน Windows VM
- พิจารณาระบบ Download Update แบบมีการยืนยันและตรวจ SHA-256 ในอนาคต แต่ปัจจุบันยังไม่ทำ Auto Install เพื่อความปลอดภัย

---

## 21. หลักการออกแบบที่ตกลงร่วมกัน

- UI ต้องไม่รก
- Action สำคัญต้องอยู่ก่อนรายการหรือ Log
- งาน Network และ Monitoring ต้องไม่บล็อก UI thread
- ระบบเสียงเก่าห้ามย้อนกลับมาปน Session ใหม่
- Optimizer ห้ามแตะโปรเซสที่ไม่ได้กำหนด
- Config migration ห้ามเขียนทับค่าผู้ใช้
- Installer ต้องเป็นไฟล์เดียว ไม่มี BIN Part
- การอัปเดตต้องตรวจผ่าน GitHub Tag แต่ไม่ดาวน์โหลด/ติดตั้งเอง
- การเปิดโปรแกรมซ้ำต้องเรียก Instance เดิม ไม่สร้างระบบซ้ำ
- ทุก Build ต้องตรวจ Version consistency, tests และ SHA-256

---

## 22. สรุปสั้นสำหรับ NotebookLM

TDitbam Streamer Suite v3.6.2 เป็นโปรแกรม Windows สำหรับสตรีมเมอร์ที่รวม Bot Live Chat TTS, CPU Optimizer, P-Core/E-Core monitoring, RAM/GPU Dashboard, Logs, Cleanup, WinGet และ Windows integration ไว้ด้วยกัน รุ่น 3.6.2 แก้ Session เสียงซ้อน, Ctrl+V ซ้ำ, Optimizer แตะ Windows processes, Startup Task ทำงานเกินจำเป็น และเพิ่ม game presets 97 รายการ รวมถึง GitHub Tag Auto Update Checker ในหน้า Settings ตัว Setup ถูก Build แล้วและมี SHA-256 แต่โค้ดล่าสุดยังไม่ได้ Commit/Push และ GitHub Release ยังเป็น Draft จึงต้องจัด Git ให้เสร็จก่อน Publish

---

## 23. ไฟล์อ้างอิงเพิ่มเติมใน Repository

- `README.md`
- `RELEASE.md`
- `RELEASE_DRAFT_TH.md`
- `Release notes.txt`
- `Project Review.txt`
- `โครงสั้ง code.txt`
- `CREDITS.md`
- `tests/`

เอกสารฉบับนี้สามารถอัปโหลดเข้า Google NotebookLM ได้โดยตรงในรูปแบบ Markdown
