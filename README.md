# 🎙️ TDitbam Streamer Suite (v3.6.1)

## อัปเดตล่าสุด — 7 สิงหาคม 2026

- ปรับ GUI ทั้งโปรแกรมด้วย design system กลาง: สี ระยะห่าง card ปุ่ม input และ typography เป็นชุดเดียวกัน
- ปรับ Sidebar ใหม่พร้อมสถานะหน้าที่เลือก และจัดทุกหน้าให้ responsive ตั้งแต่ขนาดหน้าต่าง 1000×700
- จัด workflow ของ Bot Live Chat, Optimizer, Cleanup, Windows Tools และ Settings ใหม่ให้ลำดับใช้งานชัดและลดความรก
- แก้ white flash ตอนเปิด/restore: ซ่อน native window จน dark first frame วาดเสร็จ และสร้างหน้ารองเมื่อเปิดใช้งานครั้งแรก
- ลด startup GUI จากประมาณ 893ms เหลือ 188–245ms ใน regression test พร้อม atomic Dashboard refresh ที่ไม่ลบกล่องจนว่าง
- Quick Add ไม่ redraw หรือ reset โปรแกรมที่เลือกเมื่อรายการโปรเซสจากรอบ refresh ไม่มีการเปลี่ยนแปลง
- เพิ่มระบบ **Single Instance** ป้องกันการเปิดโปรแกรมซ้ำ โดยตรวจสอบก่อนโหลด GUI, ระบบเสียง และ log handlers
- เพิ่ม **Auto Start Optimizer** ใน App Settings ให้ Optimizer เริ่มทำงานเองหลังเปิดโปรแกรม
- เปิดโปรแกรมซ้ำจะเรียกหน้าต่างเดิมขึ้นมาจาก System Tray แทนการเปิด instance ใหม่
- เพิ่มการแจ้งเตือน Windows โดยใช้ไอคอนหลัก `icon.ico` และสามารถปิดได้จาก App Settings
- Dashboard แยกแท็บ **Performance** และ **Logs** ชัดเจน โดย Log ไม่เบียดข้อมูลสำคัญบนหน้าหลัก
- Performance แสดง P-Core/E-Core, RAM, GPU และตารางโปรแกรมที่ใช้ CPU/RAM/GPU สูงสุดแบบเรียลไทม์
- Logs ยังอยู่ใน Dashboard และแยกย่อยเป็น All Logs, Bot Live Chat และ Optimizer
- ปรับ WinGet Manager เป็น UI แบบกระชับ มีสถานะคำสั่ง ค้นหา/ติดตั้งด้วย Enter และป้องกันคำสั่งทำงานซ้อนกัน
- Build v3.6.1 ใช้โหมดโฟลเดอร์แยก: `dist/StreamerSuite/StreamerSuite.exe` และไฟล์ประกอบอยู่ใน `parts/` เพื่ออัปเดตเป็นส่วนได้ง่าย
- Installer v3.6.1 เป็น Setup `.exe` ไฟล์เดียว พร้อมไฟล์ SHA-256 สำหรับตรวจสอบความสมบูรณ์
- หน้า Optimizer เพิ่มโปรแกรมได้จากรายชื่อโปรเซสที่กำลังรัน พร้อมแยกโหมด Quick Add และ Manual Entry
- ปรับประสิทธิภาพ UI: ย้าย CPU/RAM/GPU monitoring และ process scan ไป background, cache topology และรวมการอัปเดต UI/log เป็นชุด
- Quick Add ค้นหาโปรเซสได้ทันทีขณะพิมพ์ และรีเฟรชรายการอัตโนมัติทุก 5 วินาที
- เปลี่ยนชื่อระบบอ่านแชทเป็น **Bot Live Chat**
- รองรับ YouTube Live, Twitch และ TikTok Live
- เพิ่ม Voice Provider 4 ระบบ: **Edge TTS**, **gTTS**, **Gemini API Voice** และ **OpenAI API Voice**
- Gemini/OpenAI เป็นฟีเจอร์ **อยู่ในขั้นทดลอง (Experimental)** และต้องใช้ API key
- รองรับ `GEMINI_API_KEY` และ `OPENAI_API_KEY` จาก environment variable
- เพิ่ม UI สองภาษา: **ไทย** และ **English (US)** พร้อมจำค่าภาษา
- ปรับหน้า Voice Settings ให้แสดงเฉพาะตัวเลือกของ provider ที่กำลังใช้งาน
- ยกระดับ Session isolation: แยก queue/cancellation/audio player ต่อรอบ ป้องกันเสียงเก่าซ้อนหลัง Stop → Start
- แก้ `Ctrl+V` วางข้อความซ้ำ

### Voice Providers

| Provider | การตั้งค่าหลัก | สถานะ |
|---|---|---|
| Edge TTS | เสียง Premwadee/Niwat | พร้อมใช้งาน |
| gTTS | ภาษาไทย/อังกฤษ | พร้อมใช้งาน |
| Gemini API | Model, Voice, API key, Voice Style | Experimental |
| OpenAI API | Model, Voice, API key, Style, Speed | Experimental |

> API key ที่กรอกผ่าน UI จะถูกบันทึกใน `config.ini` แบบข้อความปกติ หากไม่ต้องการบันทึก key ลงไฟล์ ให้ตั้งผ่าน environment variable แทน

**TDitbam Streamer Suite** คือเครื่องมือ All-in-One สำหรับสตรีมเมอร์ที่รวมระบบ **Chat-to-Speech (TTS)** และ **System Optimizer** เข้าด้วยกัน เพื่อให้การสตรีมของคุณลื่นไหลและมีปฏิสัมพันธ์กับผู้ชมได้ดีที่สุด

---

## ✨ คุณสมบัติหลัก (Key Features)

