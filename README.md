# 🎙️ TDitbam Streamer Suite (v3.5.0)

## อัปเดตล่าสุด — 6 สิงหาคม 2026

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
2. รันไฟล์ `TDitbam-Streamer-Suite-Setup-v3.3.0.exe`
3. ทำตามขั้นตอนการติดตั้งบนหน้าจอ

### สำหรับนักพัฒนา (Developers)
หากต้องการรันจาก Source Code:
```bash
# ติดตั้ง Library ที่จำเป็น
pip install customtkinter TikTokLive edge-tts deep-translator pygame psutil pystray Pillow

# รันโปรแกรม
python main.py
```

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

---

## 📝 บันทึกการเปลี่ยนแปลง (Release Notes)
ดูรายละเอียดการอัปเดตล่าสุดได้ที่ [Release notes.txt](./Release%20notes.txt)

---

## 🤝 เครดิต (Credits)
- **Developer:** Tditbam
- **AI Assistant:** Gemini CLI , Openai codex
- **Libraries:** CustomTkinter, Edge-TTS, TikTokLive, psutil

---
*Released under MIT License - 2026 TDitbam*
