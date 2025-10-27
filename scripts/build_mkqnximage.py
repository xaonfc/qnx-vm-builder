#!/usr/bin/env python3

import shlex
import shutil
import subprocess
import sys
import re
from pathlib import Path
from config_parser import parse_config, bool_of, str_of, int_of

def main():
    if len(sys.argv) < 2:
        print("Usage: build_mkqnximage.py .config", file=sys.stderr)
        sys.exit(2)

    conf_path = Path(sys.argv[1])
    if not conf_path.exists():
        print("Config file not found:", conf_path, file=sys.stderr)
        sys.exit(1)

    cfg = parse_config(conf_path)

    mkqnx_cmd = shutil.which("mkqnximage")
    if not mkqnx_cmd:
        print("Error: 'mkqnximage' not found on PATH.", file=sys.stderr)
        sys.exit(1)

    cmd = [mkqnx_cmd]

    # Always pass --force (script-enforced)
    cmd.append("--force")

    # ARCH: check choice symbols
    arch = "x86_64"
    if bool_of(cfg, "MKQNX_ARCH_AARCH64LE"):
        arch = "aarch64le"
    cmd.append(f"--arch={arch}")

    # Behavior
    if bool_of(cfg, "MKQNX_VERBOSE"):
        cmd.append("--verbose=yes")
    ai = str_of(cfg, "MKQNX_ASSUMED_IP", "")
    if ai:
        cmd.append(f"--assumed-ip={ai}")
    if bool_of(cfg, "MKQNX_CLEAN"):
        cmd.append("--clean")
    if bool_of(cfg, "MKQNX_NOPROMPT"):
        cmd.append("--noprompt")

    # Runtime: type from choice symbols
    typ = "qemu"
    if bool_of(cfg, "MKQNX_TYPE_VMWARE"):
        typ = "vmware"
    elif bool_of(cfg, "MKQNX_TYPE_VBOX"):
        typ = "vbox"
    elif bool_of(cfg, "MKQNX_TYPE_QVM"):
        typ = "qvm"
    if typ != "qemu":
        cmd.append(f"--type={typ}")

    # cpu
    cpu = int_of(cfg, "MKQNX_CPU", 2)
    if not 1 <= cpu <= 4:
        print("Warning: MKQNX_CPU must be between 1 and 4.", file=sys.stderr)
        cpu = 2
    if cpu != 2:
        cmd.append(f"--cpu={cpu}")

    proc = str_of(cfg, "MKQNX_PROC", "")
    if proc:
        cmd.append(f"--proc={proc}")

    ram = str_of(cfg, "MKQNX_RAM", "1G")
    if not re.match(r'^[1-9][0-9]*([MG])?$', ram, re.IGNORECASE):
        print("Warning: MKQNX_RAM has invalid format; using 1G.", file=sys.stderr)
        ram = "1G"
    if ram != "1G":
        cmd.append(f"--ram={ram}")


    # Partitioning
    ps = str_of(cfg, "MKQNX_PART_SIZES", "full")
    if ps != "full":
        cmd.append(f"--part-sizes={ps}")

    for k in ("BOOT_SIZE", "SYS_SIZE", "SYS_INODES", "DATA_SIZE", "DATA_INODES"):
        val = int_of(cfg, f"MKQNX_{k}", 0)
        if val > 0:
            cmd.append(f"--{k.lower().replace('_', '-')}={val}")

    # FS & Integrity
    if not bool_of(cfg, "MKQNX_UNION"):
        cmd.append("--union=no")

    qcfs = "no"
    if bool_of(cfg, "MKQNX_QCFS_LZ4HC"):
        qcfs = "lz4hc"
    elif bool_of(cfg, "MKQNX_QCFS_ZSTD"):
        qcfs = "zstd"
    elif bool_of(cfg, "MKQNX_QCFS_YES"):
        qcfs = "yes"
    if qcfs != "no":
        cmd.append(f"--qcfs={qcfs}")

    if bool_of(cfg, "MKQNX_QTD"):
        cmd.append("--qtd=yes")
    if bool_of(cfg, "MKQNX_QTSAFEFS"):
        cmd.append("--qtsafefs=yes")

    secure_data = "no"
    if bool_of(cfg, "MKQNX_SECURE_DATA_NOSUID"):
        secure_data = "nosuid"
    elif bool_of(cfg, "MKQNX_SECURE_DATA_NOEXEC"):
        secure_data = "noexec"
    if secure_data != "no":
        cmd.append(f"--secure-data={secure_data}")

    if bool_of(cfg, "MKQNX_PATHTRUST"):
        cmd.append("--pathtrust=yes")

    zoneinfo = ""
    if bool_of(cfg, "MKQNX_ZONEINFO_YES"):
        zoneinfo = "yes"
    elif "MKQNX_ZONEINFO_PATH" in cfg:
        zoneinfo = str_of(cfg, "MKQNX_ZONEINFO_PATH", "")
    if zoneinfo and zoneinfo != "no":
        cmd.append(f"--zoneinfo={zoneinfo}")

    tz = str_of(cfg, "MKQNX_TZ", "UTC")
    if tz and tz != "UTC":
        cmd.append(f"--tz={tz}")

    # Users & SSH
    users = str_of(cfg, "MKQNX_USERS", "")
    if users:
        cmd.append(f"--users={users}")
    ssh_ident = str_of(cfg, "MKQNX_SSH_IDENT", "prompt")
    if ssh_ident and ssh_ident != "prompt":
        cmd.append(f"--ssh-ident={ssh_ident}")
    if "MKQNX_SSHD_PREGEN" in cfg:
        if bool_of(cfg, "MKQNX_SSHD_PREGEN"):
            cmd.append("--sshd-pregen=yes")
        else:
            cmd.append("--sshd-pregen=no")

    # Networking
    ip = str_of(cfg, "MKQNX_IP", "dhcp")
    if ip and ip != "dhcp":
        cmd.append(f"--ip={ip}")
    hostname = str_of(cfg, "MKQNX_HOSTNAME", "")
    if hostname:
        cmd.append(f"--hostname={hostname}")
    mac = str_of(cfg, "MKQNX_MACADDR", "")
    if mac:
        cmd.append(f"--macaddr={mac}")
    time_servers = str_of(cfg, "MKQNX_TIME_SERVERS", "pool.ntp.org")
    if time_servers and time_servers != "pool.ntp.org":
        cmd.append(f"--time-servers={time_servers}")

    # Repos & Extras
    repos = str_of(cfg, "MKQNX_REPOS", "")
    if repos:
        cmd.append(f"--repos={repos}")
    extra = str_of(cfg, "MKQNX_EXTRA_DIRS", "")
    if extra:
        cmd.append(f"--extra-dirs={extra}")

    # Security & TPM
    if not bool_of(cfg, "MKQNX_ASLR"):
        cmd.append("--aslr=no")

    if bool_of(cfg, "MKQNX_SECURE_PROCFS"):
        cmd.append("--secure-procfs=yes")
    if bool_of(cfg, "MKQNX_CERTICOM"):
        cmd.append("--certicom=yes")

    tcg = "no"
    if bool_of(cfg, "MKQNX_TCG_CMDLINE"):
        tcg = "cmdline"
    elif bool_of(cfg, "MKQNX_TCG_YES"):
        tcg = "yes"
    if tcg != "no":
        cmd.append(f"--tcg={tcg}")

    if bool_of(cfg, "MKQNX_CRYPTODEV"):
        cmd.append("--cryptodev=yes")

    policy = str_of(cfg, "MKQNX_POLICY", "none")
    if policy and policy != "none":
        cmd.append(f"--policy={policy}")

    secpol = "no"
    if bool_of(cfg, "MKQNX_SECPOL_DEVELOP"):
        secpol = "develop"
    elif bool_of(cfg, "MKQNX_SECPOL_OPEN"):
        secpol = "open"
    elif bool_of(cfg, "MKQNX_SECPOL_SECURE"):
        secpol = "secure"
    if secpol != "no":
        cmd.append(f"--secpol={secpol}")

    if bool_of(cfg, "MKQNX_QFIM"):
        cmd.append("--qfim=yes")

    # Packages
    for pkg in ("TOMCRYPT", "PERL", "PKCS11", "PYTHON", "QAUDIT", "VALGRIND"):
        sym = f"MKQNX_{pkg}"
        if bool_of(cfg, sym):
            cmd.append(f"--{pkg.lower()}=yes")

    # Diagnostics
    if bool_of(cfg, "MKQNX_IO_SOCK_DIAG"):
        cmd.append("--io-sock-diag=yes")
    if bool_of(cfg, "MKQNX_SANITIZERS"):
        cmd.append("--sanitizers=yes")
    qh = str_of(cfg, "MKQNX_QH_CONFIG", "no")
    if qh and qh != "no":
        cmd.append(f"--qh_config={qh}")

    # Hardware
    if not bool_of(cfg, "MKQNX_USB"):
        cmd.append("--usb=no")
    if bool_of(cfg, "MKQNX_GRAPHICS"):
        cmd.append("--graphics=yes")
    nfs = str_of(cfg, "MKQNX_NFS", "no")
    if nfs and nfs != "no":
        cmd.append(f"--nfs={nfs}")

    # System Flags
    if bool_of(cfg, "MKQNX_ROOT"):
        cmd.append("--root=yes")
    if not bool_of(cfg, "MKQNX_ABLELOCK"):
        cmd.append("--ablelock=no")
    if bool_of(cfg, "MKQNX_SLM"):
        cmd.append("--slm=yes")

    # Print and execute
    print("Running command:")
    print(" ".join(shlex.quote(x) for x in cmd))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print("mkqnximage exited with code", e.returncode, file=sys.stderr)
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()

