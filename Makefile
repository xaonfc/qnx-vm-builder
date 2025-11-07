KCONFIG := Kconfig
CONFIG := .config
OLDCONFIG := .config.old
SCRIPTS := scripts
PY := $(shell which python3 || which python)
BUILD_SCRIPT := $(SCRIPTS)/build_mkqnximage.py

.PHONY: help kbuild-standalone all

all: build

# Auto-detect configuration targets from the configs/ directory.
# For each file in configs/, a make target is created with the same name.
# For example, 'make myconfig' will use 'configs/myconfig' to generate .config.
CONFIG_FILES := $(wildcard configs/*)
CONFIG_TARGETS := $(notdir $(CONFIG_FILES))

.PHONY: $(CONFIG_TARGETS)
$(CONFIG_TARGETS):
	@cp configs/$@ $(CONFIG)
	@echo "#"
	@echo "# Using config: $@"
	@echo "#"

# Categorize help targets by their function

help:
	@echo "Available make targets:"
	@echo ""
	@echo " General configuration targets:"
	@echo "   menuconfig       - Launch graphical menu-based configuration"
	@echo "   nconfig          - Launch ncurses-based configuration"
	@echo "   xconfig          - Launch Qt-based configuration"
	@echo "   gconfig          - Launch GTK-based configuration"
	@echo "   config           - Basic text-based configuration"
	@echo "   oldconfig        - Update current config with new options"
	@echo "   allyesconfig     - Set all options to 'yes'"
	@echo "   allnoconfig      - Set all options to 'no'"
	@echo "   randconfig       - Generate random config"
	@echo ""
	@echo " Pre-defined configuration targets (from configs/):"
	@for config in $(CONFIG_TARGETS); do \
		printf "   %-20s - Create .config from configs/%s\n" "$$config" "$$config"; \
	done
	@echo ""
	@echo " Build targets:"
	@echo "   build            - Build the image using the current config"
	@echo ""
	@echo " Utility targets:"
	@echo "   show-config      - Display the current configuration"
	@echo "   edit-users       - Edit user accounts in the configuration"
	@echo ""
	@echo " Cleanup targets:"
	@echo "   clean            - Remove build output directories (local/, output/)"
	@echo "   distclean        - Remove build output and configuration files"
	@echo ""

KCONFIG_DIR := scripts
KCONFIG_BIN := $(KCONFIG_DIR)/kconfig

.PHONY: conf-bin mconf-bin nconf-bin qconf-bin gconf-bin

conf-bin:
	@make -C $(KCONFIG_DIR) conf

mconf-bin:
	@make -C $(KCONFIG_DIR) mconf

nconf-bin:
	@make -C $(KCONFIG_DIR) nconf

qconf-bin:
	@make -C $(KCONFIG_DIR) qconf

gconf-bin:
	@make -C $(KCONFIG_DIR) gconf

.PHONY: help menuconfig nconfig xconfig gconfig oldconfig allyesconfig allnoconfig randconfig build clean distclean show-config edit-users config

menuconfig: mconf-bin
	@$(KCONFIG_BIN)/mconf $(KCONFIG)

nconfig: nconf-bin
	@$(KCONFIG_BIN)/nconf $(KCONFIG)

xconfig: qconf-bin
	@$(KCONFIG_BIN)/qconf $(KCONFIG)

gconfig: gconf-bin
	@$(KCONFIG_BIN)/gconf $(KCONFIG)

config: conf-bin
	@$(KCONFIG_BIN)/conf $(KCONFIG)

oldconfig: conf-bin
	@$(KCONFIG_BIN)/conf --oldconfig $(KCONFIG)

allyesconfig: conf-bin
	@$(KCONFIG_BIN)/conf --allyesconfig $(KCONFIG)

allnoconfig: conf-bin
	@$(KCONFIG_BIN)/conf --allnoconfig $(KCONFIG)

# what could possibly go wrong with a random config?

randconfig: conf-bin
	@$(KCONFIG_BIN)/conf --randconfig $(KCONFIG)

$(CONFIG): $(KCONFIG)
	@make defconfig

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
	@test -d $(KCONFIG_BIN) && echo '  CLEAN   scripts/kconfig' && make -C $(KCONFIG_DIR) clean --silent || true
	@test -f $(CONFIG) && rm -f $(CONFIG) || true
	@test -f $(OLDCONFIG) && rm -f $(OLDCONFIG) || true
	@test -d include && echo '  CLEAN   include' && rm -rf include || true

