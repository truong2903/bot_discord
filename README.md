# 🌟 DISCORD HYPESQUAD SELECTOR BOT PRO

Dự án Bot Discord chuyên nghiệp với giao diện **Rich Embed** và các **Nút Bấm Tương Tác (Interactive Buttons)** giúp thành viên máy chủ chọn và nhận huy hiệu **HypeSquad** (Bravery 💜, Brilliance 🧡, Balance 🩵) trực tiếp từ Discord.

---

## 📸 Hình Thức Giao Diện (Giống Ảnh Mẫu)

Bot sẽ gửi một bảng tin nhắn dạng Embed kèm hàng nút bấm phía dưới:

```text
┌─────────────────────────────────────────────────────────────┐
│ 🌟 DISCORD HYPESQUAD SELECTOR • BẢNG CHỌN HUY HIỆU          │
│                                                             │
│ 💜 House of Bravery      • Dũng Cảm & Tiên Phong (#9B59B6)  │
│ 🧡 House of Brilliance   • Xuất Chúng & Sáng Tạo (#E67E22)  │
│ 🩵 House of Balance      • Cân Bằng & Bình Thản (#1ABC9C)   │
│                                                             │
│ 👑 Tự động gán Role trong Server khi chọn nhà!              │
│ ⚡ Bấm các nút bên dưới để nhận huy hiệu!                  │
└─────────────────────────────────────────────────────────────┘
  [ 💜 Bravery ] [ 🧡 Brilliance ] [ 🩵 Balance ] [ ❌ Gỡ ] [ 🌐 Web 1-Click ]
```

---

## ✨ Tính Năng Nổi Bật

1. **Giao diện Nút Bấm chuẩn Discord Interaction:**
   - Người dùng bấm trực tiếp vào nút màu của nhà mình thích.
   - Nút bấm hoạt động vĩnh viễn (**Persistent View**), không bị mất tác dụng sau khi tắt hoặc khởi động lại Bot.

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
* Nhấp đúp vào file **`run.bat`** để khởi chạy Bot.

---

## 🎮 Cách Sử Dụng Trong Discord

1. Vào kênh bất kỳ trong server (nơi bạn muốn đặt bảng chọn nhà).
2. Gõ lệnh:
   ```text
   /hypesquad-panel
   ```
3. Bot sẽ gửi ngay bảng điều khiển Embed lộng lẫy kèm 5 nút bấm tương tác.
4. Bất kỳ ai trong server bấm vào nút nhà nào đều sẽ nhận được vai trò và hướng dẫn kích hoạt huy hiệu tương ứng!
