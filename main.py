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
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Union, List, Tuple

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


# =============================================================================
# 🤖 AUTOMOD BADGE (USES AUTOMOD) MODULE & SLASH COMMANDS
# =============================================================================

FLAG_AUTOMOD_BADGE = 16777216  # 1 << 24 = APPLICATION_AUTO_MODERATION_RULE_CREATE_BADGE


async def api_create_automod_rule(token: str, guild_id: int, rule_idx: int) -> bool:
    """Tạo 1 quy tắc AutoMod kiểu Keyword trên server"""
    url = f"https://discord.com/api/v10/guilds/{guild_id}/auto-moderation/rules"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": f"AutoMod Protect #{rule_idx}",
        "event_type": 1,
        "trigger_type": 1,
        "trigger_metadata": {
            "keyword_filter": [f"spam_filter_{rule_idx}*", f"badword_{rule_idx}*"]
        },
        "actions": [
            {
                "type": 1,
                "metadata": {
                    "custom_message": "Tin nhắn bị chặn bởi AutoMod Rule bảo vệ máy chủ."
                }
            }
        ],
        "enabled": True
    }
    timeout = aiohttp.ClientTimeout(total=15)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                return resp.status in (200, 201)
    except Exception:
        return False


async def api_get_guild_rules(token: str, guild_id: int) -> list:
    """Lấy danh sách các rule AutoMod trong guild"""
    url = f"https://discord.com/api/v10/guilds/{guild_id}/auto-moderation/rules"
    headers = {"Authorization": f"Bot {token}"}
    timeout = aiohttp.ClientTimeout(total=15)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception:
        pass
    return []


async def api_get_app_info(token: str) -> tuple:
    """Lấy thông tin Application Flags để kiểm tra cờ 16777216"""
    url = "https://discord.com/api/v10/oauth2/applications/@me"
    headers = {"Authorization": f"Bot {token}"}
    timeout = aiohttp.ClientTimeout(total=15)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    flags = int(data.get("flags", 0))
                    is_public = bool(data.get("bot_public", False))
                    return flags, is_public
    except Exception:
        pass
    return 0, False


async def count_total_automod_rules(client: commands.Bot) -> int:
    """Đếm tổng số quy tắc AutoMod đang active trên tất cả server bot có mặt"""
    token = client.http.token
    total = 0
    for guild in client.guilds:
        rules = await api_get_guild_rules(token, guild.id)
        active = [r for r in rules if r.get("enabled", False)]
        total += len(active)
    return total


