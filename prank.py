#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#   DCS PRANK CALL TOOL - PREMIUM EDITION
#   Team    : DCS
#   Powered : ALIF ISLAM
#   Animated CLI • Full English UI • A-Z Features
# ============================================================
#   Run: python dcs_prank.py
# ============================================================

import requests
import sys
import json
import re
import os
import time
import random
import threading
from datetime import datetime

# ============================================================
#   CONFIGURATION
# ============================================================
BASE_URL = "https://cxofb.nid-bd.my.id/wrom-gpt/api.php"
HISTORY_FILE = "dcs_history.json"
FAVORITES_FILE = "dcs_favorites.json"
SETTINGS_FILE = "dcs_settings.json"

TEAM_NAME = "DCS"
POWERED_BY = "ALIF ISLAM"

PRANK_IDS = {
    "8810": "Why do you call my girlfriend?",
    "8805": "Smells like Gaza!",
    "8803": "Pizza delivery",
    "8809": "Why do you call me?",
    "8808": "You are stealing my Wi-Fi!",
    "8806": "Noise from your room",
    "8804": "Your taxi is waiting for you",
    "8807": "Your dog is very annoying!"
}

# ============================================================
#   ANSI COLORS & STYLES
# ============================================================
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"
    UNDER   = "\033[4m"
    BLINK   = "\033[5m"
    REVERSE = "\033[7m"
    BLACK   = "\033[30m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"

# ============================================================
#   SETTINGS MANAGER
# ============================================================
DEFAULT_SETTINGS = {
    "animations": True,
    "sound": True,
    "auto_copy": False,
    "verbose": True,
    "theme": "cyan"
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(s):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)

SETTINGS = load_settings()

# ============================================================
#   UTILITY FUNCTIONS
# ============================================================
def clear():
    os.system("clear" if os.name != "nt" else "cls")

def sleep_anim(sec):
    if SETTINGS.get("animations", True):
        time.sleep(sec)

def typing_effect(text, delay=0.015, color=C.WHITE):
    for ch in text:
        sys.stdout.write(f"{color}{ch}{C.RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def loading_bar(label="Processing", duration=1.5, width=30):
    if not SETTINGS.get("animations", True):
        return
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        pct = 1 - (end - time.time()) / duration
        filled = int(width * pct)
        bar = "█" * filled + "░" * (width - filled)
        sys.stdout.write(f"\r{C.CYAN}{frames[i % len(frames)]}{C.RESET} {label} {C.GREEN}[{bar}]{C.RESET} {int(pct*100):3d}%")
        sys.stdout.flush()
        time.sleep(0.07)
        i += 1
    print()

def spinner(label="Loading", duration=1.0):
    frames = ["⣾","⣽","⣻","⢿","⡿","⣟","⣯","⣷"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r{C.MAGENTA}{frames[i % len(frames)]}{C.RESET} {label}...")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write("\r" + " " * (len(label) + 15) + "\r")

def box(title, content, color=C.CYAN, width=58):
    print(f"{color}╔" + "═" * (width - 2) + "╗" + C.RESET)
    pad = (width - 2 - len(title)) // 2
    print(f"{color}║" + " " * pad + f"{C.BOLD}{title}{C.RESET}{color}" + " " * (width - 2 - pad - len(title)) + "║" + C.RESET)
    print(f"{color}╠" + "═" * (width - 2) + "╣" + C.RESET)
    for line in content.split("\n"):
        visible_len = len(re.sub(r'\033\[[0-9;]*m', '', line))
        pad = max(0, width - 3 - visible_len)
        print(f"{color}║{C.RESET} {line}" + " " * pad + f"{color}║{C.RESET}")
    print(f"{color}╚" + "═" * (width - 2) + "╝" + C.RESET)

def divider(char="─", width=60, color=C.GRAY):
    print(f"{color}{char * width}{C.RESET}")

def error_msg(msg):
    print(f"{C.RED}{C.BOLD}✖ ERROR:{C.RESET} {C.RED}{msg}{C.RESET}")

def success_msg(msg):
    print(f"{C.GREEN}{C.BOLD}✔ SUCCESS:{C.RESET} {C.GREEN}{msg}{C.RESET}")

def info_msg(msg):
    print(f"{C.CYAN}{C.BOLD}ℹ INFO:{C.RESET} {C.CYAN}{msg}{C.RESET}")

def warn_msg(msg):
    print(f"{C.YELLOW}{C.BOLD}⚠ WARNING:{C.RESET} {C.YELLOW}{msg}{C.RESET}")

# ============================================================
#   DATA VALIDATION
# ============================================================
def normalize_phone(phone: str) -> str:
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('880'):
        digits = digits[3:]
    elif digits.startswith('88'):
        digits = digits[2:]
    if not digits.startswith('0'):
        digits = '0' + digits
    return digits

def valid_phone(phone: str) -> bool:
    return bool(re.fullmatch(r'01\d{9}', phone))

# ============================================================
#   EXTERNAL API CALL
# ============================================================
def send_call(phone: str, prank_id: str) -> dict:
    params = {"phone": phone, "prank_id": prank_id}
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Termux) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    try:
        r = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        try:
            return r.json()
        except json.JSONDecodeError:
            return {"status": "raw", "response": r.text}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# ============================================================
#   HISTORY MANAGER
# ============================================================
def save_history(entry: dict):
    data = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []
    data.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    success_msg("History cleared.")

# ============================================================
#   FAVORITES MANAGER
# ============================================================
def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        return []
    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_favorites(favs):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favs, f, indent=2)

