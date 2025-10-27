#!/usr/bin/env python3
"""
Generate a simple .config from the Kconfig defaults.

Improvements:
 - Recognizes 'choice' blocks and their 'default SYMBOL' entries (writes that SYMBOL=y).
 - Validates MKQNX_CPU (must be 1..4) and MKQNX_RAM (must be <digits>[M|G]?; if no suffix M is appended).
"""
import re
import sys
from pathlib import Path

def parse_kconfig(lines):
    configs = {}   # symbol -> (type, value)
    choice_defaults = {}

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        m = re.match(r'^\s*config\s+([A-Za-z0-9_]+)', line)
        if m:
            sym = m.group(1)
            j = i + 1
            default_val = None
            while j < len(lines):
                l = lines[j].strip()
                if re.match(r'^(config|choice|menu|endmenu|endchoice)\b', l):
                    break
                dm = re.match(r'^default\s+(.*)$', l)
                if dm:
                    default_val = dm.group(1).strip()
                    default_val = re.sub(r'\s*#.*$', '', default_val).strip()
                    break
                j += 1
            if default_val is not None:
                if re.match(r'^"(.*)"$', default_val):
                    configs[sym] = ("string", re.match(r'^"(.*)"$', default_val).group(1))
                elif re.match(r'^[0-9]+$', default_val):
                    configs[sym] = ("int", default_val)
                elif default_val in ("y", "n"):
                    configs[sym] = ("bool", default_val)
                else:
                    configs[sym] = ("string", default_val.strip('"'))
            i = j
            continue

        mc = re.match(r'^\s*choice\b', line)
        if mc:
            j = i + 1
            while j < len(lines):
                lj = lines[j].strip()
                dm = re.match(r'^default\s+([A-Za-z0-9_]+)', lj)
                if dm:
                    chosen = dm.group(1)
                    choice_defaults[chosen] = True
                if re.match(r'^endchoice\b', lj):
                    break
                j += 1
            i = j + 1
            continue

        i += 1

    for sym in choice_defaults:
        if sym not in configs:
            configs[sym] = ("bool", "y")
        else:
            typ, val = configs[sym]
            if typ != "bool":
                configs[sym] = ("bool", "y")

    return configs

def validate_configs(configs):
    if "MKQNX_CPU" in configs:
        typ, val = configs["MKQNX_CPU"]
        try:
            num = int(val)
            if not (1 <= num <= 4):
                print(f"Warning: MKQNX_CPU default {val} out of 1..4; resetting to 2", file=sys.stderr)
                configs["MKQNX_CPU"] = ("int", "2")
        except (ValueError, TypeError):
            configs["MKQNX_CPU"] = ("int", "2")

    if "MKQNX_RAM" in configs:
        typ, val = configs["MKQNX_RAM"]
        if not re.match(r'^[1-9][0-9]*([MG])?$', str(val), re.IGNORECASE):
            print(f"Warning: MKQNX_RAM default '{val}' not in format <digits>[M|G]; resetting to '1G'", file=sys.stderr)
            configs["MKQNX_RAM"] = ("string", "1G")
        elif re.match(r'^[1-9][0-9]*$', str(val)):
            configs["MKQNX_RAM"] = ("string", str(val) + "M")

def write_config(out_path, kconf_path, configs):
    out_lines = [
        f"# Automatically generated default .config from {kconf_path}",
        "# Regenerate with scripts/gen_default_config.py",
        ""
    ]

    for sym in sorted(configs.keys()):
        typ, val = configs[sym]
        if typ == "bool":
            if val == "y":
                out_lines.append(f"CONFIG_{sym}=y")
        elif typ == "int":
            out_lines.append(f"CONFIG_{sym}={val}")
        elif typ == "string":
            out_lines.append(f'CONFIG_{sym}="{val}"')

    out_text = "\n".join(out_lines) + "\n"
    out_path.write_text(out_text, encoding="utf-8")
    print("Wrote", out_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: gen_default_config.py Kconfig [out_config]", file=sys.stderr)
        sys.exit(2)

    kconf_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path(".config")

    if not kconf_path.exists():
        print("Kconfig not found:", kconf_path, file=sys.stderr)
        sys.exit(1)

    lines = kconf_path.read_text(encoding="utf-8").splitlines()
    configs = parse_kconfig(lines)
    validate_configs(configs)
    write_config(out_path, kconf_path, configs)

if __name__ == "__main__":
    main()

