# 🌟 DISCORD HYPESQUAD SELECTOR BOT PRO

Dự án Bot Discord chuyên nghiệp với giao diện **Rich Embed** và các **Nút Bấm Tương Tác (Interactive Buttons)** giúp thành viên máy chủ chọn và nhận huy hiệu **HypeSquad** (Bravery 💜, Brilliance 🧡, Balance 🩵) trực tiếp từ Discord.

---

## 📸 Hình Thức Giao Diện (Chuẩn Pro VIP)

Bot sẽ gửi một bảng tin nhắn dạng Embed kèm hàng 4 nút bấm gọn gàng phía dưới:

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
│ ⚡ Bấm một trong các nút bên dưới để nhận ngôi nhà!         │
└─────────────────────────────────────────────────────────────┘
      [ 💜 Bravery ] [ 🧡 Brilliance ] [ 🩵 Balance ] [ ❌ Gỡ ]
```

---

## ✨ Tính Năng Nổi Bật

1. **Giao diện Nút Bấm Chuẩn Discord Interaction (Gọn Gàng, Sang Trọng):**
   - Hàng **4 Nút Bấm màu sắc** trực quan, tối giản, không bị rối mắt.
   - Hiển thị **Author Header** mang tên và avatar chính thức của Server.
   - Thống kê **Số lượng thành viên trực tiếp** đang ở mỗi nhà trong Server.
   - Nút bấm hoạt động vĩnh viễn (**Persistent View**), không bị mất tác dụng sau khi tắt hoặc khởi động lại Bot.
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

### 1. Bảng Chọn Huy Hiệu HypeSquad
* Gõ lệnh:
  ```text
  /hypesquad-panel
  ```
* Bot sẽ gửi ngay bảng điều khiển Embed HypeSquad kèm các nút bấm tương tác (Bravery, Brilliance, Balance, Gỡ).

### 2. Bảng Điều Khiển AutoMod Badge (Uses AutoMod)
* Gõ lệnh:
  ```text
  /tao_server
  ```
* **Cơ chế hoạt động:**
  - Bot gửi bảng điều khiển Embed chuẩn phong cách Pro VIP kèm các nút bấm tương tác:
    - `[🚀 Triển Khai 100+ Rules]`: Tự động quét và đẩy đủ 102 quy tắc AutoMod lên tất cả server bot tham gia.
    - `[🔍 Kiểm Tra Tiến Độ]`: Xem báo cáo cờ `16777216`, số lượng server và rules active theo thời gian thực.
    - `[🔗 Mời Bot Vào Server]`: Link mời bot với quyền Quản trị viên để thêm vào các server của bạn.

### 3. Bảng Điều Khiển Verified Server Badge (Tích Xanh 🟢)
* Gõ lệnh:
  ```text
  /verified_server
  ```
  *(hoặc `/verified_panel`)*
* **Cơ chế hoạt động:**
  - Bot gửi bảng điều khiển **Verified Server Hub** chuẩn phong cách NCT Pro VIP kèm bộ 6 nút bấm tương tác:
    - `[ 🔍 Audit Máy Chủ ]`: Quét máy chủ hiện tại, đánh giá tiêu chuẩn Community, rules channel, explicit content filter và chấm điểm Readiness (0 - 100%).
    - `[ ⚡ Auto-Setup Kênh & Bảo Mật ]`: Tự động tạo 5 kênh chuẩn game (`#rules-and-info`, `#game-announcements`, `#patch-notes`, `#community-chat`, `#bug-reports`) và nâng cấp bộ lọc an toàn cho máy chủ.
    - `[ 🎮 Tra Cứu Steam Game ]`: Mở Modal Popup nhập Steam App ID để bot tra cứu thông tin game trên Steam Store, kiểm tra trạng thái Playable và quét link Discord.
    - `[ 🔗 Tạo Link Proof Steam ]`: Mở Modal Popup nhập Invite link + Proof Token để sinh đường dẫn chuẩn hóa dán vào Steamworks Partner Admin.
    - `[ 📖 Cẩm Nang Claim A-Z ]`: Hướng dẫn chi tiết 5 bước từ lúc có game trên Steam đến khi Discord cấp tích xanh.
    - `[ 🚀 Discord Developer Portal ]`: Nút link mở trực tiếp trang quản trị ứng dụng Discord.
