#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=============================================================================
🌟 DISCORD HYPESQUAD SELECTOR BOT PRO
=============================================================================
Bot Discord chuyên nghiệp tích hợp giao diện Embed và các Nút Bấm Tương Tác
(Interactive Buttons & Modals) cho phép thành viên chọn và nhận huy hiệu HypeSquad
(Bravery 💜, Brilliance 🧡, Balance 🩵) trực tiếp trong server Discord.
=============================================================================
"""

import os
import sys
import json
import asyncio
import aiohttp
from typing import Optional, Union

# Cấu hình UTF-8 cho Windows CMD/PowerShell
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    os.system("")

import discord
from discord.ext import commands
from discord import app_commands

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    MAGENTA = '\033[35m'
    RESET = '\033[0m'


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"{Colors.RED}[LỖI]{Colors.RESET} Không đọc được file config.json: {e}")
    return {
        "bot_token": "",
        "guild_id": "",
        "auto_create_roles": True,
        "role_names": {
            "1": "House of Bravery",
            "2": "House of Brilliance",
            "3": "House of Balance"
        },
        "role_colors": {
            "1": "9b59b6",
            "2": "e67e22",
            "3": "1abc9c"
        }
    }


def save_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


CONFIG = load_config()

HOUSES = {
    1: {
        "name": "House of Bravery",
        "emoji": "💜",
        "color": 0x9B59B6,
        "desc": "Dũng cảm, kiên định, luôn tiên phong trong mọi thử thách.",
        "icon": "https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png"
    },
    2: {
        "name": "House of Brilliance",
        "emoji": "🧡",
        "color": 0xE67E22,
        "desc": "Xuất chúng, sáng tạo, thông thái và đầy nhiệt huyết.",
        "icon": "https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png"
    },
    3: {
        "name": "House of Balance",
        "emoji": "🩵",
        "color": 0x1ABC9C,
        "desc": "Cân bằng, hài hòa, đem lại hòa bình và sự ổn định.",
        "icon": "https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png"
    }
}


async def request_discord_hypesquad(token: str, house_id: int) -> int:
    """Gửi yêu cầu tới API Discord để nhận hoặc gỡ HypeSquad"""
    clean_token = token.strip().strip('"').strip("'")
    url = "https://discord.com/api/v9/hypesquad/online"
    headers = {
        "Authorization": clean_token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        if house_id == 0:
            async with session.delete(url, headers=headers) as resp:
                return resp.status
        else:
            payload = {"house_id": house_id}
            async with session.post(url, headers=headers, json=payload) as resp:
                return resp.status


async def assign_server_role(guild: discord.Guild, member: discord.Member, house_id: int) -> Optional[str]:
    """Tự động kiểm tra / tạo role và gán role nhà tương ứng trong server"""
    if not CONFIG.get("auto_create_roles", True):
        return None
    if not guild.me.guild_permissions.manage_roles:
        return "⚠️ Bot chưa có quyền **Quản Lý Vai Trò (Manage Roles)** nên chưa gán role được."

    role_names = CONFIG.get("role_names", {
        "1": "House of Bravery",
        "2": "House of Brilliance",
        "3": "House of Balance"
    })
    role_colors = CONFIG.get("role_colors", {
        "1": "9b59b6",
        "2": "e67e22",
        "3": "1abc9c"
    })

    # Tìm hoặc tạo 3 role
    house_roles = {}
    for hid_str, rname in role_names.items():
        hid = int(hid_str)
        existing_role = discord.utils.get(guild.roles, name=rname)
        if not existing_role:
            try:
                hex_color = int(role_colors.get(hid_str, "5865f2"), 16)
                existing_role = await guild.create_role(
                    name=rname,
                    color=discord.Color(hex_color),
                    reason="HypeSquad Selector Bot Auto Role Setup"
                )
            except Exception as e:
                print(f"Lỗi tạo role {rname}: {e}")
        house_roles[hid] = existing_role

    # Xóa các role nhà khác của member
    roles_to_remove = [r for hid, r in house_roles.items() if r and r in member.roles and hid != house_id]
    if roles_to_remove:
        try:
            await member.remove_roles(*roles_to_remove, reason="Thay đổi nhà HypeSquad")
        except Exception:
            pass

    # Gán role nhà mới
    if house_id in house_roles and house_roles[house_id]:
        target_role = house_roles[house_id]
        if target_role not in member.roles:
            try:
                await member.add_roles(target_role, reason="Nhận nhà HypeSquad qua Bot")
                return f"✅ Đã gán vai trò **@{target_role.name}** cho bạn trong server!"
            except Exception as e:
                return f"⚠️ Không thể gán vai trò: Bot cần nằm ở vị trí cao hơn role này trong mục cài đặt Server."
        else:
            return f"ℹ️ Bạn đã có sẵn vai trò **@{target_role.name}**."
    elif house_id == 0:
        return "✅ Đã gỡ bỏ các vai trò HypeSquad trong server!"

    return None


class TokenModal(discord.ui.Modal):
    """Cửa sổ Modal mở ra cho người dùng nhập Token hoặc lấy mã Console"""

    def __init__(self, house_id: int, house_name: str, emoji: str):
        # Tiêu đề Modal trên Discord không được chứa Custom Emoji (<:name:id>), chỉ nhận Unicode
        clean_emoji = "💜" if house_id == 1 else "🧡" if house_id == 2 else "🩵" if house_id == 3 else "❌"
        super().__init__(title=f"{clean_emoji} Kích Hoạt {house_name}")
        self.house_id = house_id
        self.house_name = house_name
        self.emoji = str(emoji) if emoji else clean_emoji

        self.token_input = discord.ui.TextInput(
            label="Token Discord (Để kích hoạt vào Profile)",
            style=discord.TextStyle.short,
            placeholder="Dán token của bạn vào đây (Bỏ trống nếu chỉ lấy Role)...",
            required=False,
            min_length=0,
            max_length=150
        )
        self.add_item(self.token_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        token = self.token_input.value.strip()

        role_msg = ""
        if interaction.guild and isinstance(interaction.user, discord.Member):
            role_result = await assign_server_role(interaction.guild, interaction.user, self.house_id)
            if role_result:
                role_msg = f"\n\n{role_result}"

        # Trường hợp 1: Người dùng nhập Token trực tiếp
        if token:
            status = await request_discord_hypesquad(token, self.house_id)
            if status == 204:
                embed = discord.Embed(
                    title=f"{self.emoji} Kích Hoạt Thành Công!",
                    description=(
                        f"🎉 Chúc mừng bạn đã chính thức tham gia **{self.house_name}**!\n"
                        f"Huy hiệu đã được thêm trực tiếp vào hồ sơ cá nhân Discord của bạn."
                        f"{role_msg}\n\n"
                        f"💡 *Nhấn phím **F5** trên Discord hoặc mở lại Profile để chiêm ngưỡng huy hiệu mới!*"
                    ),
                    color=HOUSES.get(self.house_id, {}).get("color", 0x5865F2)
                )
                embed.set_footer(text="🔒 Token không được lưu trữ • Hoàn toàn bảo mật")
                await interaction.followup.send(embed=embed, ephemeral=True)
            elif status == 401:
                await interaction.followup.send(
                    f"❌ **Lỗi: Token không hợp lệ hoặc đã hết hạn!**\n"
                    f"Vui lòng lấy lại Token mới hoặc sử dụng phương pháp Console F12 bên dưới.{role_msg}",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"⚠️ Máy chủ Discord trả về mã trạng thái: `{status}`.{role_msg}",
                    ephemeral=True
                )
            return

        # Trường hợp 2: Người dùng bỏ trống Token -> Cung cấp mã 1-Click F12 Console
        console_code = (
            f"fetch('/api/v9/hypesquad/online',{{method:'{'POST' if self.house_id != 0 else 'DELETE'}',"
            f"headers:{{Authorization:(webpackChunkdiscord_app.push([[Symbol()],{{}},o=>{{for(let e of Object.values(o.c)){{try{{if(e.exports?.getToken)return t=e.exports.getToken()}}catch{{}}}}}}]),t),"
            f"'Content-Type':'application/json'}},"
            f"{f'body:JSON.stringify({{house_id:{self.house_id}}})' if self.house_id != 0 else ''}"
            f"}}).then(r=>alert(r.status===204?'🎉 Thành công! F5 xem huy hiệu':'Lỗi: '+r.status));"
        )

        embed = discord.Embed(
            title=f"{self.emoji} Hướng Dẫn Kích Hoạt {self.house_name}",
            description=(
                f"Bạn đã chọn **{self.house_name}**.{role_msg}\n\n"
                f"Vì bạn không nhập Token, hãy dùng mã 1-Click tự động kích hoạt trực tiếp trên trình duyệt mà không cần chia sẻ Token:\n\n"
                f"**📌 3 Bước Siêu Tốc (10 Giây):**\n"
                f"1️⃣ Mở [Discord Web](https://discord.com/app) trên máy tính.\n"
                f"2️⃣ Bấm **F12** ➜ Chuyển qua tab **Console** (nếu hiện chữ đỏ, gõ `allow pasting` rồi ấn Enter).\n"
                f"3️⃣ Dán đoạn mã bên dưới rồi ấn **Enter**:"
            ),
            color=HOUSES.get(self.house_id, {}).get("color", 0x5865F2)
        )
        embed.add_field(
            name="📋 Sao chép mã 1 dòng bên dưới:",
            value=f"```javascript\n{console_code}\n```",
            inline=False
        )
        embed.set_footer(text="🔒 An toàn tuyệt đối • Chạy trực tiếp trong trình duyệt của bạn")
        await interaction.followup.send(embed=embed, ephemeral=True)


def get_custom_emoji(guild: Optional[discord.Guild], client: Optional[discord.Client], target_name: str, fallback: str) -> Union[discord.Emoji, str]:
    """Tìm custom emoji (kể cả emoji động Animated) trong server theo tên"""
    clean_target = target_name.strip(":").lower()

    # 1. Tìm trong server hiện tại
    if guild:
        for e in guild.emojis:
            if e.name.lower() == clean_target:
                return e
        for e in guild.emojis:
            if clean_target in e.name.lower() or e.name.lower() in clean_target:
                return e

    # 2. Tìm trong danh sách toàn bộ emoji mà bot thấy
    if client:
        for e in client.emojis:
            if e.name.lower() == clean_target:
                return e
        for e in client.emojis:
            if clean_target in e.name.lower() or e.name.lower() in clean_target:
                return e

    return fallback


def get_house_member_count(guild: Optional[discord.Guild], house_id: int) -> int:
    """Đếm số lượng thành viên đang sở hữu Role của nhà HypeSquad trong server"""
    if not guild:
        return 0
    role_names = CONFIG.get("role_names", {
        "1": "House of Bravery",
        "2": "House of Brilliance",
        "3": "House of Balance"
    })
    target_name = role_names.get(str(house_id), "").lower()
    for role in guild.roles:
        if target_name in role.name.lower() or role.name.lower() in target_name:
            return len(role.members)
    return 0


class HypeSquadPanelView(discord.ui.View):
    """View chứa các nút bấm tương tác vĩnh viễn (Persistent View)"""

    def __init__(self, guild: Optional[discord.Guild] = None, client: Optional[discord.Client] = None):
        super().__init__(timeout=None)
        if guild or client:
            bravery_e = get_custom_emoji(guild, client, "8495hypesquadhouseofbravery", "💜")
            brilliance_e = get_custom_emoji(guild, client, "7693hypesquadhouseofbrilliance", "🧡")
            balance_e = get_custom_emoji(guild, client, "1050hypesquadhouseofbalance", "🩵")

            self.btn_bravery.emoji = bravery_e
            self.btn_brilliance.emoji = brilliance_e
            self.btn_balance.emoji = balance_e

    @discord.ui.button(
        label="Bravery",
        emoji="💜",
        style=discord.ButtonStyle.primary,
        custom_id="hypesquad_btn_bravery"
    )
    async def btn_bravery(self, interaction: discord.Interaction, button: discord.ui.Button):
        custom_e = get_custom_emoji(interaction.guild, interaction.client, "8495hypesquadhouseofbravery", "💜")
        await interaction.response.send_modal(TokenModal(1, "House of Bravery", str(custom_e)))

    @discord.ui.button(
        label="Brilliance",
        emoji="🧡",
        style=discord.ButtonStyle.danger,
        custom_id="hypesquad_btn_brilliance"
    )
    async def btn_brilliance(self, interaction: discord.Interaction, button: discord.ui.Button):
        custom_e = get_custom_emoji(interaction.guild, interaction.client, "7693hypesquadhouseofbrilliance", "🧡")
        await interaction.response.send_modal(TokenModal(2, "House of Brilliance", str(custom_e)))

    @discord.ui.button(
        label="Balance",
        emoji="🩵",
        style=discord.ButtonStyle.success,
        custom_id="hypesquad_btn_balance"
    )
    async def btn_balance(self, interaction: discord.Interaction, button: discord.ui.Button):
        custom_e = get_custom_emoji(interaction.guild, interaction.client, "1050hypesquadhouseofbalance", "🩵")
        await interaction.response.send_modal(TokenModal(3, "House of Balance", str(custom_e)))

    @discord.ui.button(
        label="Gỡ Huy Hiệu",
        emoji="❌",
        style=discord.ButtonStyle.secondary,
        custom_id="hypesquad_btn_leave"
    )
    async def btn_leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TokenModal(0, "Gỡ Bỏ Huy Hiệu", "❌"))


def create_panel_embed(guild: Optional[discord.Guild] = None, client: Optional[discord.Client] = None) -> discord.Embed:
    """Tạo Embed giao diện bảng điều khiển đẹp mắt theo chuẩn Pro VIP"""
    bravery_e = get_custom_emoji(guild, client, "8495hypesquadhouseofbravery", "💜")
    brilliance_e = get_custom_emoji(guild, client, "7693hypesquadhouseofbrilliance", "🧡")
    balance_e = get_custom_emoji(guild, client, "1050hypesquadhouseofbalance", "🩵")

    bravery_count = get_house_member_count(guild, 1)
    brilliance_count = get_house_member_count(guild, 2)
    balance_count = get_house_member_count(guild, 3)

    embed = discord.Embed(
        title="🌟 DISCORD HYPESQUAD SELECTOR • BẢNG CHỌN HUY HIỆU",
        description=(
            "> ### ✨ GIA NHẬP HYPESQUAD • TỎA SÁNG CÁ TÍNH!\n"
            "> Hãy lựa chọn một trong **ba ngôi nhà danh giá** của Discord để nhận huy hiệu chính thức "
            "trên trang cá nhân và mở khóa vai trò đổi màu tên độc quyền trong máy chủ!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0x5865F2  # Blurple
    )

    # Thêm Author Header mang thương hiệu server
    if guild:
        server_icon = guild.icon.url if guild.icon else None
        embed.set_author(
            name=f"⚡ {guild.name} • Official HypeSquad Hub",
            icon_url=server_icon
        )
    elif client and client.user:
        embed.set_author(
            name=f"⚡ {client.user.name} • Official HypeSquad Hub",
            icon_url=client.user.display_avatar.url
        )

    # 3 Cột Ngôi Nhà HypeSquad với biểu tượng động và đếm số lượng thành viên
    embed.add_field(
        name=f"{bravery_e} House of Bravery",
        value=(
            "> **Châm ngôn:** Dũng Cảm & Tiên Phong\n"
            "> **Màu sắc:** Tím Hoàng Gia (`#9B59B6`)\n"
            f"> **Thành viên:** `{bravery_count} người`"
        ),
        inline=True
    )
    embed.add_field(
        name=f"{brilliance_e} House of Brilliance",
        value=(
            "> **Châm ngôn:** Xuất Chúng & Sáng Tạo\n"
            "> **Màu sắc:** Cam Nhiệt Huyết (`#E67E22`)\n"
            f"> **Thành viên:** `{brilliance_count} người`"
        ),
        inline=True
    )
    embed.add_field(
        name=f"{balance_e} House of Balance",
        value=(
            "> **Châm ngôn:** Cân Bằng & Hòa Bình\n"
            "> **Màu sắc:** Xanh Ngọc Bích (`#1ABC9C`)\n"
            f"> **Thành viên:** `{balance_count} người`"
        ),
        inline=True
    )

    embed.add_field(
        name="👑 Đặc Quyền & Tính Năng Tự Động:",
        value=(
            "> • **Vai Trò Server:** Nhận ngay Role đổi màu tên nổi bật trong danh sách thành viên.\n"
            "> • **Profile Badge:** Mở khóa huy hiệu HypeSquad thật xuất hiện trên hồ sơ cá nhân vĩnh viễn!"
        ),
        inline=False
    )

    embed.add_field(
        name="⚡ Cách Thức Nhận:",
        value=(
            "> 👉 **Bấm vào một trong các nút bên dưới** để nhận ngôi nhà bạn yêu thích!\n"
            "-# 🔒 Hệ thống kích hoạt an toàn 24/7 • Hoàn toàn bảo mật"
        ),
        inline=False
    )

    embed.set_thumbnail(url="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png")
    
    # Thiết lập Banner Đồ Họa Ngang HypeSquad
    banner_url = CONFIG.get("banner_url", "").strip() or "https://raw.githubusercontent.com/truong2903/bot_discord/main/banner.png"
    embed.set_image(url=banner_url)

    embed.set_footer(
        text="HypeSquad System v2.0 • Hoạt động 24/7 • An toàn 100%",
        icon_url="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png"
    )
    return embed


# Khởi tạo Bot với intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    # Đăng ký Persistent View để các nút bấm hoạt động mãi mãi kể cả khởi động lại bot
    bot.add_view(HypeSquadPanelView())

    # Đồng bộ Slash Commands
    guild_id = os.getenv("GUILD_ID", "").strip() or CONFIG.get("guild_id")
    if guild_id and str(guild_id).isdigit():
        guild_obj = discord.Object(id=int(guild_id))
        bot.tree.copy_global_to(guild=guild_obj)
        synced = await bot.tree.sync(guild=guild_obj)
        print(f"{Colors.GREEN}[✓]{Colors.RESET} Đã đồng bộ {len(synced)} lệnh Slash cho Guild ID: {guild_id}")
    else:
        synced = await bot.tree.sync()
        print(f"{Colors.GREEN}[✓]{Colors.RESET} Đã đồng bộ {len(synced)} lệnh Slash toàn cầu (Global)!")

    print(f"\n{Colors.GREEN}====================================================================={Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}    🤖 BOT ĐÃ SẴN SÀNG HOẠT ĐỘNG!{Colors.RESET}")
    print(f"{Colors.GREEN}====================================================================={Colors.RESET}")
    print(f" • Tên Bot    : {Colors.YELLOW}{bot.user.name}#{bot.user.discriminator}{Colors.RESET}")
    print(f" • Bot ID     : {bot.user.id}")
    print(f" • Servers    : Đang kết nối {len(bot.guilds)} máy chủ")
    print(f" • Lệnh khả dụng:")
    print(f"   - {Colors.CYAN}/hypesquad-panel{Colors.RESET}  : Gửi bảng điều khiển Embed có NÚT BẤM tương tác")
    print(f"   - {Colors.CYAN}/ping{Colors.RESET}             : Kiểm tra phản hồi bot")
    print(f"{Colors.GREEN}====================================================================={Colors.RESET}\n")


@bot.tree.command(name="hypesquad-panel", description="Gửi bảng điều khiển chọn huy hiệu HypeSquad với các nút bấm")
@app_commands.default_permissions(manage_guild=True)
async def cmd_panel(interaction: discord.Interaction):
    embed = create_panel_embed(guild=interaction.guild, client=bot)
    view = HypeSquadPanelView(guild=interaction.guild, client=bot)
    
    banner_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banner.png")
    if os.path.exists(banner_path):
        banner_file = discord.File(banner_path, filename="banner.png")
        embed.set_image(url="attachment://banner.png")
        await interaction.channel.send(embed=embed, file=banner_file, view=view)
    else:
        await interaction.channel.send(embed=embed, view=view)

    await interaction.response.send_message("✅ Đã gửi bảng điều khiển HypeSquad thành công!", ephemeral=True)


@bot.tree.command(name="ping", description="Kiểm tra độ trễ phản hồi của Bot")
async def cmd_ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Độ trễ hiện tại: `{latency}ms`", ephemeral=True)


def banner():
    print(f"""{Colors.CYAN}
  ╔═══════════════════════════════════════════════════════════╗
  ║       🌟 DISCORD HYPESQUAD SELECTOR BOT PRO               ║
  ║  Hệ thống Embed & Nút Bấm Tương Tác Chọn Huy Hiệu         ║
  ╚═══════════════════════════════════════════════════════════╝{Colors.RESET}