### 🔊 Bot Live Chat Multi-Platform
- **รองรับ 3 แพลตฟอร์มหลัก:** อ่านแชทจาก YouTube Live, Twitch และ TikTok Live พร้อมกัน
- **เสียงคุณภาพสูง:** ใช้เทคโนโลยี Edge-TTS ให้เสียงที่เป็นธรรมชาติ
- **แปลภาษาอัตโนมัติ:** รองรับการแปลแชทต่างชาติเป็นภาษาไทยทันที
- **Live Update:** ปรับเปลี่ยนเสียงและความหน่วง (Delay) ได้แบบเรียลไทม์โดยไม่ต้องรีสตาร์ทระบบ
- **ระบบกรองคำหยาบ:** มีระบบ Custom Filter ป้องกันคำไม่เหมาะสม

### 🚀 System Optimizer & Maintenance
- **CPU Core Management:** จัดการลำดับความสำคัญของโปรเซส (Process Priority)
- **P-Core / E-Core Optimization:** บังคับให้เกมรันบน P-Core เพื่อรีดประสิทธิภาพสูงสุด
- **Auto Junk Cleanup:** ล้างไฟล์ขยะในระบบอัตโนมัติเพื่อลดอาการกระตุก
- **Exclusion Logic:** ป้องกันการยุ่งเกี่ยวกับ Core 0 เพื่อความเสถียรของ Windows

### 💻 User Experience
- **Modern UI:** หน้าตาโปรแกรมสวยงาม ใช้งานง่ายด้วย CustomTkinter
- **System Tray:** ย่อโปรแกรมลง Tray มุมขวาล่างเพื่อประหยัดพื้นที่หน้าจอ
- **Context Menu:** รองรับการคลิกขวา (Cut, Copy, Paste) ทั่วทั้งโปรแกรม
- **Admin Elevation:** ขอสิทธิ์ผู้ดูแลระบบอัตโนมัติเพื่อให้ Optimizer ทำงานได้สมบูรณ์

---

## 🛠️ การติดตั้ง (Installation)

### สำหรับผู้ใช้งานทั่วไป (Standard Users)
1. ไปที่โฟลเดอร์ `installer/`
2. รันไฟล์ `TDitbam-Streamer-Suite-Setup-v3.6.1.exe`
3. ทำตามขั้นตอนการติดตั้งบนหน้าจอ

### สำหรับนักพัฒนา (Developers)
หากต้องการรันจาก Source Code:
```bash
# ติดตั้ง Library ที่จำเป็น
pip install -r requirements.txt

# รันโปรแกรม
python main.py
```

### สร้าง EXE และ Installer Parts
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
powershell -ExecutionPolicy Bypass -File .\build_release.ps1
```

หาก PowerShell ปัจจุบันไม่ได้รันเป็น Administrator สคริปต์จะเปิดหน้าต่าง UAC และเริ่ม build ใหม่ด้วยสิทธิ์ผู้ดูแลระบบอัตโนมัติ

- App แบบแยกไฟล์: `dist\StreamerSuite\StreamerSuite.exe` + `dist\StreamerSuite\parts\`
- Installer ไฟล์เดียว: `installer\TDitbam-Streamer-Suite-Setup-v3.6.1.exe`
- Checksum: `installer\TDitbam-Streamer-Suite-Setup-v3.6.1-SHA256.txt`

---

## 📖 วิธีการใช้งาน (Usage)
1. **Connections:** ใส่ Video ID หรือ Username ของแพลตฟอร์มที่ต้องการในหน้า Chat
2. **Settings:** เลือกเสียงและตั้งค่าความหน่วงที่ต้องการ (ปรับได้เรียลไทม์!)
3. **Optimizer:** เพิ่มชื่อไฟล์เกม (เช่น `valorant.exe`) เพื่อให้ระบบจัดการ Core ให้โดยอัตโนมัติ
4. **Start:** กดปุ่ม **START SYSTEM** ที่หน้า Dashboard เพื่อเริ่มทำงาน

---

## 📁 โครงสร้างไฟล์ที่สำคัญ
- `main.py`: จุดเริ่มต้นของโปรแกรม
- `core/`: เครื่องมือจัดการ TTS และระบบ Logger
- `gui/`: หน้าต่างการใช้งานและเมนูต่างๆ
- `optimizer/`: ระบบจัดการ CPU และการล้างไฟล์ขยะ
- `config.ini`: ไฟล์เก็บค่าตั้งค่าหลักของโปรแกรม
- `build_release.ps1`: ขอสิทธิ์ Administrator อัตโนมัติ แล้วสร้าง App EXE, โฟลเดอร์ `parts`, Setup EXE ไฟล์เดียว และไฟล์ SHA-256

---

## 📝 บันทึกการเปลี่ยนแปลง (Release Notes)
ดูรายละเอียดการอัปเดตล่าสุดได้ที่ [Release notes.txt](./Release%20notes.txt)

---

## 🤝 เครดิต (Credits)
- **Developer & Release Owner:** Tditbam
- **AI Development Assistance:** Gemini CLI และ OpenAI Codex
- **Runtime:** CustomTkinter, TikTokLive, edge-tts, deep-translator, pygame-ce, psutil, pystray, Pillow, gTTS และ pytchat
- **Voice/API Services:** Microsoft Edge Speech, Google Translate/gTTS, Gemini API และ OpenAI API
- **Build & Distribution:** Python, PyInstaller, Inno Setup, Git และ GitHub

ดูรายชื่อผู้พัฒนา เครื่องมือ บริการ ไลบรารี และหมายเหตุเครื่องหมายการค้าแบบเต็มได้ที่ [CREDITS.md](./CREDITS.md)

---
*Released under MIT License - 2026 TDitbam*
