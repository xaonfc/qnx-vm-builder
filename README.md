**BIG FAT WARNING**: Every code or documentation of this repository were generated or assisted by AI models such as Gemini and ChatGPT. Bugs and odd behavior are to be expected. Please open an issue for any problems or a pull request for fixes and improvements. 

Yours sincerely,
*Mario*

# buildqnx

## Overview

This project provides a set of scripts and configurations to build and run QNX within various virtual machines, including QEMU, VirtualBox, VMware, and QVM. It aims to simplify the process of setting up a QNX development environment or testing QNX applications.

## Features

*   **Multi-hypervisor Support:** Build QNX images for QEMU, VirtualBox, VMware, and QVM.
*   **Configurable QNX Image:** Utilizes Kconfig for flexible configuration of the QNX image, including architecture, CPU, RAM, networking, and security features.
*   **Automated Build Process:** Scripts to generate default configurations and build the QNX image using `mkqnximage`.
*   **Interactive User Management:** A command-line tool to easily add, edit, and manage users within the QNX image.

## Getting Started

### Prerequisites

This project relies on a few external tools. Please ensure they are installed on your system.

*   **`mkqnximage`:** This tool is required to build the QNX image. It must be installed, licensed via the QNX Software Center, and available in your system’s `$PATH`.
*   **Python 3:** The build scripts are written in Python 3.
*   **Virtualization Software:** You will need one of the supported virtualization platforms to run the generated image:
    *   QEMU
    *   VirtualBox
    *   VMware (Workstation or Player)
    *   QVM (no idea what is this)

### Installation Instructions

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt upgrade
sudo apt install git build-essential python3 qemu-system
```

**Arch Linux:**
```bash
sudo pacman -Syu
sudo pacman -S base-devel git python qemu-desktop
```

**Fedora:**
```bash
sudo dnf update && sudo dnf upgrade
sudo dnf install @development-tools git python3 qemu-kvm
```

**Note on VMware:** VMware products are proprietary and must be downloaded from the official [VMware website](https://www.vmware.com/products/desktop-hypervisor/workstation-and-fusion).

### Installation

1.  Clone this repository:
    ```bash
    git clone https://github.com/xaonfc/buildqnx
    cd buildqnx
    ```

2.  (Optional) Generate a default configuration:
    ```bash
    make defconfig
    ```

3.  (Optional) Configure the QNX image interactively:
    ```bash
    make menuconfig
    ```
    (This will automatically clone and build the necessary kconfig tools if they are not present.)

### Building the QNX Image

To build the QNX image based on your `.config` file:

```bash
make
```

This will execute the `mkqnximage` tool with the parameters specified in your `.config`.

### Managing Users

To interactively add, edit, or delete users in your QNX configuration:

```bash
make edit-users
```

### Cleaning the Project

To remove build artifacts (contents of `local/` and `output/`):

```bash
make clean
```

To remove build artifacts and the `.config` file, and the `kbuild-standalone` directory:

```bash
make distclean
```

## Configuration

The project uses a `Kconfig` file to define various options for the QNX image. You can configure these options using `make menuconfig` or by directly editing the `.config` file.

## Contributing

Contributions are welcome! Please refer to the `LICENSE` file for licensing information.

## License

This project is licensed under the GNU General Public License, version 3. See the `LICENSE` file for the full license text.

The `scripts/tools` directory contains a modified version of the Linux kernel's Kconfig scripts. These scripts are licensed under the GNU General Public License, version 2.

## Credits

- The Linux kernel developers for the Kconfig system: [torvalds/linux](https://github.com/torvalds/linux)
- [gemini-cli](https://github.com/google-gemini/gemini-cli) for helping making this project possible
- [QNX](https://blackberry.qnx.com/en) for making an awesome operating system