KCONFIG := Kconfig
CONFIG := .config
OLDCONFIG := .config.old
SCRIPTS := scripts
PY := $(shell which python3 || which python)
BUILD_SCRIPT := $(SCRIPTS)/build_mkqnximage.py

.PHONY: help kbuild-standalone all

all: build

# Categorize help targets by their function

help:
	@echo "Available make targets:"
	@echo ""
	@echo " Configuration targets:"
	@echo "   menuconfig       - Launch graphical menu-based configuration"
	@echo "   nconfig         - Launch ncurses-based configuration"
	@echo "   xconfig         - Launch Qt-based configuration"
	@echo "   gconfig         - Launch GTK-based configuration"
	@echo "   config          - Basic text-based configuration"
	@echo "   oldconfig       - Update current config with new options"
	@echo "   defconfig       - Create default config file"
	@echo "   allyesconfig    - Set all options to 'yes'"
	@echo "   allnoconfig     - Set all options to 'no'"
	@echo "   randconfig      - Generate random config"
	@echo ""
	@echo " Build targets:"
	@echo "   build           - Build the image using the current config"
	@echo ""
	@echo " Utility targets:"
	@echo "   show-config     - Display the current configuration"
	@echo "   edit-users      - Edit user accounts in the configuration"
	@echo ""
	@echo " Cleanup targets:"
	@echo "   clean           - Remove build output directories (local/, output/)"
	@echo "   distclean      - Remove build output and configuration files"
	@echo ""

KCONFIG_DIR := scripts/tools

.PHONY: conf-bin mconf-bin nconf-bin qconf-bin gconf-bin

conf-bin:
	@make -C $(KCONFIG_DIR) bin/conf

mconf-bin:
	@make -C $(KCONFIG_DIR) bin/mconf

nconf-bin:
	@make -C $(KCONFIG_DIR) bin/nconf

qconf-bin:
	@make -C $(KCONFIG_DIR) bin/qconf

gconf-bin:
	@make -C $(KCONFIG_DIR) bin/gconf

.PHONY: help menuconfig nconfig xconfig gconfig oldconfig defconfig allyesconfig allnoconfig randconfig build clean distclean show-config edit-users config

menuconfig: mconf-bin
	@$(KCONFIG_DIR)/bin/mconf $(KCONFIG)

nconfig: nconf-bin
	@$(KCONFIG_DIR)/bin/nconf $(KCONFIG)

xconfig: qconf-bin
	@$(KCONFIG_DIR)/bin/qconf $(KCONFIG)

gconfig: gconf-bin
	@$(KCONFIG_DIR)/bin/gconf $(KCONFIG)

config: conf-bin
	@$(KCONFIG_DIR)/bin/conf $(KCONFIG)

oldconfig: conf-bin
	@$(KCONFIG_DIR)/bin/conf --oldconfig $(KCONFIG)

allyesconfig: conf-bin
	@$(KCONFIG_DIR)/bin/conf --allyesconfig $(KCONFIG)

allnoconfig: conf-bin
	@$(KCONFIG_DIR)/bin/conf --allnoconfig $(KCONFIG)

# what could possibly go wrong with a random config?

randconfig: conf-bin
	@$(KCONFIG_DIR)/bin/conf --randconfig $(KCONFIG)

$(CONFIG): $(KCONFIG)
	@make defconfig

defconfig: configs/defconfig
	@cp configs/defconfig $(CONFIG)
	@echo "Wrote $(CONFIG)."

build: $(BUILD_SCRIPT) $(CONFIG)
	@echo "Running mkqnximage using $(CONFIG)..."
	@$(PY) $(BUILD_SCRIPT) $(CONFIG)

show-config: $(CONFIG)
	@echo "---- $(CONFIG) ----"
	@cat $(CONFIG) || true
	@echo "-------------------"

edit-users: $(SCRIPTS)/edit_users.py $(CONFIG)
	@echo "Launching interactive users editor..."
	@$(PY) $(SCRIPTS)/edit_users.py

clean:
	@test -d local && echo '  CLEAN   local' && rm -rf local || true
	@test -d output && echo '  CLEAN   output' && rm -rf output || true

distclean: clean
	@test -d $(KCONFIG_DIR)/bin && echo '  CLEAN   scripts/tools/kconfig' && make -C $(KCONFIG_DIR) clean --silent || true
	@test -f $(CONFIG) && rm -f $(CONFIG) || true
	@test -f $(OLDCONFIG) && rm -f $(OLDCONFIG) || true
	@test -d include && echo '  CLEAN   include' && rm -rf include || true

