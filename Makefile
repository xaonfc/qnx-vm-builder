# Minimal Makefile to operate on the Kconfig fragment and run mkqnximage
KCONFIG := Kconfig
CONFIG := .config
SCRIPTS := scripts
PY := $(shell which python3 || which python)
MENU := $(shell which menuconfig || which mconf || which kconfig-mconf || which menuconfig-qt || which xconfig)

.PHONY: all menuconfig generic build clean distclean show-config edit-users

all: build

menuconfig:
ifeq ($(MENU),)
	@echo "No 'menuconfig' frontend found in PATH."
	@echo "If you have kconfig-frontends installed, ensure 'menuconfig' or 'mconf' is on PATH."
	@echo "Fallback: run 'make generic' to generate a default .config and then 'make build'."
	@exit 1
else
	@$(MENU) $(KCONFIG)
endif

$(CONFIG): $(KCONFIG)
	@make generic

generic: $(SCRIPTS)/gen_default_config.py $(KCONFIG)
	@echo "Generating default .config from $(KCONFIG)..."
	@$(PY) $(SCRIPTS)/gen_default_config.py $(KCONFIG) $(CONFIG)
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
	    rm -rf local/* output/*; \
	    echo "clean complete."; \
	else \
	    echo "Aborted."; \
	fi

# 'distclean' removes local/, output/ AND .config (interactive confirmation required)
distclean: clean
	@read -p "DANGEROUS: this will remove .config. Continue? [y/N]: " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
	    rm -f $(CONFIG); \
	    echo "distclean complete."; \
	else \
	    echo "Aborted."; \
	fi