def toggle_favorite(prank_id):
    favs = load_favorites()
    if prank_id in favs:
        favs.remove(prank_id)
        info_msg(f"Removed {prank_id} from favorites.")
    else:
        favs.append(prank_id)
        success_msg(f"Added {prank_id} to favorites.")
    save_favorites(favs)

# ============================================================
#   HEADER BANNER (ANIMATED)
# ============================================================
BANNER_ART = r"""
  ██████╗  ██████╗███████╗
  ██╔══██╗██╔════╝██╔════╝
  ██║  ██║██║     ███████╗
  ██║  ██║██║     ╚════██║
  ██████╔╝╚██████╗███████║
  ╚═════╝  ╚═════╝╚══════╝
"""

def print_banner():
    clear()
    colors = [C.CYAN, C.BLUE, C.MAGENTA, C.RED]
    for i, line in enumerate(BANNER_ART.strip("\n").split("\n")):
        print(f"{colors[i % len(colors)]}{C.BOLD}{line}{C.RESET}")
        sleep_anim(0.03)
    print(f"{C.YELLOW}{C.BOLD}      🫀  PREMIUM PRANK CALL TOOL  🫀{C.RESET}")
    print(f"{C.GREEN}      Team    : {C.BOLD}{TEAM_NAME}{C.RESET}")
    print(f"{C.GREEN}      Powered : {C.BOLD}{POWERED_BY}{C.RESET}")
    divider("═", 60, C.CYAN)