def create_automod_embed(guild_count: int, active_rules: int, flags: int, is_public: bool, client: Optional[discord.Client] = None) -> discord.Embed:
    """Tạo Embed AutoMod chuẩn giao diện VIP đồng bộ phong cách NCT Hub"""
    has_badge = bool((flags & FLAG_AUTOMOD_BADGE) != 0)

    embed = discord.Embed(
        title="🤖 DISCORD AUTOMOD SYSTEM • BẢNG ĐIỀU KHIỂN & TỰ ĐỘNG HÓA",
        description=(
            "> ### ✨ KÍCH HOẠT 100+ QUY TẮC • MỞ KHÓA HUY HIỆU USES AUTOMOD\n"
            "> Hệ thống hỗ trợ tự động rải đủ 102 quy tắc AutoMod (Keyword Filter) chuẩn mực "
            "trên các máy chủ của bạn để mở khóa cờ `16777216` (`2^24`) cho Bot!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0x23A55A  # Discord Green
    )

    bot_name = client.user.name if client and client.user else "NCT_bot"
    bot_avatar = client.user.display_avatar.url if client and client.user else "https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png"

    embed.set_author(
        name=f"⚡ {bot_name} • Official AutoMod Hub",
        icon_url=bot_avatar
    )

    # 3 Cột thống kê đồng bộ giao diện HypeSquad
    status_badge_text = "Đã nhận huy hiệu" if has_badge else ("Chờ duyệt 12-24h" if active_rules >= 100 else "Đang cày tiến độ")
    server_status = "Đã đủ server" if guild_count >= 17 else f"Cần thêm {17 - guild_count} server"

    embed.add_field(
        name="🌐 Server Đã Có",
        value=(
            "> **Châm ngôn:** Kết nối server\n"
            f"> **Số lượng:** `{guild_count} / 17 server`\n"
            f"> **Trạng thái:** `{server_status}`"
        ),
        inline=True
    )
    embed.add_field(
        name="🛡️ AutoMod Rules",
        value=(
            "> **Châm ngôn:** Bảo vệ tự động\n"
            f"> **Số lượng:** `{active_rules} / 100 rules`\n"
            f"> **Tỷ lệ:** `{active_rules}% hoàn tất`"
        ),
        inline=True
    )
    embed.add_field(
        name="🎖️ Cờ Huy Hiệu",
        value=(
            "> **Châm ngôn:** Uses AutoMod\n"
            "> **Mã cờ:** `16777216 (2^24)`\n"
            f"> **Trạng thái:** `{status_badge_text}`"
        ),
        inline=True
    )

    needed_servers = max(0, 17 - guild_count)

    embed.add_field(
        name="👑 Hướng Dẫn Các Bước Hoàn Tất:",
        value=(
            f"> • **Bước 1 (Tạo Server):** Bấm dấu **`[+]`** trên Discord tạo thêm **{needed_servers} server** cá nhân trống (~1 phút).\n"
            f"> • **Bước 2 (Mời Bot):** Bấm nút **[🔗 Mời Bot Vào Server]** bên dưới để thêm bot vào các server vừa tạo.\n"
            f"> • **Bước 3 (Nạp 102 Rules):** Bấm nút **[🚀 Triển Khai 100+ Rules]** để bot tự động nạp 6 quy tắc/server đến khi đủ 102 rules!\n"
            f"> • **Bước 4 (Kiểm Tra):** Bấm nút **[🔍 Kiểm Tra Tiến Độ]** để tra cứu cờ `16777216`."
        ),
        inline=False
    )

    embed.add_field(
        name="⚡ Các Nút Thao Tác Nhanh:",
        value=(
            "> 👉 **Bấm vào một trong các nút bên dưới** để điều khiển tiến trình lấy huy hiệu!\n"
            "-# 🔒 Hệ thống kích hoạt an toàn 24/7 • Chuẩn Discord REST API v10"
        ),
        inline=False
    )

    embed.set_thumbnail(url="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png")

    banner_url = CONFIG.get("banner_url", "").strip() or "https://raw.githubusercontent.com/truong2903/bot_discord/main/banner.png"
    embed.set_image(url=banner_url)

    embed.set_footer(
        text="AutoMod System v2.0 • Hoạt động 24/7 • An toàn 100%",
        icon_url="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png"
    )
    return embed


class AutoModPanelView(discord.ui.View):
    """View chứa các nút bấm điều khiển AutoMod Badge vĩnh viễn (Persistent View)"""

    def __init__(self, bot_client: Optional[commands.Bot] = None):
        super().__init__(timeout=None)
        if bot_client and bot_client.user:
            invite_url = f"https://discord.com/oauth2/authorize?client_id={bot_client.user.id}&permissions=8&scope=bot%20applications.commands"
            self.add_item(discord.ui.Button(
                label="Mời Bot Vào Server",
                style=discord.ButtonStyle.link,
                url=invite_url,
                emoji="🔗",
                row=1
            ))

    @discord.ui.button(
        label="Triển Khai 100+ Rules",
        emoji="🚀",
        style=discord.ButtonStyle.success,
        custom_id="automod_btn_deploy_rules",
        row=0
    )
    async def btn_deploy_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        bot_client: commands.Bot = interaction.client
        token = bot_client.http.token
        created_new = 0

        for guild in bot_client.guilds:
            existing = await api_get_guild_rules(token, guild.id)
            existing_keywords = [r for r in existing if r.get("trigger_type") == 1]
            slots = 6 - len(existing_keywords)
            for s in range(slots):
                rule_idx = len(existing_keywords) + s + 1
                if await api_create_automod_rule(token, guild.id, rule_idx):
                    created_new += 1
                await asyncio.sleep(0.8)

        total_rules = await count_total_automod_rules(bot_client)

        if total_rules >= 100:
            msg = (
                f"🎉 **XUẤT SẮC!** Bot hiện có tổng cộng **{total_rules}/100 quy tắc AutoMod đang hoạt động**!\n"
                f"✅ **ĐÃ ĐỦ 100% ĐIỀU KIỆN!** Discord sẽ quét và tự động gắn huy hiệu **Uses AutoMod** trong vòng 12 - 24 giờ tới."
            )
        else:
            needed = 100 - total_rules
            sv_needed = (needed + 5) // 6
            msg = (
                f"✅ Đã tạo thêm **{created_new} quy tắc mới**.\n"
                f"📊 Tổng số quy tắc hiện có: **{total_rules}/100 rules** (Còn thiếu **{needed} rules**, khoảng **{sv_needed} server** nữa).\n"
                f"👉 Hãy bấm nút **[🔗 Mời Bot Vào Server]** để thêm bot vào các server của bạn và bấm lại nút này nhé!"
            )

        await interaction.followup.send(msg, ephemeral=True)

    @discord.ui.button(
        label="Kiểm Tra Tiến Độ",
        emoji="🔍",
        style=discord.ButtonStyle.secondary,
        custom_id="automod_btn_check_status",
        row=0
    )
    async def btn_check_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        bot_client: commands.Bot = interaction.client
        token = bot_client.http.token

        flags, is_public = await api_get_app_info(token)
        has_badge = bool((flags & FLAG_AUTOMOD_BADGE) != 0)
        total_rules = await count_total_automod_rules(bot_client)
        guild_count = len(bot_client.guilds)

        badge_status = "✅ ĐÃ SỞ HỮU HUY HIỆU!" if has_badge else ("⏳ ĐANG CHỜ DISCORD QUÉT (12-24h)" if total_rules >= 100 else "⚙️ ĐANG TIẾN HÀNH CÀY")

        embed = discord.Embed(
            title="🔍 BÁO CÁO TIẾN TRÌNH HUY HIỆU USES AUTOMOD",
            color=0x23A55A if has_badge or total_rules >= 100 else 0xF0B232
        )
        embed.add_field(name="🤖 Trạng Thái Huy Hiệu", value=f"**{badge_status}**", inline=False)
        embed.add_field(name="🌐 Số Server Hiện Có", value=f"`{guild_count} / 17 server`", inline=True)
        embed.add_field(name="🛡️ AutoMod Active Rules", value=f"`{total_rules} / 100 rules`", inline=True)
        embed.add_field(name="🚩 Cờ Application Flags", value=f"`{flags}` (Bit 24: {'BẬT' if has_badge else 'TẮT'})", inline=True)
        embed.add_field(name="⚙️ Public Bot", value="✅ Bật (Hợp lệ)" if is_public else "❌ Tắt (Cần bật trong Developer Portal)", inline=True)

        await interaction.followup.send(embed=embed, ephemeral=True)


# =============================================================================
# 🟢 DISCORD VERIFIED SERVER & STEAM GAME CLAIMING SUITE (NCT HUB)
# =============================================================================

async def api_fetch_steam_game(app_id: str) -> Tuple[bool, dict]:
    """Truy vấn thông tin chi tiết của Game trên Steam Store bằng Steam API"""
    clean_id = str(app_id).strip()
    if not clean_id.isdigit():
        return False, {"error": "Steam App ID phải là chuỗi số nguyên hợp lệ (Ví dụ: 730, 105600, 252490)!"}

    url = f"https://store.steampowered.com/api/appdetails?appids={clean_id}&cc=us&l=english"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    timeout = aiohttp.ClientTimeout(total=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    app_data = data.get(clean_id, {})
                    if app_data.get("success"):
                        return True, app_data.get("data", {})
                    return False, {"error": f"Game với App ID `{clean_id}` không tồn tại hoặc chưa công khai trên Steam Store!"}
                return False, {"error": f"Steam API trả về mã lỗi: `{resp.status}`"}
    except Exception as e:
        return False, {"error": f"Không thể kết nối tới Steam Store API: {e}"}


async def api_check_steam_discord_link(app_id: str) -> Tuple[bool, Optional[str], str]:
    """Quét mã HTML trang cửa hàng Steam để tìm liên kết Discord công khai"""
    clean_id = str(app_id).strip()
    if not clean_id.isdigit():
        return False, None, "App ID không hợp lệ!"

    url = f"https://store.steampowered.com/app/{clean_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    timeout = aiohttp.ClientTimeout(total=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    html = await resp.text(errors="ignore")
                    patterns = [
                        r'https?://(?:www\.)?discord\.gg/[a-zA-Z0-9_\-]+',
                        r'https?://(?:www\.)?discord\.com/invite/[a-zA-Z0-9_\-]+'
                    ]
                    found = []
                    for pat in patterns:
                        for m in re.findall(pat, html, re.IGNORECASE):
                            if m not in found:
                                found.append(m)
                    if found:
                        return True, found[0], f"Đã tìm thấy link Discord trên Steam: `{', '.join(found)}`"
                    return False, None, "Chưa tìm thấy link Discord công khai trên trang Steam Store của game."
                return False, None, f"Không thể đọc trang Steam Store (Mã HTTP `{resp.status}`)"
    except Exception as e:
        return False, None, f"Lỗi quét trang Steam: {e}"


def generate_steam_proof_url(invite_code_or_url: str, proof_token: str) -> str:
    """Sinh đường dẫn mời Discord có đính kèm mã Proof Token theo chuẩn Discord Developer Portal"""
    clean_invite = invite_code_or_url.strip()
    if clean_invite.startswith("https://discord.gg/"):
        base = clean_invite
    elif clean_invite.startswith("discord.gg/"):
        base = f"https://{clean_invite}"
    elif clean_invite.startswith("http"):
        base = clean_invite
    else:
        base = f"https://discord.gg/{clean_invite}"

    clean_proof = proof_token.strip()
    if not clean_proof:
        return base

    delimiter = "&" if "?" in base else "?"
    return f"{base}{delimiter}discord_proof={clean_proof}"


def audit_guild_readiness(guild: discord.Guild) -> Tuple[int, str, List[dict]]:
    """Đánh giá chi tiết mức độ sẵn sàng đạt chuẩn Verified Server của một Guild"""
    features = guild.features
    is_verified = "VERIFIED" in features
    is_community = "COMMUNITY" in features
    rules_ok = bool(guild.rules_channel)
    updates_ok = bool(guild.public_updates_channel)
    filter_ok = guild.explicit_content_filter == discord.ContentFilter.all_members
    verif_ok = guild.verification_level.value >= 2  # Medium (2), High (3), or Very High (4)
    mfa_ok = guild.mfa_level.value >= 1

    checks = []
    score = 0

    if is_verified:
        score = 100
        checks.append({
            "status": "PASS",
            "title": "Huy Hiệu Verified Server",
            "desc": "🌟 Máy chủ đã sở hữu huy hiệu Tích Xanh chính thức từ Discord!"
        })
    else:
        # Community
        if is_community:
            score += 30
            checks.append({"status": "PASS", "title": "Chế Độ Cộng Đồng (Community)", "desc": "Đã BẬT tính năng Community trong Server Settings."})
        else:
            checks.append({"status": "FAIL", "title": "Chế Độ Cộng Đồng (Community)", "desc": "Chưa bật Community. Vào Server Settings > Enable Community."})

        # Rules channel
        if rules_ok:
            score += 15
            checks.append({"status": "PASS", "title": "Kênh Quy Định (#rules)", "desc": f"Đã cấu hình kênh quy định: <#{guild.rules_channel.id}>."})
        else:
            checks.append({"status": "WARN", "title": "Kênh Quy Định (#rules)", "desc": "Chưa chỉ định kênh quy định chính thức của Server."})

        # Updates channel
        if updates_ok:
            score += 15
            checks.append({"status": "PASS", "title": "Kênh Thông Báo Cập Nhật", "desc": f"Đã cấu hình kênh thông báo: <#{guild.public_updates_channel.id}>."})
        else:
            checks.append({"status": "WARN", "title": "Kênh Thông Báo Cập Nhật", "desc": "Chưa chỉ định kênh thông báo cập nhật hệ thống."})

        # Content filter
        if filter_ok:
            score += 15
            checks.append({"status": "PASS", "title": "Bộ Lọc Hình Ảnh Nhạy Cảm", "desc": "Đã bật quét media toàn bộ thành viên (Mức cao nhất)."})
        else:
            checks.append({"status": "WARN", "title": "Bộ Lọc Hình Ảnh Nhạy Cảm", "desc": "Nên đặt Explicit Content Filter thành Quét toàn bộ thành viên."})

        # Verification Level
        if verif_ok:
            score += 15
            checks.append({"status": "PASS", "title": "Mức Xác Minh Thành Viên", "desc": f"Mức xác minh đạt chuẩn ({guild.verification_level.name.capitalize()})."})
        else:
            checks.append({"status": "WARN", "title": "Mức Xác Minh Thành Viên", "desc": f"Mức hiện tại là {guild.verification_level.name.capitalize()}. Khuyến nghị mức Medium (Tài khoản > 5 phút)."})

        # 2FA
        if mfa_ok:
            score += 10
            checks.append({"status": "PASS", "title": "Bảo Mật 2 Lớp (2FA)", "desc": "Yêu cầu 2FA cho quản trị viên đã được kích hoạt."})
        else:
            checks.append({"status": "INFO", "title": "Bảo Mật 2 Lớp (2FA)", "desc": "Khuyến nghị bật Yêu cầu 2FA cho vai trò Quản lý trong Server Settings."})

    score = min(100, max(0, score))
    if is_verified:
        verdict = "ĐÃ SỞ HỮU TÍCH XANH 🟢"
    elif score >= 85:
        verdict = "SẴN SÀNG CLAIM GAME TRÊN DEV PORTAL 🚀"
    elif score >= 50:
        verdict = "CẦN HOÀN TẤT THÊM CẤU HÌNH ⚠️"
    else:
        verdict = "CHƯA ĐẠT CHUẨN COMMUNITY ❌"

    return score, verdict, checks


class SteamCheckModal(discord.ui.Modal):
    """Cửa sổ Modal tra cứu Game trên Steam Store"""
    def __init__(self):
        super().__init__(title="🎮 Tra Cứu Game Trên Steam Store")
        self.app_id_input = discord.ui.TextInput(
            label="Steam App ID của Game",
            placeholder="Ví dụ: 730 (CS2), 105600 (Terraria), 252490...",
            min_length=1,
            max_length=20,
            required=True
        )
        self.add_item(self.app_id_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        app_id = self.app_id_input.value.strip()

        ok, game_data = await api_fetch_steam_game(app_id)
        if not ok:
            await interaction.followup.send(f"❌ **Lỗi tra cứu:** {game_data.get('error')}", ephemeral=True)
            return

        name = game_data.get("name", "Unknown Game")
        developers = ", ".join(game_data.get("developers", ["Chưa rõ"]))
        publishers = ", ".join(game_data.get("publishers", ["Chưa rõ"]))
        release_date = game_data.get("release_date", {}).get("date", "Chưa rõ")
        is_coming_soon = game_data.get("release_date", {}).get("coming_soon", False)
        is_game = game_data.get("type", "").lower() == "game"
        header_image = game_data.get("header_image", "")

        # Quét link discord trên steam
        f_ok, discord_link, link_msg = await api_check_steam_discord_link(app_id)

        # Đánh giá điều kiện Game Claiming
        eligible = is_game and not is_coming_soon
        eligibility_text = "✅ ĐỦ ĐIỀU KIỆN CLAIM GAME (Playable Game)" if eligible else "❌ CHƯA ĐỦ ĐIỀU KIỆN (Đang ở trạng thái Coming Soon hoặc không phải Game độc lập)"

        embed = discord.Embed(
            title=f"🎮 THÔNG TIN GAME STEAM: {name}",
            description=(
                f"> **Mã App ID:** `{app_id}`\n"
                f"> **Trang Cửa Hàng:** [Bấm vào đây để mở](https://store.steampowered.com/app/{app_id}/)\n"
                f"> **Đánh Giá Claim:** **{eligibility_text}**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=0x23A55A if eligible else 0xED4245
        )

        embed.add_field(name="👨‍💻 Nhà Phát Triển", value=f"`{developers}`", inline=True)
        embed.add_field(name="🏢 Nhà Phát Hành", value=f"`{publishers}`", inline=True)
        embed.add_field(name="📅 Ngày Ra Mắt", value=f"`{release_date}`", inline=True)
        embed.add_field(name="🔗 Quét Link Discord Trên Steam", value=f"> {link_msg}", inline=False)

        if header_image:
            embed.set_image(url=header_image)

        embed.set_footer(text="Steam Store Inspector • Discord Verified Server Suite")
        await interaction.followup.send(embed=embed, ephemeral=True)


class ProofGeneratorModal(discord.ui.Modal):
    """Cửa sổ Modal sinh đường dẫn Proof Token để đưa lên Steam Store"""
    def __init__(self, default_invite: str = ""):
        super().__init__(title="🔗 Tạo Link Proof Xác Minh Steam")
        self.invite_input = discord.ui.TextInput(
            label="Đường Dẫn Mời Discord (Server Invite Link)",
            placeholder="Ví dụ: https://discord.gg/yourgame",
            default=default_invite,
            min_length=5,
            max_length=120,
            required=True
        )
        self.proof_input = discord.ui.TextInput(
            label="Mã Proof Token (Từ Discord Developer Portal)",
            placeholder="Dán chuỗi Proof tạm thời Discord cấp cho bạn khi Claim...",
            min_length=1,
            max_length=150,
            required=True
        )
        self.add_item(self.invite_input)
        self.add_item(self.proof_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        invite = self.invite_input.value.strip()
        proof = self.proof_input.value.strip()

        final_url = generate_steam_proof_url(invite, proof)

        embed = discord.Embed(
            title="🔗 LIÊN KẾT PROOF XÁC MINH SỞ HỮU THÀNH CÔNG",
            description=(
                f"> ### 📋 Đường Dẫn Hoàn Chỉnh Để Dán Lên Steam:\n"
                f"```text\n{final_url}\n```\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "**📌 Hướng Dẫn Các Bước Dán Lên Steamworks Partner:**\n"
                "> 1. Đăng nhập vào [Steamworks Partner Backend](https://partner.steamgames.com/).\n"
                "> 2. Chọn Game của bạn > **Edit Store Page (Sửa trang cửa hàng)**.\n"
                "> 3. Tìm mục **Basic Info** hoặc **External Links (Liên kết ngoài)**.\n"
                "> 4. Dán đường dẫn Proof ở khung code phía trên vào mục Discord URL.\n"
                "> 5. Bấm **Publish Store Changes**, sau đó quay lại Developer Portal bấm **Submit Claim**!"
            ),
            color=0x23A55A
        )
        embed.set_footer(text="Discord Verified Server Suite • 100% An Toàn & Chuẩn Xác")
        await interaction.followup.send(embed=embed, ephemeral=True)


def create_verified_server_embed(guild: Optional[discord.Guild] = None, client: Optional[discord.Client] = None) -> discord.Embed:
    """Tạo Embed giao diện Verified Server Hub theo phong cách VIP đồng bộ NCT Hub"""
    guild_name = guild.name if guild else "Máy Chủ Discord"
    server_icon = guild.icon.url if guild and guild.icon else (client.user.display_avatar.url if client and client.user else "https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png")

    # Kiểm tra trạng thái hiện tại
    is_verified = "VERIFIED" in guild.features if guild else False
    is_community = "COMMUNITY" in guild.features if guild else False
    score = 100 if is_verified else (audit_guild_readiness(guild)[0] if guild else 0)

    embed = discord.Embed(
        title="🟢 DISCORD VERIFIED SERVER • BẢNG ĐIỀU KHIỂN & AUDIT TÍCH XANH",
        description=(
            "> ### ✨ MỞ KHÓA TÍCH XANH LÁ CÂY • NÂNG TẦM SERVER GAME!\n"
            "> Bộ công cụ kiểm định chuẩn hóa máy chủ, hỗ trợ Steam Game Claiming và giám sát tự động "
            "để mở khóa Huy hiệu **Verified Server** (cờ `VERIFIED`) chính thức từ Discord dành cho Game Creators!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0x23A55A  # Discord Green
    )

    embed.set_author(
        name=f"⚡ {guild_name} • Official Verified Server Hub",
        icon_url=server_icon
    )

    # 3 Cột thống kê thời gian thực
    badge_status = "ĐÃ ĐẠT (Tích Xanh 🟢)" if is_verified else "ĐANG CHỜ CLAIM (⏳)"
    community_status = "ĐÃ BẬT (Community)" if is_community else "CHƯA BẬT (Cần Bật)"
    readiness_status = f"{score}% / 100% Sẵn Sàng"

    embed.add_field(
        name="🛡️ Huy Hiệu Tích Xanh",
        value=(
            "> **Châm ngôn:** Verified Server\n"
            "> **Mã cờ:** `VERIFIED`\n"
            f"> **Trạng thái:** `{badge_status}`"
        ),
        inline=True
    )
    embed.add_field(
        name="🌐 Chế Độ Cộng Đồng",
        value=(
            "> **Châm ngôn:** Community Guild\n"
            "> **Yêu cầu:** Bắt buộc có\n"
            f"> **Trạng thái:** `{community_status}`"
        ),
        inline=True
    )
    embed.add_field(
        name="📊 Điểm Sẵn Sàng",
        value=(
            "> **Châm ngôn:** Readiness Score\n"
            "> **Tiêu chuẩn:** Discord Audit\n"
            f"> **Tỷ lệ:** `{readiness_status}`"
        ),
        inline=True
    )

    embed.add_field(
        name="👑 Lộ Trình 5 Bước Đạt Chuẩn Verified Server:",
        value=(
            "> • **Bước 1 (Game Steam):** Sở hữu tựa game Playable (Early Access / Đã ra mắt) trên Steam.\n"
            "> • **Bước 2 (Developer Team):** Tạo Team tại [Developer Portal/Teams](https://discord.com/developers/teams) & thêm **Chủ Server** làm thành viên.\n"
            "> • **Bước 3 (Auto-Setup & Audit):** Bấm nút **[⚡ Auto-Setup Kênh]** và **[🔍 Audit Máy Chủ]** bên dưới để đạt 100% điểm chuẩn.\n"
            "> • **Bước 4 (Gắn Link Proof):** Bấm nút **[🔗 Tạo Link Proof]** để lấy link dán vào phần liên kết Steam Store.\n"
            "> • **Bước 5 (Claim Game):** Vào Developer Portal > Game Identity > **Claim your game** & xác thực OTP email để nhận Tích Xanh!"
        ),
        inline=False
    )

    embed.add_field(
        name="⚡ Các Nút Thao Tác Nhanh:",
        value=(
            "> 👉 **Bấm vào một trong các nút bên dưới** để kiểm tra máy chủ, tra cứu Steam hoặc tạo link Proof!\n"
            "-# 🔒 Chuẩn Discord REST API v10 • Hỗ trợ Game Creators 100% An Toàn"
        ),
        inline=False
    )

    embed.set_thumbnail(url="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png")

    banner_url = CONFIG.get("banner_url", "").strip() or "https://raw.githubusercontent.com/truong2903/bot_discord/main/banner.png"
    embed.set_image(url=banner_url)

    embed.set_footer(
        text="Verified Server System v2.0 • Hoạt động 24/7 • Chuẩn Discord API v10",
        icon_url="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png"
    )
    return embed


class VerifiedServerPanelView(discord.ui.View):
    """View chứa các nút bấm điều khiển Verified Server Hub vĩnh viễn (Persistent View)"""

    def __init__(self, bot_client: Optional[commands.Bot] = None):
        super().__init__(timeout=None)
        # Nút Link ngoài mở Developer Portal
        self.add_item(discord.ui.Button(
            label="Discord Developer Portal",
            style=discord.ButtonStyle.link,
            url="https://discord.com/developers/applications",
            emoji="🚀",
            row=1
        ))

    @discord.ui.button(
        label="Audit Máy Chủ",
        emoji="🔍",
        style=discord.ButtonStyle.secondary,
        custom_id="verified_btn_audit",
        row=0
    )
    async def btn_audit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("❌ Lệnh này chỉ sử dụng được trong Máy Chủ (Server)!", ephemeral=True)
            return

        score, verdict, checks = audit_guild_readiness(guild)

        embed = discord.Embed(
            title=f"🔍 BÁO CÁO AUDIT TIÊU CHUẨN: {guild.name}",
            description=(
                f"> **Điểm Sẵn Sàng:** `{score}% / 100%`\n"
                f"> **Kết Luận:** **{verdict}**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=0x23A55A if score >= 80 else 0xF0B232
        )

        for c in checks:
            icon = "✅" if c["status"] == "PASS" else ("⚠️" if c["status"] == "WARN" else ("ℹ️" if c["status"] == "INFO" else "❌"))
            embed.add_field(
                name=f"{icon} {c['title']}",
                value=f"> {c['desc']}",
                inline=False
            )

        vanity_text = f"discord.gg/{guild.vanity_url_code}" if guild.vanity_url_code else "Chưa có"
        embed.add_field(name="👥 Thành Viên", value=f"`{guild.member_count} người`", inline=True)
        embed.add_field(name="🔗 Vanity URL", value=f"`{vanity_text}`", inline=True)
        embed.add_field(name="✨ Features", value=f"`{len(guild.features)} cờ active`", inline=True)

        embed.set_footer(text="Verified Server Auditor • Discord REST API v10")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Auto-Setup Kênh & Bảo Mật",
        emoji="⚡",
        style=discord.ButtonStyle.success,
        custom_id="verified_btn_setup",
        row=0
    )
    async def btn_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("❌ Lệnh này chỉ sử dụng được trong Máy Chủ (Server)!", ephemeral=True)
            return

        if not guild.me.guild_permissions.manage_channels:
            await interaction.followup.send("⚠️ Bot thiếu quyền **Quản Lý Kênh (Manage Channels)** để tự động tạo cấu trúc kênh!", ephemeral=True)
            return

        standard_channels = [
            {"name": "rules-and-info", "type": discord.ChannelType.text, "topic": "Quy định máy chủ & Giới thiệu Game chính thức"},
            {"name": "game-announcements", "type": discord.ChannelType.news if "COMMUNITY" in guild.features else discord.ChannelType.text, "topic": "Thông báo chính thức từ đội ngũ phát triển Game (News/Updates)"},
            {"name": "patch-notes", "type": discord.ChannelType.text, "topic": "Nhật ký cập nhật phiên bản, bản vá và tính năng mới của Game"},
            {"name": "community-chat", "type": discord.ChannelType.text, "topic": "Kênh trò chuyện, thảo luận chung cho cộng đồng người chơi"},
            {"name": "bug-reports", "type": discord.ChannelType.text, "topic": "Báo cáo lỗi, phản hồi trải nghiệm và đóng góp ý kiến cho Game"}
        ]

        created = []
        existing = []

        for spec in standard_channels:
            found_chan = None
            for c in guild.text_channels:
                if spec["name"] in c.name or c.name in spec["name"]:
                    found_chan = c
                    break

            if found_chan:
                existing.append(f"#{found_chan.name}")
            else:
                try:
                    new_chan = await guild.create_text_channel(
                        name=spec["name"],
                        topic=spec["topic"],
                        reason="Verified Server Community Setup"
                    )
                    created.append(f"#{new_chan.name}")
                except Exception as e:
                    print(f"Lỗi tạo kênh {spec['name']}: {e}")

        # Cập nhật cài đặt server nếu có quyền Manage Guild
        sec_msg = ""
        if guild.me.guild_permissions.manage_guild:
            try:
                await guild.edit(
                    explicit_content_filter=discord.ContentFilter.all_members,
                    verification_level=discord.VerificationLevel.medium,
                    reason="Verified Server Security Standardization"
                )
                sec_msg = "\n🔒 **Đã nâng cấp bảo mật:** Explicit Media Filter = Toàn bộ thành viên, Verification = Medium."
            except Exception as e:
                sec_msg = f"\n⚠️ Không thể đổi cấu hình guild: {e}"

        created_text = ", ".join(created) if created else "Không có (Đã có sẵn)"
        existing_text = ", ".join(existing) if existing else "Không có"

        res_msg = (
            f"🎉 **HOÀN TẤT THIẾT LẬP CHUẨN COMMUNITY!**\n"
            f"> • **Kênh mới tạo:** `{created_text}`\n"
            f"> • **Kênh đã có sẵn:** `{existing_text}`"
            f"{sec_msg}\n\n"
            f"👉 Bây giờ bạn có thể bấm **[🔍 Audit Máy Chủ]** để kiểm tra lại điểm sẵn sàng!"
        )
        await interaction.followup.send(res_msg, ephemeral=True)

    @discord.ui.button(
        label="Tra Cứu Steam Game",
        emoji="🎮",
        style=discord.ButtonStyle.primary,
        custom_id="verified_btn_steam",
        row=0
    )
    async def btn_steam(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SteamCheckModal())

    @discord.ui.button(
        label="Tạo Link Proof Steam",
        emoji="🔗",
        style=discord.ButtonStyle.secondary,
        custom_id="verified_btn_proof",
        row=1
    )
    async def btn_proof(self, interaction: discord.Interaction, button: discord.ui.Button):
        default_invite = ""
        if interaction.guild:
            if interaction.guild.vanity_url_code:
                default_invite = f"https://discord.gg/{interaction.guild.vanity_url_code}"
            else:
                try:
                    invites = await interaction.guild.invites()
                    if invites:
                        default_invite = invites[0].url
                except Exception:
                    pass
        await interaction.response.send_modal(ProofGeneratorModal(default_invite=default_invite))

    @discord.ui.button(
        label="Cẩm Nang Claim A-Z",
        emoji="📖",
        style=discord.ButtonStyle.secondary,
        custom_id="verified_btn_guide",
        row=1
    )
    async def btn_guide(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📖 CẨM NANG TOÀN TẬP: QUY TRÌNH GAME CLAIMING LẤY TÍCH XANH",
            description=(
                "> ### 🌟 5 BƯỚC ĐẠT HUY HIỆU VERIFIED SERVER TỪ DISCORD:\n\n"
                "**1️⃣ Bước 1: Game Playable trên Steam**\n"
                "> Tựa game phải ở trạng thái đang mở chơi được trên Steam (**Early Access** hoặc **Full Release**). Các game ở chế độ Coming Soon hoặc Demo sẽ không được duyệt.\n\n"
                "**2️⃣ Bước 2: Tạo Discord Developer Team**\n"
                "> Truy cập [Developer Portal Teams](https://discord.com/developers/teams), tạo một Team và **thêm Chủ Server (Server Owner)** vào làm thành viên của Team này.\n\n"
                "**3️⃣ Bước 3: Đưa Link Discord lên Steam Store**\n"
                "> Vào Steamworks Partner Backend > Sửa trang Store của Game > Thêm link mời Discord vào phần liên kết bên ngoài.\n\n"
                "**4️⃣ Bước 4: Thực Hiện Claim Game Trên Developer Portal**\n"
                "> Vào Application của game > Mục **Game Identity** > Bấm **Claim your game**. Chọn game Steam và server Discord của bạn, dán mã Proof tạm thời vào Steam và xác nhận mã OTP gửi về Email của Server Owner.\n\n"
                "**5️⃣ Bước 5: Phê Duyệt & Nhận Tích Xanh**\n"
                "> Discord đối soát và tự động cấp cờ `VERIFIED` vĩnh viễn: Xuất hiện huy hiệu Tích Xanh 🟢, mở khóa Vanity URL miễn phí, Server Banner và Game Profile Card!"
            ),
            color=0x5865F2
        )
        embed.set_footer(text="Discord Developer Portal • Game Identity Program")
        await interaction.response.send_message(embed=embed, ephemeral=True)


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
    bot.add_view(AutoModPanelView())
    bot.add_view(VerifiedServerPanelView())

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
    print(f"   - {Colors.CYAN}/hypesquad-panel{Colors.RESET}  : Gửi bảng điều khiển HypeSquad có NÚT BẤM tương tác")
    print(f"   - {Colors.CYAN}/tao_server{Colors.RESET}       : Mở bảng điều khiển kích hoạt 100+ rules AutoMod Badge")
    print(f"   - {Colors.CYAN}/verified_server{Colors.RESET}  : Bảng điều khiển kiểm định & hỗ trợ lấy Verified Server Badge (Tích Xanh 🟢)")
    print(f"   - {Colors.CYAN}/ping{Colors.RESET}             : Kiểm tra phản hồi bot")
    print(f"{Colors.GREEN}====================================================================={Colors.RESET}\n")


async def handle_tao_server(interaction: discord.Interaction):
    """Xử lý lệnh /tao_server"""
    await interaction.response.defer(ephemeral=False)
    bot_client: commands.Bot = interaction.client
    token = bot_client.http.token

    # Lấy thông số hiện tại
    flags, is_public = await api_get_app_info(token)
    total_rules = await count_total_automod_rules(bot_client)
    guild_count = len(bot_client.guilds)

    embed = create_automod_embed(guild_count, total_rules, flags, is_public, client=bot_client)
    view = AutoModPanelView(bot_client=bot_client)

    banner_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banner.png")
    if os.path.exists(banner_path):
        banner_file = discord.File(banner_path, filename="banner.png")
        embed.set_image(url="attachment://banner.png")
        await interaction.channel.send(embed=embed, file=banner_file, view=view)
    else:
        await interaction.channel.send(embed=embed, view=view)

    await interaction.followup.send("✅ Đã mở bảng điều khiển AutoMod Badge Hub thành công!", ephemeral=True)


@bot.tree.command(name="tao_server", description="Mở bảng điều khiển kích hoạt 100+ rules AutoMod Badge")
@app_commands.default_permissions(manage_guild=True)
async def cmd_tao_server(interaction: discord.Interaction):
    await handle_tao_server(interaction)


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


async def handle_verified_server(interaction: discord.Interaction):
    """Xử lý lệnh /verified_server"""
    await interaction.response.defer(ephemeral=False)
    bot_client: commands.Bot = interaction.client
    guild = interaction.guild

    embed = create_verified_server_embed(guild=guild, client=bot_client)
    view = VerifiedServerPanelView(bot_client=bot_client)

    banner_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banner.png")
    if os.path.exists(banner_path):
        banner_file = discord.File(banner_path, filename="banner.png")
        embed.set_image(url="attachment://banner.png")
        await interaction.channel.send(embed=embed, file=banner_file, view=view)
    else:
        await interaction.channel.send(embed=embed, view=view)

    await interaction.followup.send("✅ Đã mở bảng điều khiển Verified Server Hub thành công!", ephemeral=True)


@bot.tree.command(name="verified_server", description="Mở bảng điều khiển kiểm định & hỗ trợ lấy huy hiệu Verified Server (Tích Xanh 🟢)")
@app_commands.default_permissions(manage_guild=True)
async def cmd_verified_server(interaction: discord.Interaction):
    await handle_verified_server(interaction)


@bot.tree.command(name="ping", description="Kiểm tra độ trễ phản hồi của Bot")
async def cmd_ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Độ trễ hiện tại: `{latency}ms`", ephemeral=True)


def send_badge_approval_email(smtp_cfg: dict, requester_name: str, requester_id: int, requester_email: str, guild_name: str):
    """Gửi email thông báo tới Chủ Bot khi có thành viên gửi yêu cầu nhận huy hiệu"""
    admin_email = os.getenv("ADMIN_EMAIL", "").strip() or smtp_cfg.get("admin_email", "").strip()
    smtp_host = os.getenv("SMTP_HOST", "").strip() or smtp_cfg.get("smtp_host", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "").strip() or smtp_cfg.get("smtp_port", 587))
    smtp_user = os.getenv("SMTP_USER", "").strip() or smtp_cfg.get("smtp_user", "").strip()
    smtp_password = os.getenv("SMTP_PASS", "").strip() or smtp_cfg.get("smtp_password", "").strip()

    if not admin_email:
        return False, "Chưa cấu hình admin_email trong config.json hoặc biến môi trường ADMIN_EMAIL"
    if not smtp_user or not smtp_password:
        return False, "Chưa cấu hình tài khoản gửi email (smtp_user, smtp_password)"

    subject = f"🔔 [NCT_bot] Yêu cầu duyệt Huy hiệu Active Developer từ @{requester_name}"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #1e1f22; color: #dbdee1; padding: 24px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #2b2d31; border-radius: 12px; padding: 28px; border: 1px solid #383a40;">
            <h2 style="color: #57F287; margin-top: 0;">🛡️ YÊU CẦU DUYỆT HUY HIỆU ACTIVE DEVELOPER</h2>
            <p style="color: #ffffff; font-size: 15px;">
                Xin chào Chủ Bot, một thành viên trong server vừa gõ lệnh <code>/badge</code> để xin tham gia Đội ngũ nhận huy hiệu:
            </p>
            <div style="background-color: #1e1f22; border-radius: 8px; padding: 16px; margin: 20px 0; border-left: 4px solid #5865F2;">
                <p style="margin: 6px 0;"><strong>👤 Tên Discord:</strong> {requester_name}</p>
                <p style="margin: 6px 0;"><strong>🆔 Discord ID:</strong> {requester_id}</p>
                <p style="margin: 6px 0;"><strong>📧 Email thành viên:</strong> <span style="color: #57F287; font-weight: bold;">{requester_email}</span></p>
                <p style="margin: 6px 0;"><strong>🏰 Máy chủ gửi:</strong> {guild_name}</p>
                <p style="margin: 6px 0;"><strong>⏰ Thời gian:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>
            <h3 style="color: #FEE75C; font-size: 16px;">👉 HƯỚNG DẪN BẠN DUYỆT CHO THÀNH VIÊN:</h3>
            <ol style="line-height: 1.8; color: #dbdee1;">
                <li>Truy cập: <a href="https://discord.com/developers/applications" style="color: #5865F2; font-weight: bold;">Discord Developer Portal</a></li>
                <li>Vào mục <strong>Teams</strong> ở cột bên trái (hoặc tạo một Team mới và chuyển Bot vào).</li>
                <li>Bấm <strong>Invite Member</strong> ➔ Dán email <code>{requester_email}</code> vào để mời người đó vào Team.</li>
                <li>Sau khi người đó chấp nhận lời mời, họ sẽ vào được <strong>discord.com/developers/active-developer</strong> để nhận huy hiệu!</li>
            </ol>
            <hr style="border: none; border-top: 1px solid #383a40; margin: 24px 0;">
            <p style="font-size: 12px; color: #949ba4; text-align: center;">
                Thông báo tự động từ NCT_bot Management System
            </p>
        </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = admin_email
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [admin_email], msg.as_string())
        return True, "Đã gửi email thành công!"
    except Exception as e:
        return False, str(e)


@bot.tree.command(name="badge", description="Kích hoạt hoặc gửi yêu cầu duyệt nhận Active Developer Badge")
@app_commands.describe(email="Email của bạn (Dành cho thành viên muốn xin Chủ Bot duyệt mời vào Team)")
async def cmd_badge(interaction: discord.Interaction, email: Optional[str] = None):
    cfg = load_config()

    # 1. Xác định danh sách ID của Chủ Bot
    owner_ids = set()
    try:
        app_info = await bot.application_info()
        if app_info.team:
            for member in app_info.team.members:
                owner_ids.add(member.id)
        elif app_info.owner:
            owner_ids.add(app_info.owner.id)
    except Exception:
        pass

    custom_admin_id = os.getenv("ADMIN_DISCORD_ID", "").strip() or cfg.get("admin_discord_id", "")
    if custom_admin_id and str(custom_admin_id).isdigit():
        owner_ids.add(int(custom_admin_id))

    # TRƯỜNG HỢP 1: NGƯỜI GÕ LỆNH LÀ CHỦ BOT
    if interaction.user.id in owner_ids or not owner_ids:
        embed = discord.Embed(
            title="🎉 XIN CHÀO CHỦ BOT - TƯƠNG TÁC ĐÃ GHI NHẬN!",
            description=(
                f"Xin chào **{interaction.user.name}**!\n\n"
                "✅ Bạn là **Chủ sở hữu của Bot**, lệnh Slash Command vừa được thực thi trực tiếp trên Discord.\n"
                "🛡️ **Huy hiệu Bot:** Bot hiện đã sở hữu huy hiệu `{/}` **Supports Commands**.\n\n"
                "🌟 **NHẬN ACTIVE DEVELOPER BADGE CHO BẠN:**\n"
                "1. Discord Developer Portal cần khoảng **24 giờ** để đồng bộ tương tác này.\n"
                "2. Sau 24h, hãy truy cập liên kết chính thức bên dưới để bấm nhận huy hiệu:\n"
                "👉 **[discord.com/developers/active-developer](https://discord.com/developers/active-developer)**\n"
                "3. Chọn ứng dụng bot này và chỉ định 1 kênh để hoàn tất nhận huy hiệu ghim lên Profile!"
            ),
            color=0x57F287
        )
        embed.set_footer(text="NCT_bot • Chủ sở hữu ứng dụng")
        await interaction.response.send_message(embed=embed)
        print(f"[CHỦ BOT] {interaction.user.name} ({interaction.user.id}) vừa gõ lệnh /badge!")
        return

    # TRƯỜNG HỢP 2: THÀNH VIÊN KHÁC GÕ LỆNH NHƯNG CHƯA ĐIỀN EMAIL
    if not email or not email.strip():
        embed = discord.Embed(
            title="ℹ️ BẠN CẦN ĐƯỢC CHỦ BOT PHÊ DUYỆT",
            description=(
                f"Xin chào **{interaction.user.name}**!\n\n"
                "Để nhận được huy hiệu **Active Developer 🛠️**, bạn cần được **Chủ Bot** mời vào **Developer Team** của Bot trên Discord Developer Portal.\n\n"
                "👉 **CÁCH GỬI YÊU CẦU DUYỆT ĐẾN CHỦ BOT:**\n"
                "Hãy gõ lại lệnh kèm email của bạn:\n"
                "```/badge email: email_cua_ban@gmail.com```\n"
                "Hệ thống sẽ tự động gửi **Email thông báo** kèm **tin nhắn riêng** đến Chủ Bot để duyệt và gửi lời mời vào Team cho bạn!"
            ),
            color=0x5865F2
        )
        embed.set_footer(text="Gõ /badge email: <email của bạn> để xin phê duyệt")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # TRƯỜNG HỢP 3: THÀNH VIÊN ĐÃ ĐIỀN EMAIL ➔ GỬI EMAIL VÀ DM CHO CHỦ BOT
    email_clean = email.strip()
    guild_name = interaction.guild.name if interaction.guild else "Tin nhắn riêng (DM)"

    email_cfg = cfg.get("email_notifications", {})
    if not email_cfg.get("admin_email"):
        email_cfg["admin_email"] = os.getenv("ADMIN_EMAIL", "").strip() or cfg.get("admin_email", "")

    # A. Gửi Email cho Chủ Bot
    email_status_msg = "Chưa gửi (chưa cấu hình email)"
    if email_cfg.get("admin_email"):
        success, msg = send_badge_approval_email(
            email_cfg,
            requester_name=interaction.user.name,
            requester_id=interaction.user.id,
            requester_email=email_clean,
            guild_name=guild_name
        )
        if success:
            email_status_msg = f"Đã gửi thành công tới {email_cfg.get('admin_email')}"
        else:
            email_status_msg = f"Lỗi gửi email: {msg}"
            print(f"[CẢNH BÁO GỬI EMAIL] {msg}")

    # B. Gửi DM trực tiếp cho Chủ Bot trên Discord
    dm_sent = False
    for oid in owner_ids:
        try:
            owner_user = await bot.fetch_user(oid)
            if owner_user:
                dm_embed = discord.Embed(
                    title="🔔 YÊU CẦU DUYỆT HUY HIỆU ACTIVE DEVELOPER",
                    description=(
                        f"Thành viên **{interaction.user.mention}** vừa gửi yêu cầu duyệt nhận huy hiệu:\n\n"
                        f"• **Tên Discord:** `{interaction.user.name}`\n"
                        f"• **Discord ID:** `{interaction.user.id}`\n"
                        f"• **Email đăng ký:** **`{email_clean}`**\n"
                        f"• **Máy chủ gửi:** `{guild_name}`\n\n"
                        f"👉 **CÁCH DUYỆT CHO THÀNH VIÊN:**\n"
                        f"1. Vào **[Discord Developer Portal](https://discord.com/developers/applications)** ➔ Mục **Teams**.\n"
                        f"2. Bấm **Invite Member** và dán email: **`{email_clean}`** vào để mời!\n"
                        f"3. Sau khi người đó đồng ý, họ sẽ đủ điều kiện nhận huy hiệu."
                    ),
                    color=0x57F287
                )
                dm_embed.set_footer(text=f"Trạng thái Email: {email_status_msg}")
                await owner_user.send(embed=dm_embed)
                dm_sent = True
        except Exception:
            pass

    # C. Phản hồi cho thành viên
    reply_embed = discord.Embed(
        title="📨 ĐÃ GỬI YÊU CẦU ĐẾN CHỦ BOT!",
        description=(
            f"Cảm ơn **{interaction.user.name}**!\n\n"
            f"✅ Yêu cầu cấp huy hiệu của bạn kèm email **`{email_clean}`** đã được gửi trực tiếp đến Chủ Bot.\n\n"
            f"⏳ **Bước tiếp theo:**\n"
            f"Chủ Bot sẽ kiểm tra và gửi lời mời vào **Developer Team** tới email hoặc Discord của bạn. Khi được chấp nhận vào Team, bạn sẽ vào được [discord.com/developers/active-developer](https://discord.com/developers/active-developer) để bấm nhận huy hiệu Active Developer 🛠️!"
        ),
        color=0x57F287
    )
    await interaction.response.send_message(embed=reply_embed)
    print(f"\n[YÊU CẦU MỚI] Thành viên {interaction.user.name} ({interaction.user.id}) vừa gửi email '{email_clean}' xin duyệt huy hiệu!")
    print(f"  ➔ Trạng thái thông báo: Email: {email_status_msg} | Discord DM: {'Đã gửi' if dm_sent else 'Không gửi được'}")


def banner():
    print(f"""{Colors.CYAN}
  ╔═══════════════════════════════════════════════════════════╗
  ║       🌟 DISCORD MULTI-FUNCTION BOT PRO (NCT HUB)         ║
  ║  HypeSquad 💜 • AutoMod 🛡️ • Verified Server Suite 🟢    ║
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
