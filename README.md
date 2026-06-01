# 🚀 TDitbam Streamer Suite Pro v3.1.0

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows)

**TDitbam Streamer Suite Pro** เป็นเครื่องมือแบบ All-in-One สำหรับสตรีมเมอร์ที่รวมระบบ **Chat-to-Speech (TTS)** ระดับสูงและ **CoreOptimizer (v3 Engine)** เข้าด้วยกัน เพื่อมอบประสบการณ์การสตรีมที่ไหลลื่นและมีปฏิสัมพันธ์กับผู้ชมได้ดียิ่งขึ้น

---

## ✨ คุณสมบัติหลัก (Key Features)

### 🎙️ Chat-TTS (Multi-Platform)
- **สนับสนุน 3 แพลตฟอร์มหลัก:** ดึงแชทสดจาก **YouTube Live, Twitch และ TikTok** พร้อมกัน
- **เสียงพากย์ธรรมชาติ:** ใช้ `edge-tts` เพื่อเสียงพากย์ภาษาไทยที่นุ่มนวลและเป็นธรรมชาติ
- **ระบบแปลภาษาอัตโนมัติ:** แปลแชทภาษาต่างประเทศเป็นภาษาไทยแบบ Real-time
- **ระบบกรองคำหยาบ (Profanity Filter):** ป้องกันการอ่านข้อความที่ไม่เหมาะสมออกอากาศ
- **ปรับแต่งได้ละเอียด:** ปรับ Delay ต่อตัวอักษร, เลือกเสียงพากย์ และตั้งค่า Filter ได้ตามต้องการ

### 🚀 CoreOptimizer Pro (v3 Engine)
- **Hybrid CPU Support:** จัดการ Intel P-Cores และ E-Cores อย่างชาญฉลาดสำหรับ CPU รุ่นใหม่
- **Auto-Affinity Control:** บังคับให้เกมใช้ P-Cores เพื่อลด Latency และเพิ่ม FPS
- **Core 0 Protection:** ปกป้อง Core หลักของ OS เพื่อป้องกันระบบค้าง
- **Managed Directories:** ตั้งค่าโฟลเดอร์ให้โปรแกรมที่รันข้างในได้รับ Priority สูงสุดอัตโนมัติ

### 🧹 Advanced Maintenance
- **System Junk Cleaner:** ลบไฟล์ขยะใน Windows และ User Temp
- **GPU Shader Cache Cleanup:** ล้าง Cache ของ **NVIDIA, AMD และ Intel** เพื่อลดอาการกระตุก (Stuttering) ในเกม
- **Auto-Cleanup:** ระบบล้างไฟล์ขยะอัตโนมัติตามรอบเวลาที่กำหนด (เช่น ทุก 24 ชม.)

---

## 🛠️ การติดตั้ง (Installation)

### 1. ความต้องการของระบบ
- Windows 10 หรือ 11 (แนะนำ 64-bit)
- Python 3.10 ขึ้นไป
- สิทธิ์ Administrator (สำหรับการใช้งาน Optimizer)

### 2. ติดตั้ง Library ที่จำเป็น
```bash
pip install -r requirements.txt
```

### 3. เริ่มใช้งาน
รันโปรแกรมผ่าน GUI (แนะนำ):
```bash
python main.py
```
หรือรันเฉพาะระบบ Optimizer ผ่าน CLI:
```bash
python main.py --cli
```

---

## 📂 โครงสร้างโปรเจค (Project Structure)
- `core/`: ระบบ Chat-TTS และ Chat Collectors (YouTube, Twitch, TikTok)
- `optimizer/`: Engine ของระบบ CoreOptimizer v3
- `docs/`: คู่มือการใช้งานและประวัติการอัพเดท
- `main.py`: จุดเข้าใช้งานหลักของโปรแกรม (Dashboard)

---

## 🤝 การสนับสนุนและพัฒนา
โปรเจคนี้พัฒนาโดย **TDitbam** ร่วมกับ **Gemini CLI Agent** เพื่อให้สตรีมเมอร์มีเครื่องมือที่ทรงพลังและใช้งานง่ายที่สุด

หากพบปัญหาหรือมีข้อเสนอแนะ สามารถเปิด Issue ได้ที่หน้า GitHub นี้เลยครับ!

---
*Note: การใช้ระบบ Optimizer จำเป็นต้องรันโปรแกรมด้วยสิทธิ์ Administrator เพื่อการเข้าถึงระบบจัดการ Core ของ CPU*
