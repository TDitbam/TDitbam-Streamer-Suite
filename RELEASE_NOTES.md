# 🚀 บันทึกการอัปเดต (Release Notes) - TDitbam Streamer Suite Pro v3.1.0

## 🌟 มีอะไรใหม่ (What's New)

### 🚀 ระบบ CoreOptimizer Pro (v3 Engine)
- **Hybrid Core Management:** รองรับการจัดการ CPU รุ่นใหม่ (Intel P-Cores/E-Cores) อย่างเต็มรูปแบบ เพื่อเพิ่ม FPS และลดความหน่วงในเกม
- **Auto Junk Cleanup v2:** เพิ่มระบบล้างขยะอัตโนมัติที่ผู้ใช้สามารถตั้งรอบเวลา (Interval) ได้เองผ่านหน้า GUI
- **GPU Shader Cache Cleaner:** เพิ่มระบบล้าง Cache ของการ์ดจอ (NVIDIA, AMD, Intel) เพื่อลดอาการ Stuttering (ภาพกระตุกเป็นพักๆ) ขณะสตรีม

### 🎙️ ระบบ Chat-TTS Improvements
- **UI Restoration:** กู้คืนและปรับปรุงส่วนควบคุม Delay/Char, Max Delay และระบบ Filter คำหยาบให้กลับมาใช้งานได้สมบูรณ์ 100%
- **Platform Stability:** ปรับปรุงการเชื่อมต่อกับ YouTube, Twitch และ TikTok ให้เสถียรยิ่งขึ้น

### 🛠️ การปรับปรุงระบบ (System Enhancements)
- **Non-Blocking GUI:** ปรับปรุงระบบปุ่ม Start ให้ทำงานแบบ Async ทั้งหมด หน้าโปรแกรมจะไม่ค้างแม้จะกดเริ่มหลาย Service พร้อมกัน
- **Administrator Elevation:** เพิ่มระบบขอสิทธิ์ผู้ดูแลระบบอัตโนมัติเมื่อเปิดโปรแกรม เพื่อให้ Optimizer ทำงานได้ถูกต้อง
- **Direct Execution Support:** ปรับปรุงโค้ดให้สามารถดับเบิลคลิก `main.py` หรือใช้ไฟล์ `RUN_SUITE.bat` เพื่อรันโปรแกรมได้ทันทีโดยไม่ต้องพิมพ์คำสั่งใน CMD

### 📦 การจัดส่งโปรแกรม (Distribution)
- **Standalone EXE:** แจกจ่ายในรูปแบบไฟล์ `.exe` ตัวเดียวจบ ไม่ต้องติดตั้ง Python ในเครื่องปลายทาง
- **Professional Installer:** มาพร้อมตัวติดตั้ง (Inno Setup) ที่รองรับทั้งภาษาไทยและอังกฤษ

---

## 📦 ข้อมูลทางเทคนิค (Technical Details)
- **Version:** 3.1.0
- **Build Date:** 2 มิถุนายน 2569
- **Required OS:** Windows 10/11 (64-bit)

----
*พัฒนาโดย TDitbam ร่วมกับ Gemini CLI Agent - เพื่อสตรีมเมอร์ไทยทุกคน*