# ============================================================
#   INPUT HANDLER
# ============================================================
def get_input(prompt, color=C.WHITE):
    try:
        return input(f"{color}{C.BOLD}➤ {prompt}{C.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""

def pause():
    print()
    input(f"{C.GRAY}Press Enter to continue...{C.RESET}")

# ============================================================
#   LIST PRANKS
# ============================================================
def list_pranks():
    print_banner()
    print(f"{C.YELLOW}{C.BOLD}🎭 AVAILABLE PRANK IDs{C.RESET}\n")
    favs = load_favorites()
    for i, (pid, desc) in enumerate(PRANK_IDS.items(), 1):
        star = f"{C.YELLOW}★{C.RESET}" if pid in favs else f"{C.GRAY}☆{C.RESET}"
        print(f"  {star} {C.CYAN}{C.BOLD}{i:>2}.{C.RESET} {C.GREEN}{pid}{C.RESET} — {desc}")
    print()
    divider()
    print(f"{C.GRAY}Total: {len(PRANK_IDS)} pranks | Favorites: {len(favs)}{C.RESET}")
    pause()

# ============================================================
#   MAKE A CALL
# ============================================================
def make_call_flow():
    print_banner()
    print(f"{C.YELLOW}{C.BOLD}📞 NEW PRANK CALL{C.RESET}\n")
    raw = get_input("Enter phone number (e.g. 01923181812 or +8801923181812):", C.CYAN)
    if not raw:
        warn_msg("Cancelled.")
        pause()
        return
    phone = normalize_phone(raw)
    if not valid_phone(phone):
        error_msg(f"Invalid number '{phone}'. Required format: 01XXXXXXXXX (11 digits).")
        pause()
        return
    success_msg(f"Normalized: {phone}")
    sleep_anim(0.4)

    print()
    print(f"{C.YELLOW}{C.BOLD}🎭 SELECT PRANK{C.RESET}\n")
    keys = list(PRANK_IDS.keys())
    favs = load_favorites()
    for i, pid in enumerate(keys, 1):
        star = f"{C.YELLOW}★{C.RESET}" if pid in favs else f"{C.GRAY}☆{C.RESET}"
        print(f"  {star} {C.CYAN}{i:>2}.{C.RESET} {C.GREEN}{pid}{C.RESET} — {PRANK_IDS[pid]}")
    print(f"  {C.RED} 0.{C.RESET} Cancel")
    print()
    choice = get_input("Select prank:", C.CYAN)
    if choice == "0" or not choice:
        warn_msg("Cancelled.")
        pause()
        return
    if not choice.isdigit() or not (1 <= int(choice) <= len(keys)):
        error_msg("Invalid choice.")
        pause()
        return
    prank_id = keys[int(choice) - 1]

    print()
    divider("═", 60, C.CYAN)
    info_msg(f"Phone  : {phone}")
    info_msg(f"Prank  : {prank_id} — {PRANK_IDS[prank_id]}")
    divider("═", 60, C.CYAN)
    print()
    loading_bar("Sending call", 1.5)

    result = send_call(phone, prank_id)

    success = False
    try:
        success = bool(result.get("response", {}).get("success"))
    except:
        success = False

    print()
    if success:
        print(f"{C.GREEN}{C.BOLD}✅ CALL SENT SUCCESSFULLY!{C.RESET}")
        msg = result.get("response", {}).get("message", "")
        if msg:
            print(f"{C.CYAN}   {msg}{C.RESET}")
    else:
        print(f"{C.RED}{C.BOLD}❌ CALL FAILED!{C.RESET}")
        msg = result.get("response", {}).get("message") or result.get("error") or "Unknown error"
        print(f"{C.RED}   {msg}{C.RESET}")

    save_history({
        "phone": phone,
        "prank_id": prank_id,
        "success": success,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "response": result
    })

    if SETTINGS.get("verbose", True):
        print()
        print(f"{C.YELLOW}API RESPONSE:{C.RESET}")
        print(f"{C.GRAY}{json.dumps(result, indent=2, ensure_ascii=False)}{C.RESET}")

    pause()

# ============================================================
#   HISTORY VIEW
# ============================================================
def show_history():
    print_banner()
    print(f"{C.YELLOW}{C.BOLD}📜 CALL HISTORY{C.RESET}\n")
    data = load_history()
    if not data:
        warn_msg("History is empty.")
        pause()
        return
    for i, e in enumerate(reversed(data[-25:]), 1):
        status = f"{C.GREEN}OK  {C.RESET}" if e.get("success") else f"{C.RED}FAIL{C.RESET}"
        print(f"  {C.CYAN}{i:>2}.{C.RESET} [{status}] {C.WHITE}{e.get('phone')}{C.RESET} | ID {C.GREEN}{e.get('prank_id')}{C.RESET} | {C.GRAY}{e.get('time')}{C.RESET}")
    print()
    divider()
    print(f"{C.GRAY}Total records: {len(data)}{C.RESET}")
    print()
    print(f"  {C.RED}1.{C.RESET} Clear history")
    print(f"  {C.CYAN}0.{C.RESET} Back")
    ch = get_input("Choice:", C.CYAN)
    if ch == "1":
        clear_history()
        pause()

# ============================================================
#   FAVORITES VIEW
# ============================================================
def manage_favorites():
    print_banner()
    print(f"{C.YELLOW}{C.BOLD}⭐ FAVORITE PRANKS{C.RESET}\n")
    favs = load_favorites()
    if not favs:
        warn_msg("No favorites yet.")
        pause()
        return
    for i, pid in enumerate(favs, 1):
        print(f"  {C.YELLOW}★{C.RESET} {C.CYAN}{i}.{C.RESET} {C.GREEN}{pid}{C.RESET} — {PRANK_IDS.get(pid, 'Unknown')}")
    print()
    print(f"  {C.RED}r.{C.RESET} Remove a favorite")
    print(f"  {C.CYAN}0.{C.RESET} Back")
    ch = get_input("Choice:", C.CYAN)
    if ch.lower() == "r":
        idx = get_input("Enter number to remove:", C.CYAN)
        if idx.isdigit() and 1 <= int(idx) <= len(favs):
            pid = favs[int(idx) - 1]
            favs.remove(pid)
            save_favorites(favs)
            success_msg(f"Removed {pid} from favorites.")
        else:
            error_msg("Invalid index.")
        pause()

# ============================================================
#   SETTINGS VIEW
# ============================================================
def settings_menu():
    global SETTINGS
    while True:
        print_banner()
        print(f"{C.YELLOW}{C.BOLD}⚙️  SETTINGS{C.RESET}\n")
        for i, (k, v) in enumerate(SETTINGS.items(), 1):
            status = f"{C.GREEN}ON{C.RESET}" if v is True else (f"{C.RED}OFF{C.RESET}" if v is False else f"{C.CYAN}{v}{C.RESET}")
            print(f"  {C.CYAN}{i}.{C.RESET} {k:<15} : {status}")
        print()
        print(f"  {C.CYAN}0.{C.RESET} Back")
        ch = get_input("Toggle which setting:", C.CYAN)
        if ch == "0":
            break
        if ch.isdigit() and 1 <= int(ch) <= len(SETTINGS):
            key = list(SETTINGS.keys())[int(ch) - 1]
            if isinstance(SETTINGS[key], bool):
                SETTINGS[key] = not SETTINGS[key]
            else:
                new_val = get_input(f"New value for {key}:", C.CYAN)
                SETTINGS[key] = new_val
            save_settings(SETTINGS)
            success_msg(f"{key} updated.")

# ============================================================
#   STATS VIEW
# ============================================================
def show_stats():
    print_banner()
    print(f"{C.YELLOW}{C.BOLD}📊 STATISTICS{C.RESET}\n")
    data = load_history()
    total = len(data)
    success = sum(1 for e in data if e.get("success"))
    fail = total - success
    if total == 0:
        warn_msg("No data yet.")
        pause()
        return
    print(f"  {C.CYAN}Total Calls    :{C.RESET} {C.BOLD}{total}{C.RESET}")
    print(f"  {C.GREEN}Successful     :{C.RESET} {C.BOLD}{success}{C.RESET}")
    print(f"  {C.RED}Failed         :{C.RESET} {C.BOLD}{fail}{C.RESET}")
    rate = (success / total) * 100
    bar_len = 40
    filled = int(bar_len * rate / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"  {C.YELLOW}Success Rate   :{C.RESET} {C.GREEN}[{bar}]{C.RESET} {rate:.1f}%")
    print()
    # Top pranks
    from collections import Counter
    counter = Counter(e.get("prank_id") for e in data)
    print(f"{C.YELLOW}{C.BOLD}Top Pranks:{C.RESET}")
    for pid, cnt in counter.most_common(5):
        print(f"  {C.GREEN}{pid}{C.RESET} — {cnt} calls | {PRANK_IDS.get(pid, '?')}")
    pause()

# ============================================================
#   ABOUT
# ============================================================
def show_about():
    print_banner()
    box(
        "ABOUT",
        f"""{C.CYAN}Tool Name   :{C.RESET} DCS Premium Prank Call Tool
{C.CYAN}Version     :{C.RESET} 2.0.0
{C.CYAN}Team        :{C.RESET} {C.BOLD}{TEAM_NAME}{C.RESET}
{C.CYAN}Powered By  :{C.RESET} {C.BOLD}{POWERED_BY}{C.RESET}
{C.CYAN}API         :{C.RESET} cxofb.nid-bd.my.id
{C.CYAN}Platform    :{C.RESET} Termux / Linux / Windows
{C.CYAN}Language    :{C.RESET} Python 3.x

{C.YELLOW}Features:{C.RESET}
  • 8 prank types
  • Animated CLI interface
  • Call history & statistics
  • Favorites system
  • Settings manager
  • Full English UI
""",
        C.CYAN
    )
    pause()

# ============================================================
#   MAIN MENU
# ============================================================
def main_menu():
    while True:
        print_banner()
        print(f"{C.BOLD}{C.WHITE}  MAIN MENU{C.RESET}\n")
        print(f"  {C.CYAN}1.{C.RESET} 📞  Make a prank call")
        print(f"  {C.CYAN}2.{C.RESET} 🎭  List all prank IDs")
        print(f"  {C.CYAN}3.{C.RESET} 📜  Call history")
        print(f"  {C.CYAN}4.{C.RESET} ⭐  Manage favorites")
        print(f"  {C.CYAN}5.{C.RESET} 📊  Statistics")
        print(f"  {C.CYAN}6.{C.RESET} ⚙️   Settings")
        print(f"  {C.CYAN}7.{C.RESET} ℹ️   About")
        print(f"  {C.RED}0.{C.RESET} 🚪  Exit")
        print()
        choice = get_input("Select an option:", C.CYAN)

        if choice == "1":
            make_call_flow()
        elif choice == "2":
            list_pranks()
        elif choice == "3":
            show_history()
        elif choice == "4":
            manage_favorites()
        elif choice == "5":
            show_stats()
        elif choice == "6":
            settings_menu()
        elif choice == "7":
            show_about()
        elif choice == "0":
            print_banner()
            typing_effect(f"Goodbye! Thanks for using {TEAM_NAME} tool.", 0.03, C.GREEN)
            print(f"{C.GRAY}Powered by {POWERED_BY}{C.RESET}")
            time.sleep(1)
            break
        else:
            error_msg("Invalid option.")
            time.sleep(1)

# ============================================================
#   ENTRY POINT
# ============================================================
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Interrupted by user.{C.RESET}")
        sys.exit(0)
