KCONFIG_SRCDIR := kconfig
LDIALOG_SRCDIR := $(KCONFIG_SRCDIR)/lxdialog
INCLUDE_SRCDIR := include

CC := gcc
CXX := g++
FLEX := flex
BISON := bison
MOC := moc
PKG_CONFIG := pkg-config

BINDIR := kconfig

OBJDIR := kconfig

CPPFLAGS := -I$(KCONFIG_SRCDIR) -I. -I$(INCLUDE_SRCDIR) -I$(OBJDIR) $(shell $(PKG_CONFIG) --cflags Qt5Core Qt5Gui Qt5Widgets) $(shell $(PKG_CONFIG) --cflags gtk+-3.0)
CFLAGS := -O2
CXXFLAGS := -O2 -std=c++11 -fPIC
LDFLAGS := 

ifeq ($(V),1)
  Q = 
else
  Q = @
endif

COMMON_SRCS := confdata.c expr.c menu.c preprocess.c symbol.c util.c

GENERATED_SRCS := lexer.lex.c parser.tab.c parser.tab.h

# Common object files
COMMON_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(COMMON_SRCS)))
COMMON_OBJS += $(addprefix $(OBJDIR)/, lexer.lex.o parser.tab.o)

# conf sources and objects
CONF_SRCS := conf.c
CONF_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(CONF_SRCS)))

# nconf sources and objects
NCONF_SRCS := nconf.c nconf.gui.c mnconf-common.c
NCONF_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(NCONF_SRCS)))

# mconf sources and objects
LDIALOG_SRCS := $(wildcard $(LDIALOG_SRCDIR)/*.c)
LDIALOG_OBJS := $(patsubst $(LDIALOG_SRCDIR)/%.c,$(OBJDIR)/lxdialog_%.o,$(LDIALOG_SRCS))
MCONF_SRCS := mconf.c mnconf-common.c
MCONF_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(MCONF_SRCS)))

# qconf sources and objects
QCONF_SRCS := qconf.cc images.c
QCONF_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.cc,%.o,$(filter %.cc,$(QCONF_SRCS))))
QCONF_OBJS += $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(filter %.c,$(QCONF_SRCS))))
QCONF_OBJS += $(OBJDIR)/qconf-moc.o

# gconf sources and objects
GCONF_SRCS := gconf.c images.c
GCONF_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(filter %.c,$(GCONF_SRCS))))

# Targets
all: $(BINDIR)/conf $(BINDIR)/nconf $(BINDIR)/mconf $(BINDIR)/qconf $(BINDIR)/gconf

$(BINDIR)/conf: $(COMMON_OBJS) $(CONF_OBJS)
	@echo "  LD      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $(COMMON_OBJS) $(CONF_OBJS) $(LDFLAGS)

$(BINDIR)/nconf: $(COMMON_OBJS) $(NCONF_OBJS)
	@echo "  LD      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $(COMMON_OBJS) $(NCONF_OBJS) $(LDFLAGS) -lncurses -lmenu -lpanel

$(BINDIR)/mconf: $(COMMON_OBJS) $(MCONF_OBJS) $(LDIALOG_OBJS)
	@echo "  LD      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $(COMMON_OBJS) $(MCONF_OBJS) $(LDIALOG_OBJS) $(LDFLAGS) -lcurses

$(BINDIR)/qconf: $(COMMON_OBJS) $(QCONF_OBJS)
	@echo "  LD      $@"
	@$(CXX) $(CPPFLAGS) $(CXXFLAGS) -o $@ $(COMMON_OBJS) $(QCONF_OBJS) $(LDFLAGS) $(shell $(PKG_CONFIG) --libs Qt5Core Qt5Gui Qt5Widgets)

$(BINDIR)/gconf: $(COMMON_OBJS) $(GCONF_OBJS) $(KCONFIG_SRCDIR)/gconf.ui
	@echo "  LD      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $(COMMON_OBJS) $(GCONF_OBJS) $(LDFLAGS) $(shell $(PKG_CONFIG) --libs gtk+-3.0)

$(KCONFIG_SRCDIR)/gconf.ui:
	@echo "  CP      $@"
	@cp linux/scripts/kconfig/gconf.ui $@



$(OBJDIR)/%.o: $(KCONFIG_SRCDIR)/%.c
	@echo "  CC      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

# Compilation rules for nconf sources
$(OBJDIR)/nconf.o: $(KCONFIG_SRCDIR)/nconf.c
	@echo "  CC      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

$(OBJDIR)/nconf.gui.o: $(KCONFIG_SRCDIR)/nconf.gui.c
	@echo "  CC      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

$(OBJDIR)/mnconf-common.o: $(KCONFIG_SRCDIR)/mnconf-common.c
	@echo "  CC      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

# Compilation rules for mconf sources
$(OBJDIR)/mconf.o: $(KCONFIG_SRCDIR)/mconf.c
	@echo "  CC      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

# Compilation rules for lxdialog sources
$(OBJDIR)/lxdialog_%.o: $(LDIALOG_SRCDIR)/%.c
	@echo "  CC      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

# Compilation rules for qconf sources
$(OBJDIR)/qconf.o: $(KCONFIG_SRCDIR)/qconf.cc
	@echo "  CXX     $@"
	@$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c -o $@ $<

$(OBJDIR)/images.o: $(KCONFIG_SRCDIR)/images.c
	@echo "  CC      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

$(OBJDIR)/qconf-moc.o: $(OBJDIR)/qconf-moc.cc
	@echo "  CXX     $@"
	@$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c -o $@ $<

$(OBJDIR)/qconf-moc.cc: $(KCONFIG_SRCDIR)/qconf.h
	@echo "  MOC     $@"
	@$(MOC) $(KCONFIG_SRCDIR)/qconf.h -o $@

# Lexer and parser rules
$(OBJDIR)/lexer.lex.o: $(OBJDIR)/lexer.lex.c
	@echo "  CC      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $(OBJDIR)/lexer.lex.c

$(OBJDIR)/lexer.lex.c: $(KCONFIG_SRCDIR)/lexer.l $(OBJDIR)/parser.tab.h
	@echo "  FLEX    $@"
	@$(FLEX) -o $@ $<

$(OBJDIR)/parser.tab.o: $(OBJDIR)/parser.tab.c
	@echo "  CC      $@"
	@$(CC) $(CPPFLAGS) $(CFLAGS) -DYYDEBUG -c -o $@ $(OBJDIR)/parser.tab.c

$(OBJDIR)/parser.tab.c $(OBJDIR)/parser.tab.h: $(KCONFIG_SRCDIR)/parser.y
	@echo "  BISON   $@"
	@$(BISON) -d --verbose -o $(OBJDIR)/parser.tab.c $<

conf: $(BINDIR)/conf
nconf: $(BINDIR)/nconf
mconf: $(BINDIR)/mconf
qconf: $(BINDIR)/qconf
gconf: $(BINDIR)/gconf

.PHONY: all clean conf nconf mconf qconf gconf

clean:
	rm -f $(KCONFIG_SRCDIR)/conf $(KCONFIG_SRCDIR)/nconf $(KCONFIG_SRCDIR)/mconf $(KCONFIG_SRCDIR)/qconf $(KCONFIG_SRCDIR)/gconf
	rm -f $(KCONFIG_SRCDIR)/*.o $(KCONFIG_SRCDIR)/*.lex.c $(KCONFIG_SRCDIR)/*.output $(KCONFIG_SRCDIR)/*.tab.c $(KCONFIG_SRCDIR)/*.tab.h $(KCONFIG_SRCDIR)/*-moc.cc
