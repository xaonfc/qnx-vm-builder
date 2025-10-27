#!/usr/bin/env python3
"""
Interactive editor for MKQNX_USERS in .config.

Features:
- Supports unlimited users
- Add / edit / delete / move entries
- Password entry hides input (use '-' to indicate explicit NO password)
- Saves result to CONFIG_MKQNX_USERS="user1/pass1:user2:..."
- If .config is missing, auto-generate using scripts/gen_default_config.py
"""
import sys
import re
import subprocess
from pathlib import Path
import getpass
from config_parser import parse_config

CONFIG_PATH = Path(".config")
GEN_SCRIPT = Path("scripts/gen_default_config.py")

USERNAME_RE = re.compile(r'^[A-Za-z0-9_-]+$')

def read_config_lines(path: Path):
    if path.exists():
        return path.read_text(encoding="utf-8").splitlines()
    return []

def write_config_lines(path: Path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def render_users_to_string(user_entries):
    """
    user_entries: list of tuples (username, password_or_none_or_dash)
    password rules:
      None or "" -> omitted in the output (mkqnximage will create password)
      "-" -> explicit no-password marker (will be user/- in result)
      otherwise -> use provided password
    """
    parts = []
    for user, pwd in user_entries:
        if not user:
            continue
        if pwd is None or pwd == "":
            parts.append(user)
        else:
            parts.append(f"{user}/{pwd}")
    return ":".join(parts)

def parse_users_from_string(s):
    """
    returns list of (user, pwd_or_none_or_dash)
    """
    out = []
    if not s:
        return out
    for item in s.split(":"):
        if not item:
            continue
        if "/" in item:
            u, p = item.split("/", 1)
            out.append((u, p))
        else:
            out.append((item, None))
    return out

def input_with_default(prompt, default):
    return input(f"{prompt} [{default or ''}] ") or default

def require_config():
    if not CONFIG_PATH.exists():
        if GEN_SCRIPT.exists():
            print(".config not found — generating defaults with scripts/gen_default_config.py ...")
            rc = subprocess.call([sys.executable, str(GEN_SCRIPT), "Kconfig", str(CONFIG_PATH)])
            if rc != 0:
                print(f"Failed to generate .config (gen script returned {rc})", file=sys.stderr)
                sys.exit(1)
            print("Generated", CONFIG_PATH)
        else:
            print(".config not found and gen_default_config.py missing. Create .config first.", file=sys.stderr)
            sys.exit(1)

def show_menu(user_entries):
    print("\nConfigured users:")
    if not user_entries:
        print("  <none>")
    else:
        for i, (u, p) in enumerate(user_entries, 1):
            pwd_disp = "<empty>" if (p is None or p == "") else ("'-' (no-password)" if p == "-" else "***")
            print(f"  {i}. {u}  ({pwd_disp})")
    print("\nActions:")
    print("  a  Add user")
    print("  eN Edit user number N (e.g. e2 to edit #2)")
    print("  pN Show password for user N")
    print("  dN Delete user number N")
    print("  mN M Move user N to position M (e.g. m3 1 moves #3 to pos 1)")
    print("  s  Save and exit")
    print("  c  Cancel (exit without saving)")
    print("  h  Help (this menu)\n")

def add_user(user_entries):
    while True:
        name = input("Enter username (allowed characters A-Za-z0-9_-). Empty to cancel: ").strip()
        if not name:
            print("Add cancelled.")
            return
        if not USERNAME_RE.match(name):
            print("Invalid username. Only letters, numbers, '-' and '_' allowed. Try again.")
            continue
        break
    pwd = getpass.getpass("Enter password (leave empty to omit; enter '-' to explicitly set no-password): ")
    if pwd == "":
        pwd = None
    user_entries.append((name, pwd))
    print("Added.")

def edit_user(user_entries, idx):
    if not (0 <= idx < len(user_entries)):
        print("Invalid index.")
        return
    cur_name, cur_pwd = user_entries[idx]
    print(f"Editing user #{idx+1}: '{cur_name}'")
    new_name = input_with_default("New username", cur_name).strip()
    if not new_name:
        print("Username cannot be empty; edit cancelled.")
        return
    if not USERNAME_RE.match(new_name):
        print("Invalid username characters; edit cancelled.")
        return
    # password editing
    print("Password editing: leave empty to keep current, enter '-' to explicitly set no-password,")
    pwd_prompt = "(current: none)" if (cur_pwd is None or cur_pwd == "") else "(current: set or '-' )"
    new_pwd = getpass.getpass(f"New password {pwd_prompt}: ")
    if not new_pwd:
        # keep existing
        new_pwd = cur_pwd
    user_entries[idx] = (new_name, new_pwd)
    print("Updated.")

def show_password(user_entries, idx):
    if not (0 <= idx < len(user_entries)):
        print("Invalid index.")
        return
    u, p = user_entries[idx]
    print(f"Password for user '{u}': {p or '<none>'}")

def delete_user(user_entries, idx):
    if not (0 <= idx < len(user_entries)):
        print("Invalid index.")
        return
    u, p = user_entries[idx]
    confirm = input(f"Delete user '{u}'? [y/N]: ").strip().lower()
    if confirm == "y":
        user_entries.pop(idx)
        print("Deleted.")
    else:
        print("Cancelled.")

def move_user(user_entries, src_idx, dst_idx):
    if not (0 <= src_idx < len(user_entries) and 0 <= dst_idx <= len(user_entries)):
        print("Invalid indices.")
        return
    item = user_entries.pop(src_idx)
    user_entries.insert(dst_idx, item)
    print(f"Moved to position {dst_idx+1}.")

def save_users_to_config(user_entries):
    lines = read_config_lines(CONFIG_PATH)
    users_str = render_users_to_string(user_entries)
    new_line = f'CONFIG_MKQNX_USERS="{users_str}"'
    found = False
    out_lines = []
    for ln in lines:
        if re.match(r'^\s*CONFIG_MKQNX_USERS=', ln):
            out_lines.append(new_line)
            found = True
        else:
            out_lines.append(ln)
    if not found:
        out_lines.append(new_line)
    write_config_lines(CONFIG_PATH, out_lines)
    print("Saved to", CONFIG_PATH)

def process_actions(user_entries):
    while True:
        show_menu(user_entries)
        choice = input("Choose action: ").strip()
        if not choice:
            continue

        action, arg = (choice[0], choice[1:])

        if action == 'a':
            add_user(user_entries)
        elif action == 'e':
            try:
                idx = int(arg) - 1
                edit_user(user_entries, idx)
            except (ValueError, IndexError):
                print("Invalid edit command. Use eN (e.g. e2).")
        elif action == 'p':
            try:
                idx = int(arg) - 1
                show_password(user_entries, idx)
            except (ValueError, IndexError):
                print("Invalid command. Use pN (e.g. p2).")
        elif action == 'd':
            try:
                idx = int(arg) - 1
                delete_user(user_entries, idx)
            except (ValueError, IndexError):
                print("Invalid delete command. Use dN (e.g. d3).")
        elif action == 'm':
            try:
                parts = arg.strip().split()
                if len(parts) != 2:
                    raise ValueError()
                src = int(parts[0]) - 1
                dst = int(parts[1]) - 1
                move_user(user_entries, src, dst)
            except (ValueError, IndexError):
                print("Invalid move usage. Use mSRC DST (e.g. m3 1).")
        elif action == 's':
            save_users_to_config(user_entries)
            return
        elif action == 'c':
            print("Cancelled — no changes saved.")
            return
        elif action == 'h':
            continue
        else:
            if re.match(r'^[0-9]+$', choice):
                try:
                    idx = int(choice) - 1
                    edit_user(user_entries, idx)
                except (ValueError, IndexError):
                    print("Invalid index.")
            else:
                print("Unknown command. Enter 'h' for help.")

def main():
    require_config()
    config = parse_config(CONFIG_PATH)
    users_raw = config.get("MKQNX_USERS", "")
    user_entries = parse_users_from_string(users_raw)
    process_actions(user_entries)

if __name__ == "__main__":
    main()

