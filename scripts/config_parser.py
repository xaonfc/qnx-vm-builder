
import re

def parse_config(conf_path):
    """Parses a .config file and returns a dictionary of key-value pairs."""
    cfg = {}
    for ln in conf_path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        m = re.match(r'^CONFIG_([A-Za-z0-9_]+)=(.*)$', ln)
        if not m:
            continue
        key = m.group(1)
        val = m.group(2).strip()
        if val == "y":
            cfg[key] = True
        elif val == "n":
            cfg[key] = False
        else:
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                cfg[key] = val[1:-1]
            else:
                cfg[key] = val
    return cfg

def bool_of(cfg, k):
    """Returns the boolean value of a key in the config."""
    return bool(cfg.get(k, False))

def str_of(cfg, k, default=""):
    """Returns the string value of a key in the config."""
    v = cfg.get(k, None)
    if v is None:
        return default
    return str(v)

def int_of(cfg, k, default=0):
    """Returns the integer value of a key in the config."""
    return int(str_of(cfg, k, str(default)))