""")


def main():
    banner()
    cfg = load_config()
    token = os.getenv("BOT_TOKEN", "").strip() or os.getenv("DISCORD_TOKEN", "").strip() or cfg.get("bot_token", "").strip()

    if not token:
        print(f"{Colors.YELLOW}[CẦN CẤU HÌNH]{Colors.RESET} Chưa tìm thấy Token của Bot Discord.")
        user_input = input(f"{Colors.CYAN}👉 Nhập Bot Token của bạn: {Colors.RESET}").strip()
        if not user_input:
            print(f"{Colors.RED}[LỖI]{Colors.RESET} Token không được để trống! Thoát chương trình.")
            sys.exit(1)
        token = user_input
        cfg["bot_token"] = token

        guild_in = input(f"{Colors.CYAN}👉 Nhập Guild ID (Server ID) để test lệnh tức thì (bỏ trống nếu muốn dùng Global): {Colors.RESET}").strip()
        if guild_in:
            cfg["guild_id"] = guild_in
        save_config(cfg)
        print(f"{Colors.GREEN}[✓]{Colors.RESET} Đã lưu cấu hình vào file config.json!\n")

    try:
        bot.run(token)
    except discord.LoginFailure:
        print(f"\n{Colors.RED}[LỖI]{Colors.RESET} Bot Token không chính xác! Vui lòng kiểm tra lại token trong file config.json.")
    except Exception as e:
        print(f"\n{Colors.RED}[LỖI]{Colors.RESET} Đã xảy ra sự cố khi chạy bot: {e}")


if __name__ == "__main__":
    main()
