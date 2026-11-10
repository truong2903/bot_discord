# 🌟 DISCORD HYPESQUAD SELECTOR BOT PRO

Dự án Bot Discord chuyên nghiệp với giao diện **Rich Embed** và các **Nút Bấm Tương Tác (Interactive Buttons)** giúp thành viên máy chủ chọn và nhận huy hiệu **HypeSquad** (Bravery 💜, Brilliance 🧡, Balance 🩵) trực tiếp từ Discord.

---

## 📸 Hình Thức Giao Diện (Chuẩn Pro VIP)

Bot sẽ gửi một bảng tin nhắn dạng Embed kèm Menu thả xuống và hàng nút bấm phía dưới:

```text
┌─────────────────────────────────────────────────────────────┐
│ ⚡ [TÊN SERVER] • Official HypeSquad Hub                    │
│ 🌟 DISCORD HYPESQUAD SELECTOR • BẢNG CHỌN HUY HIỆU          │
│                                                             │
│ > ### ✨ GIA NHẬP HYPESQUAD • TỎA SÁNG CÁ TÍNH!             │
│ > Hãy lựa chọn một trong ba ngôi nhà danh giá...            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ 💜 House of Bravery      • Dũng Cảm & Tiên Phong            │
│                          • Thành viên: X người              │
│ 🧡 House of Brilliance   • Xuất Chúng & Sáng Tạo            │
│                          • Thành viên: Y người              │
│ 🩵 House of Balance      • Cân Bằng & Hòa Bình              │
│                          • Thành viên: Z người              │
│                                                             │
│ 👑 Đặc Quyền: Gán Role đổi màu tên & Profile Badge thật     │
│ ⚡ Bấm nút bên dưới hoặc chọn Menu để nhận huy hiệu!        │
└─────────────────────────────────────────────────────────────┘
  [ 🔽 Hoặc chọn nhanh ngôi nhà tại đây... (Select Menu) ]
  [ 💜 Bravery ] [ 🧡 Brilliance ] [ 🩵 Balance ] [ ❌ Gỡ ]
```

---

## ✨ Tính Năng Nổi Bật

1. **Giao diện Nút Bấm & Menu Dropdown chuẩn Discord Interaction:**
   - Hỗ trợ cả **4 Nút Bấm màu sắc** và **Menu Thả Xuống (Dropdown Select)** tiện lợi.
   - Hiển thị **Author Header** mang tên và avatar chính thức của Server.
   - Thống kê **Số lượng thành viên trực tiếp** đang ở mỗi nhà trong Server.
   - Nút bấm và Menu hoạt động vĩnh viễn (**Persistent View**), không bị mất tác dụng sau khi tắt hoặc khởi động lại Bot.
   - Tự động nhận diện và hiển thị **Emoji Động (Animated Emojis)** của server trên cả Embed và nút bấm!

2. **2 Trong 1 (Server Role & Profile Badge):**
   - **Vai Trò Server (Server Role):** Bot tự động tạo 3 vai trò tương ứng và gán ngay cho người bấm trong Server (hiển thị màu tên đẹp mắt).
   - **Huy Hiệu Hồ Sơ (Profile Badge):** 
     - Mở cửa sổ **Modal Popup** ngay trên Discord: Người dùng có thể dán Token để Bot kích hoạt huy hiệu thật vào hồ sơ trong 1 giây.
     - Hoặc nếu không muốn nhập Token: Bot sẽ gửi đoạn mã **1-Click F12 Console** chỉ người đó nhìn thấy (*Ephemeral message*) để kích hoạt trên Discord Web an toàn 100%.

---

## 🚀 Hướng Dẫn Cài Đặt Trong 3 Phút

### Bước 1: Tạo Bot Trên Discord Developer Portal
1. Truy cập [Discord Developer Portal](https://discord.com/developers/applications).
2. Bấm **New Application** ➜ Đặt tên (ví dụ: `HypeSquad Manager`).
3. Vào mục **Bot** ở thanh menu bên trái:
   - Bấm **Reset Token** để sao chép **Bot Token**.
   - Cuộn xuống phần **Privileged Gateway Intents**: Bật **Server Members Intent** và **Message Content Intent** ➜ Bấm **Save Changes**.
4. Vào mục **Installation** hoặc **OAuth2 > URL Generator**:
   - Chọn scope: `bot`, `applications.commands`.
   - Chọn permissions: `Manage Roles` (Quản lý vai trò), `Send Messages`, `Embed Links`, `Use External Emojis`.
   - Sao chép đường link vừa tạo và dán vào trình duyệt để **mời bot vào server của bạn**.

### Bước 2: Điền Token Vào Bot
Mở file `config.json` và dán Token vào:
```json
{
  "bot_token": "DÁN_BOT_TOKEN_VÀO_ĐÂY",
  "guild_id": "ID_SERVER_CỦA_BẠN (Tùy chọn, để đồng bộ lệnh nhanh)",
  "auto_create_roles": true
}
```
*(Nếu không điền trước, khi chạy bot lần đầu chương trình sẽ tự động hỏi và lưu lại cho bạn)*.

### Bước 3: Khởi Chạy
* Khởi chạy Bot trên nền tảng hosting hoặc nhấp đúp vào file **`run.bat`** trên máy tính.

---

## 🎮 Cách Sử Dụng Trong Discord

1. Vào kênh bất kỳ trong server (nơi bạn muốn đặt bảng chọn nhà).
2. Gõ lệnh:
   ```text
   /hypesquad-panel
   ```
3. Bot sẽ gửi ngay bảng điều khiển Embed lộng lẫy kèm các nút bấm tương tác.
4. Bất kỳ ai trong server bấm vào nút nhà nào đều sẽ nhận được vai trò và hướng dẫn kích hoạt huy hiệu tương ứng!
