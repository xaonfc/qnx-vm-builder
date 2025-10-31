KCONFIG := Kconfig
CONFIG := .config
OLDCONFIG := .config.old
SCRIPTS := scripts
PY := $(shell which python3 || which python)

.PHONY: help kbuild-standalone

all: build

help:
	@echo "Available targets:"
	@echo "  config       - Update .config using a line-oriented program"
	@echo "  menuconfig   - Interactively configure the QNX image (builds kbuild-standalone if needed)"
	@echo "  oldconfig    - Update .config using Kconfig, preserving existing answers and setting new options to default"
	@echo "  defconfig    - Generate a default .config from Kconfig"
	@echo "  allyesconfig - Generate a .config with all options set to yes"
	@echo "  allnoconfig  - Generate a .config with all options set to no"
	@echo "  build        - Build the QNX image using mkqnximage"
	@echo "  show-config  - Display the current .config file"
	@echo "  edit-users   - Launch interactive users editor"
	@echo "  clean        - Remove build output directories (local/ and output/)"
	@echo "  distclean    - Remove build output, .config, and kbuild-standalone directory"

KCONFIG_DIR := scripts/kconfig-standalone

.PHONY: build-kconfig

build-kconfig:
	@if [ ! -f "$(KCONFIG_DIR)/bin/mconf" ]; then \
		make -C $(KCONFIG_DIR); \
	fi

.PHONY: help menuconfig oldconfig defconfig allyesconfig allnoconfig build clean distclean show-config edit-users config
menuconfig: build-kconfig
	@$(KCONFIG_DIR)/bin/mconf $(KCONFIG)

config: build-kconfig
	@$(KCONFIG_DIR)/bin/conf $(KCONFIG)

oldconfig: build-kconfig
	@$(KCONFIG_DIR)/bin/conf --oldconfig $(KCONFIG)

allyesconfig: build-kconfig
	@$(KCONFIG_DIR)/bin/conf --allyesconfig $(KCONFIG)

allnoconfig: build-kconfig
	@$(KCONFIG_DIR)/bin/conf --allnoconfig $(KCONFIG)

$(CONFIG): $(KCONFIG)
	@make defconfig

defconfig: configs/defconfig
	@cp configs/defconfig $(CONFIG)
	@echo "Wrote $(CONFIG)."

build: $(SCRIPTS)/build_mkqnximage.py $(CONFIG)
	@echo "Running mkqnximage using $(CONFIG)..."
	@$(PY) $(SCRIPTS)/build_mkqnximage.py $(CONFIG)

show-config: $(CONFIG)
	@echo "---- $(CONFIG) ----"
	@cat $(CONFIG) || true
	@echo "-------------------"

edit-users: $(SCRIPTS)/edit_users.py $(CONFIG)
	@echo "Launching interactive users editor..."
	@$(PY) $(SCRIPTS)/edit_users.py

# 'clean' removes build output directories (interactive confirmation required)
clean:
	@read -p "This will remove contents of local/ and output/ (if present). Continue? [y/N]: " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
	    rm -rf local output; \
	    echo "clean complete."; \
	else \
	    echo "Aborted."; \
	fi

# 'distclean' removes local/, output/ AND .config (interactive confirmation required)
distclean: clean
	@read -p "DANGEROUS: this will remove .config. Continue? [y/N]: " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
	    rm -f $(CONFIG) $(OLDCONFIG); \
	    make -C $(KCONFIG_DIR) clean; \
	    rm -rf kbuild-standalone; \
	    echo "distclean complete."; \
	else \
	    echo "Aborted."; \
	fi

