# TDitbam Streamer Suite v3.6.2

รุ่นนี้เน้นแก้บัคสำคัญ เพิ่มความปลอดภัยของ Optimizer และทำให้การตั้งค่าโปรแกรมใช้งานง่ายขึ้น พร้อมเพิ่มระบบตรวจสอบอัปเดตผ่าน GitHub Tag

## แก้บัคสำคัญ

- แก้ Optimizer ไปปรับ `explorer.exe`, `dwm.exe`, `RuntimeBroker.exe` และโปรเซส Windows ที่ผู้ใช้ไม่ได้กำหนด
- Optimizer จะปรับ CPU affinity และ priority เฉพาะโปรแกรม โฟลเดอร์ หรือเกมใน preset เท่านั้น
- แก้อาการเดสก์ท็อปและเมาส์ทำงานผิดปกติคล้ายถูกกด `Windows + D`
- แยกการทำงานของ **Start Minimized** และ **Run on Windows Startup** ออกจากกันอย่างชัดเจน
- Task Scheduler จะถูกแก้ไขเฉพาะเมื่อเปลี่ยนค่า Run on Windows Startup จริง
- ป้องกัน Startup Task เดิมหาย หากการสร้าง Task ใหม่ไม่สำเร็จ
- แก้เสียง Bot Live Chat จาก Session เก่ากลับมาเล่นซ้อนหลัง Stop แล้ว Start ใหม่
- แก้ `Ctrl + V` วางข้อความซ้ำ

## ระบบตรวจสอบอัปเดต

- เพิ่ม Auto Check Update ผ่าน GitHub Tags API
- ตรวจสอบอัตโนมัติหนึ่งครั้งในเบื้องหลังหลังเปิดโปรแกรม โดยไม่ทำให้ UI ค้าง
- หน้า Settings แสดงเวอร์ชันปัจจุบัน, GitHub Tag ล่าสุด และสถานะอัปเดต
- เพิ่มสวิตช์เปิด/ปิด Auto Check พร้อมปุ่ม **ตรวจสอบตอนนี้** และ **เปิดหน้ารีลีส**
- ระบบจะไม่ดาวน์โหลดหรือติดตั้งอัปเดตเอง ผู้ใช้เป็นผู้ยืนยันการดาวน์โหลดทุกครั้ง
- รองรับข้อความภาษาไทยและ English (US)

## Preset เกมยอดนิยม

- เพิ่ม preset ชื่อโปรเซสเกมยอดนิยม 97 รายการ ครอบคลุม Steam, Epic, Riot, Battle.net และเกมออนไลน์หลัก
- แยก `PopularGames` ออกจาก Custom Targets เพื่อให้หน้า Optimizer ไม่รกและโหลดเร็ว
- ค่าที่ผู้ใช้กำหนดเองมีสิทธิ์สูงกว่า preset เสมอ
- Migration เพิ่ม preset เพียงครั้งเดียวและไม่เขียนทับค่าเดิมของผู้ใช้
- ไม่เพิ่ม launcher, anti-cheat หรือ shared runtime เช่น `javaw.exe`
- บันทึก `optimizer_config.ini` แบบ atomic ลดโอกาสไฟล์ config เสียหาย

## Dashboard และ UI

- ปรับ UI ทั้งโปรแกรมให้ใช้สี ระยะห่าง Card ปุ่ม และตัวอักษรในรูปแบบเดียวกัน
- แยก Dashboard เป็นแท็บ **Performance** และ **Logs**
- แสดง P-Core/E-Core, RAM, GPU และโปรแกรมที่ใช้ทรัพยากรสูงสุดแบบเรียลไทม์
- Logs แยกเป็น All Logs, Bot Live Chat และ Optimizer
- Quick Add รองรับการค้นหาโปรเซสขณะพิมพ์และรีเฟรชรายการอัตโนมัติ
- ลดอาการ UI หน่วงและสีขาวกระพริบระหว่างเปิดหรือเปลี่ยนหน้า
- เพิ่ม Single Instance ป้องกันการเปิดโปรแกรมซ้ำ
- เพิ่ม Auto Start Optimizer และ Windows Notifications

## Bot Live Chat และระบบเสียง

- เปลี่ยนชื่อระบบ Chat-TTS เป็น **Bot Live Chat**
- แยก Session, message queue, audio queue และ audio player ออกจากกันทุกครั้งที่ Start
- Stop จะยกเลิก worker, หยุดเสียง และป้องกันข้อมูลเก่าเข้าสู่ Session ใหม่
- รองรับ Edge TTS, gTTS, Gemini API Voice และ OpenAI API Voice
- Gemini และ OpenAI API Voice ยังอยู่ในขั้นทดลอง
- รองรับภาษาไทยและ English (US)

## ไฟล์ติดตั้ง

- Setup เป็นไฟล์ `.exe` ไฟล์เดียว ไม่มีไฟล์ `.bin` หรือ Part แยก
- ตัวโปรแกรมใช้ `StreamerSuite.exe` พร้อมโฟลเดอร์ `parts` สำหรับ dependency
- เพิ่มข้อมูล File Version และ Product Version เป็น `3.6.2`
- Build และ Installer ขอสิทธิ์ Administrator ตามฟีเจอร์ Windows ที่โปรแกรมใช้งาน

## ดาวน์โหลด

ดาวน์โหลดไฟล์ `TDitbam-Streamer-Suite-Setup-v3.6.2.exe` จาก Assets ด้านล่าง แล้วเปิดเพื่อติดตั้งได้ทันที

SHA-256:

`6762FFF425F4BE5058833A2D7A0F88C209CAD5D4D21BA9462A2EEB1A9A407695`

ขอบคุณทุกคนที่ทดลองใช้งานและแจ้งบัคครับ
